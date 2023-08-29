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

st.set_page_config(page_title='Visão Restaurantes')
layout='wide'

#---------------------------------------------------------

df_original = pd.read_csv('cccandido/curry_company/dataset/train.csv')

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

st.header('Marketplace - Visão Restaurantes')

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
        
        col1, col2, col3, col4, col5, col6 = st.columns ( 6 )
        
        with col1:
                        
            unicos = len (df.loc[:,'Delivery_person_ID'].unique())
            col1.metric('Entregadores únicos', unicos)
            
        with col2:
            
            cols  = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']
            
            df['distance'] = df.loc[:, cols].apply( lambda x: haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ), axis=1 )

            avg_distance = np.round( df['distance'].mean() , 2)
            col2.metric ( 'Distancia media das entregas ', avg_distance)
        
        with col3:
            
            cols = ['Time_taken(min)','Festival']
            df_aux = df.loc [:, cols].groupby ('Festival').agg( {'Time_taken(min)': ['mean','std']} )
            
            df_aux.columns = ['avg_time','std_time']
            df_aux = df_aux.reset_index()
            
            linhas_selecionadas = df_aux['Festival'] == 'Yes'
            df_aux = np.round ( df_aux.loc[linhas_selecionadas, 'avg_time'], 2)
            
            col3.metric('Tempo médio de entrega c/ festival', df_aux)
        
        with col4:
            
            cols = ['Time_taken(min)','Festival']
            df_aux = df.loc [:, cols].groupby ('Festival').agg( {'Time_taken(min)': ['mean','std']} )
            
            df_aux.columns = ['avg_time','std_time']
            df_aux = df_aux.reset_index()
            
            linhas_selecionadas = df_aux['Festival'] == 'Yes'
            df_aux = np.round ( df_aux.loc[linhas_selecionadas, 'std_time'], 2)
            
            col4.metric('Tempo médio de entrega c/ festival', df_aux)
        
        with col5:
            
            cols = ['Time_taken(min)','Festival']
            df_aux = df.loc [:, cols].groupby ('Festival').agg( {'Time_taken(min)': ['mean','std']} )
            
            df_aux.columns = ['avg_time','std_time']
            df_aux = df_aux.reset_index()
            
            linhas_selecionadas = df_aux['Festival'] == 'No'
            df_aux = np.round ( df_aux.loc[linhas_selecionadas, 'avg_time'], 2)
            
            col5.metric('Tempo médio de entrega c/ festival', df_aux)
        
        with col6:
            
            cols = ['Time_taken(min)','Festival']
            df_aux = df.loc [:, cols].groupby ('Festival').agg( {'Time_taken(min)': ['mean','std']} )
            
            df_aux.columns = ['avg_time','std_time']
            df_aux = df_aux.reset_index()
            
            linhas_selecionadas = df_aux['Festival'] == 'No'
            df_aux = np.round ( df_aux.loc[linhas_selecionadas, 'std_time'], 2)
            
            col6.metric('Tempo médio de entrega c/ festival', df_aux)
            
    with st.container():
        st.markdown ("""___""")
        st.title ('Tempo médio de entrega por cidade')
        
        cols = ['City','Time_taken(min)']
        df_aux = df.loc[:,cols].groupby('City').agg( {'Time_taken(min)':['mean','std']} )
                                                                             
        df_aux.columns = ['avg_time','std_time']
            
        df_aux = df_aux.reset_index()
                                                                             
        fig = go.Figure()
            
        fig.add_trace(go.Bar(name='Control', 
                                 x=df_aux['City'],
                                 y=df_aux['avg_time'],
                                 error_y=dict( type='data', array=df_aux['std_time'] ) ) )
        
        fig = fig.update_layout(barmode='group')
            
        st.plotly_chart ( fig ) 
                                   
            
        
    with st.container():
        st.markdown ("""___""")
        
        st.title ('Distribuição do tempo')
        
        col1, col2 = st.columns ( 2 , gap = 'large')
        
        with col1:
           
            
            cols  = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']
            
            df['distance'] = df.loc[:, cols].apply( lambda x: haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ), axis=1 )

            avg_distance = df.loc[:,['City','distance']].groupby('City').mean().reset_index() 
            
            
            fig = go.Figure(data=[go.Pie(labels=avg_distance['City'], values=avg_distance['distance'],pull=[0,0.1,0])])
            
            st.plotly_chart( fig )
                     
            
        with col2:
         
            
            cols = ['City','Time_taken(min)','Road_traffic_density']
            df_aux = df.loc[:,cols].groupby(['City','Road_traffic_density']).agg( {'Time_taken(min)':['mean','std']} )
                                                                             
            df_aux.columns = ['avg_time','std_time']
            
            df_aux = df_aux.reset_index()
                                                                                        
            fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='avg_time',
                              color='std_time', color_continuous_scale='RdBu',
                              color_continuous_midpoint=np.average(df_aux['std_time'] ) ) 
    
            
            st.plotly_chart ( fig ) 
    
    with st.container():
        st.markdown ("""___""")
        
        st.title ('Distribuição da distância')
        
        cols = ['City','Time_taken(min)','Type_of_order']
        df_aux = df.loc[:,cols].groupby(['City','Type_of_order']).agg( {'Time_taken(min)':['mean','std']} )
        
        df_aux.columns = ['avg_time','std_time']
        
        df_aux = df_aux.reset_index()
        
        st.dataframe(df_aux)
        
    
