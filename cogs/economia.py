import discord
from discord.ext import commands
from discord import app_commands
from database import cursor, conexao # Importa a conexão lá do database.py

def criar_embed(titulo, descricao, cor):
    return discord.Embed(title=titulo, description=descricao, color=discord.Color(cor))

class Economia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="registrar", description="Cria sua conta e ganhe 1000 pontos iniciais.")
    async def registrar(self, interaction: discord.Interaction):
        cursor.execute("SELECT saldo FROM usuarios WHERE id = ?", (interaction.user.id,))
        if cursor.fetchone():
            embed = criar_embed("⚠️ Aviso", f"{interaction.user.mention}, você já possui uma conta ativa no sistema.", 0xe74c3c)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            cursor.execute("INSERT INTO usuarios (id, saldo) VALUES (?, ?)", (interaction.user.id, 1000))
            conexao.commit()
            embed = criar_embed("🎉 Bem-vindo!", f"Conta criada com sucesso para {interaction.user.mention}.\nVocê recebeu **1000 pontos** iniciais.", 0x2ecc71)
            await interaction.response.send_message(embed=embed)

    @app_commands.command(name="saldo", description="Verifica quantos pontos você tem na sua carteira.")
    async def saldo(self, interaction: discord.Interaction):
        cursor.execute("SELECT saldo FROM usuarios WHERE id = ?", (interaction.user.id,))
        resultado = cursor.fetchone()
        if resultado:
            embed = criar_embed("💰 Carteira Virtual", f"Olá {interaction.user.mention}, seu saldo atual é de:\n**{resultado[0]} pontos**.", 0x3498db)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = criar_embed("❌ Erro", f"{interaction.user.mention}, você ainda não possui uma conta. Use `/registrar`.", 0xe74c3c)
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="transferir", description="Transfere pontos para outro usuário.")
    @app_commands.describe(membro="Quem vai receber os pontos?", valor="Quantos pontos quer enviar?")
    async def transferir(self, interaction: discord.Interaction, membro: discord.Member, valor: int):
        if valor <= 0:
            embed = criar_embed("⚠️ Operação Inválida", "O valor da transferência deve ser maior que zero!", 0xe74c3c)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        if interaction.user.id == membro.id:
            embed = criar_embed("⚠️ Operação Inválida", "Você não pode transferir pontos para si mesmo!", 0xe74c3c)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        cursor.execute("SELECT saldo FROM usuarios WHERE id = ?", (interaction.user.id,))
        remetente = cursor.fetchone()
        if not remetente or remetente[0] < valor:
            embed = criar_embed("💸 Saldo Insuficiente", "Você não tem pontos suficientes ou não possui conta.", 0xe74c3c)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        cursor.execute("SELECT saldo FROM usuarios WHERE id = ?", (membro.id,))
        if not cursor.fetchone():
            embed = criar_embed("❌ Erro", f"O usuário {membro.mention} não possui conta no sistema.", 0xe74c3c)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        cursor.execute("UPDATE usuarios SET saldo = saldo - ? WHERE id = ?", (valor, interaction.user.id))
        cursor.execute("UPDATE usuarios SET saldo = saldo + ? WHERE id = ?", (valor, membro.id))
        conexao.commit()

        embed = criar_embed("💸 Transferência Realizada", f"Sucesso! {interaction.user.mention} transferiu **{valor} pontos** para {membro.mention}.", 0x2ecc71)
        await interaction.response.send_message(embed=embed)

# Função obrigatória para o main.py carregar este arquivo
async def setup(bot):
    await bot.add_cog(Economia(bot))