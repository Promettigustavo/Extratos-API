"""
Script para analisar detalhadamente o PDF de exemplo do IBE Santander
Extrai informações de layout, formatação, estrutura e conteúdo
"""

import PyPDF2
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
import pdfplumber

def analisar_pdf_completo(pdf_path):
    """Analisa PDF extraindo todas as informações de layout"""
    
    print("="*80)
    print("ANÁLISE DETALHADA DO PDF DE EXEMPLO IBE SANTANDER")
    print("="*80)
    
    # ========== ANÁLISE COM PyPDF2 ==========
    print("\n" + "="*80)
    print("1. ESTRUTURA DO DOCUMENTO (PyPDF2)")
    print("="*80)
    
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        
        print(f"\nNúmero de páginas: {len(reader.pages)}")
        print(f"Metadados:")
        if reader.metadata:
            for key, value in reader.metadata.items():
                print(f"  {key}: {value}")
        
        # Primeira página
        page = reader.pages[0]
        
        # Dimensões
        mediabox = page.mediabox
        print(f"\nDimensões da página:")
        print(f"  Largura: {float(mediabox.width)} pts ({float(mediabox.width)/72*25.4:.1f} mm)")
        print(f"  Altura: {float(mediabox.height)} pts ({float(mediabox.height)/72*25.4:.1f} mm)")
        print(f"  A4 padrão: {A4[0]/mm:.1f}mm x {A4[1]/mm:.1f}mm")
        
        # Texto extraído
        texto = page.extract_text()
        print(f"\nTEXTO COMPLETO EXTRAÍDO:")
        print("-"*80)
        print(texto)
        print("-"*80)
    
    # ========== ANÁLISE COM PDFPLUMBER ==========
    print("\n" + "="*80)
    print("2. ANÁLISE DETALHADA DE LAYOUT (pdfplumber)")
    print("="*80)
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            page = pdf.pages[0]
            
            # Dimensões
            print(f"\nDimensões da página:")
            print(f"  Largura: {page.width} pts ({page.width/72*25.4:.1f} mm)")
            print(f"  Altura: {page.height} pts ({page.height/72*25.4:.1f} mm)")
            
            # Texto com posições
            print(f"\n" + "-"*80)
            print("PALAVRAS COM POSIÇÕES (primeiras 50):")
            print("-"*80)
            words = page.extract_words()
            for i, word in enumerate(words[:50]):
                print(f"{i+1:3d}. '{word['text']:30s}' | "
                      f"x0:{word['x0']:6.1f} x1:{word['x1']:6.1f} | "
                      f"top:{word['top']:6.1f} bottom:{word['bottom']:6.1f} | "
                      f"fontsize:{word.get('height', 0):4.1f}")
            
            # Tabelas
            print(f"\n" + "-"*80)
            print("TABELAS DETECTADAS:")
            print("-"*80)
            tables = page.extract_tables()
            print(f"Número de tabelas: {len(tables)}")
            
            for idx, table in enumerate(tables):
                print(f"\nTabela {idx + 1}:")
                print(f"  Linhas: {len(table)}")
                print(f"  Colunas: {len(table[0]) if table else 0}")
                print(f"  Primeiras linhas:")
                for i, row in enumerate(table[:5]):
                    print(f"    Linha {i+1}: {row}")
            
            # Imagens
            print(f"\n" + "-"*80)
            print("IMAGENS:")
            print("-"*80)
            images = page.images
            print(f"Número de imagens: {len(images)}")
            for i, img in enumerate(images):
                print(f"\nImagem {i+1}:")
                print(f"  x0: {img['x0']}, x1: {img['x1']}")
                print(f"  top: {img['top']}, bottom: {img['bottom']}")
                print(f"  width: {img['width']}, height: {img['height']}")
            
            # Linhas/Retângulos
            print(f"\n" + "-"*80)
            print("ELEMENTOS GRÁFICOS:")
            print("-"*80)
            
            rects = page.rects
            print(f"Retângulos: {len(rects)}")
            if rects:
                print(f"  Primeiros 10:")
                for i, rect in enumerate(rects[:10]):
                    print(f"    {i+1}. x0:{rect['x0']:6.1f} top:{rect['top']:6.1f} "
                          f"x1:{rect['x1']:6.1f} bottom:{rect['bottom']:6.1f}")
            
            lines = page.lines
            print(f"\nLinhas: {len(lines)}")
            if lines:
                print(f"  Primeiras 10:")
                for i, line in enumerate(lines[:10]):
                    print(f"    {i+1}. x0:{line['x0']:6.1f} top:{line['top']:6.1f} "
                          f"x1:{line['x1']:6.1f} bottom:{line['bottom']:6.1f}")
            
            # Análise de fontes
            print(f"\n" + "-"*80)
            print("FONTES UTILIZADAS:")
            print("-"*80)
            chars = page.chars
            fontes = {}
            for char in chars:
                font_name = char.get('fontname', 'Unknown')
                font_size = char.get('size', 0)
                key = f"{font_name} {font_size:.1f}pt"
                fontes[key] = fontes.get(key, 0) + 1
            
            print(f"Total de caracteres: {len(chars)}")
            print(f"\nFontes encontradas (ordenadas por frequência):")
            for font, count in sorted(fontes.items(), key=lambda x: x[1], reverse=True):
                print(f"  {font}: {count} caracteres")
            
            # Cores
            print(f"\n" + "-"*80)
            print("CORES UTILIZADAS:")
            print("-"*80)
            cores = {}
            for char in chars:
                color = char.get('stroking_color', char.get('non_stroking_color', 'N/A'))
                if color:
                    cores[str(color)] = cores.get(str(color), 0) + 1
            
            for cor, count in sorted(cores.items(), key=lambda x: x[1], reverse=True):
                print(f"  {cor}: {count} caracteres")
    
    except Exception as e:
        print(f"\n❌ Erro ao analisar com pdfplumber: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*80)
    print("ANÁLISE COMPLETA")
    print("="*80)

if __name__ == "__main__":
    pdf_path = "comprovante-ibe-C76C2FC5-74C4-4086-90F8-A7E23D1B912C (1).pdf"
    analisar_pdf_completo(pdf_path)
