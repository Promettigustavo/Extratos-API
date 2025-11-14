"""
Script para testar download de PDF de extrato via API Santander
Testa se existe endpoint similar ao de comprovantes
"""

from buscar_extratos_bancarios import SantanderExtratosBancarios
from datetime import datetime, timedelta
import time

def testar_pdf_extrato():
    """
    Testa a funcionalidade de download de PDF de extrato
    """
    print("=" * 80)
    print("TESTE DE DOWNLOAD DE PDF DE EXTRATO VIA API")
    print("=" * 80)
    
    # Usar fundo de teste
    fundo_teste = "AUTO X"
    
    print(f"\n📋 Fundo: {fundo_teste}")
    
    # Criar cliente
    cliente = SantanderExtratosBancarios(fundo_teste)
    
    # Buscar contas
    print("\n" + "=" * 80)
    print("PASSO 1: Listar contas")
    print("=" * 80)
    
    contas = cliente.listar_contas()
    
    if not contas:
        print("❌ Nenhuma conta encontrada")
        return
    
    # Usar primeira conta
    conta = contas[0]
    branch_code = conta.get('branchCode')
    account_number = conta.get('number')
    
    print(f"\n✅ Usando conta: {branch_code}.{account_number}")
    
    # Período de teste: últimos 7 dias
    data_fim = datetime.now()
    data_inicio = data_fim - timedelta(days=7)
    
    data_inicio_str = data_inicio.strftime("%Y-%m-%d")
    data_fim_str = data_fim.strftime("%Y-%m-%d")
    
    print(f"   Período: {data_inicio_str} a {data_fim_str}")
    
    # PASSO 2: Solicitar geração do PDF
    print("\n" + "=" * 80)
    print("PASSO 2: Solicitar geração do PDF")
    print("=" * 80)
    
    resultado_solicitacao = cliente.solicitar_pdf_extrato(
        branch_code,
        account_number,
        data_inicio_str,
        data_fim_str
    )
    
    if not resultado_solicitacao:
        print("\n⚠️  Endpoint não disponível ou erro na solicitação")
        print("   A API de extratos pode não ter endpoint de PDF")
        print("   Continuaremos usando PDF gerado localmente")
        return
    
    request_id = resultado_solicitacao.get('request_id')
    account_id = resultado_solicitacao.get('account_id')
    
    if not request_id:
        print("❌ request_id não retornado")
        return
    
    # PASSO 3: Aguardar e consultar status
    print("\n" + "=" * 80)
    print("PASSO 3: Aguardar processamento e consultar status")
    print("=" * 80)
    
    max_tentativas = 10
    intervalo = 3  # segundos
    
    for tentativa in range(1, max_tentativas + 1):
        print(f"\n🔍 Tentativa {tentativa}/{max_tentativas}")
        
        status_result = cliente.consultar_status_pdf_extrato(account_id, request_id)
        
        if not status_result:
            print("❌ Erro ao consultar status")
            break
        
        status = status_result.get('status')
        url = status_result.get('url')
        
        if url:
            print(f"✅ PDF pronto! Status: {status}")
            
            # PASSO 4: Baixar PDF
            print("\n" + "=" * 80)
            print("PASSO 4: Baixar PDF")
            print("=" * 80)
            
            arquivo_pdf = cliente.baixar_pdf_extrato(url, branch_code, account_number)
            
            if arquivo_pdf:
                print("\n" + "=" * 80)
                print("✅ SUCESSO! PDF DE EXTRATO BAIXADO VIA API")
                print("=" * 80)
                print(f"Arquivo: {arquivo_pdf}")
            else:
                print("\n❌ Falha no download do PDF")
            
            break
        
        elif status in ['PROCESSING', 'PENDING', 'REQUESTED']:
            print(f"⏳ Ainda processando... (status: {status})")
            if tentativa < max_tentativas:
                print(f"   Aguardando {intervalo} segundos...")
                time.sleep(intervalo)
        else:
            print(f"❌ Status inesperado: {status}")
            break
    else:
        print("\n⏱️  Timeout: PDF não ficou pronto a tempo")
    
    print("\n" + "=" * 80)
    print("TESTE CONCLUÍDO")
    print("=" * 80)


if __name__ == "__main__":
    try:
        testar_pdf_extrato()
    except KeyboardInterrupt:
        print("\n\n⚠️  Teste interrompido pelo usuário")
    except Exception as e:
        print(f"\n\n❌ Erro durante teste: {e}")
        import traceback
        traceback.print_exc()
