import streamlit as st
import pandas as pd
from scripts.st_functions import *

def render_page():
    open_styles()
    if not user_is_verified(): return
    st.title('MPs Finder')
    add_description_to_page('Encuentra a los <b>MPs que estés buscando</b> con los siguientes filtros')
    allow_filtering()

def allow_filtering():
    finder = load_finder()
    available_processes, available_show_columns, available_main_processes = finder.get_picklists_lists()
    state_options = finder.get_states().state.sort_values().to_list()

    chosen_processes = st.sidebar.multiselect(
        label='Choose processes',
        options=available_processes
    )

    if len(chosen_processes) == 0: return

    
    chosen_state = st.sidebar.multiselect(
        label='Choose state',
        options=state_options,
        max_selections=1
    )

    if len(chosen_state) == 0: return
    chosen_state = chosen_state[0]

    display_columns = st.sidebar.multiselect(
        label='Choose columns to display',
        options=available_show_columns
    )

    # Opciones adicionales
    st.sidebar.text('Choose aditional options')
    col_1, col2 = st.sidebar.columns(2)
    only_active = col_1.checkbox('Active')
    search_region = col_1.checkbox('Search Region')
    only_developing = col2.checkbox('Developing')
    filter_by_main_process = col2.checkbox('Main process')
    

    if filter_by_main_process: 
        if len(chosen_processes) > 1:
            main_process = st.sidebar.selectbox('Choose main process', chosen_processes)
        else:
            main_process = chosen_processes[0]
    else: 
        main_process = None

    found_mps = finder.filter_mps_manufacturing(
        chosen_processes=chosen_processes,
        chosen_state=chosen_state,
        show_columns=display_columns,
        only_active=only_active,
        only_developing=only_developing,
        search_region=search_region,
        main_process=main_process
    )

    if found_mps.size <= 0:
        st.warning('No MPs were found with that criteria')
        return 

    st.markdown('### MPs Found')
    st.dataframe(found_mps, use_container_width=True)

    available_mps = found_mps.index.values
    chosen_mps = st.sidebar.multiselect(
        label='Choose MP for contact information', 
        options=available_mps
    )

    if len(chosen_mps) == 0: return
    if not st.sidebar.button('🔍'): return

    contact_info = finder.get_contact_info(
        mps=chosen_mps
    )

    if contact_info is None or contact_info.size <= 0:
        st.warning('There is no contact information on those MPs')
        return
    
    st.markdown('#### Contact Information')
    st.dataframe(
        contact_info,
        use_container_width=True, 
        hide_index=False
    )



if __name__ == '__main__':
    render_page()