import json
from st_functions import *
import streamlit as st
from scripts.automations import Automations

def load_credentials() -> Automations:
    '''
    Esta función se encarga de cargar las credenciales necesarias y regresa el objeto ya listo para correr las automatizaciones.

    :return: loaded Automations object
    '''
    mb_col, st_col = st.columns(2)
    # Recibimos los json files con las credenciales
    with mb_col:
        st.markdown('##### Metabase Credentials')
        new_login = st.checkbox('New Login')
        mb_credentials = st.file_uploader('Metabase Credentials', type='json', accept_multiple_files=False, label_visibility='collapsed')

    with st_col:
        st.markdown('##### Salesforce Credentials')
        st.markdown('#')
        sf_credentials = st.file_uploader('Salesforce Credentials', type='json', accept_multiple_files=False, label_visibility='collapsed')    

    if mb_credentials and sf_credentials:
        automations = Automations(
            mb_credentials=json.load(mb_credentials),
            sf_credentials=json.load(sf_credentials),
            new_login=new_login,
            logins_are_paths=False
        )
        if new_login: st.json({'current-token':automations.get_mb_token()}, expanded=False)
        st.success('Your credentials were loaded')
        st.session_state.automations = automations
    

def render_page():
    open_styles()
    add_description_to_page('Carga las credenciales correspondientes.')
    st.title('Upload your credentials')

    # Handle session state
    if ('automations' in st.session_state and st.session_state.automations is None) or 'automations' not in st.session_state:
        load_credentials()
    else:
        st.write('Your credentials are already loaded')
        if st.button('Logout'): 
            st.session_state.automations = None
            st.session_state.finder = None
            st.rerun()

if __name__ == '__main__':
    render_page()