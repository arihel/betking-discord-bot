
<h1 align="center">🎰 BetKing - Discord Betting Bot</h1>

<p align="center">
  <img src="https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54" alt="Python">
  <img src="https://img.shields.io/badge/discord.py-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="Discord.py">
  <img src="https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite">
  <img src="https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
</p>

<p align="center">
  <strong>Sistema modular de economia virtual e apostas dinâmicas projetado para alta performance e segurança.</strong>
</p>

---

## 📖 Sobre o Projeto
O **BetKing** é um bot de Discord que implementa uma economia pulsante baseada em eventos. Utilizando uma arquitetura de **Cogs** para modularização e **SQLite** para persistência, ele oferece um mercado de apostas com **Odds Dinâmicas (Pari-Mutuel)**, onde o prêmio é ajustado automaticamente conforme o volume de apostas no pote.

---

## 📸 Demonstração Visual
> [!TIP]
> **Atenção Designer:** Substitua o link abaixo pelo seu GIF de alta qualidade exportado do After Effects/Premiere para mostrar o bot em ação!

<p align="center">
  <img src="https://via.placeholder.com/800x400?text=GIF+DEMONSTRATIVO+MOTION+DESIGN+AQUI" alt="Showcase do Bot" width="80%">
</p>

---

## 🚀 Funcionalidades Principais

| Módulo | Comando | Descrição |
| :--- | :--- | :--- |
| 💰 **Economia** | `/registrar` | Cria conta com bônus inicial de 1000 pontos. |
| 💰 **Economia** | `/saldo` | Consulta privada de pontos (mensagem efêmera). |
| 💰 **Economia** | `/transferir` | Envio seguro de pontos entre usuários. |
| 🎲 **Apostas** | `/criar_evento` | [Admin] Abre novos mercados de apostas. |
| 🎲 **Apostas** | `/apostar` | Participação em eventos com escolha de Opção A ou B. |
| 🎲 **Apostas** | `/finalizar_evento` | [Admin] Encerra o mercado e paga os vencedores. |
| 🛡️ **Gestão** | `/excluir_evento` | [Admin] Remove evento e **estorna os pontos** automaticamente. |

---

## 🛠️ Arquitetura e Estrutura
O projeto foi estruturado para facilitar a manutenção e garantir o isolamento de funções (Separação de Preocupações):

```text
├── 📁 cogs/             # Módulos de comandos independentes
│   ├── economia.py      # Lógica financeira e carteira
│   └── apostas.py       # Lógica de jogo e eventos
├── database.py         # Conexão centralizada com SQLite
├── main.py             # Orquestrador principal e carregador de Cogs
├── Dockerfile          # Containerização da aplicação
└── requirements.txt    # Dependências do sistema
```
## 🎰 Lógica de Pagamento
O bot utiliza o sistema de **Odds Dinâmicas**, garantindo que a casa nunca perca e que o prêmio seja proporcional ao risco:

$$Prêmio = ValorApostado \times \left( \frac{PoteTotal}{TotalVencedor} \right)$$

---

## ⚙️ Instalação e Execução

### 1. Clonar e Configurar
```bash
git clone https://github.com/arihel/betking-discord-bot.git
cd betking-discord-bot
```

Crie um arquivo `.env` com seu token:
`DISCORD_TOKEN=seu_token_aqui`

### 2. Rodar via Docker (Recomendado)
```bash
docker build -t betking-bot .
docker run -d --name betking -v "$(pwd)/cassino.db:/app/cassino.db" betking-bot
```

---

## 🛡️ Foco em Cybersecurity
Buscando um desenvolvimento focado em boas práticas de cibersegurança, o projeto implementa:

* **Prevenção de SQL Injection:** Queries parametrizadas com placeholders `?`.
* **Segurança de Credenciais:** Isolamento completo via variáveis de ambiente (`.env`).
* **Integridade de Dados:** Sistema de estorno automático em caso de cancelamento de eventos.

---

<p align="center">
  Desenvolvido com ☕ por <strong>Arihel Secron</strong><br>
  <em>Motion Designer & Estudante de Sistemas de Informação</em><br><br>
  <a href="[https://github.com/arihel](https://github.com/arihel)">GitHub</a> • <a href="[https://linkedin.com/in/arihelsecron](https://linkedin.com/in/arihelsecron)">LinkedIn</a>
</p>



Motion Designer & Bacharel de Sistemas de Informação



<a href="https://www.google.com/search?q=https://github.com/arihel">GitHub</a> • <a href="https://www.google.com/search?q=https://linkedin.com/in/arihelsecron">LinkedIn</a>
</p>
