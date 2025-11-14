from buscar_extratos_bancarios import SantanderExtratosBancarios
from datetime import datetime, timedelta

api = SantanderExtratosBancarios('CONDOLIVRE FIDC')
contas = api.listar_contas()
print(f'\nContas encontradas: {len(contas)}')

if contas:
    conta = contas[0]
    branch = conta.get('branchCode')
    account = conta.get('number')
    print(f'Conta: {branch}.{account}')
    
    data_inicial = datetime.now() - timedelta(days=7)
    data_final = datetime.now()
    
    trans = api.buscar_transacoes(branch, account, data_inicial, data_final)
    print(f'\n✅ Total de transações reais nos últimos 7 dias: {len(trans)}')
    
    if trans:
        print('\nPrimeiras 3 transações:')
        for i, t in enumerate(trans[:3], 1):
            print(f'\n{i}. Data: {t.get("transactionDate")}')
            print(f'   Histórico: {t.get("transactionName")}')
            print(f'   Valor: R$ {t.get("amount")}')
            print(f'   Tipo: {t.get("creditDebitType")}')
else:
    print('Nenhuma conta encontrada')
