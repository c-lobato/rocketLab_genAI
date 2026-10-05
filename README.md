# 🎬 CineData Analytics - Assistente Text-to-SQL

Projeto do módulo de GenAI do bootcamp Rocket Lab 2026.2. Esta aplicação consiste em um agente de Inteligência Artificial capaz de traduzir perguntas feitas em linguagem natural para consultas SQL, executá-las em um banco de dados local (SQLite) e retornar as respostas de forma clara para o usuário.

## 🚀 Funcionalidades

- **Chat Interativo:** Interface web amigável construída com Streamlit.
- **Consultas em Linguagem Natural:** O agente entende o schema do banco e gera queries SQL complexas (camada Gold).
- **Memória de Conversa:** Histórico de conversa mantido durante o uso da aplicação.
- **Painel de Controle:** Sugestões de perguntas rápidas, monitoramento de cota de requisições e métricas do banco de dados em tempo real.

## 🛠️ Tecnologias Utilizadas

- **Linguagem:** Python
- **Interface Web:** Streamlit
- **Framework de Agentes:** PydanticAI
- **LLM:** OpenRouter API (`nvidia/nemotron-3.5-lightning:free` / compatível com padrão OpenAI)
- **Banco de Dados:** SQLite

## ⚙️ Como executar o projeto localmente

Siga o passo a passo abaixo para configurar o ambiente e rodar a aplicação na sua máquina.

### 1. Clonar o repositório

```bash
git clone https://github.com/c-lobato/rocketLab_genAI.git
cd rocketLab
```

### 2. Configurar o Ambiente Virtual

Crie e ative um ambiente virtual para isolar as dependências:

```bash
python -m venv venv
```

Ativar no Windows:

```powershell
venv\Scripts\activate
```

Ativar no Linux/Mac:

```bash
source venv/bin/activate
```

### 3. Instalar as dependências

Com o ambiente virtual ativado, instale as bibliotecas necessárias:

```bash
pip install pydantic-ai streamlit python-dotenv openai requests
```

### 4. Configurar as Variáveis de Ambiente e Banco de Dados

Crie um arquivo chamado `.env` na raiz do projeto.

Adicione a sua chave de API do OpenRouter no seguinte formato:

```env
OPENROUTER_API_KEY="sk-or-v1-SUA_CHAVE_AQUI"
```

**OBS:** Certifique-se de que o arquivo do banco de dados `cinerocket.db` (camada Gold) esteja localizado na mesma pasta raiz do arquivo `main.py`.

### 5. Executar a aplicação

Inicie o servidor do Streamlit com o comando:

```bash
streamlit run main.py
```

A aplicação abrirá automaticamente no seu navegador padrão no endereço http://localhost:8501.