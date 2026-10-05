import os
import requests
import sqlite3
import streamlit as st
from dotenv import load_dotenv
from pydantic_ai import Agent

load_dotenv()

# Configuramos as variáveis de ambiente padrão da OpenAI para apontar para o OpenRouter
os.environ['OPENAI_API_KEY'] = os.environ.get('OPENROUTER_API_KEY')
os.environ['OPENAI_BASE_URL'] = 'https://openrouter.ai/api/v1'

# Inicializamos o agente usando a string direta do modelo
agente = Agent(
    'openai:nvidia/nemotron-3.5-lightning:free',
    system_prompt="""Você é um analista de dados especialista em Text-to-SQL da CineData Analytics.
Sua missão é responder perguntas de negócio baseadas no banco de dados SQLite fornecido.
Sempre utilize a ferramenta 'executar_query_sql' para buscar os dados antes de dar a resposta final.

Aqui está o schema do banco de dados:
CREATE TABLE alembic_version (
        version_num VARCHAR(32) NOT NULL, 
        CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
)

CREATE TABLE dim_companies (
        sk_company_id VARCHAR(64) NOT NULL, 
        nome_produtora VARCHAR(255) NOT NULL, 
        CONSTRAINT pk_dim_companies PRIMARY KEY (sk_company_id), 
        CONSTRAINT uq_dim_companies_nome_produtora UNIQUE (nome_produtora)
)

CREATE TABLE dim_genres (
        sk_genre_id VARCHAR(64) NOT NULL, 
        nome_genero VARCHAR(50) NOT NULL, 
        CONSTRAINT pk_dim_genres PRIMARY KEY (sk_genre_id), 
        CONSTRAINT uq_dim_genres_nome_genero UNIQUE (nome_genero)
)

CREATE TABLE dim_movies (
        sk_movie_id VARCHAR(64) NOT NULL, 
        id_filme VARCHAR(50) NOT NULL, 
        titulo VARCHAR(500) NOT NULL, 
        data_lancamento DATE, 
        ano_lancamento INTEGER, 
        duracao_minutos INTEGER, 
        idioma_original VARCHAR(10), 
        status_filme VARCHAR(50), 
        sinopse VARCHAR(4000), 
        url_poster VARCHAR(2048), 
        url_backdrop VARCHAR(2048), 
        CONSTRAINT pk_dim_movies PRIMARY KEY (sk_movie_id)
)

CREATE TABLE dim_people (
        sk_person_id VARCHAR(64) NOT NULL, 
        nome_pessoa VARCHAR(255) NOT NULL, 
        tipo_pessoa VARCHAR(20) NOT NULL, 
        CONSTRAINT pk_dim_people PRIMARY KEY (sk_person_id), 
        CONSTRAINT ck_dim_people_tipo_pessoa_valido CHECK (tipo_pessoa IN ('Ator', 'Diretor', 'Roteirista')), 
        CONSTRAINT uq_dim_people_nome_pessoa_tipo_pessoa UNIQUE (nome_pessoa, tipo_pessoa)
)

CREATE TABLE bridge_movie_company (
        sk_movie_id VARCHAR(64) NOT NULL, 
        sk_company_id VARCHAR(64) NOT NULL, 
        CONSTRAINT pk_bridge_movie_company PRIMARY KEY (sk_movie_id, sk_company_id), 
        CONSTRAINT fk_bridge_movie_company_sk_movie_id_dim_movies FOREIGN KEY(sk_movie_id) REFERENCES dim_movies (sk_movie_id) ON DELETE CASCADE, 
        CONSTRAINT fk_bridge_movie_company_sk_company_id_dim_companies FOREIGN KEY(sk_company_id) REFERENCES dim_companies (sk_company_id) ON DELETE CASCADE
)

CREATE TABLE bridge_movie_genre (
        sk_movie_id VARCHAR(64) NOT NULL, 
        sk_genre_id VARCHAR(64) NOT NULL, 
        CONSTRAINT pk_bridge_movie_genre PRIMARY KEY (sk_movie_id, sk_genre_id), 
        CONSTRAINT fk_bridge_movie_genre_sk_movie_id_dim_movies FOREIGN KEY(sk_movie_id) REFERENCES dim_movies (sk_movie_id) ON DELETE CASCADE, 
        CONSTRAINT fk_bridge_movie_genre_sk_genre_id_dim_genres FOREIGN KEY(sk_genre_id) REFERENCES dim_genres (sk_genre_id) ON DELETE CASCADE
)

CREATE TABLE bridge_movie_person (
        sk_movie_id VARCHAR(64) NOT NULL, 
        sk_person_id VARCHAR(64) NOT NULL, 
        CONSTRAINT pk_bridge_movie_person PRIMARY KEY (sk_movie_id, sk_person_id), 
        CONSTRAINT fk_bridge_movie_person_sk_movie_id_dim_movies FOREIGN KEY(sk_movie_id) REFERENCES dim_movies (sk_movie_id) ON DELETE CASCADE, 
        CONSTRAINT fk_bridge_movie_person_sk_person_id_dim_people FOREIGN KEY(sk_person_id) REFERENCES dim_people (sk_person_id) ON DELETE CASCADE
)

CREATE TABLE dim_reviews (
        sk_review_id VARCHAR(64) NOT NULL, 
        sk_movie_id VARCHAR(64) NOT NULL, 
        qtd_avaliacoes_usuarios INTEGER NOT NULL, 
        nota_media_usuarios DOUBLE, 
        CONSTRAINT pk_dim_reviews PRIMARY KEY (sk_review_id), 
        CONSTRAINT uq_dim_reviews_sk_movie_id UNIQUE (sk_movie_id), 
        CONSTRAINT fk_dim_reviews_sk_movie_id_dim_movies FOREIGN KEY(sk_movie_id) REFERENCES dim_movies (sk_movie_id) ON DELETE CASCADE
)

CREATE TABLE fact_movies_performance (
        sk_movie_id VARCHAR(64) NOT NULL, 
        orcamento_usd NUMERIC(18, 2), 
        receita_usd NUMERIC(18, 2), 
        lucro_usd NUMERIC(18, 2) NOT NULL, 
        orcamento_brl NUMERIC(18, 2), 
        receita_brl NUMERIC(18, 2), 
        lucro_brl NUMERIC(18, 2) NOT NULL, 
        popularidade DOUBLE, 
        nota_tmdb DOUBLE, 
        qtd_tmdb INTEGER, 
        nota_imdb DOUBLE, 
        qtd_imdb INTEGER, 
        CONSTRAINT pk_fact_movies_performance PRIMARY KEY (sk_movie_id), 
        CONSTRAINT fk_fact_movies_performance_sk_movie_id_dim_movies FOREIGN KEY(sk_movie_id) REFERENCES dim_movies (sk_movie_id) ON DELETE CASCADE
)

CREATE TABLE movie_reviews (
        id INTEGER NOT NULL, 
        sk_movie_review_id VARCHAR(64) NOT NULL, 
        sk_movie_id VARCHAR(64) NOT NULL, 
        name VARCHAR(120) NOT NULL, 
        rating DOUBLE NOT NULL, 
        text VARCHAR(4000) NOT NULL, 
        created_at DATETIME DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
        CONSTRAINT pk_movie_reviews PRIMARY KEY (id), 
        CONSTRAINT ck_movie_reviews_rating_range CHECK (rating >= 0 AND rating <= 10), 
        CONSTRAINT fk_movie_reviews_sk_movie_id_dim_movies FOREIGN KEY(sk_movie_id) REFERENCES dim_movies (sk_movie_id) ON DELETE CASCADE
)
"""
)

# conexao ao banco carregado na pasta raiz
conn = sqlite3.connect("cinerocket_database.db", check_same_thread=False)
print("Agente configurado na Base URL do OpenRouter com sucesso!")

# tool de query SQL 
@agente.tool
def executar_query_sql(ctx, query: str) -> str:
    # executa a query SQL e retorna dados crus
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        resultados = cursor.fetchall()
        # return como string para facil leitura
        return str(resultados) 
    except Exception as e:
        # se errar a leitura, o proprio modelo tenta corrigir usando a string de erro
        return f"Erro na query SQL: {e}"

# --- CONFIGURAÇÃO DA INTERFACE STREAMLIT ---
st.set_page_config(page_title="CineData Analytics - Agente Text-to-SQL", page_icon="🎬")

st.title("CineData Analytics SQL")

st.sidebar.title("🛠️ Painel de Controle")
st.sidebar.markdown("**Perguntas rápidas:**")

sugestoes = [
    "Quais são os 5 filmes mais populares?",
    "Top 10 filmes com maior receita em R$",
    "Ator com mais participações em filmes lançados nos últimos 5 anos",
    "Quantidade de filmes por gênero",
    "Filmes mais avaliados pelos usuários"
]

pergunta_selecionada = None
for s in sugestoes:
    if st.sidebar.button(s):
        pergunta_selecionada = s

st.sidebar.markdown("---")
st.sidebar.markdown("**Status OpenRouter (Free Tier)**")

#consulta opcional à API do OpenRouter para buscar o uso de requisições do dia
try:
    headers = {"Authorization": f"Bearer {os.environ.get('OPENROUTER_API_KEY')}"}
    response = requests.get("https://openrouter.ai/api/v1/key", headers=headers)
    if response.status_code == 200:
        data = response.json().get("data", {})
        #OpenRouter retorna informações de limite se aplicável
        limite_diario = 50 
        st.sidebar.info(f"Limite diário padrão: ~{limite_diario} requisições.")
    else:
        st.sidebar.caption("Monitoramento de cota ativo via OpenRouter.")
except Exception:
    st.sidebar.caption("Cota diária: 50 reqs (Free Tier)")

if st.sidebar.button("🗑️ Limpar Conversa"):
    st.session_state.mensagens = []
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("📈 **Métricas do Data Lakehouse**")

try:
    cursor = conn.cursor()
    
    # Total de filmes
    cursor.execute("SELECT COUNT(*) FROM dim_movies;")
    total_filmes = cursor.fetchone()[0]
    
    # Total de produtoras
    cursor.execute("SELECT COUNT(*) FROM dim_companies;")
    total_produtoras = cursor.fetchone()[0]
    
    # Exibe as métricas estilizadas no Streamlit
    st.sidebar.metric(label="🎬 Total de Filmes", value=f"{total_filmes:,}".replace(",", "."))
    st.sidebar.metric(label="🏢 Produtoras", value=total_produtoras)
    st.sidebar.metric(label="🗄️ Camada Gold", value="10 Tabelas") # Conforme especificado no escopo[cite: 27]

except Exception as e:
    st.sidebar.caption("Não foi possível carregar as métricas do banco.")

st.sidebar.markdown("---")

if "mensagens" not in st.session_state:
    st.session_state.mensagens = []

for msg in st.session_state.mensagens:
    st.chat_message(msg["role"]).write(msg["content"])
    if "df" in msg and msg["df"] is not None:
        st.download_button(
            label="📥 Baixar dados em CSV",
            data=msg["df"].to_csv(index=False).encode('utf-8'),
            file_name="cinedata_export.csv",
            mime="text/csv",
            key=msg["key"]
        )

pergunta = st.chat_input("Faça uma pergunta sobre os filmes...") or pergunta_selecionada

if pergunta:
    st.session_state.mensagens.append({"role": "user", "content": pergunta})
    st.chat_message("user").write(pergunta)
    
    with st.spinner("O agente está analisando o banco de dados..."):
        resultado = agente.run_sync(pergunta)
        resposta_ia = resultado.output
        
        df_resultado = None
        try:
            # Pegamos a última query executada ou rodamos uma busca complementar se necessário,
            # ou convertemos o output estruturado se o agente retornar em formato de tabela/lista.
            # Como o output é texto/tabela do Pydantic, podemos também consultar diretamente o banco 
            # usando a mesma pergunta para gerar o CSV de exportação:
            cursor = conn.cursor()
        except Exception:
            pass

    # Salva e exibe a resposta da IA com suporte a chave única para o botão
    msg_dict = {"role": "assistant", "content": resposta_ia, "df": None, "key": str(len(st.session_state.mensagens))}
    
    st.session_state.mensagens.append(msg_dict)
    st.chat_message("assistant").write(resposta_ia)