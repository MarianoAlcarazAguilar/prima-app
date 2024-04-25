import os
import warnings
import numpy as np
import pandas as pd
from my_apis.mb_connection import MetabaseConnection
from my_apis.sheets_functions import SheetsFunctions
from my_apis.sf_connection import SalesforceConnection, SalesforceFunctions

class ItemManager:
    '''
    Esta clase permite que los ususarios interactúen con los items de ichigo
    '''
    def __init__(self, mbc:MetabaseConnection, sf:SheetsFunctions, sfc:SalesforceFunctions) -> None:
        warnings.filterwarnings('error') # Para poder cachar warnings como exceptions.

        self.__DATABASE_ID = 6
        self.__CATEGORIES_FILE = 'templates/pricing_catalogue.xlsx'
        
        self.__sfc = sfc
        self.__sff = SalesforceFunctions(sfc)
        self.__mbc = mbc
        self.__items = self.__load_items()
        self.__manufacturing_products = self.__load_products()
        self.categories, self.subcategories = self.__load_categories() 
        self.__sheets = sf

    def __load_products(self) -> pd.DataFrame:
        '''
        TODO: función que cargue los productos existentes en Salesforce de manufactura con columnas id, Name, manufacturing_product_category__c
        '''

    def add_new_entry(self, rfq_id:int, categories:pd.DataFrame):
        
        new_entry = (
            self
            .__items
            .query(f'rfq_id == {rfq_id}')
            .merge(categories.dropna(), on='item_id') # No queremos guardarlos si no tienen tanto categoría como subcategoría
            .dropna(subset=['unit_price'])
            .query('unit_price != 0')
        )

        # TODO: mandar estos datos a salesforce
        new_entry.to_excel('templates/auxiliar_new_entry.xlsx', index=False)

        self.__sheets.add_multiple_records(new_entry, drop_duplicates=['rfq_id', 'item_id', 'mp_id'])

    def get_rfq_info(self, rfq_id:int) -> dict:
        '''
        Esta función regresa un diccionario con la información del item especificado

        :param rfq_id: número del rfq que se busca

        :return: diccionario con la información en el siguiente formato, o None si no se encontró el rfq.
        {
            'quotations':pd.DataFrame,
            'rfq_info':pd.DataFrame
        }
        '''
        items = self.__items

        if rfq_id not in items.rfq_id.values: return None

        data_dict = {
            'quotations': self.__get_items_from_rfq(rfq_id),
            'rfq_info': self.__get_rfq_info_df(rfq_id)
        }
        return data_dict

    def __get_items_from_rfq(self, rfq_id:int) -> pd.DataFrame:
        '''
        Esta función auxiliar da formato a los items de un rfq dado

        :param rfq_id: id del rfq que se busca
        :param transpose: si se quiere transponer el df resultante para darle más importancia a los MPs que los items
        '''
        answer = (
            self
            .__items
            .query('rfq_id == @rfq_id')
            .pivot_table(index='item_id', columns='mp_name', values='unit_price', aggfunc='first')
            .replace({0.0:None, np.NaN:None})
            .dropna(how='all', axis=0)
        )
        transpose = answer.columns.size > answer.index.size
        transpose = False
        if transpose: answer = answer.transpose()
        return answer
    
    def __get_rfq_info_df(self, rfq_id:int) -> pd.DataFrame:
        '''
        Saca los datos del rfq porque sino vienen repetidos

        :param rfq_id: el id del rfq que se busca
        '''
        answer = (
            self
            .__items
            .query('rfq_id == @rfq_id')
            [['rfq_name', 'customer_name', 'main_process', 'pod', 'rfq_id']]
            .drop_duplicates()
            .set_index('rfq_id')
            .transpose()
        )
        return answer
    
    def __load_categories(self) -> tuple:
        '''
        Esta función regresa los datos de las categorías y subacategorías disponibles para la calsificación
        '''
        # TODO: utilizar el catálogo de productos que se cargó de sf en vez del excel, pues ese no se estará actualizando
        data = pd.read_excel(self.__CATEGORIES_FILE)
        
        categories = data.category.dropna().sort_values().unique().tolist()
        subcategories = data.sub_category.dropna().sort_values().unique().tolist()

        return categories, subcategories
    
    def get_subcategories(self, category:str) -> list:
        '''
        Esta función da una lista de las subcategorías correspondientes a la categoría especificada

        :param category: nombre de la categoría que se busca

        :return: lista con las subcategorías, None en caso de que la categoría no coincida con ninguna existente
        '''
        if category is None:
            return []
        subcategories = (
            self
            .__subcategories
            .query('category == @category')
            .sub_category
            .sort_values()
            .dropna()
            .unique()
            .tolist()
        )
        return subcategories
    
    def allow_item_classification(self, rfq_id:int) -> pd.DataFrame:
        '''
        Esta función te da los items de un rfq con sus respectias columnas para permitir que el usuario seleccione las que quiera

        :param rfq_id: id del rfq que se busca
        :return: pd.DataFrame
        '''
        items = self.__items
        if rfq_id not in items.rfq_id.values: return None

        answer = (
            self
            .__items
            .query('rfq_id == @rfq_id')
            [['item_id']]
            .drop_duplicates()
            .assign(
                category=None, 
                subcategory=None
            )
            .set_index('item_id')
        )
        return answer

    def get_items(self) -> pd.DataFrame:
        return self.__items

    def __load_items(self) -> pd.DataFrame:
        '''
        Esta función saca los items de los RFQs que están en Metabase
        '''
        items = (
            self
            .__execute_query_in_mb(
                query='queries/items_quotations.sql',
                id_col='item_quote_id'
            )
        )
        return items

    def __execute_query_in_mb(self, query:str, id_col:str=None) -> pd.DataFrame:
        '''
        Esta función ejectua un query en metabase y regresa los resultados en un dataframe.

        :param query: el query a ejecutar, puede ser el path a un sql file.
        :param id_col: id_col es necesario cuando se extraen más de 2,000 registros de MB porque es por el que se ordenan para poder sacarlos todos.
        '''
        original_query = query
        try:
            with open(original_query, 'r') as f:
                query = f.read()
        except FileNotFoundError:
            query = original_query

        try:
            mb_data = (
                self
                .__mbc
                .query_data(query, database_id=self.__DATABASE_ID)
            )
        except UserWarning:
            if id_col is None:
                raise('Es necesario especificar id_col')
            
            mb_data = (
                self
                .__mbc
                .query_more_data(query, database_id=self.__DATABASE_ID, id_col=id_col)
            )

        return mb_data