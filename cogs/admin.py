import discord
from discord.ext import commands
from discord import app_commands
from database import cursor, conexao

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="setcanal", description="[Admin] Define o canal onde os jogos serão anunciados.")
    @app_commands.checks.has_permissions(administrator=True) # Trava de Segurança (Cybersecurity)
    async def setcanal(self, interaction: discord.Interaction, canal: discord.TextChannel):
        try:
            # Salva ou atualiza o canal escolhido para este servidor específico
            cursor.execute("""
                INSERT INTO configuracoes (guild_id, canal_id) 
                VALUES (?, ?) 
                ON CONFLICT(guild_id) DO UPDATE SET canal_id = excluded.canal_id
            """, (interaction.guild.id, canal.id))
            conexao.commit()
            
            # Um Embed de confirmação para manter o design (Motion/UX)
            embed = discord.Embed(
                title="⚙️ Configuração Salva",
                description=f"O canal de anúncios automáticos foi definido para {canal.mention}.",
                color=0x3498db # Azul
            )
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Erro no banco de dados: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Admin(bot))