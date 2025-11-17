"""
Dashboard Streamlit para Busca de Extratos Bancários
Identidade Visual: Kanastra
Bancos suportados: Santander (Itaú e Arbi em desenvolvimento)
Acesso restrito: apenas e-mails @kanastra.com.br ou @liminedtvm.com
"""

import streamlit as st
from datetime import datetime, timedelta
import os
import sys
import re

# Adicionar diretório ao path para imports
sys.path.insert(0, os.path.dirname(__file__))

# Configuração da página
st.set_page_config(
    page_title="Extratos Bancários - Kanastra",
    page_icon="https://www.kanastra.design/symbol.svg",
    layout="wide"
)

"""
Dashboard Streamlit para Busca de Extratos Bancários
Identidade Visual: Kanastra
Bancos suportados: Santander (Itaú e Arbi em desenvolvimento)
Acesso restrito via Streamlit Authentication (configurar no Cloud)
"""

import streamlit as st
from datetime import datetime, timedelta
import os
import sys
import re

# Adicionar diretório ao path para imports
sys.path.insert(0, os.path.dirname(__file__))

# Configuração da página
st.set_page_config(
    page_title="Extratos Bancários - Kanastra",
    page_icon="https://www.kanastra.design/symbol.svg",
    layout="wide"
)

# ========== AUTENTICAÇÃO VIA STREAMLIT CLOUD ==========
# Instruções de configuração:
# 1. No Streamlit Cloud, vá em Settings > Secrets
# 2. Adicione:
#    [auth]
#    emails_permitidos = ["email1@kanastra.com.br", "email2@kanastra.com.br", "email3@liminedtvm.com"]
# 3. Ou configure "Viewer authentication" em Settings > Sharing para restringir por e-mail do Google

# Verificar se está usando autenticação do Streamlit Cloud
def verificar_autenticacao_streamlit():
    """
    Verifica se o app está usando autenticação nativa do Streamlit Cloud.
    Se sim, o e-mail do usuário estará disponível em st.experimental_user
    """
    try:
        # Tentar obter e-mail do usuário autenticado pelo Streamlit Cloud
        user_info = st.experimental_user
        if user_info and hasattr(user_info, 'email'):
            email = user_info.email.lower()
            # Verificar se o e-mail é de domínio permitido
            dominios_permitidos = ["@kanastra.com.br", "@liminedtvm.com"]
            if any(email.endswith(dominio) for dominio in dominios_permitidos):
                st.session_state.usuario_email = email
                st.session_state.autenticado = True
                return True
            else:
                st.error(f"❌ Acesso negado! O e-mail {email} não pertence aos domínios autorizados (@kanastra.com.br ou @liminedtvm.com)")
                st.stop()
        return False
    except:
        # Se não estiver no Streamlit Cloud ou sem autenticação, retorna False
        return False

# Verificar autenticação do Streamlit Cloud primeiro
if verificar_autenticacao_streamlit():
    # Usuário autenticado via Streamlit Cloud
    pass
else:
    # Fallback: verificar se há lista de e-mails em secrets (para desenvolvimento local)
    try:
        emails_permitidos = st.secrets.get("auth", {}).get("emails_permitidos", [])
        if emails_permitidos and isinstance(emails_permitidos, list):
            # Modo de desenvolvimento com lista de e-mails
            if "autenticado" not in st.session_state:
                st.session_state.autenticado = False
            
            if not st.session_state.autenticado:
                st.markdown('<div style="text-align: center;"><h1>🔐 Acesso Restrito</h1></div>', unsafe_allow_html=True)
                st.markdown('<div style="text-align: center;"><h3>Extratos Bancários - Kanastra</h3></div>', unsafe_allow_html=True)
                st.markdown("---")
                
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.warning("⚠️ **Modo de desenvolvimento ativo**\n\nEm produção, use a autenticação nativa do Streamlit Cloud.")
                    st.info(f"📋 **E-mails autorizados:** {len(emails_permitidos)} cadastrado(s)")
                    
                    with st.form("login_dev"):
                        email = st.selectbox("📧 Selecione seu e-mail:", [""] + emails_permitidos)
                        if st.form_submit_button("🔓 Acessar (DEV)", use_container_width=True):
                            if email:
                                st.session_state.autenticado = True
                                st.session_state.usuario_email = email
                                st.rerun()
                            else:
                                st.error("Selecione um e-mail válido")
                    
                    st.caption("🛡️ Sistema protegido | Kanastra © 2025")
                st.stop()
        else:
            # Sem autenticação configurada - mostrar aviso
            st.error("""
            ⚠️ **ATENÇÃO: Autenticação não configurada!**
            
            Para proteger este aplicativo:
            
            **Opção 1 (Recomendado): Autenticação Nativa do Streamlit Cloud**
            1. Vá em **Settings > Sharing** no Streamlit Cloud
            2. Ative **"Viewer authentication"**
            3. Adicione os e-mails autorizados (@kanastra.com.br ou @liminedtvm.com)
            
            **Opção 2: Secrets (Desenvolvimento)**
            1. Vá em **Settings > Secrets**
            2. Adicione:
            ```
            [auth]
            emails_permitidos = ["email1@kanastra.com.br", "email2@liminedtvm.com"]
            ```
            """)
            st.stop()
    except:
        # Erro ao acessar secrets
        st.error("❌ Erro ao verificar configuração de autenticação. Configure secrets ou autenticação do Streamlit Cloud.")
        st.stop()


# CSS customizado - Kanastra Brand
st.markdown("""
<style>
    /* Cores Kanastra */
    :root {
        --kanastra-green: #193c32;
        --tech-green-1: #1e5546;
        --tech-green-2: #14735a;
        --tech-green-3: #2daa82;
        --light-gray: #f3f2f3;
    }
    
    /* Headers */
    .main-header {
        font-size: 2.8rem;
        font-weight: 700;
        color: #193c32;
        margin-bottom: 0.5rem;
        font-family: 'Inter', sans-serif;
    }
    .sub-header {
        font-size: 1.3rem;
        color: #1e5546;
        margin-bottom: 1.5rem;
        font-weight: 400;
    }
    
    /* Seções */
    .section-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #193c32;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 3px solid #2daa82;
        padding-bottom: 0.5rem;
    }
    
    /* Botões */
    .stButton>button {
        background-color: #14735a !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        padding: 0.75rem 2rem !important;
        border: none !important;
        transition: all 0.3s ease !important;
        font-size: 1.1rem !important;
    }
    .stButton>button:hover {
        background-color: #2daa82 !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(20, 115, 90, 0.4) !important;
    }
    
    /* Success/Info boxes */
    .success-box {
        padding: 1rem;
        border-radius: 8px;
        background-color: #d4edda;
        border-left: 5px solid #2daa82;
        margin: 1rem 0;
        color: #193c32;
    }
    .info-box {
        padding: 1rem;
        border-radius: 8px;
        background-color: #f3f2f3;
        border-left: 5px solid #1e5546;
        margin: 1rem 0;
        color: #193c32;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background-color: #f3f2f3;
        padding: 0.5rem;
        border-radius: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        color: #193c32;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
    }
    .stTabs [aria-selected="true"] {
        color: #14735a;
        background-color: white;
        border-radius: 6px;
    }
    
    /* Inputs */
    .stSelectbox label, .stMultiSelect label, .stCheckbox label, .stDateInput label {
        color: #193c32 !important;
        font-weight: 600 !important;
    }
    
    /* Containers */
    .element-container {
        background-color: white;
    }
    
    /* Cards de fundos */
    .fundo-card {
        padding: 0.75rem;
        background-color: #f3f2f3;
        border-radius: 6px;
        margin-bottom: 0.5rem;
        border-left: 3px solid #2daa82;
    }
    .fundo-card strong {
        color: #193c32;
    }
    
    /* Progress bar */
    .stProgress > div > div > div > div {
        background-color: #2daa82;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #14735a;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #f3f2f3;
    }
    [data-testid="stSidebar"] h3 {
        color: #193c32;
        font-weight: 700;
    }
    [data-testid="stSidebar"] .stRadio > label {
        color: #193c32;
        font-weight: 600;
    }
    
    /* Cards de banco na sidebar */
    .banco-card {
        padding: 0.75rem 1rem;
        margin: 0.5rem 0;
        border-radius: 6px;
        border: 1px solid #e0e0e0;
        background-color: white;
        text-align: center;
        font-size: 1rem;
        transition: all 0.2s ease;
    }
    .banco-card.selected {
        background-color: #14735a;
        color: white;
        border-color: #14735a;
        font-weight: 600;
    }
    .banco-card.disabled {
        background-color: #f8f8f8;
        color: #aaa;
        border-color: #e5e5e5;
    }
</style>
""", unsafe_allow_html=True)

# Header com logo Kanastra
col_logo, col_title, col_logout = st.columns([1, 5, 1])
with col_logo:
    st.image("https://www.kanastra.design/symbol-green.svg", width=100)
with col_title:
    st.markdown('<div class="main-header">Extratos Bancários</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Geração automatizada de extratos em formato Excel e PDF</div>', unsafe_allow_html=True)
with col_logout:
    # Mostrar informações do usuário se disponível
    if "usuario_email" in st.session_state and st.session_state.usuario_email:
        st.write("")  # Espaço
        st.caption(f"👤 {st.session_state.usuario_email.split('@')[0]}")
        # Botão de logout apenas se estiver em modo dev (com session_state)
        if "autenticado" in st.session_state:
            if st.button("🚪 Sair", use_container_width=True):
                st.session_state.autenticado = False
                st.session_state.usuario_email = None
                st.rerun()

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
    st.error(f"❌ Erro ao carregar credenciais: {str(e)}")
    st.info("""
    **Configuração necessária:**
    - **Streamlit Cloud**: Configure os secrets em Settings > Secrets
    - **Local**: Crie o arquivo `credenciais_bancos.py` com as credenciais
    
    Veja o arquivo `DEPLOY.md` para mais detalhes.
    """)
    st.stop()

# Lista de fundos disponíveis
fundos_disponiveis = sorted(list(SANTANDER_FUNDOS.keys()))

st.markdown("---")

# ========== SEÇÃO 1: SELEÇÃO DE FUNDOS ==========
st.markdown('<div class="section-title">📁 Seleção de Fundos</div>', unsafe_allow_html=True)

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
st.markdown('<div class="section-title">📅 Definição de Período</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    preset_periodo = st.selectbox(
        "Período pré-definido:",
        ["Últimos 7 dias", "Últimos 15 dias", "Últimos 30 dias", "Mês atual", "Mês anterior", "Personalizado"],
        help="Escolha um período pré-definido ou selecione 'Personalizado' para definir datas específicas"
    )

# Calcular datas baseado no preset
hoje = datetime.now().date()
if preset_periodo == "Últimos 7 dias":
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
    st.error("❌ Data inicial não pode ser maior que data final")

# ========== SEÇÃO 3: FORMATOS DE EXPORTAÇÃO ==========
st.markdown('<div class="section-title">📄 Formatos de Exportação</div>', unsafe_allow_html=True)

col1, col2 = st.columns([1, 2])

with col1:
    st.info("📊 **Excel (.xlsx)** sempre será gerado")
    gerar_pdf = st.checkbox("📑 Gerar também PDF (.pdf)", value=True, help="Gera arquivo PDF no formato Internet Banking Empresarial")

with col2:
    formatos_str = ["Excel"]
    if gerar_pdf:
        formatos_str.append("PDF")
    st.success(f"✅ Formatos que serão gerados: **{' e '.join(formatos_str)}**")

st.markdown("---")

# ========== BOTÃO DE GERAÇÃO ==========
buscar_disabled = (
    len(fundos_selecionados) == 0 or
    data_inicial > data_final
)

# Inicializar session_state para controlar execução
if 'processando' not in st.session_state:
    st.session_state.processando = False

if st.button("▶️ Gerar Extratos", disabled=buscar_disabled or st.session_state.processando, use_container_width=True):
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
            st.warning("⚠️ Nenhum arquivo foi gerado. Verifique se os fundos selecionados têm contas cadastradas no período.")
        else:
            status_text.success(f"✅ {len(arquivos_gerados)} arquivo(s) gerado(s) com sucesso!")
            
    except Exception as e:
        progress_bar.progress(1.0)
        status_text.error("❌ Erro durante processamento")
        st.error(f"❌ Erro: {str(e)}")
        import traceback
        with st.expander("🔴 Detalhes do erro"):
            st.code(traceback.format_exc())
    
    finally:
        # Restaurar stdout
        sys.stdout = old_stdout
        
        # Liberar estado de processamento
        st.session_state.processando = False
    
    # Mostrar resultados apenas se há arquivos gerados
    if arquivos_gerados:
        st.markdown("---")
        st.markdown('<div class="section-title">📥 Arquivos Gerados</div>', unsafe_allow_html=True)
        
        # Agrupar por tipo
        excels = [f for f in arquivos_gerados if f.endswith('.xlsx')]
        pdfs = [f for f in arquivos_gerados if f.endswith('.pdf')]
        
        # Resumo simples
        st.success(f"✅ {len(excels)} planilha(s) Excel e {len(pdfs)} arquivo(s) PDF gerado(s)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if excels:
                st.markdown(f"**📊 Excel:** {len(excels)} arquivo(s)")
        
        with col2:
            if pdfs:
                st.markdown(f"**📑 PDF:** {len(pdfs)} arquivo(s)")
        
        # Botão para baixar ZIP com todos os arquivos
        st.markdown("---")
        
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
