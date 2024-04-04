import streamlit as st
import pandas as pd
from st_functions import *

def render_page():
    open_styles()
    if not user_is_verified(): return
    st.title('MPs Finder')
    add_description_to_page('Elige los <b>productos y estados</b> que buscas')
    # Aquí sabemos ya que automations está cargado, por lo tanto, no se va a romper el finder
    allow_filtering()

def allow_filtering():
    finder = load_finder()
    products_options = finder.get_product_catalgue().product_name.sort_values().to_list()
    state_options = finder.get_states().state.sort_values().to_list()

    chosen_state = st.sidebar.selectbox(
        label='Choose state',
        options=state_options
    )

    chosen_products = st.sidebar.multiselect(
        label='Choose products',
        options=products_options
    )

    # Permitimos agregar opciones adicionales
    st.sidebar.text('Choose aditional options')
    col1, col2, col3 = st.sidebar.columns(3)
    show_region_mps = col1.checkbox('Region')
    show_quotes = col2.checkbox('Quotes')
    show_wos = col3.checkbox('Wos')
    show_status = col1.checkbox('Status')
    show_type = col2.checkbox('Type')
    show_score = col3.checkbox('Score')

    if len(chosen_products) == 0 : 
        st.text('Please choose products to continue')
        return

    search_results = finder.filter_mps_raw_materials(
        chosen_products, 
        chosen_state,
        show_region_mps=show_region_mps,
        show_quotes=show_quotes,
        show_wos=show_wos,
        show_status=show_status,
        show_type=show_type,
        show_score=show_score
    )
    
    if search_results.size <= 0:
        st.warning('No MPs were found with that criteria')
        return 
    
    # Revisamos que no falten productos
    columns = search_results.columns.to_list()
    # columns.remove('total_products')
    missing_products = list(set(chosen_products).difference(columns))
     
    
    st.markdown('### MPs Found')
    st.dataframe(
        search_results.reset_index(), 
        use_container_width=True, 
        hide_index=True
    )
    if len(missing_products) > 0:
        st.warning(f'This products were NOT found:\n {missing_products}')

    available_mps = search_results.index.values
    chosen_mps = st.sidebar.multiselect(
        label='Choose MP for contact information', 
        options=available_mps
    )

    if len(chosen_mps) == 0: return

    if not st.sidebar.button('🔍'): return

    # Aquí guardamos la búsqueda
    # Esto nos permitirá mejorar el modelo de matching eventualmente
    finder.register_raw_materials_search(
        products=chosen_products,
        state=chosen_state,
        chosen_mps=chosen_mps,
        show_region_mps=show_region_mps,
        show_quotes=show_quotes,
        show_wos=show_wos,
        show_status=show_status,
        show_type=show_type,
        show_score=show_score
    )

    contact_info = finder.get_contact_info(
        mps=chosen_mps
    )

    if contact_info.size <= 0:
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