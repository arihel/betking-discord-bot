import discord
from discord.ext import commands
from discord import app_commands
import time
from database import cursor, conexao

class Economia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="registrar", description="Crie sua conta para começar a apostar.")
    async def registrar(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        
        cursor.execute("SELECT id FROM usuarios WHERE id = ?", (user_id,))
        if cursor.fetchone():
            return await interaction.response.send_message("❌ Você já possui uma conta registrada!", ephemeral=True)

        try:
            # Cria o usuário com 1000 pontos e last_daily zerado
            cursor.execute("INSERT INTO usuarios (id, saldo, last_daily) VALUES (?, 1000, 0)", (user_id,))
            conexao.commit()
            await interaction.response.send_message("🎉 Bem-vindo! Conta criada com sucesso. Você recebeu **1000 pontos** iniciais.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Erro ao criar conta: {e}", ephemeral=True)

    @app_commands.command(name="saldo", description="Veja quantos pontos você tem disponíveis.")
    async def saldo(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        
        cursor.execute("SELECT saldo FROM usuarios WHERE id = ?", (user_id,))
        usuario = cursor.fetchone()

        if not usuario:
            return await interaction.response.send_message("❌ Você ainda não tem uma conta. Use `/registrar`.", ephemeral=True)

        embed = discord.Embed(title="💰 Seu Saldo", description=f"Você tem **R$ {usuario[0]}** disponíveis para apostas.", color=0x2ecc71)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="resgatar_diario", description="Receba seus 200 pontos diários.")
    async def resgatar_diario(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        agora = int(time.time())
        vinte_quatro_horas = 86400

        cursor.execute("SELECT saldo, last_daily FROM usuarios WHERE id = ?", (user_id,))
        usuario = cursor.fetchone()

        if not usuario:
            return await interaction.response.send_message("❌ Use `/registrar` primeiro!", ephemeral=True)

        saldo_atual, last_daily = usuario

        tempo_passado = agora - last_daily
        if tempo_passado < vinte_quatro_horas:
            restante = vinte_quatro_horas - tempo_passado
            horas = restante // 3600
            minutos = (restante % 3600) // 60
            return await interaction.response.send_message(f"⏳ Você já resgatou hoje! Volte em **{horas}h {minutos}min**.", ephemeral=True)

        try:
            cursor.execute("UPDATE usuarios SET saldo = saldo + 200, last_daily = ? WHERE id = ?", (agora, user_id))
            conexao.commit()

            embed = discord.Embed(
                title="🎁 Resgate Diário",
                description=f"Você recebeu **200 pontos**! Seu novo saldo é **R$ {saldo_atual + 200}**.",
                color=0x2ecc71
            )
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"❌ Erro ao processar resgate: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Economia(bot))