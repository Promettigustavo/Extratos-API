"""
Dashboard Streamlit para Busca de Extratos Bancários
Identidade Visual: Kanastra
Bancos suportados: Santander (Itaú e Arbi em desenvolvimento)
"""

import streamlit as st
from datetime import datetime, timedelta
import os
import sys

# Adicionar diretório ao path para imports
sys.path.insert(0, os.path.dirname(__file__))

# Configuração da página
st.set_page_config(
    page_title="Extratos Bancários - Kanastra",
    page_icon="https://www.kanastra.design/symbol.svg",
    layout="wide"
)

# CSS customizado - Kanastra Brand (Visual Moderno)
st.markdown("""
<style>
    /* Cores Kanastra */
    :root {
        --kanastra-green: #193c32;
        --tech-green-1: #1e5546;
        --tech-green-2: #14735a;
        --tech-green-3: #2daa82;
        --light-gray: #f8f9fa;
        --white: #ffffff;
    }
    
    /* Background geral */
    .main {
        background: #ffffff;
    }
    
    /* Headers */
    .main-header {
        font-size: 2.8rem;
        font-weight: 700;
        color: #193c32;
        margin-bottom: 0.5rem;
        font-family: 'Inter', sans-serif;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.05);
    }
    .sub-header {
        font-size: 1.3rem;
        color: #1e5546;
        margin-bottom: 1.5rem;
        font-weight: 400;
    }
    
    /* Seções com cards modernos */
    .section-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #193c32;
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding: 1rem;
        background: linear-gradient(135deg, #14735a 0%, #2daa82 100%);
        color: white;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(20, 115, 90, 0.2);
    }
    
    /* Botões modernos com gradiente */
    .stButton>button {
        background: linear-gradient(135deg, #14735a 0%, #2daa82 100%) !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 12px !important;
        padding: 0.75rem 2rem !important;
        border: none !important;
        transition: all 0.3s ease !important;
        font-size: 1.1rem !important;
        box-shadow: 0 4px 12px rgba(20, 115, 90, 0.25) !important;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #2daa82 0%, #14735a 100%) !important;
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(20, 115, 90, 0.4) !important;
    }
    .stButton>button:active {
        transform: translateY(-1px);
    }
    
    /* Success/Info boxes com sombra */
    .success-box {
        padding: 1.25rem;
        border-radius: 12px;
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border: none;
        margin: 1rem 0;
        color: #193c32;
        box-shadow: 0 3px 10px rgba(45, 170, 130, 0.15);
    }
    .info-box {
        padding: 1.25rem;
        border-radius: 12px;
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border: 1px solid #e9ecef;
        margin: 1rem 0;
        color: #193c32;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.08);
    }
    
    /* Tabs com visual moderno */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background: white;
        padding: 0.75rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    .stTabs [data-baseweb="tab"] {
        color: #193c32;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #f8f9fa;
    }
    .stTabs [aria-selected="true"] {
        color: white;
        background: linear-gradient(135deg, #14735a 0%, #2daa82 100%);
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(20, 115, 90, 0.3);
    }
    
    /* Inputs com visual limpo */
    .stSelectbox label, .stMultiSelect label, .stCheckbox label, .stDateInput label {
        color: #193c32 !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }
    
    /* Select boxes */
    .stSelectbox > div > div, .stMultiSelect > div > div {
        border-radius: 10px !important;
        border: 2px solid #e9ecef !important;
        transition: all 0.3s ease !important;
    }
    .stSelectbox > div > div:focus-within, .stMultiSelect > div > div:focus-within {
        border-color: #2daa82 !important;
        box-shadow: 0 0 0 3px rgba(45, 170, 130, 0.1) !important;
    }
    
    /* Date inputs */
    .stDateInput > div > div > input {
        border-radius: 10px !important;
        border: 2px solid #e9ecef !important;
    }
    
    /* Containers com sombra suave */
    .element-container {
        background-color: transparent;
    }
    
    /* Cards de fundos modernos */
    .fundo-card {
        padding: 1rem;
        background: white;
        border-radius: 12px;
        margin-bottom: 0.75rem;
        border: 1px solid #e9ecef;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
        transition: all 0.3s ease;
    }
    .fundo-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(45, 170, 130, 0.15);
        border-color: #2daa82;
    }
    .fundo-card strong {
        color: #14735a;
    }
    
    /* Progress bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #14735a 0%, #2daa82 100%);
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #14735a;
        font-weight: 700;
    }
    
    /* Sidebar com gradiente */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, #f8f9fa 100%);
        border-right: 1px solid #e9ecef;
    }
    [data-testid="stSidebar"] h3 {
        color: #193c32;
        font-weight: 700;
    }
    [data-testid="stSidebar"] .stRadio > label {
        color: #193c32;
        font-weight: 600;
    }
    
    /* Cards de banco na sidebar - Visual moderno */
    .banco-card {
        padding: 1rem 1.25rem;
        margin: 0.75rem 0;
        border-radius: 12px;
        border: 2px solid #e9ecef;
        background: white;
        text-align: center;
        font-size: 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
        cursor: pointer;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
    }
    .banco-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    .banco-card.selected {
        background: linear-gradient(135deg, #14735a 0%, #2daa82 100%);
        color: white;
        border-color: transparent;
        font-weight: 700;
        box-shadow: 0 4px 12px rgba(20, 115, 90, 0.3);
    }
    .banco-card.disabled {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        color: #adb5bd;
        border-color: #dee2e6;
        cursor: not-allowed;
        box-shadow: none;
    }
    .banco-card.disabled:hover {
        transform: none;
    }
    
    /* Info boxes melhoradas */
    .stAlert {
        border-radius: 12px !important;
        border: none !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08) !important;
    }
    
    /* Checkboxes */
    .stCheckbox {
        background: white;
        padding: 0.75rem;
        border-radius: 10px;
        border: 1px solid #e9ecef;
        transition: all 0.3s ease;
    }
    .stCheckbox:hover {
        border-color: #2daa82;
        box-shadow: 0 2px 8px rgba(45, 170, 130, 0.1);
    }
    
    /* Dividers */
    hr {
        border: none;
        border-top: 2px solid #e9ecef;
        margin: 2rem 0;
    }
    
    /* Multi-select tags */
    .stMultiSelect [data-baseweb="tag"] {
        background: linear-gradient(135deg, #14735a 0%, #2daa82 100%);
        border-radius: 8px;
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        background: white;
        border-radius: 10px;
        border: 1px solid #e9ecef;
        transition: all 0.3s ease;
    }
    .streamlit-expanderHeader:hover {
        border-color: #2daa82;
        box-shadow: 0 2px 8px rgba(45, 170, 130, 0.1);
    }
    
    /* Code blocks */
    pre {
        background: #f8f9fa !important;
        border-radius: 10px !important;
        border: 1px solid #e9ecef !important;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #14735a 0%, #2daa82 100%);
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #193c32;
    }

</style>
""", unsafe_allow_html=True)

# Header com logo Kanastra
col_logo, col_title = st.columns([1, 6])
with col_logo:
    st.image("https://www.kanastra.design/symbol-green.svg", width=100)
with col_title:
    st.markdown('<div class="main-header">Extratos Bancários</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Geração automatizada de extratos em formato Excel e PDF</div>', unsafe_allow_html=True)

# ========== SIDEBAR: SELEÇÃO DE BANCO ==========
with st.sidebar:
    st.markdown("### 🏦 Banco")
    
    # Card Santander (ativo)
    st.markdown('<div class="banco-card selected">Santander</div>', unsafe_allow_html=True)
    banco_selecionado = "Santander"
    
    # Cards futuros (desabilitados)
    st.markdown('<div class="banco-card disabled">Itaú</div>', unsafe_allow_html=True)
    st.markdown('<div class="banco-card disabled">Arbi</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("**📊 Formatos**")
    st.markdown("• Excel (.xlsx)")
    st.markdown("• PDF (.pdf)")

# Import condicional - suporta tanto ambiente local quanto Streamlit Cloud
try:
    # Tentar carregar config_credentials primeiro (suporta Streamlit Secrets)
    try:
        from config_credentials import SANTANDER_FUNDOS
    except ImportError:
        # Fallback para credenciais locais
        from credenciais_bancos import SANTANDER_FUNDOS
    
    from buscar_extratos_bancarios import SantanderExtratosBancarios, main
    import buscar_extratos_bancarios
    # Desabilitar logs verbosos
    buscar_extratos_bancarios.VERBOSE = False
    HAS_CREDENCIAIS = True
except ImportError as e:
    HAS_CREDENCIAIS = False
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%); padding: 1.5rem; border-radius: 12px; border-left: 4px solid #f44336; margin: 1rem 0;">
        <strong style="color: #c62828; font-size: 1.2rem;">❌ Erro ao carregar credenciais</strong><br>
        <span style="color: #b71c1c; font-size: 0.95rem;">{str(e)}</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div style="background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); padding: 1.5rem; border-radius: 12px; border-left: 4px solid #2196f3; margin: 1rem 0;">
        <strong style="color: #1565c0; font-size: 1.1rem;">ℹ️ Configuração necessária</strong><br><br>
        <ul style="color: #0d47a1; margin-left: 1rem;">
            <li><strong>Streamlit Cloud:</strong> Configure os secrets em Settings > Secrets</li>
            <li><strong>Local:</strong> Crie o arquivo <code>credenciais_bancos.py</code> com as credenciais</li>
        </ul>
        <span style="color: #424242; font-size: 0.9rem;">Veja o arquivo <code>DEPLOY.md</code> para mais detalhes.</span>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# Lista de fundos disponíveis
fundos_disponiveis = sorted(list(SANTANDER_FUNDOS.keys()))

st.markdown("---")

# ========== SEÇÃO 1: SELEÇÃO DE FUNDOS ==========
st.markdown("""
<div style="background: white; padding: 1.5rem; border-radius: 16px; box-shadow: 0 4px 16px rgba(0,0,0,0.08); margin-bottom: 2rem;">
    <div style="font-size: 1.5rem; font-weight: 600; color: #193c32; margin-bottom: 1rem; display: flex; align-items: center;">
        <span style="background: linear-gradient(135deg, #14735a 0%, #2daa82 100%); color: white; padding: 0.5rem 1rem; border-radius: 10px; margin-right: 1rem;">📁</span>
        Seleção de Fundos
    </div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([3, 1])

with col1:
    selecionar_todos = st.checkbox("✅ Selecionar todos os fundos", value=False)
    
    if selecionar_todos:
        fundos_selecionados = fundos_disponiveis
    else:
        fundos_selecionados = st.multiselect(
            "Escolha os fundos:",
            options=fundos_disponiveis,
            default=[],
            help="Selecione um ou mais fundos para gerar extratos"
        )

with col2:
    st.metric("Fundos Selecionados", len(fundos_selecionados), delta=f"de {len(fundos_disponiveis)}")

# ========== SEÇÃO 2: PERÍODO ==========
st.markdown("""
<div style="background: white; padding: 1.5rem; border-radius: 16px; box-shadow: 0 4px 16px rgba(0,0,0,0.08); margin-bottom: 2rem;">
    <div style="font-size: 1.5rem; font-weight: 600; color: #193c32; margin-bottom: 1rem; display: flex; align-items: center;">
        <span style="background: linear-gradient(135deg, #14735a 0%, #2daa82 100%); color: white; padding: 0.5rem 1rem; border-radius: 10px; margin-right: 1rem;">📅</span>
        Definição de Período
    </div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    preset_periodo = st.selectbox(
        "Período pré-definido:",
        ["Últimos 3 dias", "Últimos 7 dias", "Últimos 15 dias", "Últimos 30 dias", "Mês atual", "Mês anterior", "Último ano", "Últimos 2 anos", "Personalizado"],
        help="Escolha um período pré-definido ou selecione 'Personalizado' para definir datas específicas"
    )

# Calcular datas baseado no preset
hoje = datetime.now().date()
if preset_periodo == "Últimos 3 dias":
    data_inicial_default = hoje - timedelta(days=3)
    data_final_default = hoje
elif preset_periodo == "Últimos 7 dias":
    data_inicial_default = hoje - timedelta(days=7)
    data_final_default = hoje
elif preset_periodo == "Últimos 15 dias":
    data_inicial_default = hoje - timedelta(days=15)
    data_final_default = hoje
elif preset_periodo == "Últimos 30 dias":
    data_inicial_default = hoje - timedelta(days=30)
    data_final_default = hoje
elif preset_periodo == "Mês atual":
    data_inicial_default = hoje.replace(day=1)
    data_final_default = hoje
elif preset_periodo == "Mês anterior":
    primeiro_dia_mes_atual = hoje.replace(day=1)
    ultimo_dia_mes_anterior = primeiro_dia_mes_atual - timedelta(days=1)
    data_inicial_default = ultimo_dia_mes_anterior.replace(day=1)
    data_final_default = ultimo_dia_mes_anterior
elif preset_periodo == "Último ano":
    data_inicial_default = hoje - timedelta(days=365)
    data_final_default = hoje
elif preset_periodo == "Últimos 2 anos":
    data_inicial_default = hoje - timedelta(days=730)
    data_final_default = hoje
else:  # Personalizado
    data_inicial_default = hoje - timedelta(days=7)
    data_final_default = hoje

with col2:
    if preset_periodo == "Personalizado":
        data_inicial = st.date_input("📅 Data inicial:", value=data_inicial_default)
    else:
        data_inicial = st.date_input("📅 Data inicial:", value=data_inicial_default, disabled=True)

with col3:
    if preset_periodo == "Personalizado":
        data_final = st.date_input("📅 Data final:", value=data_final_default)
    else:
        data_final = st.date_input("📅 Data final:", value=data_final_default, disabled=True)

# Validação de datas
if data_inicial > data_final:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%); padding: 1.25rem; border-radius: 12px; border-left: 4px solid #f44336;">
        <strong style="color: #c62828;">❌ Data inicial não pode ser maior que data final</strong>
    </div>
    """, unsafe_allow_html=True)

# ========== SEÇÃO 3: FORMATOS DE EXPORTAÇÃO ==========
st.markdown("""
<div style="background: white; padding: 1.5rem; border-radius: 16px; box-shadow: 0 4px 16px rgba(0,0,0,0.08); margin-bottom: 2rem;">
    <div style="font-size: 1.5rem; font-weight: 600; color: #193c32; margin-bottom: 1rem; display: flex; align-items: center;">
        <span style="background: linear-gradient(135deg, #14735a 0%, #2daa82 100%); color: white; padding: 0.5rem 1rem; border-radius: 10px; margin-right: 1rem;">📄</span>
        Formatos de Exportação
    </div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); padding: 1rem; border-radius: 12px; border-left: 4px solid #2196f3;">
        <strong style="color: #1565c0;">📊 Excel (.xlsx)</strong><br>
        <span style="color: #424242; font-size: 0.9rem;">Sempre será gerado</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    gerar_pdf = st.checkbox("📑 Gerar também PDF (.pdf)", value=True, help="Gera arquivo PDF no formato Internet Banking Empresarial")

with col2:
    formatos_str = ["Excel"]
    if gerar_pdf:
        formatos_str.append("PDF")
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%); padding: 1.25rem; border-radius: 12px; border-left: 4px solid #2daa82; margin-top: 1rem;">
        <strong style="color: #14735a; font-size: 1.1rem;">✅ Formatos selecionados</strong><br>
        <span style="color: #193c32; font-size: 1rem; font-weight: 600;">{' e '.join(formatos_str)}</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# ========== BOTÃO DE GERAÇÃO ==========
buscar_disabled = (
    len(fundos_selecionados) == 0 or
    data_inicial > data_final
)

# Inicializar session_state para controlar execução
if 'processando' not in st.session_state:
    st.session_state.processando = False

# Container destacado para o botão
st.markdown("""
<div style="background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%); padding: 2rem; border-radius: 16px; box-shadow: 0 6px 20px rgba(0,0,0,0.1); text-align: center; border: 2px solid #e9ecef;">
    <div style="font-size: 1.3rem; font-weight: 600; color: #193c32; margin-bottom: 1rem;">
        🚀 Pronto para gerar os extratos?
    </div>
</div>
""", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

if st.button("▶️ Gerar Extratos", disabled=buscar_disabled or st.session_state.processando, use_container_width=True, key="btn_gerar"):
    # Marcar como processando para evitar cliques duplos
    st.session_state.processando = True
    
    # 🧹 LIMPEZA: Remover arquivos antigos da pasta de saída (silencioso)
    pasta_saida = os.getcwd()
    
    arquivos_antigos = []
    for arquivo in os.listdir(pasta_saida):
        if arquivo.startswith('exportar-Santander') or arquivo.startswith('comprovante-ibe'):
            caminho_completo = os.path.join(pasta_saida, arquivo)
            try:
                os.remove(caminho_completo)
                arquivos_antigos.append(arquivo)
            except:
                pass  # Silenciar erros de remoção
    
    # Barra de progresso e status
    progress_container = st.container()
    with progress_container:
        progress_bar = st.progress(0)
        status_text = st.empty()
    
    # Preparar parâmetros - converter date para datetime
    from datetime import datetime as dt
    data_inicial_dt = dt.combine(data_inicial, dt.min.time())
    data_final_dt = dt.combine(data_final, dt.max.time())
    
    # Atualizar status inicial
    status_text.info(f"🔄 Iniciando busca de extratos para {len(fundos_selecionados)} fundo(s)...")
    progress_bar.progress(0.1)
    
    # Capturar stdout para silenciar logs técnicos
    import sys
    from io import StringIO
    
    old_stdout = sys.stdout
    sys.stdout = StringIO()  # Redirecionar para silenciar
    
    arquivos_gerados = []
    
    # Marcar timestamp de início
    from datetime import datetime, timedelta
    timestamp_inicio = datetime.now() - timedelta(minutes=15)
    
    # Silenciar stdout (remover logs técnicos)
    old_stdout = sys.stdout
    sys.stdout = StringIO()
    
    try:
        # Status: Buscando extratos
        status_text.info("📡 Conectando à API e buscando extratos...")
        progress_bar.progress(0.2)
        
        # Chamar função main com lista de fundos e objetos datetime
        main(
            fundos=fundos_selecionados,
            data_inicial=data_inicial_dt,
            data_final=data_final_dt,
            pasta_saida=pasta_saida,
            gerar_pdf=gerar_pdf
        )
        
        # Atualizar progresso: gerando arquivos
        progress_bar.progress(0.6)
        status_text.info("📄 Gerando arquivos Excel e PDF...")
        
        # Forçar flush/sync dos arquivos
        import time
        time.sleep(1)  # Garantir que arquivos foram escritos
        
        # Status: Organizando arquivos
        progress_bar.progress(0.8)
        status_text.info("📂 Organizando arquivos gerados...")
        
        # Buscar arquivos gerados nos últimos 15 minutos
        todos_arquivos = os.listdir(pasta_saida)
        
        # Procurar arquivos Excel
        for arquivo in todos_arquivos:
            if arquivo.endswith('.xlsx') and arquivo.startswith('exportar-Santander'):
                arquivo_completo = os.path.join(pasta_saida, arquivo)
                if datetime.fromtimestamp(os.path.getmtime(arquivo_completo)) > timestamp_inicio:
                    arquivos_gerados.append(arquivo_completo)
        
        # Procurar arquivos PDF se solicitado
        if gerar_pdf:
            for arquivo in todos_arquivos:
                if arquivo.endswith('.pdf') and arquivo.startswith('comprovante-ibe'):
                    arquivo_completo = os.path.join(pasta_saida, arquivo)
                    if datetime.fromtimestamp(os.path.getmtime(arquivo_completo)) > timestamp_inicio:
                        arquivos_gerados.append(arquivo_completo)
        
        progress_bar.progress(1.0)
        
        # Mensagens de conclusão
        if len(arquivos_gerados) == 0:
            status_text.warning("⚠️ Nenhum arquivo gerado")
            st.markdown("""
            <div style="background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%); padding: 1.25rem; border-radius: 12px; border-left: 4px solid #ff9800;">
                <strong style="color: #e65100;">⚠️ Nenhum arquivo foi gerado</strong><br>
                <span style="color: #bf360c; font-size: 0.95rem;">Verifique se os fundos selecionados têm contas cadastradas no período.</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            status_text.success(f"✅ {len(arquivos_gerados)} arquivo(s) gerado(s) com sucesso!")
            
    except Exception as e:
        progress_bar.progress(1.0)
        status_text.error("❌ Erro durante processamento")
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%); padding: 1.5rem; border-radius: 12px; border-left: 4px solid #f44336;">
            <strong style="color: #c62828; font-size: 1.2rem;">❌ Erro durante processamento</strong><br>
            <span style="color: #b71c1c; font-size: 0.95rem;">{str(e)}</span>
        </div>
        """, unsafe_allow_html=True)
        import traceback
        with st.expander("🔴 Ver detalhes técnicos do erro"):
            st.code(traceback.format_exc())
    
    finally:
        # Restaurar stdout
        sys.stdout = old_stdout
        
        # Liberar estado de processamento
        st.session_state.processando = False
    
    # Mostrar resultados apenas se há arquivos gerados
    if arquivos_gerados:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background: white; padding: 1.5rem; border-radius: 16px; box-shadow: 0 4px 16px rgba(0,0,0,0.08); margin-bottom: 2rem;">
            <div style="font-size: 1.5rem; font-weight: 600; color: #193c32; margin-bottom: 1rem; display: flex; align-items: center;">
                <span style="background: linear-gradient(135deg, #14735a 0%, #2daa82 100%); color: white; padding: 0.5rem 1rem; border-radius: 10px; margin-right: 1rem;">📥</span>
                Arquivos Gerados
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Agrupar por tipo
        excels = [f for f in arquivos_gerados if f.endswith('.xlsx')]
        pdfs = [f for f in arquivos_gerados if f.endswith('.pdf')]
        
        # Resumo com cards visuais
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); padding: 1.5rem; border-radius: 12px; text-align: center; box-shadow: 0 3px 10px rgba(0,0,0,0.08);">
                <div style="font-size: 2.5rem;">✅</div>
                <div style="font-size: 1.8rem; font-weight: 700; color: #2e7d32; margin: 0.5rem 0;">{len(arquivos_gerados)}</div>
                <div style="color: #1b5e20; font-weight: 600;">Arquivos Gerados</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if excels:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); padding: 1.5rem; border-radius: 12px; text-align: center; box-shadow: 0 3px 10px rgba(0,0,0,0.08);">
                    <div style="font-size: 2.5rem;">📊</div>
                    <div style="font-size: 1.8rem; font-weight: 700; color: #1565c0; margin: 0.5rem 0;">{len(excels)}</div>
                    <div style="color: #0d47a1; font-weight: 600;">Planilhas Excel</div>
                </div>
                """, unsafe_allow_html=True)
        
        with col3:
            if pdfs:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #fce4ec 0%, #f8bbd0 100%); padding: 1.5rem; border-radius: 12px; text-align: center; box-shadow: 0 3px 10px rgba(0,0,0,0.08);">
                    <div style="font-size: 2.5rem;">📑</div>
                    <div style="font-size: 1.8rem; font-weight: 700; color: #c2185b; margin: 0.5rem 0;">{len(pdfs)}</div>
                    <div style="color: #880e4f; font-weight: 600;">Arquivos PDF</div>
                </div>
                """, unsafe_allow_html=True)
        
        # Botão para baixar ZIP com todos os arquivos
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # Criar arquivo ZIP em memória com estrutura de pastas
        from zipfile import ZipFile, ZIP_DEFLATED, ZIP_STORED
        from io import BytesIO
        import re
        
        # Extrair informações dos nomes de arquivo para organização
        def extrair_info_arquivo(caminho_arquivo):
            """Extrai fundo e período do nome do arquivo"""
            nome = os.path.basename(caminho_arquivo)
            
            # Padrão: exportar-Santander - Extrato DD de MMMM de YYYY-AGENCIA-CONTA.xlsx
            # ou: comprovante-ibe-UUID.pdf
            
            # Para Excel, extrair data do nome
            if nome.endswith('.xlsx'):
                match = re.search(r'Extrato (\d{2} de \w+ de \d{4})', nome)
                periodo = match.group(1) if match else "sem_data"
            else:
                # Para PDF, usar período selecionado pelo usuário
                periodo = f"{data_inicial.strftime('%d-%m-%Y')} a {data_final.strftime('%d-%m-%Y')}"
            
            return periodo
        
        # Agrupar arquivos por fundo
        arquivos_por_fundo = {}
        
        # Criar mapeamento: nome_longo -> fundo_id (para nomes curtos nas pastas)
        nome_para_id = {}
        for fundo_id in fundos_selecionados:
            if fundo_id in SANTANDER_FUNDOS:
                nome_longo = SANTANDER_FUNDOS[fundo_id].get('nome', fundo_id)
                nome_para_id[nome_longo] = fundo_id
        
        for arquivo in arquivos_gerados:
            # Identificar fundo pelo nome do arquivo
            nome = os.path.basename(arquivo)
            
            # Extrair nome do fundo do nome do arquivo
            fundo_nome = "Sem_Fundo"  # Default
            
            # Padrão Excel: exportar-Santander - Extrato DD de MMMM de YYYY-FUNDO-AGENCIA-CONTA.xlsx
            # Padrão PDF: comprovante-ibe-FUNDO-AGENCIA-CONTA.pdf
            
            if nome.startswith('exportar-Santander'):
                # Excel: formato "exportar-Santander - Extrato DD de MMMM de YYYY-FUNDO-AGENCIA-CONTA.xlsx"
                # Extrair tudo entre último "de YYYY-" e penúltimo "-"
                match = re.search(r'de \d{4}-(.+?)-\d{4}-\d+\.xlsx$', nome)
                if match:
                    fundo_nome = match.group(1).strip()
                else:
                    print(f"   ⚠️ Não conseguiu extrair fundo do Excel: {nome}")
            elif nome.startswith('comprovante-ibe'):
                # PDF: formato "comprovante-ibe-FUNDO-AGENCIA-CONTA.pdf"
                # Extrair tudo entre "comprovante-ibe-" e "-AGENCIA-CONTA.pdf"
                match = re.search(r'comprovante-ibe-(.+?)-\d{4}-\d+\.pdf$', nome)
                if match:
                    fundo_nome = match.group(1).strip()
                else:
                    print(f"   ⚠️ Não conseguiu extrair fundo do PDF: {nome}")
            
            # Se não conseguiu extrair, tentar usar fundos_selecionados
            if fundo_nome == "Sem_Fundo" and len(fundos_selecionados) == 1:
                fundo_nome = fundos_selecionados[0]
            
            # Converter nome longo para ID curto
            fundo_id_curto = nome_para_id.get(fundo_nome, fundo_nome)
            
            if fundo_id_curto not in arquivos_por_fundo:
                arquivos_por_fundo[fundo_id_curto] = []
            arquivos_por_fundo[fundo_id_curto].append(arquivo)
        
        print(f"\n📁 Fundos identificados: {len(arquivos_por_fundo)}")
        
        # Criar mapeamento: nome_longo -> fundo_id (para nomes curtos nas pastas)
        nome_para_id = {}
        for fundo_id in fundos_selecionados:
            if fundo_id in SANTANDER_FUNDOS:
                nome_longo = SANTANDER_FUNDOS[fundo_id].get('nome', fundo_id)
                nome_para_id[nome_longo] = fundo_id
        
        for arquivo in arquivos_gerados:
            # Identificar fundo pelo nome do arquivo
            nome = os.path.basename(arquivo)
            
            # Extrair nome do fundo do nome do arquivo
            fundo_nome = "Sem_Fundo"  # Default
            
            # Padrão Excel: exportar-Santander - Extrato DD de MMMM de YYYY-FUNDO-AGENCIA-CONTA.xlsx
            # Padrão PDF: comprovante-ibe-FUNDO-AGENCIA-CONTA.pdf
            
            if nome.startswith('exportar-Santander'):
                # Excel: formato "exportar-Santander - Extrato DD de MMMM de YYYY-FUNDO-AGENCIA-CONTA.xlsx"
                match = re.search(r'de \d{4}-(.+?)-\d{4}-\d+\.xlsx$', nome)
                if match:
                    fundo_nome_longo = match.group(1)
                    # Converter nome longo para ID curto
                    fundo_nome = nome_para_id.get(fundo_nome_longo, fundo_nome_longo)
            elif nome.startswith('comprovante-ibe'):
                # PDF: formato "comprovante-ibe-FUNDO-AGENCIA-CONTA.pdf"
                match = re.search(r'comprovante-ibe-(.+?)-\d{4}-\d+', nome)
                if match:
                    fundo_nome_longo = match.group(1)
                    fundo_nome = nome_para_id.get(fundo_nome_longo, fundo_nome_longo)
            
            # Adicionar ao dicionário
            if fundo_nome not in arquivos_por_fundo:
                arquivos_por_fundo[fundo_nome] = []
            arquivos_por_fundo[fundo_nome].append(arquivo)
        
        # Criar ZIP com estrutura organizada: FUNDO/DATA/extrato.xlsx e extrato.pdf
        from zipfile import ZipFile, ZIP_STORED
        from io import BytesIO
        
        zip_buffer = BytesIO()
        
        try:
            # ZIP_STORED = sem compressão (mais confiável)
            with ZipFile(zip_buffer, 'w', ZIP_STORED) as zip_file:
                contador = 0
                
                # Agrupar arquivos por fundo E conta
                for fundo_id, arquivos in arquivos_por_fundo.items():
                    # Usar o ID do fundo diretamente (já é curto)
                    fundo_safe = fundo_id.replace(' ', '_')
                    
                    # Período para subpasta - formato curto (DDMMAAAA_DDMMAAAA)
                    periodo_str = f"{data_inicial.strftime('%d%m%Y')}_{data_final.strftime('%d%m%Y')}"
                    
                    # Agrupar arquivos por conta dentro do fundo
                    arquivos_por_conta = {}
                    
                    for arquivo in arquivos:
                        if os.path.exists(arquivo):
                            nome_original = os.path.basename(arquivo)
                            
                            # Extrair agência e conta do nome do arquivo
                            agencia = None
                            conta = None
                            
                            if 'exportar-Santander' in nome_original:
                                # Formato: exportar-Santander - Extrato ... -FUNDO-AGENCIA-CONTA.xlsx
                                match = re.search(r'-(\d{4})-(\d+)\.xlsx$', nome_original)
                                if match:
                                    agencia = match.group(1)
                                    conta = match.group(2)
                            elif 'comprovante-ibe' in nome_original:
                                # Formato: comprovante-ibe-FUNDO-AGENCIA-CONTA.pdf
                                match = re.search(r'-(\d{4})-(\d+)', nome_original)
                                if match:
                                    agencia = match.group(1)
                                    conta = match.group(2)
                            
                            if agencia and conta:
                                conta_key = f"{agencia}_{conta}"
                                if conta_key not in arquivos_por_conta:
                                    arquivos_por_conta[conta_key] = {'excel': None, 'pdf': None}
                                
                                if arquivo.endswith('.xlsx'):
                                    arquivos_por_conta[conta_key]['excel'] = arquivo
                                elif arquivo.endswith('.pdf'):
                                    arquivos_por_conta[conta_key]['pdf'] = arquivo
                    
                    # Adicionar arquivos ao ZIP organizados por conta
                    for conta_key, arquivos_conta in arquivos_por_conta.items():
                        # Se há apenas uma conta, não criar subpasta de conta
                        if len(arquivos_por_conta) == 1:
                            # Estrutura: FUNDO/DATA/extrato.xlsx
                            pasta_destino = f"{fundo_safe}/{periodo_str}"
                        else:
                            # Estrutura: FUNDO/DATA/CONTA/extrato.xlsx
                            pasta_destino = f"{fundo_safe}/{periodo_str}/{conta_key}"
                        
                        # Adicionar Excel
                        if arquivos_conta['excel']:
                            caminho_zip = f"{pasta_destino}/extrato.xlsx"
                            zip_file.write(arquivos_conta['excel'], caminho_zip)
                            contador += 1
                        
                        # Adicionar PDF
                        if arquivos_conta['pdf']:
                            caminho_zip = f"{pasta_destino}/extrato.pdf"
                            zip_file.write(arquivos_conta['pdf'], caminho_zip)
                            contador += 1
            
            # Obter bytes do ZIP
            zip_bytes = zip_buffer.getvalue()
            zip_size = len(zip_bytes)
            
            # Nome do arquivo ZIP
            data_hora = datetime.now().strftime("%Y%m%d_%H%M%S")
            periodo_str = f"{data_inicial.strftime('%d-%m-%Y')}_a_{data_final.strftime('%d-%m-%Y')}"
            nome_zip = f"extratos_bancarios_{periodo_str}_{data_hora}.zip"
            
            # Botão de download
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.download_button(
                    label="📥 Baixar Todos os Arquivos (ZIP)",
                    data=zip_bytes,
                    file_name=nome_zip,
                    mime="application/zip",
                    use_container_width=True
                )
                st.caption(f"💾 {len(arquivos_gerados)} arquivo(s) • {zip_size/1024/1024:.2f} MB")
            
        except Exception as e:
            st.error(f"Erro ao criar ZIP: {e}")
    else:
        st.warning("⚠️ Nenhum arquivo foi gerado. Verifique os fundos selecionados.")

# ========== INFORMAÇÕES E AJUDA ==========
st.markdown("---")
st.markdown('<div class="section-title">ℹ️ Informações</div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📖 Como Usar", "📋 Fundos Disponíveis", "📄 Sobre os Formatos"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### Passo a Passo
        
        1. **📁 Selecione os fundos**
           - Use a caixa de seleção múltipla
           - Ou marque "Selecionar todos"
        
        2. **📅 Defina o período**
           - Escolha um preset comum
           - Ou selecione "Personalizado" para datas específicas
        
        3. **📄 Escolha os formatos**
           - Excel para planilhas
           - PDF para documentos formatados
           - Ou ambos!
        """)
    
    with col2:
        st.markdown("""
        ### Dicas Importantes
        
        - ⏱️ O processamento pode levar alguns minutos dependendo da quantidade de fundos
        - 📁 Os arquivos são salvos no diretório do projeto
        - ⚠️ Certifique-se de que as credenciais estão configuradas
        - 🔄 A data final não pode ser anterior à data inicial
        """)

with tab2:
    st.markdown(f"### Total de {len(fundos_disponiveis)} fundos cadastrados")
    
    # Exibir em grid
    cols = st.columns(4)
    for idx, fundo_id in enumerate(fundos_disponiveis):
        fundo_info = SANTANDER_FUNDOS[fundo_id]
        with cols[idx % 4]:
            st.markdown(f"""
            <div class="fundo-card">
                <strong>{fundo_id}</strong><br>
                <small>{fundo_info.get('nome', 'Sem nome')}</small>
            </div>
            """, unsafe_allow_html=True)

with tab3:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 📊 Formato Excel (.xlsx)
        
        **Características:**
        - Layout IBE Santander
        - Estrutura: AGENCIA | CONTA
        - Tabela com SALDO ANTERIOR
        - Colunas: Data, Histórico, Documento, Valor, Saldo
        - Valores negativos em vermelho
        - Cálculo progressivo de saldo
        
        **Ideal para:**
        - Análises em planilhas
        - Manipulação de dados
        - Integração com outros sistemas
        """)
    
    with col2:
        st.markdown("""
        ### 📑 Formato PDF (.pdf)
        
        **Características:**
        - Layout Internet Banking Empresarial
        - Cabeçalho completo com logo
        - Breadcrumb de navegação
        - Tabela de transações formatada
        - Legenda de símbolos (a, b, p)
        - Composição de saldo (A, B, C)
        - Rodapé com contatos Santander
        
        **Ideal para:**
        - Arquivamento
        - Apresentações
        - Comprovantes oficiais
        """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #1e5546; padding: 1rem;'>
    <p><strong>Kanastra</strong> • Sistema de Extratos Bancários Santander</p>
    <p style='font-size: 0.9rem;'>© 2025 Kanastra • Desenvolvido com Streamlit</p>
</div>
""", unsafe_allow_html=True)
