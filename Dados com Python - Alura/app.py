import streamlit as st
import pandas as pd
import plotly.express as px
from translation import translations, seniority_map, contract_map, company_size_map, remote_map, language_options 

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
@st.cache_data
def load_data():
    return pd.read_csv(
        "https://raw.githubusercontent.com/vqrca/dashboard_salarios_dados/refs/heads/main/dados-imersao-final.csv"
    )

df = load_data()

# --- Seletor de Idioma ---
language_label = st.sidebar.selectbox("🌐 Language / Idioma", ["Português", "English"])
language = language_options[language_label]
t = translations[language]

# --- Inverter mapas para filtrar pelo valor traduzido ---
def invert_map(mapping):
    """Retorna dicionário {valor_traduzido: valor original}. """
    return {v: k for k, v in mapping.items()}

# --- Barra Lateral (Filtros) ---
st.sidebar.header(t["filters"])

# Filtro de Ano
anos_disponiveis = sorted(df['ano'].unique())
anos_selecionados = st.sidebar.multiselect(t["year"], anos_disponiveis)

# Filtro de Senioridade
sen_map = seniority_map[language]
sen_valores_traduzidos = sorted(
    [sen_map.get(v, v) for v in df["senioridade"].unique()]
)
sen_selecionados_trad = st.sidebar.multiselect(t["seniority"], sen_valores_traduzidos)
sen_inv = invert_map(sen_map)
senioridades_selecionadas = [sen_inv.get(v, v) for v in sen_selecionados_trad]

# Filtro por Tipo de Contrato
con_map = contract_map[language]
con_valores_traduzidos = sorted(
    [con_map.get(v, v) for v in df["contrato"].unique()]
)
con_selecionados_trad = st.sidebar.multiselect(t["contract"], con_valores_traduzidos)
con_inv = invert_map(con_map)
contratos_selecionados = [con_inv.get(v, v) for v in con_selecionados_trad]

# Filtro por Tamanho da Empresa
tam_map = company_size_map[language]
tam_valores_traduzidos = sorted(
    [tam_map.get(v, v) for v in df["tamanho_empresa"].unique()]
)
tam_selecionados_trad = st.sidebar.multiselect(t["company_size"], tam_valores_traduzidos)
tam_inv = invert_map(tam_map)
tamanhos_selecionados = [tam_inv.get(v, v) for v in tam_selecionados_trad]

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

# --- Valores do DF traduzidos ---
rem_map = remote_map[language]
 
df_exibir = df_filtrado.copy()

df_exibir["senioridade"] = df_exibir["senioridade"].map(sen_map).fillna(df_exibir["senioridade"])

df_exibir["contrato"] = df_exibir["contrato"].map(con_map).fillna(df_exibir["contrato"])

df_exibir["tamanho_empresa"] = df_exibir["tamanho_empresa"].map(tam_map).fillna(df_exibir["tamanho_empresa"])

df_exibir["remoto"] = pd.to_numeric(df_exibir["remoto"], errors='coerce').map(rem_map).fillna(df_exibir["remoto"])

# --- Renomear colunas
col_rename = {
    "ano": t["col_ano"],
    "cargo": t["col_cargo"],
    "senioridade": t["col_senioridade"],
    "contrato": t["col_contrato"],
    "tamanho_empresa": t["col_tamanho_empresa"],
    "remoto": t["col_remoto"],
    "residencia_iso3": t["col_residencia_iso3"],
    "usd": t["col_usd"],
}
df_exibir = df_exibir.rename(columns=col_rename)

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
    salario_medio, salario_maximo, total_registros, cargo_mais_frequente = 0, 0, 0, "N/A"

col1, col2, col3, col4 = st.columns(4)
col1.metric(t["avg_salary"], f"${salario_medio:,.0f}")
col2.metric(t["max_salary"], f"${salario_maximo:,.0f}")
col3.metric(t["total_records"], f"{total_registros:,}")
col4.metric(t["most_common_role"], cargo_mais_frequente)

st.markdown("---")

# --- Análises Visuais com Plotly ---
st.subheader(t["charts"])

df_graf = df_filtrado.copy()
df_graf["remoto"] = pd.to_numeric(df_graf["remoto"], errors='coerce').map(rem_map).fillna(df_graf["remoto"])

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    if not df_filtrado.empty:
        top_cargos = df_filtrado.groupby('cargo')['usd'].mean().nlargest(10).sort_values(ascending=True).reset_index()
        grafico_cargos = px.bar(
            top_cargos,
            x='usd',
            y='cargo',
            orientation='h',
            title=t["chart_top10_title"],
            labels={'usd': t["chart_top10_x"], 'cargo': ''}
        )
        grafico_cargos.update_layout(title_x=0.1, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(grafico_cargos, use_container_width=True)
    else:
        st.warning(t["warn_roles"])

with col_graf2:
    if not df_filtrado.empty:
        grafico_hist = px.histogram(
            df_filtrado,
            x='usd',
            nbins=30,
            title=t["chart_hist_title"],
            labels={'usd': t["chart_hist_x"], 'count': ''}
        )
        grafico_hist.update_layout(title_x=0.1)
        st.plotly_chart(grafico_hist, use_container_width=True)
    else:
        st.warning(t["warn_dist"])

col_graf3, col_graf4 = st.columns(2)

with col_graf3:
    if not df_filtrado.empty:
        remoto_contagem = df_graf['remoto'].value_counts().reset_index()
        remoto_contagem.columns = ['tipo_trabalho', 'quantidade']
        grafico_remoto = px.pie(
            remoto_contagem,
            names='tipo_trabalho',
            values='quantidade',
            title=t["chart_pie_title"],
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
        st.warning(t["warn_remote"])

with col_graf4:
    if not df_filtrado.empty:
        df_ds = df_filtrado[df_filtrado['cargo'] == 'Data Scientist']
        media_ds_pais = df_ds.groupby('residencia_iso3')['usd'].mean().reset_index()
        grafico_paises = px.choropleth(media_ds_pais,
            locations='residencia_iso3',
            color='usd',
            color_continuous_scale='Blues',
            title=t["chart_map_title"],
            labels={'usd': t["chart_map_color"], 'residencia_iso3': t["chart_map_location"]})
        grafico_paises.update_layout(title_x=0.1)
        st.plotly_chart(grafico_paises, use_container_width=True)
    else:
        st.warning(t["warn_map"]) 

# --- Tabela de Dados Detalhados ---
st.subheader(t["detailed_data"])
st.dataframe(df_exibir)
