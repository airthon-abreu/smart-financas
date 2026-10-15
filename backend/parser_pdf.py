import re
import unicodedata
from io import BytesIO
from pypdf import PdfReader
from typing import List, Dict, Any

REGEX_LINHA_DESPESA = re.compile(
    r'^(?P<desc>.*?)\s+R\$\s*(?P<valor>[\d\.,]+)\s+(?P<dt_lanc>\d{2}/\d{2}/\d{4})\s+(?P<dt_venc>\d{2}/\d{2}/\d{4})\s+(?P<efetiva>-|\d{2}/\d{2}/\d{4})\s+(?P<resto>.*)$'
)

REGEX_PARCELA = re.compile(r'(\d{1,2})/(\d{1,2})\b')

# Dicionário de expansão garantida para os seus cartões e categorias
MAPA_NOMES_COMPLETOS = {
    '1cartão': '1Cartão Atacadão',
    '1cartao': '1Cartão Atacadão',
    '2cartão': '2Cartão Itaú Extra',
    '2cartao': '2Cartão Itaú Extra',
    '3cartão': '3Cartão Mercado Pago',
    '3cartao': '3Cartão Mercado Pago',
    '4cartão': '4Cartão Visa Click',
    '4cartao': '4Cartão Visa Click',
    '6linha': '6Linha Mercadopago',
    '7shopee': '7Shopee',
    '8izamara': '8Izamara',
    'reserva': 'Reserva De Emergência',
    'carro': 'Carro',
    'moradia': 'Moradia',
    'pagamentos': 'Pagamentos'
}

def limpar_valor(valor_str: str) -> float:
    limpo = valor_str.replace('.', '').replace(',', '.')
    return float(limpo)

def normalizar_texto(texto: str) -> str:
    return unicodedata.normalize('NFKC', texto).strip()

def extrair_categoria_completa(resto: str):
    resto_norm = normalizar_texto(resto)
    
    # 1. Tenta extrair pela estrutura do final da linha:
    # <CATEGORIA> <SUBCATEGORIA> <CARTAO> <CONTA>
    match = re.search(r'^(?P<cat>.*?)\s+(?P<subcat>[A-Za-zÀ-ÿ]+)\s+(?P<cartao>-|\S+)\s+(?P<conta>Conta\s+\S+|\S+)$', resto_norm, re.IGNORECASE)
    
    if match:
        categoria = match.group('cat').strip()
        subcategoria = match.group('subcat').strip()
        cartao = match.group('cartao').strip()
        conta = match.group('conta').strip()
    else:
        tokens = resto_norm.split()
        if len(tokens) >= 4:
            conta = tokens[-1]
            cartao = tokens[-2]
            subcategoria = tokens[-3]
            categoria = " ".join(tokens[:-3])
        else:
            categoria = resto_norm
            subcategoria = "Outros"
            cartao = "-"
            conta = "-"

    # 2. Expansão garantida por prefixo (assegura que '2Cartão' vire '2Cartão Itaú Extra', etc.)
    cat_lower = categoria.lower()
    for prefixo, nome_completo in MAPA_NOMES_COMPLETOS.items():
        if cat_lower.startswith(prefixo) or cat_lower == prefixo:
            categoria = nome_completo
            break

    return categoria, subcategoria, cartao, conta

def extrair_dados_pdf(arquivo_bytes: bytes) -> Dict[str, Any]:
    leitor = PdfReader(BytesIO(arquivo_bytes))
    linhas_texto = []
    
    for pagina in leitor.pages:
        texto = pagina.extract_text()
        if texto:
            linhas_texto.extend(texto.splitlines())

    despesas: List[Dict[str, Any]] = []
    mes_referencia = None

    for linha in linhas_texto:
        match_periodo = re.search(r'\d{2}/(\d{2})/(\d{4})\s*-\s*\d{2}/\d{2}/\d{4}', linha)
        if match_periodo:
            mes_referencia = f"{match_periodo.group(2)}-{match_periodo.group(1)}"
            break

    palavras_fixas = [
        'aluguel', 'água', 'agua', 'energia', 'internet', 'reserva',
        'corte de cabelo', 'amazon prime', 'youtube', 'garrafões dágua',
        'ajuda segurança'
    ]

    for linha in linhas_texto:
        linha = linha.strip()
        match = REGEX_LINHA_DESPESA.match(linha)
        if not match:
            continue

        dados = match.groupdict()
        desc = dados['desc'].strip()
        valor = limpar_valor(dados['valor'])
        dt_lanc = dados['dt_lanc']
        dt_venc = dados['dt_venc']
        efetiva = dados['efetiva']
        resto = dados['resto'].strip()

        partes_venc = dt_venc.split('/')
        mes_venc = f"{partes_venc[2]}-{partes_venc[1]}"
        if not mes_referencia:
            mes_referencia = mes_venc

        categoria, subcategoria, cartao, conta = extrair_categoria_completa(resto)

        parc_match = REGEX_PARCELA.search(desc)
        if parc_match:
            parcela_atual = int(parc_match.group(1))
            total_parcelas = int(parc_match.group(2))
            tipo_despesa = 'Parcelada'
        else:
            parcela_atual = 1
            total_parcelas = 1
            desc_lower = desc.lower()
            cat_lower = categoria.lower()
            if any(p in desc_lower or p in cat_lower for p in palavras_fixas):
                tipo_despesa = 'Fixa'
            else:
                tipo_despesa = 'Variavel'

        despesas.append({
            "descricao": desc,
            "valor": valor,
            "data_lancamento": f"{partes_venc[2]}-{partes_venc[1]}-{partes_venc[0]}",
            "data_vencimento": f"{partes_venc[2]}-{partes_venc[1]}-{partes_venc[0]}",
            "efetivada": efetiva,
            "categoria": categoria,
            "subcategoria": subcategoria,
            "cartao": cartao,
            "conta": conta,
            "tipo_despesa": tipo_despesa,
            "parcela_atual": parcela_atual,
            "total_parcelas": total_parcelas,
            "mes_referencia": mes_venc
        })

    return {
        "mes_referencia": mes_referencia,
        "total_registros": len(despesas),
        "despesas": despesas
    }