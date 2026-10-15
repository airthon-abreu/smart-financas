from collections import defaultdict
from typing import List, Dict, Any

def calcular_proximo_mes(ano_mes: str, incremento: int) -> str:
    ano, mes = map(int, ano_mes.split('-'))
    total_meses = (ano * 12 + mes - 1) + incremento
    novo_ano = total_meses // 12
    novo_mes = (total_meses % 12) + 1
    return f"{novo_ano:04d}-{novo_mes:02d}"

def gerar_projecao_12_meses(despesas: List[Dict[str, Any]], mes_base: str) -> List[Dict[str, Any]]:
    projecoes = []
    total_mes_base_fixo_parc = 0.0

    for i in range(12):
        mes_futuro = calcular_proximo_mes(mes_base, i)
        total_fixo = 0.0
        total_parcelado = 0.0
        parcelas_ativas = []
        parcelas_terminando = []

        for d in despesas:
            tipo = d["tipo_despesa"]
            valor = d["valor"]
            
            if tipo == "Fixa":
                total_fixo += valor
            elif tipo == "Parcelada":
                parcela_neste_mes = d["parcela_atual"] + i
                if parcela_neste_mes <= d["total_parcelas"]:
                    total_parcelado += valor
                    info_p = {
                        "descricao": d["descricao"],
                        "categoria": d["categoria"],
                        "parcela": f"{parcela_neste_mes}/{d['total_parcelas']}",
                        "valor": valor,
                        "ultima": parcela_neste_mes == d["total_parcelas"]
                    }
                    parcelas_ativas.append(info_p)
                    if parcela_neste_mes == d["total_parcelas"]:
                        parcelas_terminando.append(info_p)

        total_combinado = total_fixo + total_parcelado
        if i == 0:
            total_mes_base_fixo_parc = total_combinado

        liberado_vs_atual = round(max(0.0, total_mes_base_fixo_parc - total_combinado), 2)

        projecoes.append({
            "mes": mes_futuro,
            "total_combinado": round(total_combinado, 2),
            "total_fixo": round(total_fixo, 2),
            "total_parcelado": round(total_parcelado, 2),
            "liberado_vs_atual": liberado_vs_atual,
            "qtd_parcelas_vivas": len(parcelas_ativas),
            "parcelas_terminando": parcelas_terminando
        })

    return projecoes

def extrair_insights(despesas: List[Dict[str, Any]], mes_base: str) -> Dict[str, Any]:
    total_geral = sum(d["valor"] for d in despesas)
    if total_geral == 0:
        return {}

    totais_por_tipo = defaultdict(float)
    for d in despesas:
        totais_por_tipo[d["tipo_despesa"]] += d["valor"]

    totais_categoria = defaultdict(float)
    for d in despesas:
        totais_categoria[d["categoria"]] += d["valor"]

    ranking_categoria = sorted(
        [{"categoria": k, "valor": round(v, 2), "pct": round((v / total_geral) * 100, 1)} 
         for k, v in totais_categoria.items()],
        key=lambda x: x["valor"],
        reverse=True
    )

    terminando_agora = [d for d in despesas if d["tipo_despesa"] == "Parcelada" and d["parcela_atual"] == d["total_parcelas"]]
    terminando_proximo = [d for d in despesas if d["tipo_despesa"] == "Parcelada" and d["parcela_atual"] + 1 == d["total_parcelas"]]
    valor_liberado_prox_mes = sum(d["valor"] for d in terminando_agora)

    gastos_reserva = sum(d["valor"] for d in despesas if "reserva" in d["descricao"].lower() or "reserva" in d["categoria"].lower())

    mensagens = []
    if valor_liberado_prox_mes > 0:
        mensagens.append({
            "tipo": "positivo",
            "titulo": "Alívio Financeiro Iminente!",
            "texto": f"Você quitará {len(terminando_agora)} conta(s) este mês. Isso liberará R$ {valor_liberado_prox_mes:.2f} do seu orçamento a partir do próximo mês."
        })

    pct_parcelas = (totais_por_tipo['Parcelada'] / total_geral) * 100
    if pct_parcelas > 35:
        mensagens.append({
            "tipo": "alerta",
            "titulo": "Atenção ao Parcelamento no Cartão",
            "texto": f"{pct_parcelas:.1f}% das suas despesas são parceladas (R$ {totais_por_tipo['Parcelada']:.2f}). Evite novas compras a prazo para acelerar sua economia."
        })

    if gastos_reserva > 0:
        mensagens.append({
            "tipo": "positivo",
            "titulo": "Aporte na Reserva de Emergência",
            "texto": f"Parabéns! Você destinou R$ {gastos_reserva:.2f} ({((gastos_reserva/total_geral)*100):.1f}% do total) para a sua segurança financeira."
        })

    return {
        "total_geral": round(total_geral, 2),
        "fixas": round(totais_por_tipo["Fixa"], 2),
        "parceladas": round(totais_por_tipo["Parcelada"], 2),
        "variaveis": round(totais_por_tipo["Variavel"], 2),
        "ranking_categoria": ranking_categoria,
        "terminando_este_mes": terminando_agora,
        "terminando_proximo_mes": terminando_proximo,
        "valor_liberado_prox_mes": round(valor_liberado_prox_mes, 2),
        "mensagens": mensagens
    }