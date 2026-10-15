# ⚡ SmartFinanças Pro — Inteligência Financeira & Forecast

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Vue.js-3.x-4FC08D?style=for-the-badge&logo=vue.js&logoColor=white" alt="Vue.js" />
  <img src="https://img.shields.io/badge/Chart.js-4.x-FF6384?style=for-the-badge&logo=chart.js&logoColor=white" alt="Chart.js" />
  <img src="https://img.shields.io/badge/SQLite-WAL_Mode-003B57?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite" />
  <img src="https://img.shields.io/badge/TailwindCSS-Dark_Cockpit-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white" alt="Tailwind" />
</p>

Sistema de inteligência de dados financeiros, projeção de fluxo de caixa mês a mês e extração automatizada de relatórios em PDF gerados por aplicativos de gestão (ex: *Minhas Finanças*).

O projeto elimina o retrabalho de planilhas manuais ao ler faturas e relatórios brutos, identificar compras parceladas embutidas no texto e projetar com precisão matemática a **curva de extinção de dívidas e liberação de renda para os próximos 12 meses**.

---

<!-- Caso adicione uma imagem, coloque na pasta docs/ e aponte aqui -->
<!-- <p align="center"><img src="docs/preview.png" alt="Dashboard Preview" width="90%" /></p> -->

---

## 🎯 Problema Resolvido

Muitos aplicativos móveis de finanças consolidam despesas, mas pecam em:
1. **Visão de Fluxo Futuro:** Não mostram com clareza o impacto de compras parceladas terminando nos meses seguintes.
2. **Classificação Automática:** Não extraem parcelamentos embutidos na descrição das notas (ex: `6/14`, `2/10`).
3. **Visão de Alívio Orçamentário:** Não quantificam exatamente quanto dinheiro será liberado mês a mês quando parcelas terminarem.

O **SmartFinanças Pro** automatiza esse pipeline: recebe o extrato PDF, estrutura as despesas em banco relacional, aplica regras de negócio financeiras e plota dashboards analíticos.

---

## ✨ Principais Funcionalidades

- **📄 Parser Inteligente de PDF (Regex + NLP Normalizer):**
  - Identifica colunas, valores monetários em BRL, datas de emissão/vencimento e cartões.
  - Detecta automaticamente marcações de parcelamento (ex: `Notebook vaio 2/10`, `FIES 6/14`).
  - Dicionário de expansão para normalização de nomes de emissores e operadoras de cartão.

- **📈 Motor de Projeção Financeira (Forecast 12 Meses):**
  - Algoritmo que projeta custos fixos essenciais e calcula a extinção das parcelas ativas mês a mês.
  - Gráfico híbrido (*Stacked Bars + Neon Line*) exibindo o **Total Combinado** e a **Economia Liberada**.

- **💡 Motor de Insights Algorítmicos:**
  - Alerta de alívio orçamentário iminente (contas quitadas no mês corrente).
  - Diagnóstico de comprometimento excessivo com cartões de crédito.
  - Monitoramento e métricas de aporte à Reserva de Emergência.

- **🔍 Cockpit Reativo com Filtros Livres:**
  - Busca textual em tempo real por descrição.
  - Filtro por cartão/categoria e classificação de despesa (*Fixa*, *Parcelada*, *Variável*).
  - Ordenação dinâmica por valor, data de vencimento e nome.

---

## 🛠️ Stack Tecnológica

| Camada | Tecnologia | Propósito |
|---|---|---|
| **Backend** | Python 3 + FastAPI | API REST assíncrona, de alta performance e tipada com Pydantic |
| **PDF Extraction**| PyPDF + RegEx Engines | Leitura de buffers de PDF e tokenização contextual |
| **Banco de Dados** | SQLite (Modo WAL) | Armazenamento transacional leve, atômico e sem dependências externas |
| **Frontend** | Vue 3 Composition API | Reatividade e binding dinâmico de estados e filtros |
| **Estilização** | Tailwind CSS (Dark Cockpit) | Design moderno voltado para dashboards de alta densidade de dados |
| **Data Viz** | Chart.js | Gráficos de rosca (Donut) e gráficos combinados de barras e linha |

---

## 📁 Estrutura do Projeto

```text
smart-financas/
├── backend/
│   ├── config.py             # Configuração de diretórios e paths
│   ├── database.py           # Conexão SQLite (WAL mode) e migrações
│   ├── parser_pdf.py         # Engine de extração e normalização do PDF
│   ├── insights_engine.py    # Algoritmos de projeção e diagnóstico financeiro
│   └── main.py               # Servidor FastAPI e rotas REST
├── frontend/
│   └── index.html            # SPA Vue 3 + Tailwind CSS + Chart.js
├── .gitignore                # Proteção contra vazamento de dados locais (*.db, *.pdf)
├── README.md                 # Documentação técnica do projeto
└── requirements.txt          # Dependências do ecossistema Python