import json
from scripts.st_functions import *
import streamlit as st
from scripts.automations import Automations

def load_credentials() -> Automations:
    '''
    Esta función se encarga de cargar las credenciales necesarias y regresa el objeto ya listo para correr las automatizaciones.

    :return: loaded Automations object
    '''
    with st.sidebar.expander('ℹ Help'):
        col1, col2 = st.columns(2)

        col1.markdown('''
        <a href='https://www.loom.com/share/ffe2ad426dc44c9cb3696efba36294d4?sid=393dec18-7f69-425c-9bbf-97952a27642e'>How to get my metabase credentials?</a>
        ''', unsafe_allow_html=True)

        with open('templates/mb_credentials.json', 'r') as f:
            json_string = json.dumps(json.load(f))

        col2.download_button(
            label='📥 Metabase template',
            file_name='mb_credentials.json',
            mime='application/json',
            data=json_string
        )

        show_sf_help = False
        if show_sf_help:
            st.markdown('<hr>', unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            col1.markdown('''
            <a href='https://www.loom.com/share/79d9e76b08d74dc4be67f6529a03cc62?sid=e5b1d3bd-c8cb-4de0-915e-da2f4ace5604'>How to get my salesforce credentials?</a>
            ''', unsafe_allow_html=True) 

            with open('templates/sf_credentials.json', 'r') as f:
                json_string = json.dumps(json.load(f))

            col2.download_button(
                label='📥 Salesforce template',
                file_name='sf_credentials.json',
                mime='application/json',
                data=json_string
            )

    mb_col, st_col = st.columns(2)
    # Recibimos los json files con las credenciales
    with mb_col:
        st.markdown('##### Metabase Credentials')
        new_login = st.checkbox('New Login')
        mb_credentials = st.file_uploader('Metabase Credentials', type='json', accept_multiple_files=False, label_visibility='collapsed')

    login_with_my_sf_credentials = False # si es true va a marcar error hasta que se carguen las credenciales
    with st_col:
        if login_with_my_sf_credentials:
            st.markdown('##### Salesforce Credentials')
            st.markdown('#')
            sf_credentials = st.file_uploader('Salesforce Credentials', type='json', accept_multiple_files=False, label_visibility='collapsed') 
            sf_credentials = json.load(sf_credentials)   
        else:
            sf_credentials=None

    if mb_credentials:
        automations = Automations(
            mb_credentials=json.load(mb_credentials),
            sf_credentials=sf_credentials,
            new_login=new_login,
            logins_are_paths=False,
            sf_login=login_with_my_sf_credentials
        )
        if new_login: st.json({'current-token':automations.get_mb_token()}, expanded=False)
        st.success('Your credentials were loaded')
        st.session_state.automations = automations
    

def render_page():
    open_styles()

    # Handle session state
    if ('automations' in st.session_state and st.session_state.automations is None) or 'automations' not in st.session_state:
        add_description_to_page('Carga las credenciales correspondientes.')
        st.title('Upload your credentials')
        load_credentials()
    else:
        st.title('Your credentials have been loaded')
        if st.sidebar.button('Logout'): 
            st.session_state.automations = None
            st.session_state.finder = None
            st.rerun()

if __name__ == '__main__':
    render_page()