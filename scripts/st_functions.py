import streamlit as st
import openpyxl as xl
from scripts.mps_finder import MPsFinder

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
            user='default-user'
        )
        st.session_state.finder = finder
        return finder
    else:
        return st.session_state.finder
