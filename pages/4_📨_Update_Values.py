import streamlit as st
import pandas as pd
from scripts.st_functions import *

def show_errors(errors:list):
    if len(errors) == 0: return
    
    errors_df = pd.DataFrame(errors)[['Index']]
    st.markdown('##### Errores')
    st.dataframe(errors_df, use_container_width=True, hide_index=True)


def render_page():
    open_styles()
    if not user_is_verified(): 
        return
    if not st.session_state.full_login:
        st.info("Access with full credentials to see this page")
        return
    
    automations = st.session_state.automations
    if automations.get_user() != "mariano.alcaraz@prima.ai":
        st.warning('Sorry, you are not authorized to view this page')
        return
    else:
        st.title('Hello Mariano')
    
    add_description_to_page('Elige el tipo de valor que deseas actualizar.')
    choice = st.sidebar.radio('Update', options=['WOs & Quotes', 'MP Status', 'Main Process', 'OTIF', 'Scorecards', 'Last WOs Date'], label_visibility='collapsed')

    if choice == 'WOs & Quotes':
        update_wos_quotes()
    elif choice == 'MP Status':
        update_status()
    elif choice == 'Main Process':
        update_main_process()
    elif choice == 'OTIF':
        update_otif()
    elif choice == 'Scorecards':
        update_scorecards()
    elif choice == 'Last WOs Date':
        update_last_wo_date()

def update_scorecards():
    automations = st.session_state.automations

    st.markdown('### Sube el archivo de Excel')
    
    col_file, col_sheet = st.columns(2)

    file = col_file.file_uploader('Sube el excel con scores', type=['xlsx'], accept_multiple_files=False, label_visibility='collapsed')

    if file:
        # Handle multiple sheet names
        sheets = get_sheet_names(file)
        if len(sheets) > 1:
            col_sheet.markdown('##### Elige la hoja')
            sheet_name = col_sheet.selectbox('Elige la hoja', options=sheets, label_visibility='collapsed')
        else:
            sheet_name = sheets[0]

        if sheet_name is not None:
            if st.button('Update Scorecards'):
                try:
                    errors = automations.update_scorecards(
                        file=file,
                        sheet_name=sheet_name,
                        verbose=False
                    )
                    st.success('Scorecard values have been updated')
                    show_errors(errors)
                except IndexError:
                    st.error('No se encontró el ID del MP')

def update_otif():
    automations = st.session_state.automations
    mb_query = 'queries/otif_mb.sql'
    sf_query = 'queries/otif_sf.sql'
    mb_is_path = True
    sf_is_path = True
    verbose = False

    if st.button('Update OTIF'):
        errors = automations.update_otif(
            mb_query = mb_query,
            sf_query = sf_query,
            mb_is_path = mb_is_path,
            sf_is_path = sf_is_path,
            verbose = verbose
        )
        st.success('OTIF values have been updated')
        show_errors(errors=errors)

def update_main_process():
    automations = st.session_state.automations
    mb_query = 'queries/process_count_mb.sql'
    sf_query = 'queries/main_process_sf.sql'

    if st.button('Update Main Process'):
        errors, diferentes = automations.update_main_process(
            mb_query = mb_query,
            sf_query = sf_query,
            mb_is_path = True,
            sf_is_path = True,
            verbose=True
        )
        st.success('Main Processes have been updated')
        col_errores, col_diferentes = st.columns((.25,.75))
        with col_errores:
            show_errors(errors)

        with col_diferentes:
            st.markdown('##### Asignaciones distintas')
            st.dataframe(diferentes, use_container_width=True, hide_index=False)


def update_status():
    automations = st.session_state.automations
    query = 'queries/status_mb.sql'

    if st.button('Update Status'):
        errors = automations.update_status(
            query=query,
            is_path=True,
            verbose=True
        )
        st.success('Status has been updated.')
        show_errors(errors=errors)


def update_wos_quotes():
    automations = st.session_state.automations
    mb_query = 'queries/wos_quotes_mb.sql'
    sf_query = 'queries/wos_quotes_sf.sql'

    if st.button('Update WOs and Quotes'):
        errors = automations.update_wos_quotes(
            mb_query=mb_query,
            sf_query=sf_query,
            mb_is_path=True,
            sf_is_path=True,
            verbose=True
        )
        st.success('WOs and Quotes have been updated')
        show_errors(errors=errors)

def update_last_wo_date():
    automations = st.session_state.automations

    mb_query = 'queries/last_wo_date_mb.sql'
    sf_query = 'queries/last_wo_date_sf.sql'

    if st.button('Update last wo dates'):
        errors = automations.update_last_wo_date(
            mb_query=mb_query,
            sf_query=sf_query,
            mb_is_path=True,
            sf_is_path=True,
            verbose=True
        )
        st.success('Last wo dates have been updated')
        show_errors(errors=errors)
    
if __name__ == '__main__':
    render_page()