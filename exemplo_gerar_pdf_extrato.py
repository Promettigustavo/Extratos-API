"""
Exemplo de uso do buscar_extratos_bancarios.py com geração de PDF
"""

from datetime import datetime, timedelta
from buscar_extratos_bancarios import main

# Exemplo 1: Buscar últimos 30 dias com PDF
print("="*80)
print("EXEMPLO 1: Extratos dos últimos 30 dias (Excel + PDF)")
print("="*80)
main(
    fundos=["911_BANK"],
    data_inicial=datetime.now() - timedelta(days=30),
    data_final=datetime.now(),
    gerar_pdf=True
)

# Exemplo 2: Buscar período específico apenas Excel
print("\n" + "="*80)
print("EXEMPLO 2: Período específico (apenas Excel)")
print("="*80)
main(
    fundos=["911_BANK"],
    data_inicial=datetime(2025, 11, 1),
    data_final=datetime(2025, 11, 14),
    gerar_pdf=False  # Não gerar PDF
)

# Exemplo 3: Salvar em pasta específica
print("\n" + "="*80)
print("EXEMPLO 3: Salvar em pasta Extratos/")
print("="*80)
import os
pasta_extratos = "Extratos"
os.makedirs(pasta_extratos, exist_ok=True)

main(
    fundos=["911_BANK"],
    data_inicial=datetime.now() - timedelta(days=7),
    data_final=datetime.now(),
    pasta_saida=pasta_extratos,
    gerar_pdf=True
)
