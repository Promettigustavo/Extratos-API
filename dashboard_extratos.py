"""
Dashboard Streamlit para Busca de Extratos Bancários Santander
Identidade Visual: Kanastra
"""

import streamlit as st
from datetime import datetime, timedelta
import os
import sys

# Adicionar diretório ao path para imports
sys.path.insert(0, os.path.dirname(__file__))

# Configuração da página
st.set_page_config(
    page_title="Extratos Bancários Santander - Kanastra",
    page_icon="https://www.kanastra.design/symbol.svg",
    layout="wide"
)

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
</style>
""", unsafe_allow_html=True)

# Header com logo Kanastra
col_logo, col_title = st.columns([1, 6])
with col_logo:
    st.image("https://www.kanastra.design/symbol-green.svg", width=100)
with col_title:
    st.markdown('<div class="main-header">Extratos Bancários Santander</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Geração automatizada de extratos em formato Excel e PDF</div>', unsafe_allow_html=True)

# Import condicional - suporta tanto ambiente local quanto Streamlit Cloud
try:
    # Tentar carregar config_credentials primeiro (suporta Streamlit Secrets)
    try:
        from config_credentials import SANTANDER_FUNDOS
    except ImportError:
        # Fallback para credenciais locais
        from credenciais_bancos import SANTANDER_FUNDOS
    
    from buscar_extratos_bancarios import SantanderExtratosBancarios, main
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
    
    # Barra de progresso e status
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Preparar parâmetros - converter date para datetime
    from datetime import datetime as dt
    data_inicial_dt = dt.combine(data_inicial, dt.min.time())
    data_final_dt = dt.combine(data_final, dt.max.time())
    pasta_saida = os.getcwd()
    
    status_text.text(f"🔄 Processando {len(fundos_selecionados)} fundo(s)...")
    progress_bar.progress(0.1)
    
    # Container para logs em tempo real
    log_container = st.expander("📋 Logs de Processamento", expanded=True)
    
    # Capturar stdout
    import sys
    from io import StringIO
    
    old_stdout = sys.stdout
    sys.stdout = log_output = StringIO()
    
    arquivos_gerados = []
    
    # Marcar timestamp de início - buscar arquivos dos últimos 15 minutos
    from datetime import datetime, timedelta
    timestamp_inicio = datetime.now() - timedelta(minutes=15)
    
    try:
        # Chamar função main com lista de fundos e objetos datetime
        main(
            fundos=fundos_selecionados,
            data_inicial=data_inicial_dt,
            data_final=data_final_dt,
            pasta_saida=pasta_saida,
            gerar_pdf=gerar_pdf
        )
        
        progress_bar.progress(0.8)
        status_text.text("🔍 Buscando arquivos gerados...")
        
        # Forçar flush/sync dos arquivos antes de criar ZIP
        import sys
        sys.stdout.flush()
        import time
        time.sleep(0.5)  # Pequena pausa para garantir que arquivos foram escritos
        
        # Buscar arquivos gerados nos últimos 15 minutos
        import glob
        
        # Debug: listar todos os arquivos no diretório
        todos_arquivos = os.listdir(pasta_saida)
        arquivos_xlsx = [f for f in todos_arquivos if f.endswith('.xlsx')]
        arquivos_pdf = [f for f in todos_arquivos if f.endswith('.pdf')]
        
        print(f"\n🔍 DEBUG - Arquivos no diretório {pasta_saida}:")
        print(f"   Excel encontrados: {len(arquivos_xlsx)}")
        for f in arquivos_xlsx[:5]:  # Mostrar os 5 primeiros
            print(f"      - {f}")
        print(f"   PDF encontrados: {len(arquivos_pdf)}")
        for f in arquivos_pdf[:5]:  # Mostrar os 5 primeiros
            print(f"      - {f}")
        
        # Procurar TODOS os arquivos Excel gerados (novo padrão com nome do fundo)
        # Padrão: exportar-Santander - Extrato DD de MMMM de YYYY-FUNDO-AGENCIA-CONTA.xlsx
        for arquivo in arquivos_xlsx:
            arquivo_completo = os.path.join(pasta_saida, arquivo)
            if arquivo_completo not in arquivos_gerados:  # Evitar duplicatas
                if datetime.fromtimestamp(os.path.getmtime(arquivo_completo)) > timestamp_inicio:
                    arquivos_gerados.append(arquivo_completo)
                    print(f"   ✅ Adicionado: {arquivo}")
        
        # Procurar TODOS os arquivos PDF se solicitado
        # Padrão: comprovante-ibe-FUNDO-AGENCIA-CONTA-UUID.pdf
        if gerar_pdf:
            for arquivo in arquivos_pdf:
                arquivo_completo = os.path.join(pasta_saida, arquivo)
                # Excluir exemplos ou arquivos antigos
                if "(1).pdf" not in arquivo and arquivo_completo not in arquivos_gerados:
                    if datetime.fromtimestamp(os.path.getmtime(arquivo_completo)) > timestamp_inicio:
                        arquivos_gerados.append(arquivo_completo)
                        print(f"   ✅ Adicionado: {arquivo}")
        
        progress_bar.progress(1.0)
        status_text.text("✅ Processamento concluído!")
        
        # Debug: mostrar total de arquivos encontrados
        print(f"\n📊 Total de arquivos detectados: {len(arquivos_gerados)}")
        print(f"   - Excel: {len([f for f in arquivos_gerados if f.endswith('.xlsx')])}")
        print(f"   - PDF: {len([f for f in arquivos_gerados if f.endswith('.pdf')])}")
        
        # Validar se há arquivos antes de continuar
        if len(arquivos_gerados) == 0:
            st.warning("⚠️ Nenhum arquivo foi gerado. Verifique se os fundos selecionados têm contas cadastradas.")
            st.session_state.processando = False
            st.stop()
            
    except Exception as e:
        progress_bar.progress(1.0)
        status_text.text("❌ Erro durante processamento")
        st.error(f"❌ Erro: {str(e)}")
        import traceback
        with st.expander("🔴 Detalhes do erro"):
            st.code(traceback.format_exc())
    
    finally:
        # Restaurar stdout e mostrar logs
        sys.stdout = old_stdout
        log_text = log_output.getvalue()
        
        with log_container:
            if log_text:
                st.code(log_text, language="text")
            else:
                st.info("Nenhum log capturado")
        
        # Liberar estado de processamento
        st.session_state.processando = False
    
    # Mostrar resultados
    st.markdown("---")
    
    if arquivos_gerados:
        st.markdown('<div class="section-title">📥 Arquivos Gerados</div>', unsafe_allow_html=True)
        
        st.success(f"🎉 Total: {len(arquivos_gerados)} arquivo(s) gerado(s) com sucesso!")
        
        # Informação sobre fundos sem transações
        if len(fundos_selecionados) > 1:
            st.info("ℹ️ **Nota:** Fundos sem transações no período também tiveram arquivos gerados mostrando apenas os saldos atuais. Confira o resumo nos logs acima.")
        
        # Agrupar por tipo
        excels = [f for f in arquivos_gerados if f.endswith('.xlsx')]
        pdfs = [f for f in arquivos_gerados if f.endswith('.pdf')]
        
        col1, col2 = st.columns(2)
        
        with col1:
            if excels:
                st.markdown("**📊 Arquivos Excel:**")
                # Mostrar apenas os primeiros 10, depois resumo
                for arquivo in sorted(excels)[:10]:
                    tamanho = os.path.getsize(arquivo) / 1024  # KB
                    nome = os.path.basename(arquivo)
                    # Encurtar nome se muito longo
                    if len(nome) > 50:
                        nome = nome[:47] + "..."
                    st.markdown(f"- `{nome}` ({tamanho:.1f} KB)")
                if len(excels) > 10:
                    st.markdown(f"- ... e mais {len(excels) - 10} arquivo(s)")
        
        with col2:
            if pdfs:
                st.markdown("**📑 Arquivos PDF:**")
                # Mostrar apenas os primeiros 10, depois resumo
                for arquivo in sorted(pdfs)[:10]:
                    tamanho = os.path.getsize(arquivo) / 1024  # KB
                    nome = os.path.basename(arquivo)
                    # Encurtar nome se muito longo
                    if len(nome) > 50:
                        nome = nome[:47] + "..."
                    st.markdown(f"- `{nome}` ({tamanho:.1f} KB)")
                if len(pdfs) > 10:
                    st.markdown(f"- ... e mais {len(pdfs) - 10} arquivo(s)")
        
        st.info(f"📁 Diretório: `{os.path.dirname(arquivos_gerados[0])}`")
        
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
        for arquivo in arquivos_gerados:
            # Identificar fundo pelo nome do arquivo
            nome = os.path.basename(arquivo)
            
            # Extrair nome do fundo do nome do arquivo
            fundo_nome = "Sem_Fundo"  # Default
            
            # Padrão Excel: exportar-Santander - Extrato DD de MMMM de YYYY-FUNDO-AGENCIA-CONTA.xlsx
            # Padrão PDF: comprovante-ibe-FUNDO-AGENCIA-CONTA-UUID.pdf
            
            if nome.startswith('exportar-Santander'):
                # Excel: formato "exportar-Santander - Extrato DD de MMMM de YYYY-FUNDO-AGENCIA-CONTA.xlsx"
                # Extrair tudo entre último "de YYYY-" e penúltimo "-"
                match = re.search(r'de \d{4}-(.+?)-\d{4}-\d+\.xlsx$', nome)
                if match:
                    fundo_nome = match.group(1).strip()
                else:
                    print(f"   ⚠️ Não conseguiu extrair fundo do Excel: {nome}")
            elif nome.startswith('comprovante-ibe'):
                # PDF: formato "comprovante-ibe-FUNDO-AGENCIA-CONTA-UUID.pdf"
                # UUID pode ter maiúsculas, minúsculas e hífens
                match = re.search(r'comprovante-ibe-(.+?)-\d{4}-\d+-[A-Fa-f0-9\-]+\.pdf$', nome, re.IGNORECASE)
                if match:
                    fundo_nome = match.group(1).strip()
                else:
                    print(f"   ⚠️ Não conseguiu extrair fundo do PDF: {nome}")
            
            # Se não conseguiu extrair, tentar usar fundos_selecionados
            if fundo_nome == "Sem_Fundo" and len(fundos_selecionados) == 1:
                fundo_nome = fundos_selecionados[0]
            
            if fundo_nome not in arquivos_por_fundo:
                arquivos_por_fundo[fundo_nome] = []
            arquivos_por_fundo[fundo_nome].append(arquivo)
        
        print(f"\n📁 Fundos identificados: {len(arquivos_por_fundo)}")
        for fundo in sorted(arquivos_por_fundo.keys()):
            print(f"   - {fundo}: {len(arquivos_por_fundo[fundo])} arquivo(s)")
        
        # Criar ZIP com configuração mais compatível
        zip_buffer = BytesIO()
        arquivos_adicionados = 0
        arquivos_com_erro = []
        
        print(f"\n📦 Iniciando criação do ZIP...")
        
        try:
            # Usar ZIP_DEFLATED com nível de compressão baixo para melhor compatibilidade
            with ZipFile(zip_buffer, 'w', ZIP_DEFLATED, allowZip64=True, compresslevel=1) as zip_file:
                for fundo, arquivos in arquivos_por_fundo.items():
                    # Criar nome de pasta seguro (sem caracteres especiais)
                    fundo_safe = fundo.strip()
                    fundo_safe = re.sub(r'[^\w\s-]', '', fundo_safe)  # Remove caracteres especiais
                    fundo_safe = re.sub(r'\s+', '_', fundo_safe)  # Espaços -> underscore
                    fundo_safe = re.sub(r'_+', '_', fundo_safe)  # Múltiplos underscores -> um
                    fundo_safe = fundo_safe.strip('_')  # Remove underscores das pontas
                    
                    # Limitar tamanho (max 80 chars para deixar espaço pro resto do caminho)
                    if len(fundo_safe) > 80:
                        fundo_safe = fundo_safe[:80].rstrip('_')
                    
                    print(f"\n📂 Processando fundo: {fundo_safe}")
                    
                    # Período para subpasta
                    periodo_str = f"{data_inicial.strftime('%d-%m-%Y')}_a_{data_final.strftime('%d-%m-%Y')}"
                    
                    for arquivo in arquivos:
                        if not os.path.exists(arquivo):
                            print(f"   ⚠️ Arquivo não encontrado: {arquivo}")
                            arquivos_com_erro.append(arquivo)
                            continue
                        
                        nome_arquivo = os.path.basename(arquivo)
                        
                        # Estrutura: FUNDO/DATA/arquivo.ext
                        caminho_zip = f"{fundo_safe}/{periodo_str}/{nome_arquivo}"
                        
                        try:
                            # Validar encoding
                            caminho_zip.encode('cp437')  # Encoding padrão do ZIP
                            
                            # Adicionar ao ZIP
                            zip_file.write(arquivo, caminho_zip)
                            arquivos_adicionados += 1
                            
                            if arquivos_adicionados <= 10:
                                print(f"   ✅ {nome_arquivo[:60]}")
                            elif arquivos_adicionados == 11:
                                print(f"   ... (mostrando apenas primeiros 10 por fundo)")
                                
                        except UnicodeEncodeError:
                            # Se falhar no cp437, tentar com nome simplificado
                            print(f"   ⚠️ Encoding inválido, simplificando: {nome_arquivo[:40]}...")
                            nome_simples = re.sub(r'[^\w\s.-]', '', nome_arquivo)
                            caminho_zip = f"{fundo_safe}/{periodo_str}/{nome_simples}"
                            try:
                                zip_file.write(arquivo, caminho_zip)
                                arquivos_adicionados += 1
                            except Exception as e:
                                print(f"   ❌ ERRO: {e}")
                                arquivos_com_erro.append(arquivo)
                        except Exception as e:
                            print(f"   ❌ ERRO ao adicionar: {e}")
                            arquivos_com_erro.append(arquivo)
            
            print(f"\n✅ {arquivos_adicionados} arquivo(s) adicionados ao ZIP")
            if arquivos_com_erro:
                print(f"⚠️  {len(arquivos_com_erro)} arquivo(s) com erro")
            
        except Exception as e:
            print(f"\n❌ ERRO CRÍTICO ao criar ZIP: {e}")
            import traceback
            traceback.print_exc()
            st.error(f"Erro ao criar ZIP: {e}")
            zip_buffer = None
        
        # Aguardar um pouco para garantir que o ZIP foi completamente escrito
        import time
        time.sleep(0.2)
        
        if zip_buffer and arquivos_adicionados > 0:
            # CRÍTICO: Não fazer seek antes de obter o valor completo
            # Vamos criar uma cópia do buffer para garantir integridade
            try:
                zip_bytes = zip_buffer.getvalue()
                print(f"\n📦 ZIP finalizado: {len(zip_bytes)} bytes ({len(zip_bytes)/1024:.1f} KB)")
                
                # Recriar buffer com os bytes completos
                zip_buffer = BytesIO(zip_bytes)
                zip_size = len(zip_bytes)
            except Exception as e:
                print(f"❌ Erro ao finalizar ZIP: {e}")
                st.error(f"Erro ao finalizar ZIP: {e}")
                zip_buffer = None
        
        if zip_buffer:
            # Testar integridade do ZIP
            zip_valido = False
            try:
                zip_buffer.seek(0)
                with ZipFile(zip_buffer, 'r') as test_zip:
                    zip_info = test_zip.namelist()
                    print(f"✅ ZIP válido com {len(zip_info)} arquivo(s)")
                    for info in zip_info[:10]:  # Mostrar os primeiros 10
                        print(f"   - {info}")
                    if len(zip_info) > 10:
                        print(f"   ... e mais {len(zip_info) - 10} arquivo(s)")
                zip_buffer.seek(0)  # Voltar ao início após teste
                zip_valido = True
            except Exception as e:
                print(f"❌ ERRO: ZIP está corrompido! {e}")
                import traceback
                traceback.print_exc()
                st.error(f"ZIP inválido: {e}")
            
            # Nome do arquivo ZIP
            data_hora = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_zip = f"extratos_santander_{data_hora}.zip"
            
            # Botão de download apenas se ZIP for válido
            if zip_valido:
                col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
                with col_btn2:
                    st.download_button(
                        label="📦 Baixar Todos os Comprovantes (ZIP)",
                        data=zip_buffer.getvalue(),  # Usar getvalue() ao invés do buffer direto
                        file_name=nome_zip,
                        mime="application/zip",
                        use_container_width=True
                    )
                    st.caption(f"Download: {nome_zip} ({len(arquivos_gerados)} arquivo(s) - {zip_size/1024:.1f} KB)")
            else:
                st.error("❌ Não foi possível criar o arquivo ZIP. Verifique os logs para mais detalhes.")
        elif arquivos_adicionados == 0:
            st.warning("⚠️ Nenhum arquivo foi adicionado ao ZIP. Verifique se os arquivos foram gerados corretamente.")
        else:
            st.error("❌ Erro ao criar ZIP. Verifique os logs para mais detalhes.")
    else:
        st.markdown('<div class="section-title">⚠️ Atenção</div>', unsafe_allow_html=True)
        st.warning("Nenhum arquivo foi detectado como gerado recentemente.")
        
        # Debug: Mostrar todos os arquivos Excel e PDF no diretório
        with st.expander("🔍 Debug - Arquivos no diretório"):
            import glob
            
            st.markdown("**Arquivos Excel encontrados:**")
            todos_excel = glob.glob(os.path.join(pasta_saida, "exportar-Santander*.xlsx"))
            if todos_excel:
                for arq in sorted(todos_excel)[-10:]:  # Últimos 10
                    mtime = datetime.fromtimestamp(os.path.getmtime(arq))
                    st.text(f"  {os.path.basename(arq)} - Modificado: {mtime.strftime('%d/%m/%Y %H:%M:%S')}")
            else:
                st.text("  Nenhum arquivo Excel encontrado")
            
            st.markdown("**Arquivos PDF encontrados:**")
            todos_pdf = glob.glob(os.path.join(pasta_saida, "comprovante-ibe*.pdf"))
            if todos_pdf:
                for arq in sorted(todos_pdf)[-10:]:  # Últimos 10
                    mtime = datetime.fromtimestamp(os.path.getmtime(arq))
                    st.text(f"  {os.path.basename(arq)} - Modificado: {mtime.strftime('%d/%m/%Y %H:%M:%S')}")
            else:
                st.text("  Nenhum arquivo PDF encontrado")
            
            st.markdown(f"**Diretório de busca:** `{pasta_saida}`")

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
