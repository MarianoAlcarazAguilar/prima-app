import streamlit as st
# import openpyxl as xl
from scripts.mps_finder import MPsFinder
from scripts.item_manager import ItemManager
from my_apis.sheets_functions import SheetsFunctions

def open_styles(location='templates/style.css'):
    
    st.set_page_config(
        layout='wide', 
        initial_sidebar_state='expanded',
        page_title='Prima',
        page_icon='🏬'
    )

    with open(location) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def add_description_to_page(text:str):
    st.sidebar.write(f'''
        <p class="paragraph" align="left">
            {text}
        </p>''',
    unsafe_allow_html=True)

def get_sheet_names(file):
    '''
    Función para sacar los nombres de las sheets en un excel file.

    :param file: bytes o path.
    :return: lista con los nombres
    '''
    return None
    return xl.load_workbook(file).sheetnames

def user_is_verified() -> bool:
    '''
    Esta función revisa que las credenciales ya estén cargadas
    '''
    if 'automations' not in st.session_state or st.session_state.automations is None:
        add_description_to_page('Para poder actualizar los campos disponibles, <b>carga tus credenciales primero</b>')
        st.error('Your credentials are not loaded yet')
        return False
    return True

def load_finder() -> MPsFinder:
    '''
    Solo llamar esta función si automations ya está cargada en session_state
    '''
    automations = st.session_state.automations
    if 'finder' not in st.session_state or st.session_state.finder is None:
        finder = MPsFinder(
            sfc=automations.get_salesforce_connection(), 
            mbc=automations.get_metabase_connection(),
            user=automations.get_user()
        )
        st.session_state.finder = finder
        return finder
    else:
        return st.session_state.finder
    
def load_item_manager() -> ItemManager:
    '''
    Solo llamar esta función si automations ya está cargada en session state
    '''
    automations = st.session_state.automations
    if 'item_manager' not in st.session_state or st.session_state.item_manager is None:
        # Cargamos la funcionalidad de sheets
        sf = SheetsFunctions(
            # Esto es lo que se puede cambiar si se necesita
            spreadsheet_id='1LulC3zt4pxsMXe70W9YtSNJYKY6FvGLWucBAhRBfsH4',
            credentials='templates/sheets_credentials.json',
            token='templates/sheets_token.json',
            sheet_name='Sheet1'
        )

        item_manager = ItemManager(
            mbc=automations.get_metabase_connection(),
            sf=sf,
            sfc=automations.get_salesforce_connection()
        )
        st.session_state.item_manager = item_manager
        return item_manager
    else:
        return st.session_state.item_manager

