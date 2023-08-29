import streamlit as st
from PIL import Image

st.set_page_config(
    page_title='Home'
)

image = Image.open ('imgteste.jpg' )
st.sidebar.image ( image, width=300)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""___""")

st.write ('# Curry Company Growth Dashboard')

st.markdown (
    """
    Growth Dashboard foi construido para acompanhar as métricas de crescimento dos Entregadores e dos Restauranes.
    ### Como utilizar esse Growth Dashboard?
    - Visão empresa:
        - Visão gerencial: métricas gerais de comportamento
        - Visão tática: indicadores semais de crescimento
        - Visão geográfica: insights de geolocalização
    - Visõ entregador: acompanhamento dos indicadores semanais de crescimento
    - Visãorestaurante: indicadores semanais de crescimento dos restaurantes
    ### Ask for Help
    - Time de Data Science no Discord 
    """ 
    )