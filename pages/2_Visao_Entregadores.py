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

#---------------------------------------------------------

df_original = pd.read_csv('train.csv')

df = df_original

# LIMPEZA DO DATAFRAME

#limpeza dos espaços

df['ID'] = df['ID'].str.strip()
df['Delivery_person_ID'] = df['Delivery_person_ID'].str.strip()
df['Delivery_person_Age'] = df['Delivery_person_Age'].str.strip()
df['Road_traffic_density'] = df['Road_traffic_density'].str.strip()
df['Type_of_order'] = df['Type_of_order'].str.strip()
df['Type_of_vehicle'] = df['Type_of_vehicle'].str.strip()
df['Festival'] = df['Festival'].str.strip()
df['City'] = df['City'].str.strip()

# Comando para remover o texto de números

df = df.reset_index( drop=True )

# Retirando os numeros da coluna Time_taken(min)

df['Time_taken(min)'] = df['Time_taken(min)'].apply( lambda x: x.split(  '(min) ') [1] )
df['Time_taken(min)'] = df['Time_taken(min)'].astype(float)

# Conversao de texto para data

df['Order_Date'] = pd.to_datetime( df['Order_Date'], format='%d-%m-%Y' )

# removendo NaN

linha = df['City'] != 'NaN'
df['City'] = df.loc[linha,'City']

linha = df['Delivery_person_Ratings'] != 'NaN ' 
df['Delivery_person_Ratings'] = df.loc[linha,'Delivery_person_Ratings'].astype(float)

linha = df['Delivery_person_Age'] != 'NaN'
df['Delivery_person_Age'] = df.loc[linha,'Delivery_person_Age'].astype(int)

linha = df['Road_traffic_density'] != 'NaN'
df['Road_traffic_density'] = df.loc[linha,'Road_traffic_density']

linha = df['Weatherconditions'] != 'NaN '
df['Weatherconditions'] = df.loc[linha,'Weatherconditions']



# ---------------------------------------------------------------
############## SIDEBAR IN STREAMLIT ###############
# ---------------------------------------------------------------

st.header('Marketplace - Visão Entregadores')

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

# ---------------------------------------------------------------
############## lAYOUT NO STREAMLIT ###############
# ---------------------------------------------------------------

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', 'nome', 'nome'] )

with tab1:
    with st.container():
        st.title('Overall Metrics')
        
        col1, col2, col3, col4 = st.columns ( 4 , gap='large' )
        
        #maior idade entregadores
        with col1:
           
            
            maior_idade = df.loc[:,'Delivery_person_Age'].max()
            col1.metric ('Maior Idade', maior_idade)
        
        #menor idade entregadores
        with col2:
          
            
            menor_idade = df.loc[:,'Delivery_person_Age'].min()
            col2.metric ('Menor Idade', menor_idade)
            
            
        with col3:
            
            melhor_condicao = df.loc[:,'Vehicle_condition'].max()
            col3.metric ('Melhor Condição', melhor_condicao)
          
        with col4:
            
            pior_condicao = df.loc[:,'Vehicle_condition'].min()
            col4.metric ('Pior Condição', pior_condicao)
          
    
    with st.container():
        st.markdown ("""___""")
        st.title ('Avaliações')
        
        col1, col2 = st.columns (2)
        with col1:
            st.markdown ( '##### Avaliação media por Entregador')
            
            aval_media = (df.loc[:,['Delivery_person_Ratings', 'Delivery_person_ID']]
                          .groupby(['Delivery_person_ID','Delivery_person_Ratings'])
                          .mean()
                          .reset_index())
            
            st.dataframe (aval_media)
            
        with col2:
            st.markdown ( '##### Avaliação media por Trânsito')
            
            aval_media_transito = df.loc[:,['Delivery_person_Ratings', 'Road_traffic_density']].groupby('Road_traffic_density').agg({ 'Delivery_person_Ratings': ['mean','std']})
                         
            #mudando nome das colunas
            aval_media_transito.columns = ['Delivery_mean','Delivery_std']                       
            #resetar index
            aval_media_transito = aval_media_transito.reset_index()
            
            st.dataframe (aval_media_transito)
            
            #--------------
            
            st.markdown ( '##### Avaliação media por Clima')
            
            aval_media_clima = df.loc[:,['Delivery_person_Ratings', 'Weatherconditions']].groupby('Weatherconditions').mean()
            
            st.dataframe (aval_media_clima)
            
   
    with st.container():
        st.markdown ("""___""")
        st.title ('Velocidade de Entrega')
        
                
        col1, col2 = st.columns (2)
        
        with col1:
            st.markdown( '##### Top Entregadores mais rapidos')
                        
            cols=['Delivery_person_ID','City','Time_taken(min)']
            df2 = (df.loc[:,cols]
                     .groupby(['City','Delivery_person_ID'])
                     .mean()
                     .sort_values(['City','Time_taken(min)'],ascending=True).reset_index())
                
              
            df_aux1 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
            df_aux2 = df2.loc[df2['City'] == 'Urban', :].head(10)
            df_aux3 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)
        
            df3 = pd.concat( [df_aux1, df_aux2, df_aux3] ).reset_index (drop=True)
            st.dataframe (df3) 
        
        with col2:
            st.markdown( '##### Top Entregadores mais lentos')
              
            cols=['Delivery_person_ID','City','Time_taken(min)']
            df2 = (df.loc[:,cols]
                     .groupby(['City','Delivery_person_ID'])
                     .mean()
                     .sort_values(['City','Time_taken(min)'],ascending=False).reset_index())
                
              
            df_aux1 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
            df_aux2 = df2.loc[df2['City'] == 'Urban', :].head(10)
            df_aux3 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)
        
            df3 = pd.concat( [df_aux1, df_aux2, df_aux3] ).reset_index(drop=False)
            st.dataframe (df3)