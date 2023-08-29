import pandas as pd
import re
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from haversine import haversine
import streamlit as st
from PIL import Image 
import folium 
from streamlit_folium import folium_static

st.set_page_config(page_title='Visão Empresa')
layout='wide'

#---------------------------------------------------------
#--------- FUNÇÕES ---------------------------------------
#---------------------------------------------------------

#tabela de pedidos por dia - primeiro container 
def order_metric (df):
            
    cols = ['ID','Order_Date']
    df_aux = df.loc[:,cols].groupby('Order_Date').count().reset_index()
    df_aux.columns = ['Order Date','ID']
    fig = px.bar(df_aux, x='Order Date', y='ID')
    
    return fig

# segundo container - col1 
def traffic_order_share(df):
            
    cols = ['ID','Road_traffic_density']

    df_aux = df.loc[:,cols].groupby('Road_traffic_density').count().reset_index()

                    # transformando em porcentagem
    df_aux['%'] = 100 * (df_aux['ID'] / df_aux['ID'].sum())

                    # grafico de pizza
    fig = px.pie(df_aux, values='%', names='Road_traffic_density')

    return fig

#terceiro container - col 2
def traffic_order_city (df):
               
    cols = ['ID', 'City', 'Road_traffic_density']

    df_aux = df.loc[:,cols].groupby(['City', 'Road_traffic_density']).count().reset_index()

    # grafico de barrar agrupado e colorido

    fig = px.bar(df_aux, x='City', y='ID', color='Road_traffic_density', barmode='group')

    return fig

#quarto container - tab 2 - pedidos por semana

def order_by_week(df):
     #descobrindo a semana das datas
    df['semana'] = df['Order_Date'].dt.strftime('%U')

     #criando a tabela
    cols = ['ID', 'semana']
    df_linha = df.loc[:,cols].groupby('semana').count().reset_index()

     #criando grafico
    fig = px.line (df_linha, x='semana',y='ID')

    return fig

def order_share_week (df): 
    df['semana'] = df['Order_Date'].dt.strftime('%U')
     #pedido por entregador
    cols = ['ID', 'semana']
    aux1 = df.loc[:,cols].groupby('semana').count().reset_index()

    #pedido por semana
    cols = ['Delivery_person_ID','semana']
    aux2 = df.loc[:,cols].groupby('semana').nunique().reset_index()

    #juntando as duas tabelas por inner
    df_aux = pd.merge (aux1, aux2, how='inner', on='semana')

    #descobrindo quantidade de pedidos por entregador
    df_aux['pedido_por_entregador'] = df_aux['ID'] / df_aux ['Delivery_person_ID']

    #grafico de linha
    fig = px.line(df_aux, x='semana', y='pedido_por_entregador')

    return fig 

#ultimo container - mapa
def country_maps (df ):
    df_aux = df.loc[:,['City', 'Delivery_location_latitude', 'Delivery_location_longitude','Road_traffic_density']].groupby(['City','Road_traffic_density']).median().reset_index()
    df_aux = df_aux.loc[df_aux['City'] != 'NaN', :]   
    df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]                                                                                                                       
            # Desenhar o mapa
    map = folium.Map()

    for index, location_info in df_aux.iterrows():
                folium.Marker( [location_info['Delivery_location_latitude'],
                             location_info['Delivery_location_longitude']],
                             popup=location_info[['City', 'Road_traffic_density']] ).add_to( map )


    folium_static( map, width=1024 , height=600 )  

# --------------- LIMPEZA DO DATAFRAME --------------------------

def clean_code ( df ):
    
    """ esta funcao tem a responsabilidade de limpar o dataframe
    
        Tipos de limpeza:
        1. Remoção do dados NaN
        2. Mudança do tipo da coluna de dados
        3. Remoção dos espaços das variáveis de texto
        4. Formatação da coluna de datas
        5. Limpeza da coluna de tempo (remoção do texto da variável numérica
        
        Input: Dataframe
        Output: Dataframe
    """

    # LIMPEZA DO DATAFRAME

    #limpeza dos espaços

    df['ID'] = df['ID'].str.strip()
    df['Delivery_person_ID'] = df['Delivery_person_ID'].str.strip()
    df['Road_traffic_density'] = df['Road_traffic_density'].str.strip()
    df['Type_of_order'] = df['Type_of_order'].str.strip()
    df['Type_of_vehicle'] = df['Type_of_vehicle'].str.strip()
    df['Festival'] = df['Festival'].str.strip()
    df['City'] = df['City'].str.strip()

    # Comando para remover o texto de números

    df = df.reset_index( drop=True )

    # Retirando os numeros da coluna Time_taken(min)

    df['Time_taken(min)'] = df['Time_taken(min)'].apply( lambda x: x.split(  '(min) ') [1] )
    df['Time_taken(min)'] = df['Time_taken(min)'].astype(int)

    # Conversao de texto para data

    df['Order_Date'] = pd.to_datetime( df['Order_Date'], format='%d-%m-%Y' )

    # removendo NaN

    linha = df['City'] != 'NaN'
    df['City'] = df.loc[linha,'City']

    linha = df['Road_traffic_density'] != 'NaN'
    df['Road_traffic_density'] = df.loc[linha,'Road_traffic_density']

    return df

# -----------------INICIO DA ESTRUTURA LÓGICA DO CÓDIGO -----------------------------

# import dataset
df_original = pd.read_csv('train.csv')

# limpando os dados
df = clean_code (df_original)

# ---------------------------------------------------------------
############## SIDEBAR IN STREAMLIT ###############
# ---------------------------------------------------------------

st.header('Marketplace - Visão Cliente')

image = Image.open ('imgteste.jpg' )
st.sidebar.image ( image, width=300)


st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""___""")

st.sidebar.markdown('## Selecione uma data limite')
date_slider=st.sidebar.slider (
    'Data limite',
    value=pd.datetime( 2022, 4, 13 ),
    min_value = pd.datetime( 2022, 2, 11 ),
    max_value = pd.datetime( 2022, 4, 6 ),
    format = 'DD-MM-YYYY' )
    
st.sidebar.markdown ( """___""" )
    
traffic_options=st.sidebar.multiselect (
    'Quais as condições do trânsito?',
    ['Low','Medium','High', 'Jam'],
    default = ['Low'] )
    
st.sidebar.markdown ("""___""")

# linkando filtro de data
linhas_selecionadas = df['Order_Date'] < date_slider
df = df.loc [linhas_selecionadas, :]

# linkando filtro de transito
linhas_selecionadas = df['Road_traffic_density'].isin ( traffic_options )
df = df.loc [linhas_selecionadas, :]


st.dataframe (df)
# ---------------------------------------------------------------
############## lAYOUT NO STREAMLIT ###############
# ---------------------------------------------------------------

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'] )

with tab1: #pedidos
    with st.container():
        #grafico pedidos por dia
        fig = order_metric (df)
        st.markdown ('# Orders by Day')
        st.plotly_chart (fig, use_container_width=True) #comando do streamlite p conseguir mostrar o gráfico
    
    #--------colocando proximos graficos em duas colunas
    with st.container ():
        col1, col2 = st.columns( 2 )
        
        with col1: 
            fig = traffic_order_share (df)
            st.header('Traffic Order Share')
            st.plotly_chart(fig, use_container_width=True)
                
        
        with col2: 
            st.header ('Traffic Order City')
            fig = traffic_order_city (df)
            st.plotly_chart(fig, use_container_width=True)
            
    
with tab2:
    with st.container():
        st.markdown ('# Orders by Week')
        fig = order_by_week (df)
        st.plotly_chart (fig, use_container_width=True)

    
    with st.container():
        st.markdown ('# Order Share by Week')
        fig = order_share_week (df)
        st.plotly_chart (fig, use_container_width=True)
        
with tab3:
    with st.container():
        st.markdown('# Country Maps')
        country_maps (df)

        
