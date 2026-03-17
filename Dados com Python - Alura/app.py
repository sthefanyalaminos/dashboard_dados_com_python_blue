import streamlit as st
import pandas as pd
import plotly.express as px
from translation import translations as translation

# --- Configuração da Página ---
# Define o título da página, o ícone e o layout para ocupar a largura inteira.
st.set_page_config(
    page_title="Dashboard de Salários na Área de Dados",
    page_icon="📊",
    layout="wide",
)

st.markdown("""
<style>
/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #0E1A2B;
}

/* Labels */
section[data-testid="stSidebar"] label {
    color: #4DA3FF !important;
    font-weight: 600;
}

/* Caixa do multiselect */
div[data-baseweb="select"] > div {
    background-color: #132A46 !important;
    border: 1px solid #4DA3FF !important;
}

/* Texto interno */
div[data-baseweb="select"] span {
    color: #EAF3FF !important;
}

/* Dropdown */
ul[role="listbox"] {
    background-color: #132A46 !important;
}

/* Selecionado */
li[aria-selected="true"] {
    background-color: #4DA3FF !important;
    color: #0E1A2B !important;
}

/* Hover */
li:hover {
    background-color: #2E7CD6 !important;
    color: white !important;
}
            
/* Chips (itens selecionados no multiselect) */
div[data-baseweb="tag"] {
    background-color: #2563EB !important;
    color: white !important;
    border-radius: 6px !important;
    border: 1px solid #60A5FA !important;
}

/* Texto do chip */
div[data-baseweb="tag"] span {
    color: white !important;
}

/* Ícone X */
div[data-baseweb="tag"] svg {
    fill: #DBEAFE !important;
}
            
span[data-baseweb="tag"] {
    background-color: #2563EB !important;
}

            
</style>
""", unsafe_allow_html=True)




# --- Carregamento dos dados ---
df = pd.read_csv("https://raw.githubusercontent.com/vqrca/dashboard_salarios_dados/refs/heads/main/dados-imersao-final.csv")

# --- Seletor de Idioma ---
language = st.sidebar.selectbox(
    "🌐 Language",
    ["Português", "English"]
)

if language == "Português":
    t = translation["pt"]
else:
    t = translation["en"]

t = translation[language]

# --- Barra Lateral (Filtros) ---
st.sidebar.header(t["filters"])

# Filtro de Ano
anos_disponiveis = sorted(df['ano'].unique())
anos_selecionados = st.sidebar.multiselect(t["year"], anos_disponiveis)

# Filtro de Senioridade
senioridades_disponiveis = sorted(df['senioridade'].unique())
senioridades_selecionadas = st.sidebar.multiselect(t["seniority"], senioridades_disponiveis)

# Filtro por Tipo de Contrato
contratos_disponiveis = sorted(df['contrato'].unique())
contratos_selecionados = st.sidebar.multiselect(t["contract"], contratos_disponiveis)

# Filtro por Tamanho da Empresa
tamanhos_disponiveis = sorted(df['tamanho_empresa'].unique())
tamanhos_selecionados = st.sidebar.multiselect(t["company_size"], tamanhos_disponiveis)

# --- Filtragem do DataFrame ---
# O dataframe principal é filtrado com base nas seleções feitas na barra lateral.
df_filtrado = df.copy()
if anos_selecionados:
    df_filtrado = df_filtrado[df_filtrado["ano"].isin(anos_selecionados)]

if senioridades_selecionadas:
    df_filtrado = df_filtrado[df_filtrado["senioridade"].isin(senioridades_selecionadas)]

if contratos_selecionados:
    df_filtrado = df_filtrado[df_filtrado["contrato"].isin(contratos_selecionados)]

if tamanhos_selecionados:
    df_filtrado = df_filtrado[df_filtrado["tamanho_empresa"].isin(tamanhos_selecionados)]

# --- Conteúdo Principal ---
st.title(t["title"])
st.markdown(t["description"])

# --- Métricas Principais (KPIs) ---
st.subheader(t["metrics"])

if not df_filtrado.empty:
    salario_medio = df_filtrado['usd'].mean()
    salario_maximo = df_filtrado['usd'].max()
    total_registros = df_filtrado.shape[0]
    cargo_mais_frequente = df_filtrado["cargo"].mode()[0]
else:
    salario_medio, salario_mediano, salario_maximo, total_registros, cargo_mais_comum = 0, 0, 0, "N/A"

col1, col2, col3, col4 = st.columns(4)
col1.metric(t["avg_salary"], f"${salario_medio:,.0f}")
col2.metric(t["max_salary"], f"${salario_maximo:,.0f}")
col3.metric(t["total_records"], f"{total_registros:,}")
col4.metric(t["most_common_role"], cargo_mais_frequente)

st.markdown("---")

# --- Análises Visuais com Plotly ---
st.subheader(t["charts"])

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    if not df_filtrado.empty:
        top_cargos = df_filtrado.groupby('cargo')['usd'].mean().nlargest(10).sort_values(ascending=True).reset_index()
        grafico_cargos = px.bar(
            top_cargos,
            x='usd',
            y='cargo',
            orientation='h',
            title="Top 10 cargos por salário médio",
            labels={'usd': 'Média salarial anual (USD)', 'cargo': ''}
        )
        grafico_cargos.update_layout(title_x=0.1, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(grafico_cargos, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de cargos.")

with col_graf2:
    if not df_filtrado.empty:
        grafico_hist = px.histogram(
            df_filtrado,
            x='usd',
            nbins=30,
            title="Distribuição de salários anuais",
            labels={'usd': 'Faixa salarial (USD)', 'count': ''}
        )
        grafico_hist.update_layout(title_x=0.1)
        st.plotly_chart(grafico_hist, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de distribuição.")

col_graf3, col_graf4 = st.columns(2)

with col_graf3:
    if not df_filtrado.empty:
        remoto_contagem = df_filtrado['remoto'].value_counts().reset_index()
        remoto_contagem.columns = ['tipo_trabalho', 'quantidade']
        grafico_remoto = px.pie(
            remoto_contagem,
            names='tipo_trabalho',
            values='quantidade',
            title='Proporção dos tipos de trabalho',
            hole=0.5,
            color_discrete_sequence=[ 
                "#1E3A8A",  
                "#2563EB",  
                "#60A5FA",   
                ]
        )
        grafico_remoto.update_traces(textinfo='percent+label')
        grafico_remoto.update_layout(title_x=0.1)
        st.plotly_chart(grafico_remoto, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico dos tipos de trabalho.")

with col_graf4:
    if not df_filtrado.empty:
        df_ds = df_filtrado[df_filtrado['cargo'] == 'Data Scientist']
        media_ds_pais = df_ds.groupby('residencia_iso3')['usd'].mean().reset_index()
        grafico_paises = px.choropleth(media_ds_pais,
            locations='residencia_iso3',
            color='usd',
            color_continuous_scale='Blues',
            title='Salário médio de Cientista de Dados por país',
            labels={'usd': 'Salário médio (USD)', 'residencia_iso3': 'País'})
        grafico_paises.update_layout(title_x=0.1)
        st.plotly_chart(grafico_paises, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de países.") 

# --- Tabela de Dados Detalhados ---
st.subheader(t["detailed_data"])
st.dataframe(df_filtrado)
