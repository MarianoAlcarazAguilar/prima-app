import os
import pandas as pd
from datetime import datetime, timezone
from my_apis.sf_connection import SalesforceConnection
from my_apis.mb_connection import MetabaseConnection

class MPsFinder:
    '''
    Esta clase tiene toda la funcionalidad necesaria para busar MPs con base en productos y estados seleccionados
    '''
    def __init__(self, sfc:SalesforceConnection, mbc:MetabaseConnection, user:str) -> None:
        self.__DATABASE_ID = 6
        self.__RM_SEARCH_LOG_TEMPLATE = 'templates/rm_search_log_template.xlsx'
        self.__RM_SEARCH_LOG = 'logs/rm_search_log.parquet'
    
        self.__sfc = sfc
        self.__mbc = mbc
        self.__user = user
        self.__catalogue = self.__load_catalogue()
        self.__states = self.__load_states()
        self.__addresses = self.__load_addresses()
        self.__mps = self.__load_mps()
        self.__rm_mps = self.__load_rm_mps(interval_days=30)
        self.__rm_mps_db = self.__load_rm_mps_db()

        self.__start_search_log(self.__RM_SEARCH_LOG_TEMPLATE, self.__RM_SEARCH_LOG)

    def __load_addresses(self) -> pd.DataFrame:
        '''
        Esta función carga las direcciones de los MPs
        '''
        direcciones = self.__execute_query_in_sf(
            query='queries/addresses.sql',
            is_path=True,
            rename_output={'Account__c':'mp_id', 'location__StateCode__s':'state_code'}
        )
        return direcciones
        
    def __load_mps(self) -> pd.DataFrame:
        '''
        Esta función carga los MPs de manufactura para poder filtrarlos como se desee.
        '''
        rename_dict = {
            'Account_Status__c':'status',
            'Completed_Work_Orders__c':'wos',
            'Number_of_RFQs_MP_has_quoted__c':'quotes', 
            'NDA_status__c':'nda',
            'truora_test__c':'truora',
            'syntage_test__c':'syntage',
            'Id':'mp_id'
        }

        mps = self.__execute_query_in_sf(
            query='queries/mps_manufacturing.sql',
            is_path=True,
            rename_output=rename_dict
        )

        capabilities = (
            mps
            .rename(lambda x: x.replace('_capability__c', ''), axis=1)
            .rename(lambda x: x.replace('__c', ''), axis=1)
            .merge(self.__addresses, on='mp_id', how='inner')
            .merge(self.__states, on='state_code')
            .query('main_process != "Material Sourcing"') # Quitamos a los MPs de raw materials
        )
        return capabilities
    
    def get_picklists_lists(self) -> tuple:
        '''
        Esta función regresa las opciones disponibles de filtrado y de display para las columnas que se usan en los MPs de manufactura.
        También regresa los main processes disponibles.

        :return: (list of filter columns, list of display columns, list of main processes)
        '''
        main_processes = self.__mps.main_process.dropna().unique().tolist()
        
        filter_columns = [
            'machining',
            'logistics',
            'formation',
            'tooling',
            'heavy_fab',
            'laboratory',
            'finishing',
            'joining_welding',
            'light_fab',
            'other'
        ]

        display_columns = [
            'main_process',
            'status',
            'wos',
            'quotes',
            'nda',
            'truora',
            'syntage',
            'last_wo_date',
            'global_score'
        ]
        return filter_columns, display_columns, main_processes
    
    def filter_mps_manufacturing(self, chosen_processes:list, chosen_state:str, show_columns:list, only_active:bool, only_developing:bool, search_region:bool, main_process:str) -> pd.DataFrame:
        '''
        Esta función busca a los MPs que hagan match con los filtros que se quieran aplicar.
        '''
        mps_db = self.__mps
        # 1. Encontramos las columnas por las cuales vamos a ordenar
        sort_columns = ['total_processes']
        available_sort_columns = ['wos', 'quotes', 'global_score'] # Estas son las que están disponibles para ordenar dentro de las opciones
        sort_columns.extend(list(set(available_sort_columns).intersection(set(show_columns))))
        show_columns.append('Name')


        # 2. Filtramos ubicaciones dependiendo de lo que quieran
        if search_region:
            chosen_region = self.__states.query('state == @chosen_state').region.values[0]
            location_filter = mps_db.query('region == @chosen_region')
            show_columns.append('state')
        else: 
            location_filter = mps_db.query('state == @chosen_state')


        # 3. Filtramos el status deseado (o ninguno)
        if only_active and only_developing: 
            status_filter = location_filter.query('wos > 0 or quotes > 0')
        elif only_active: 
            status_filter = location_filter.query('wos > 0')
        elif only_developing: 
            status_filter = location_filter.query('status == "Developing MP (Quoted)"')
        else: 
            status_filter = location_filter


        # 4. Filtramos solo aquellos del main process deseado
        process_name_match = {
            'machining':'Machining',
            'logistics':'Logistics',
            'formation':'Metal Formation',
            'tooling':'Other', #   WARNING : FALTA DEFINIR EL MAIN PROCESS DE TOOLING
            'heavy_fab':'Heavy Fab',
            'laboratory':'Laboratory',
            'finishing':'Finishing',
            'joining_welding':'Joining and Welding',
            'light_fab':'Light Fabrication',
            'other':'Other'
        }
        process_filter = status_filter
        if main_process is not None: 
            main_process = process_name_match[main_process]
            process_filter = status_filter.query('main_process == @main_process')


        filtered_values = (
            process_filter
            .query(' or '.join(chosen_processes)) # filtramos los procesos que se quiere
            .drop_duplicates(subset=['Name'])
            .set_index(show_columns)
            [chosen_processes]
            .astype(int)
            .assign(total_processes=lambda x: x.sum(axis=1))
            .sort_values(sort_columns, ascending=False)
            .drop(['total_processes'], axis=1)
            .astype(bool)
            .reset_index()
            .set_index('Name')
        )
        return filtered_values
        
    def __start_search_log(self, log_template:str, log_path:str) -> bool:
        '''
        Esta función inicia un nuevo search log. Literal lo único que hace es leer el template
        de excel y lo pasa a un parquet

        :param log_template: ubicación del archivo excel con el formato del log
        :param log_path: dónde se quiere guardar el nuevo archivo

        :return: booleano indicando si el archivo se creó (True) o si no se creó pues ya existía (False)

        Eg. start_search_log('../templates/raw_materials_search_log.xlsx', '../rm_search_log.parquet')
        '''
        search_log_extension = log_path.split('.')[-1]
        template_extension = log_template.split('.')[-1]
        
        if search_log_extension != 'parquet':
            raise Exception('Search log file must be parquet type')

        # Revisamos que el search log no exista, porque sino lo sobreescribiríamos
        if os.path.exists(log_path): 
            return False
            
        if template_extension == 'xlsx':
            template = pd.read_excel(log_template)
        elif template_extension == 'csv':
            template = pd.read_csv(log_template)
        else:
            raise Exception(f'Unsupported format for template: {template_extension}')

        template.to_parquet(log_path, index=False)
        return True
    
    def __add_search_log_entry(self, search_log_path:str, entry_dict:dict) -> None:
        '''
        Esta función se encarga de registrar una búsqueda en el log de búsquedas.
        La ventaja es que funciona para cualquier tipo de log, sin importar si las columnas son diferentes.
        Esto es útil si las búsquedas tienen diferentes parámetros que se quieren guardar.

        :param search_log_path: ubicación del archivo parquet del log que se está usando
        :param entry_dict: diccionario con los datos de la nueva entrada. Se verifica que las columnas coincidan
        '''
        # Convertimos el diccionario a dataframe
        search_log_extension = search_log_path.split('.')[-1]
        
        if search_log_extension != 'parquet':
            raise Exception(f'Unsupported format for search log: {search_log_extension}')

        try:
            search_log = pd.read_parquet(search_log_path)
        except FileNotFoundError:
            self.__start_search_log(self.__RM_SEARCH_LOG_TEMPLATE, self.__RM_SEARCH_LOG)
            search_log = pd.read_parquet(search_log_path)
        new_entry = pd.DataFrame({key: [value] for key, value in entry_dict.items()})
        
        # Verificamos que las columnas coincidan con las del search log
        cols_are_equal = set(search_log.columns) == set(new_entry.columns)
        
        if not cols_are_equal: 
            missing_cols = set(search_log.columns) - set(new_entry.columns)
            raise Exception(f'Missing columns in new entry: {missing_cols}')
            
        # Juntamos los dataframes y los guardamos
        # Nos aseguramos de que no esté vacío el log actual, porque sino es mamona la chingadera esta
        if search_log.size > 0:
            pd.concat((search_log, new_entry), ignore_index=True).to_parquet(search_log_path, index=False)
        else:
            new_entry.to_parquet(search_log_path, index=False)

    def get_product_catalgue(self) -> pd.DataFrame:
        return self.__catalogue
    
    def get_mps_db(self) -> pd.DataFrame:
        return self.__rm_mps_db
    
    def get_states(self) -> pd.DataFrame:
        return self.__states
    
    def get_mps(self) -> pd.DataFrame:
        return self.__rm_mps

    def __execute_query_in_sf(self, query:str, is_path:bool=False, rename_output:dir={}) -> pd.DataFrame:
        '''
        Esta función ejecuta un query en salesforce y regresa los resultados en un dataframe.
        '''
        if is_path:
            with open(query, 'r') as f:
                query = f.read()

        sf_data = (
            self
            .__sfc
            .extract_data(query)
            .rename(rename_output, axis=1)
        )
        
        return sf_data
    
    def __execute_query_in_mb(self, query:str, is_path:bool=False, id_col:str=None) -> pd.DataFrame:
        '''
        Esta función ejectua un query en metabase y regresa los resultados en un dataframe.

        :param query: el query a ejecutar, puede ser el path a un sql file.
        :param is_path: wether or not to load the query from the specified file 
        :param id_col: id_col es necesario cuando se extraen más de 2,000 registros de MB porque es por el que se ordenan para poder sacarlos todos.
        '''
        if is_path:
            with open(query, 'r') as f:
                query = f.read()

        try:
            mb_data = (
                self
                .__mbc
                .query_data(query, database_id=self.__DATABASE_ID)
            )
        except UserWarning:
            assert id_col is not None, "Es necesario especificar id_col"
            mb_data = (
                self
                .__mbc
                .query_more_data(query, database_id=self.__DATABASE_ID, id_col=id_col)
            )

        return mb_data

    def __load_catalogue(self) -> pd.DataFrame:
        '''
        Esta función saca el catálogo de productos de raw materials de Salesforce.

        :return: catálogo en df
        '''
        catalogue = self.__execute_query_in_sf(
            query='queries/products_catalogue.sql', 
            is_path=True, 
            rename_output={'Id':'product_id', 'Name':'product_name', 'Family':'product_family', 'rm_material__c':'material'}
        )
        return catalogue
    
    def __load_rm_mps(self, interval_days:int=30) -> pd.DataFrame:
        '''
        Esta función carga la lista de MPs y sus nombres.

        :param interval_days: el número de días a considerar para buscar los quotes y wos que los MPs han hecho.
        '''
        mps = self.__execute_query_in_sf(
            query='queries/mps_names.sql',
            is_path=True,
            rename_output={'Id':'mp_id', 'Name':'mp_name', 'Account_Status__c':'status', 'supply_chain_category__c':'mp_type', 'global_score__c':'score'}
        )

        docs_on_interval = self.__load_docs_on_interval(interval_days=interval_days)

        mps = (
            mps
            .merge(docs_on_interval, on='mp_id', how='left')
            .fillna({'quotes':0, 'wos':0})
            .astype({'quotes':int, 'wos':int})
        )

        return mps
    
    def __date_on_interval(self, date:pd.DatetimeIndex, n_days:int=30) -> bool:
        '''
        Esta función verifica si la fecha dada está en el intervalo de días especificado a partir del día de hoy.

        :param date: fecha a evaluar
        :param n_days: número de días en el intervalo a considerar

        :return: booleano si la fecha está o no en ese intervalo
        '''
        fecha_actual = datetime.now(timezone.utc)
        diferencia = (fecha_actual - date).days
        return abs(diferencia) <= n_days
    
    def __load_docs_on_interval(self, interval_days:int=30) -> pd.DataFrame:
        '''
        Esta función carga el número de quotes y working orders que los MPs han tenido en el intervalo de tiempo especificado.

        :param interval_days: número de días hacia atrás a partir de hoy a considerar.

        :return: dataframe con columnas mp_id (sf id for accounts), qutoes, wos correspondiente al número de documentos en el intervalo
        '''
        docs_data = self.__execute_query_in_mb(
            query='queries/docs_on_interval.sql',
            is_path=True,
            id_col='doc_id'
        )

        docs_on_interval = (
            docs_data
            .assign(
                doc_date=lambda x: pd.to_datetime(x.doc_date, format='ISO8601'),
                on_interval=lambda df: df.doc_date.apply(lambda x: self.__date_on_interval(x, interval_days))
            )
            .query('on_interval')
            .pivot_table(
                index='mp_id',
                columns='tipo',
                values='doc_id',
                aggfunc='count',
                fill_value=0
            )
            .reset_index()
        )
        return docs_on_interval

    def __load_states(self) -> pd.DataFrame:
        '''
        Esta función carga los estados y sus códigos

        :return: pd.DataFrame con los estados y sus códigos
        '''
        state_codes = (
            self
            .__execute_query_in_sf(
                query='queries/states.sql',
                is_path=True,
                rename_output={'States__c':'state', 'state_code__c':'state_code', 'Region__c':'region'}
            )
            .replace({'Ciudad de México':'Mexico City'})
        )
        return state_codes 
    
    def __load_rm_mps_db(self) -> pd.DataFrame:
        '''
        Esta función se encarga de crear un dataframe con los MPs, sus respectivas ubicaciones y productos

        :return: pd.DataFrame
        '''
        existing_products = self.__execute_query_in_sf(
            query='queries/mps_products.sql',
            is_path=True,
            rename_output={'product__c':'product_id', 'account__c':'mp_id'}
        )

        direcciones = self.__addresses

        db = (
            direcciones
            .merge(self.__rm_mps, on='mp_id', how='left')
            .merge(self.__states, on='state_code')
            .merge(existing_products, on='mp_id')
            .merge(self.__catalogue, on='product_id')
        )

        return db

    def filter_mps_raw_materials(self, products:list, state:str, show_region_mps:bool, show_quotes:bool, show_wos:bool, show_status:bool, show_type:bool, show_score:bool) -> pd.DataFrame:
        '''
        Esta función busca los mps que hagan match con los filtros especificados.

        :param products: lista con los nombres de los productos
        :param state: string con el nombre del estado que se desea buscar

        :return: dataframe formateado para el display
        '''
        pivot_index = ['mp_name']
        if show_quotes: pivot_index.append('quotes')
        if show_wos: pivot_index.append('wos')
        if show_status: pivot_index.append('status')
        if show_type: pivot_index.append('mp_type')
        if show_score: pivot_index.append('score')
    
        if not show_region_mps:
            search_result = (
                self
                .__rm_mps_db
                .query('product_name in @products')
                .query('state == @state')
                .drop_duplicates(subset=['mp_id', 'product_id'])
                .pivot(index=pivot_index, columns='product_name', values='state')
                .fillna(0)
                .astype(bool)
                .assign(total_products=lambda x: x.sum(axis=1))
                .sort_values('total_products', ascending=False)
                .reset_index()
                .set_index('mp_name')
            )
        else:
            state_region = self.__states.query('state == @state').region.values[0]
            pivot_index.append('state')
            search_result = (
                self
                .__rm_mps_db
                .query('product_name in @products')
                .query('region == @state_region')
                .drop_duplicates(subset=['mp_id', 'product_id'])
                .pivot(index=pivot_index, columns='product_name', values='state')
                .fillna(0)
                .astype(bool)
                .assign(total_products=lambda x: x.sum(axis=1))
                .sort_values(['total_products', 'state'], ascending=False)
                .reset_index()
                .set_index('mp_name')
                .rename({'state':state_region}, axis=1)
            )
        return search_result.drop(['total_products'], axis=1)
    
    def register_raw_materials_search(self, products:list, state:str, chosen_mps:list, show_region_mps:bool, show_quotes:bool, show_wos:bool, show_status:bool, show_type:bool, show_score:bool) -> None:
        '''
        Esta función se encarga de registrar las búsquedas que los usuarios hagan de raw_materials. 
        Queremos tener control de qué MPs buscan y cuándo.
        '''
        entry_dict = {
            'user':self.__user,
            'date':datetime.now(),
            'state':state,
            'products':products,
            'mps':chosen_mps,
            'region':show_region_mps,
            'quotes':show_quotes,
            'wos':show_wos,
            'status':show_status,
            'type':show_type,
            'score':show_score
        }

        self.__add_search_log_entry(search_log_path=self.__RM_SEARCH_LOG, entry_dict=entry_dict)
    
    def get_contact_info(self, mps:list) -> pd.DataFrame:
        '''
        Dada una lista de nombres de mps, regresa la información de los contactos relacionados.

        :param mps: lista con los nombres de los MPs que se buscan

        :return: pd.DataFrame con los contactos, regresa None si no hay contactos relacionados
        '''
        chosen_mps_ids = self.__rm_mps.query('mp_name in @mps').mp_id.values.tolist()
        if len(chosen_mps_ids) == 0: return None

        query = f'''
        select AccountId, LastName, FirstName, Phone, MobilePhone, Email, Title
        from Contact
        where {' or '.join([f"AccountId = '{mp_id}'" for mp_id in chosen_mps_ids])}
        '''

        try:
            aux_contacts = self.__execute_query_in_sf(query)
        except KeyError:
            return None
        mps_contacts = (
            aux_contacts
            .dropna(subset=['Phone', 'MobilePhone', 'Email', 'Title'], how='all')
            .rename({'AccountId':'mp_id'}, axis=1)
            .merge(self.__rm_mps[['mp_id', 'mp_name']], on='mp_id')
            .set_index('mp_name')
            .drop(['mp_id'], axis=1)
            .dropna(axis=1, how='all')
        )

        return mps_contacts