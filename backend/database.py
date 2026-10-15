import sqlite3
from contextlib import contextmanager
from backend.config import CAMINHO_BANCO

@contextmanager
def obter_conexao():
    conexao = sqlite3.connect(str(CAMINHO_BANCO), timeout=30.0)
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA journal_mode=WAL;")
    conexao.execute("PRAGMA foreign_keys=ON;")
    try:
        yield conexao
        conexao.commit()
    except Exception:
        conexao.rollback()
        raise
    finally:
        conexao.close()

def corrigir_nomes_antigos(cursor):
    """Auto-corrige os registros que ficaram salvos com nome encurtado no banco."""
    mapa_correcao = {
        '1Cartão': '1Cartão Atacadão',
        '2Cartão': '2Cartão Itaú Extra',
        '3Cartão': '3Cartão Mercado Pago',
        '4Cartão': '4Cartão Visa Click',
        '6Linha': '6Linha Mercadopago',
        '7Shopee': '7Shopee',
        '8Izamara': '8Izamara',
        'Reserva': 'Reserva De Emergência'
    }
    for curto, completo in mapa_correcao.items():
        cursor.execute("UPDATE despesas SET categoria = ? WHERE categoria = ?", (completo, curto))

def criar_tabelas():
    with obter_conexao() as conexao:
        cursor = conexao.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS despesas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                descricao TEXT NOT NULL,
                valor REAL NOT NULL,
                data_lancamento DATE,
                data_vencimento DATE NOT NULL,
                efetivada TEXT,
                categoria TEXT,
                subcategoria TEXT,
                cartao TEXT,
                conta TEXT,
                tipo_despesa TEXT,
                parcela_atual INTEGER,
                total_parcelas INTEGER,
                mes_referencia TEXT NOT NULL
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_mes_ref ON despesas(mes_referencia);')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_categoria ON despesas(categoria);')
        
        # Executa a auto-correção imediata
        corrigir_nomes_antigos(cursor)
        
    print("[Banco] Tabelas prontas e categorias auto-corrigidas com sucesso.") 