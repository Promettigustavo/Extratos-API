"""
Mapeamento de contas conhecidas para cada fundo
Baseado nos extratos históricos já gerados
"""

# Contas conhecidas dos fundos (agência.conta)
CONTAS_CONHECIDAS = {
    "CONDOLIVRE FIDC": [
        {"agencia": "2271", "conta": "130137784"},
        {"agencia": "2271", "conta": "130176356"}
    ],
    # Adicionar outras contas conforme necessário
    # Baseado nos diretórios existentes em Extratos/
}

def obter_contas_fundo(nome_fundo: str):
    """
    Retorna lista de contas conhecidas para um fundo
    
    Args:
        nome_fundo: Nome do fundo conforme SANTANDER_FUNDOS
        
    Returns:
        Lista de dicts com 'agencia' e 'conta'
    """
    return CONTAS_CONHECIDAS.get(nome_fundo, [])

def adicionar_conta_fundo(nome_fundo: str, agencia: str, conta: str):
    """
    Adiciona nova conta conhecida para um fundo
    """
    if nome_fundo not in CONTAS_CONHECIDAS:
        CONTAS_CONHECIDAS[nome_fundo] = []
    
    nova_conta = {"agencia": agencia, "conta": conta}
    if nova_conta not in CONTAS_CONHECIDAS[nome_fundo]:
        CONTAS_CONHECIDAS[nome_fundo].append(nova_conta)
        return True
    return False