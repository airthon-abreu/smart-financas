from contextlib import asynccontextmanager
from typing import Optional
from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

import backend.database as db
from backend.config import PASTA_FRONTEND
from backend.parser_pdf import extrair_dados_pdf
from backend.insights_engine import gerar_projecao_12_meses, extrair_insights

@asynccontextmanager
async def lifespan(app: FastAPI):
    db.criar_tabelas()
    yield

app = FastAPI(title="SmartFinanças Pro", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/upload-pdf")
async def upload_pdf(arquivo: UploadFile = File(...)):
    if not arquivo.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Por favor, envie um arquivo PDF válido.")

    conteudo = await arquivo.read()
    try:
        dados = extrair_dados_pdf(conteudo)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Erro ao processar PDF: {str(e)}")

    if not dados["despesas"]:
        raise HTTPException(status_code=400, detail="Nenhuma despesa reconhecida na estrutura do arquivo.")

    mes_ref = dados["mes_referencia"]

    # Salva/Sobrescreve no SQLite para o mês de referência
    with db.obter_conexao() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM despesas WHERE mes_referencia = ?", (mes_ref,))
        for d in dados["despesas"]:
            cur.execute('''
                INSERT INTO despesas (
                    descricao, valor, data_lancamento, data_vencimento, efetivada,
                    categoria, subcategoria, cartao, conta, tipo_despesa,
                    parcela_atual, total_parcelas, mes_referencia
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                d["descricao"], d["valor"], d["data_lancamento"], d["data_vencimento"],
                d["efetivada"], d["categoria"], d["subcategoria"], d["cartao"],
                d["conta"], d["tipo_despesa"], d["parcela_atual"], d["total_parcelas"], mes_ref
            ))

    return {
        "mensagem": f"Importação concluída! {dados['total_registros']} registros importados para {mes_ref}.",
        "mes_referencia": mes_ref
    }

@app.get("/api/meses")
def listar_meses():
    with db.obter_conexao() as conn:
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT mes_referencia FROM despesas ORDER BY mes_referencia DESC")
        meses = [row["mes_referencia"] for row in cur.fetchall()]
    return meses

@app.get("/api/dashboard")
def obter_dashboard(mes: Optional[str] = Query(None)):
    with db.obter_conexao() as conn:
        cur = conn.cursor()
        if not mes:
            cur.execute("SELECT mes_referencia FROM despesas ORDER BY mes_referencia DESC LIMIT 1")
            row = cur.fetchone()
            if not row:
                return {"vazio": True}
            mes = row["mes_referencia"]

        cur.execute("SELECT * FROM despesas WHERE mes_referencia = ? ORDER BY valor DESC", (mes,))
        despesas = [dict(r) for r in cur.fetchall()]

    insights = extrair_insights(despesas, mes)
    projecao = gerar_projecao_12_meses(despesas, mes)

    return {
        "vazio": False,
        "mes_atual": mes,
        "despesas": despesas,
        "insights": insights,
        "projecao": projecao
    }

# Servidor estático do frontend
if PASTA_FRONTEND.exists():
    app.mount("/", StaticFiles(directory=str(PASTA_FRONTEND), html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    # Alterado para a porta 9000
    uvicorn.run("backend.main:app", host="127.0.0.1", port=9000, reload=True)