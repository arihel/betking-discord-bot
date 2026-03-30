import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# Carrega o Token
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Configura a Classe Base do Bot
class BetKingBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=discord.Intents.default())

    # O setup_hook roda de forma assíncrona antes do bot conectar
    async def setup_hook(self):
        print("Carregando módulos...")
        # Lê a pasta 'cogs' e carrega os arquivos .py
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')
                print(f"Módulo {filename} carregado!")
        
        # Sincroniza os Slash Commands com o Discord
        await self.tree.sync()
        print("✅ Slash Commands sincronizados!")

    async def on_ready(self):
        print(f'🤖 Bot 100% Online e Modularizado! Logado como {self.user}')

# Inicia o Bot
bot = BetKingBot()
bot.run(TOKEN)