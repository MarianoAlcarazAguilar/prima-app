import streamlit as st
import pandas as pd
from scripts.st_functions import *

def render_page():
    open_styles()
    if not user_is_verified(): return
    st.subheader('Geo Location')
    add_description_to_page('Elige el <b>producto</b> que buscas')
    # Aquí sabemos ya que automations está cargado, por lo tanto, no se va a romper el finder
    allow_geolocation()


def allow_geolocation():
    if 'chosen_product' not in st.session_state:
        st.session_state.chosen_product = None

    finder = load_finder()

    handle_product_selection(finder)
    chosen_product = st.session_state.chosen_product
    
    if chosen_product is None: return
    figure, data = finder.plot_product_availability(chosen_product, quantiles=True)
    
    tab_fig, tab_data = st.tabs(['Map', 'Data'])

    with tab_fig:
        
        st.pyplot(
            figure, 
            use_container_width=False
        )

    with tab_data:
        display_data = (
            data
            .drop(['geometry'], axis=1)
            .dropna(subset=['total'])
            .sort_values(['total', 'state'], ascending=[0,1])
        )
        st.dataframe(
            data=display_data,
            hide_index=True,
            use_container_width=True
        )
        
def update_chosen_product(product:str):
    st.session_state.chosen_product = product
    
    
def handle_product_selection(finder:MPsFinder) -> str:
    '''
    Esta función se encarga de obtener el producto que el usuario requiera, ya sea directamente con el nombre o seleccionando
    y filtrando por familia y material
    '''
    catalogue = finder.get_product_catalgue()

    products_options = catalogue.product_name.sort_values().to_list()
    material_options = catalogue.material.drop_duplicates().sort_values().to_list()
    
    tab_product, tab_material = st.sidebar.tabs(['Products', 'Materials'])

    with tab_product:
        chosen_product_from_product = st.selectbox(
            label='Choose products',
            options=products_options,
            index=None,
            label_visibility='collapsed',
            placeholder='Choose product'
        )
        if chosen_product_from_product is None: return

        st.button(
            label='🔍 Search product',
            on_click=update_chosen_product,
            args=(chosen_product_from_product,)
        )
        

    with tab_material:
        # Primero seleccionan el material
        chosen_material = st.selectbox(
            label='Choose material',
            options=material_options,
            index=None, 
            label_visibility='collapsed',
            placeholder='Choose material'
        )
        if chosen_material is None: return None

        # Luego seleccionan la familia
        family_options = (
            catalogue
            .query('material == @chosen_material')
            .product_family
            .drop_duplicates()
            .sort_values()
            .to_list()
        )
        
        if len(family_options) == 1:
            chosen_family = family_options[0]
        else:
            chosen_family = st.selectbox(
                label='Choose family',
                options=family_options,
                placeholder='Families ...',
                index=None,
                label_visibility='collapsed'
            )

        if chosen_family is None: return None

        # Luego seleccionan el producto
        available_products = (
            catalogue
            .query('material == @chosen_material')
            .query('product_family == @chosen_family')
            .product_name
            .drop_duplicates()
            .sort_values()
            .to_list()
        )
        
        chosen_product_from_material = st.selectbox(
            label='Choose product',
            options=available_products,
            index=None,
            placeholder='Choose product',
            label_visibility='collapsed'
        )
        if chosen_product_from_material is None: return
        st.button(
            label='🔍 Search product',
            on_click=update_chosen_product,
            args=(chosen_product_from_material,),
            key='search_2'
        )   

if __name__ == '__main__':
    render_page()