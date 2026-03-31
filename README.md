<h1 align="center">🎰 BetKing - Discord Betting Bot</h1>

<p align="center">
  <img src="https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54" alt="Python">
  <img src="https://img.shields.io/badge/discord.py-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="Discord.py">
  <img src="https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite">
  <img src="https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
</p>

<p align="center">
  <strong>Sistema modular de economia virtual e apostas automatizadas via API real, projetado para alta performance e segurança.</strong>
</p>

---

## 📖 Sobre o Projeto
O **BetKing** é um bot de entretenimento que integra o mundo das apostas esportivas ao Discord. Através da conexão com a **API-Football**, o sistema monitora partidas de futebol em tempo real, automatizando o ciclo de vida de uma aposta: desde a abertura do mercado até o pagamento dos vencedores. 

O projeto foi desenvolvido com foco em **Cybersecurity**, garantindo que as transações virtuais sejam íntegras e protegidas contra exploits comuns.

---

## 📸 Demonstração Visual
> [!TIP]
> [PLACEHOLDER] GIF mostrando o bot respondendo aos comandos e o anúncio automático de novos jogos para impressionar quem visita seu repositório.

<p align="center">
  <img src="https://via.placeholder.com/800x400?text=GIF+DEMONSTRATIVO+MOTION+DESIGN+AQUI" alt="Showcase do Bot" width="80%">
</p>

---

## 🚀 Funcionalidades Completas

### 💰 Sistema de Economia (Módulo do Usuário)
* **`/registrar`**: Inicia a jornada do usuário, criando uma carteira digital com um bônus de boas-vindas de **1000 pontos**.
* **`/saldo`**: Exibe o saldo atual do usuário de forma privada.
* **`/resgatar_diario`**: Sistema de fidelização que concede **200 pontos** a cada 24 horas, controlado rigorosamente via Unix Timestamp para evitar resgates múltiplos.
* **`/transferir`**: Permite a movimentação de pontos entre usuários do servidor, promovendo a interação social.

### 🎲 Sistema de Apostas & Real-Time
* **`/ver_eventos`**: Interface visual que lista todos os jogos disponíveis, exibindo os times, IDs e o volume de apostas atual.
* **`/apostar`**: Permite escolher entre a Vitória do Time A, Time B ou o **Empate (Opção C)**. O sistema valida se o usuário possui saldo e se o evento ainda aceita entradas.
* **Automação de Resultados**: O bot verifica periodicamente a API e, assim que uma partida encerra, identifica o vencedor, calcula os prêmios e notifica o canal automaticamente.

### 🛡️ Comandos Administrativos (Gestão & Auditoria)
* **`/criar_evento`**: Permite a abertura manual de mercados para eventos que não estão na API (ex: torneios internos).
* **`/editar_evento`**: Ajusta nomes de times ou títulos de eventos já criados para correção de erros.
* **`/excluir_evento`**: Comando de emergência que remove um mercado e realiza o **estorno automático** de todos os pontos apostados para os respectivos usuários.
* **`/finalizar_evento`**: Fallback de segurança que permite ao Admin definir o vencedor manualmente em caso de instabilidade na API.

---

## 🏗️ Arquitetura e Segurança (Foco em Cybersecurity)
Como um projeto de **Sistemas de Informação**, o BetKing implementa camadas de proteção críticas:

1.  **Prevenção de SQL Injection**: Uso obrigatório de consultas parametrizadas (`?`) em todas as interações com o SQLite.
2.  **Anti-Exploit Temporal**: O bot cruza o timestamp da API com o horário do servidor. Se um usuário tentar apostar em um jogo que já começou, a transação é recusada e o evento é fechado.
3.  **Proteção de Variáveis Sensíveis**: Isolamento total de Tokens e Chaves de API via arquivo `.env`, impedindo vazamentos em logs de versionamento.
4.  **Gerenciamento de Concorrência**: Configuração de `timeout` no banco de dados para suportar múltiplas apostas simultâneas sem corrupção de dados.

---

## ⚙️ Estrutura do Repositório
    ├── 📁 cogs/               # Módulos independentes (Cogs)
    │   ├── economia.py        # Gestão financeira e recompensas
    │   ├── apostas.py         # Comandos de jogo e administração
    │   └── automacao.py       # Loop de API e verificação de resultados
    ├── database.py           # Configuração de Schema e segurança do SQLite
    ├── main.py               # Arquivo principal (Entry Point)
    ├── iniciar_bot.bat       # Script de automação para Windows (Local)
    ├── Dockerfile            # Configuração para deploy em containers
    └── requirements.txt      # Dependências do projeto

---

## 🛠️ Como Instalar e Rodar

1.  **Clone o projeto**: `git clone https://github.com/arihel/betking-discord-bot.git`
2.  **Variáveis**: Crie um `.env` com seu `DISCORD_TOKEN` e sua `API_SPORTS_KEY`.
3.  **Ambiente**: Instale as dependências com `pip install -r requirements.txt`.
4.  **Execução**:
    * **Local**: Use o arquivo `iniciar_bot.bat` para carregar o ambiente automaticamente.
    * **Docker**: `docker build -t betking . && docker run betking`

---

<p align="center">
  Desenvolvido por <strong>Arihel Secron</strong><br>
  <em>Estudante de Cybersecurity & Sistemas de Informação</em><br><br>
  <a href="https://github.com/arihel">GitHub</a> • <a href="https://linkedin.com/in/arihelsecron">LinkedIn</a>
</p>