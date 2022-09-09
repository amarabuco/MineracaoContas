import streamlit as st
import plotly.express as px
from datetime import datetime
import pandas as pd
import requests
import urllib.parse

st.set_page_config(
    page_title='Addicted',
    page_icon="📈",
    layout='wide'
)

st.write(""" # Reajuste de Aditivos """)

ujs = requests.get('https://sistemas.tce.pe.gov.br/DadosAbertos/UnidadesJurisdicionadas!json').json()['resposta']
df_ujs = pd.DataFrame(ujs['conteudo'])

uj = st.selectbox(
    ujs['entidade'], 
    df_ujs['ORGAO']       
    )
ano = st.selectbox(
    'Exercício', 
    list(range(2022,2015,-1))       
    )

sg_uj = df_ujs.loc[df_ujs['ORGAO'] == uj]['SIGLA'].values[0]
sg_uj

# f"https://sistemas.tce.pe.gov.br/DadosAbertos/TermoAditivo!json?SiglaUG={sg_uj}&AnoTermoAditivo={ano}"
aditivos = requests.get(f"https://sistemas.tce.pe.gov.br/DadosAbertos/TermoAditivo!json?SiglaUG={sg_uj}&AnoTermoAditivo={ano}").json()['resposta']
df_at = pd.DataFrame(aditivos['conteudo'])

if len(df_at) > 1:

    contratos = requests.get(f"https://sistemas.tce.pe.gov.br/DadosAbertos/Contratos!json?SiglaUG={sg_uj}&AnoContrato=>2017").json()['resposta']
    df_ct = pd.DataFrame(contratos['conteudo'])
    
    contratos_aditivos = df_ct.merge(df_at, on='CodigoContrato')
    
    st.write('Aditivos: ', str(len(contratos_aditivos)))
    contratos_aditivos = contratos_aditivos.loc[~(contratos_aditivos['ValorTermoAditivo'].isna())]
    contratos_aditivos['ValorTermoAditivo'] = contratos_aditivos['ValorTermoAditivo'].astype('float')
    contratos_aditivos['Valor'] = contratos_aditivos['Valor'].astype('float')
    # contratos_aditivos[['Valor', 'ValorTermoAditivo']]
    contratos_aditivos['Reajuste'] = ((contratos_aditivos['ValorTermoAditivo'].astype('float')/ contratos_aditivos['Valor'].astype('float')) - 1)*100
    contratos_aditivos.rename({'Vigencia_x':'VigContrato', 'Vigencia_y':'VigAditivo'}, axis=1, inplace=True)
    
    # for t in ['VigContrato', 'VigAditivo']:
    #     vig_ct = contratos_aditivos[t].str.split(' ', expand=True)
    #     vig_ct[0] = pd.to_datetime(vig_ct[0], infer_datetime_format=True)
    #     vig_ct[2] = pd.to_datetime(vig_ct[2], infer_datetime_format=True)
    #     contratos_aditivos['Dur'+t] = (vig_ct[2] - vig_ct[0]).dt.days
    
    adt_resumo = contratos_aditivos[['CodigoContrato', 'AnoContrato_x','VigContrato', 'VigAditivo', 'Objeto','Reajuste', 'Valor', 'ValorTermoAditivo', 'JustificativaTermoAditivo']].sort_values('Reajuste', ascending=False)
    # adt_resumo = contratos_aditivos[['CodigoContrato', 'AnoContrato_x','DurVigContrato', 'DurVigAditivo', 'Objeto','Reajuste', 'Valor', 'ValorTermoAditivo', 'JustificativaTermoAditivo']].sort_values('Reajuste', ascending=False)
    
    slice_ = ['Reajuste']
    def style_negative(v, props=''):
        return props if v > 25 else None

    # st.write(adt_resumo.style.set_properties(**{'background-color': '#ffffb3'}, subset=slice_))
    st.write(adt_resumo.style.applymap(style_negative, props='color:red;',subset=slice_).set_properties(**{'background-color': '#ffffb3'}, subset=slice_))

else:
    st.write('Não há aditivos no período.')