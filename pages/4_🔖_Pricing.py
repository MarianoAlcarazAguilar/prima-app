import streamlit as st
import pandas as pd
from scripts.st_functions import *

def render_page():
    open_styles()
    if not user_is_verified(): return
    st.title('Pricing Hub')
    add_description_to_page('Esta página permite acceder a los items de las quotations')
    
    # Ahora sí podemos hacer lo que queramos con los items
    # Lo primero que quiero probar es obtener información con base en el rfq id
    # Necesitamos que el usuario cargue las credenciales y el json de sheets
    
    show_rfq_info()

def show_rfq_info():
    '''
    Esta función administra la funcionalidad necesaria para ver los datos de un rfq
    '''
    # Aquí sabemos que el usuario ya está dado de alta
    item_manager = load_item_manager()

    rfq_id = st.sidebar.number_input('RFQ ID', min_value=1, placeholder="Type a number...", value=None)
    if rfq_id is None: return

    

    data_dict = item_manager.get_rfq_info(rfq_id)
    
    if data_dict is None: 
        st.warning(f'There is no information available for RFQ {rfq_id}')
        return
    
    st.sidebar.dataframe(data_dict['rfq_info'], use_container_width=True)

    tab_display_prices, tab_classify_items = st.tabs(['Quotations', 'Items'])
    height = (data_dict['quotations'].shape[0] + 1)*35+3

    with tab_display_prices:
        st.dataframe(
            data_dict['quotations'], 
            use_container_width=True,
            height=height
        )

    with tab_classify_items:
        automations = st.session_state.automations
        if automations.get_user() not in ["mariano.alcaraz@prima.ai", "fernando.villalobos@prima.ai"]:
            st.info('Sorry, you are not authorized to view this page')
            return
        
        changed_data = st.data_editor(
            item_manager.allow_item_classification(rfq_id),
            use_container_width=True,
            height=height,
            column_config={
                'category':st.column_config.SelectboxColumn(
                    label='Categoría',
                    width='medium',
                    help='Choose the main category',
                    default=None,
                    options=item_manager.categories
                ),
                'subcategory':st.column_config.SelectboxColumn(
                    label='Subcategoría',
                    width='medium',
                    help='Elige la subcategoría',
                    default=None,
                    options=item_manager.subcategories
                ),
                'item_id':st.column_config.TextColumn(
                    label='Item'
                )
            }
        )
        
        col_button, col_succes = st.columns((.2,.8))
        if not col_button.button('✔ Done'): return
        
        item_manager.add_new_entry(rfq_id=rfq_id, categories=changed_data)
        col_succes.success('Changes have been saved')

    

if __name__ == '__main__':
    render_page()