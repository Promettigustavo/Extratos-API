"""
Teste para descobrir o período máximo de busca de transações na API Santander

Este script testa diferentes períodos para identificar o limite da API:
- 30 dias (padrão geralmente aceito)
- 60 dias
- 90 dias
- 6 meses
- 1 ano

Resultado: imprime o período máximo que retorna transações sem erro
"""

from datetime import datetime, timedelta
from buscar_extratos_bancarios import SantanderExtratosBancarios

# Configuração do teste
FUNDO_TESTE = "CONDOLIVRE FIDC"  # Alterar para um fundo que você tenha acesso
PERIODOS_TESTE = [
    ("30 dias", 30),
    ("60 dias", 60),
    ("90 dias", 90),
    ("6 meses", 180),
    ("1 ano", 365),
    ("2 anos", 730)
]

def testar_periodo(cliente, conta, periodo_dias):
    """
    Testa busca de transações para um período específico
    
    Returns:
        (sucesso, num_transacoes, mensagem_erro)
    """
    data_final = datetime.now()
    data_inicial = data_final - timedelta(days=periodo_dias)
    
    print(f"\n{'='*60}")
    print(f"Testando período: {periodo_dias} dias")
    print(f"Data inicial: {data_inicial.strftime('%d/%m/%Y')}")
    print(f"Data final: {data_final.strftime('%d/%m/%Y')}")
    print(f"{'='*60}")
    
    try:
        branch_code = conta.get('branchCode') or conta.get('agencyCode')
        account_number = conta.get('number') or conta.get('accountNumber')
        
        if not branch_code or not account_number:
            return False, 0, "Conta sem branch_code ou account_number"
        
        transacoes = cliente.buscar_transacoes(
            branch_code,
            account_number,
            data_inicial=data_inicial,
            data_final=data_final
        )
        
        if transacoes is None:
            return False, 0, "API retornou None (possível erro de autenticação)"
        
        num_transacoes = len(transacoes)
        print(f"✅ SUCESSO: {num_transacoes} transação(ões) encontrada(s)")
        
        if num_transacoes > 0:
            print(f"   Primeira transação: {transacoes[0].get('transactionDate')}")
            print(f"   Última transação: {transacoes[-1].get('transactionDate')}")
        
        return True, num_transacoes, None
        
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
        return False, 0, str(e)


def main():
    print("="*80)
    print("TESTE DE PERÍODO MÁXIMO - API SANTANDER")
    print("="*80)
    print(f"\nFundo de teste: {FUNDO_TESTE}")
    
    try:
        # Criar cliente
        print("\n🔧 Criando cliente...")
        cliente = SantanderExtratosBancarios(FUNDO_TESTE)
        
        # Listar contas
        print("🏦 Listando contas...")
        contas = cliente.listar_contas()
        
        if not contas or len(contas) == 0:
            print("❌ Nenhuma conta encontrada. Verifique as credenciais.")
            return
        
        print(f"✅ {len(contas)} conta(s) encontrada(s)")
        
        # Usar primeira conta para teste
        conta = contas[0]
        branch = conta.get('branchCode') or conta.get('agencyCode')
        account = conta.get('number') or conta.get('accountNumber')
        print(f"📊 Testando com conta: {branch}.{account}")
        
        # Resultados
        resultados = []
        
        # Testar cada período
        for nome_periodo, dias in PERIODOS_TESTE:
            sucesso, num_trans, erro = testar_periodo(cliente, conta, dias)
            resultados.append({
                'periodo': nome_periodo,
                'dias': dias,
                'sucesso': sucesso,
                'transacoes': num_trans,
                'erro': erro
            })
            
            # Se falhou, provavelmente atingimos o limite
            if not sucesso:
                print(f"\n⚠️ Limite provavelmente atingido em {dias} dias")
                break
        
        # Resumo
        print("\n" + "="*80)
        print("RESUMO DOS TESTES")
        print("="*80)
        
        for r in resultados:
            status = "✅" if r['sucesso'] else "❌"
            print(f"{status} {r['periodo']:15} ({r['dias']:4} dias): ", end="")
            if r['sucesso']:
                print(f"{r['transacoes']} transação(ões)")
            else:
                print(f"FALHOU - {r['erro']}")
        
        # Identificar período máximo com sucesso
        periodos_sucesso = [r for r in resultados if r['sucesso']]
        if periodos_sucesso:
            max_periodo = max(periodos_sucesso, key=lambda x: x['dias'])
            print(f"\n🎯 PERÍODO MÁXIMO TESTADO COM SUCESSO: {max_periodo['periodo']} ({max_periodo['dias']} dias)")
        else:
            print("\n❌ Nenhum período testado com sucesso")
        
        print("\n" + "="*80)
        print("RECOMENDAÇÕES:")
        print("="*80)
        if periodos_sucesso:
            if max_periodo['dias'] >= 365:
                print("✅ API aceita períodos de 1 ano ou mais")
                print("   Considere usar períodos mais longos no dashboard")
            elif max_periodo['dias'] >= 90:
                print("✅ API aceita períodos de 90 dias ou mais")
                print("   Período atual do dashboard (30 dias) está OK")
            else:
                print(f"⚠️ API aceita apenas até {max_periodo['dias']} dias")
                print(f"   Limite o período máximo no dashboard para {max_periodo['dias']} dias")
        
    except Exception as e:
        print(f"\n❌ ERRO GERAL: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
