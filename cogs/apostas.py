import discord
from discord.ext import commands
from discord import app_commands
from database import cursor, conexao

def criar_embed(titulo, descricao, cor):
    return discord.Embed(title=titulo, description=descricao, color=discord.Color(cor))

class Apostas(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="criar_evento", description="[ADMIN] Abre um novo evento de apostas.")
    @app_commands.describe(titulo="Nome do evento", opcao_a="Primeira opção", opcao_b="Segunda opção")
    @app_commands.default_permissions(administrator=True)
    async def criar_evento(self, interaction: discord.Interaction, titulo: str, opcao_a: str, opcao_b: str):
        cursor.execute("INSERT INTO eventos (titulo, opcao_a, opcao_b, status) VALUES (?, ?, ?, 'aberto')", (titulo, opcao_a, opcao_b))
        conexao.commit()
        evento_id = cursor.lastrowid 
        
        embed = discord.Embed(title="📢 NOVA APOSTA ABERTA!", color=discord.Color(0xf1c40f))
        embed.add_field(name="🏆 Evento", value=titulo, inline=False)
        embed.add_field(name="🅰️ Opção A", value=opcao_a, inline=True)
        embed.add_field(name="🆚", value="vs", inline=True)
        embed.add_field(name="🅱️ Opção B", value=opcao_b, inline=True)
        embed.set_footer(text=f"ID do Evento: {evento_id} | Use o comando /apostar para participar!")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="ver_eventos", description="Mostra todos os eventos de apostas abertos no momento.")
    async def ver_eventos(self, interaction: discord.Interaction):
        cursor.execute("SELECT id, titulo, opcao_a, opcao_b FROM eventos WHERE status = 'aberto'")
        eventos_ativos = cursor.fetchall()

        if not eventos_ativos:
            embed = criar_embed("📭 Sem eventos", "No momento não há eventos abertos para apostas.", 0x3498db)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        embed = discord.Embed(title="🏆 Eventos Disponíveis para Apostas", description="Confira as partidas e use `/apostar` com o ID correspondente.", color=discord.Color(0x3498db))
        for evento in eventos_ativos:
            ev_id, titulo, op_a, op_b = evento
            cursor.execute("SELECT COUNT(*) FROM apostas WHERE evento_id = ?", (ev_id,))
            total_apostas = cursor.fetchone()[0]
            embed.add_field(name=f"🆔 `{ev_id}` - {titulo}", value=f"🅰️ {op_a} vs 🅱️ {op_b}\n👥 Apostas realizadas: **{total_apostas}**", inline=False)
        embed.set_footer(text="BetKing - Sistema de Economia Virtual")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="editar_evento", description="[ADMIN] Altera os detalhes de um evento existente.")
    @app_commands.describe(evento_id="ID do evento", titulo="Novo título", opcao_a="Nova Opção A", opcao_b="Nova Opção B")
    @app_commands.default_permissions(administrator=True)
    async def editar_evento(self, interaction: discord.Interaction, evento_id: int, titulo: str = None, opcao_a: str = None, opcao_b: str = None):
        cursor.execute("SELECT id FROM eventos WHERE id = ?", (evento_id,))
        if not cursor.fetchone():
            embed = criar_embed("❌ Erro", f"Evento ID `{evento_id}` não encontrado.", 0xe74c3c)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        if titulo: cursor.execute("UPDATE eventos SET titulo = ? WHERE id = ?", (titulo, evento_id))
        if opcao_a: cursor.execute("UPDATE eventos SET opcao_a = ? WHERE id = ?", (opcao_a, evento_id))
        if opcao_b: cursor.execute("UPDATE eventos SET opcao_b = ? WHERE id = ?", (opcao_b, evento_id))
        conexao.commit()
        embed = criar_embed("✅ Sucesso", f"Evento `{evento_id}` atualizado com sucesso!", 0x2ecc71)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="excluir_evento", description="[ADMIN] Remove evento e estorna os pontos para os usuários.")
    @app_commands.default_permissions(administrator=True)
    async def excluir_evento(self, interaction: discord.Interaction, evento_id: int):
        cursor.execute("SELECT titulo FROM eventos WHERE id = ?", (evento_id,))
        evento = cursor.fetchone()
        if not evento:
            embed = criar_embed("❌ Erro", f"Não encontrei nenhum evento com o ID `{evento_id}`.", 0xe74c3c)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        cursor.execute("SELECT usuario_id, valor FROM apostas WHERE evento_id = ?", (evento_id,))
        apostas = cursor.fetchall()
        for usuario_id, valor in apostas:
            cursor.execute("UPDATE usuarios SET saldo = saldo + ? WHERE id = ?", (valor, usuario_id))

        cursor.execute("DELETE FROM apostas WHERE evento_id = ?", (evento_id,))
        cursor.execute("DELETE FROM eventos WHERE id = ?", (evento_id,))
        conexao.commit()
        embed = criar_embed("🗑️ Evento Excluído", f"O evento **{evento[0]}** foi removido.\n💰 **{len(apostas)}** apostas foram estornadas.", 0xe74c3c)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="apostar", description="Aposte seus pontos em um evento aberto.")
    @app_commands.choices(opcao=[app_commands.Choice(name="Opção A", value="A"), app_commands.Choice(name="Opção B", value="B")])
    async def apostar(self, interaction: discord.Interaction, evento_id: int, opcao: app_commands.Choice[str], valor: int):
        if valor <= 0:
            embed = criar_embed("⚠️ Erro", "O valor da aposta deve ser maior que zero!", 0xe74c3c)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        cursor.execute("SELECT status FROM eventos WHERE id = ?", (evento_id,))
        evento = cursor.fetchone()
        if not evento or evento[0] != 'aberto':
            embed = criar_embed("🔒 Fechado", "Evento inexistente ou já fechado!", 0xe74c3c)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        cursor.execute("SELECT saldo FROM usuarios WHERE id = ?", (interaction.user.id,))
        usuario = cursor.fetchone()
        if not usuario or usuario[0] < valor:
            embed = criar_embed("💸 Saldo Insuficiente", f"Você não tem pontos suficientes para essa aposta.", 0xe74c3c)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        cursor.execute("UPDATE usuarios SET saldo = saldo - ? WHERE id = ?", (valor, interaction.user.id))
        cursor.execute("INSERT INTO apostas (evento_id, usuario_id, opcao, valor) VALUES (?, ?, ?, ?)", (evento_id, interaction.user.id, opcao.value, valor))
        conexao.commit()
        embed = criar_embed("🎰 Aposta Confirmada!", f"{interaction.user.mention} apostou **{valor} pontos** na **Opção {opcao.value}** do evento `{evento_id}`.", 0x2ecc71)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="finalizar_evento", description="[ADMIN] Encerra um evento e paga os vencedores.")
    @app_commands.choices(vencedor=[app_commands.Choice(name="Opção A", value="A"), app_commands.Choice(name="Opção B", value="B")])
    @app_commands.default_permissions(administrator=True)
    async def finalizar_evento(self, interaction: discord.Interaction, evento_id: int, vencedor: app_commands.Choice[str]):
        cursor.execute("SELECT titulo, status FROM eventos WHERE id = ?", (evento_id,))
        evento = cursor.fetchone()
        if not evento or evento[1] != 'aberto':
            embed = criar_embed("⚠️ Aviso", "Evento não encontrado ou já fechado.", 0xe74c3c)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        cursor.execute("SELECT SUM(valor) FROM apostas WHERE evento_id = ? AND opcao = 'A'", (evento_id,))
        total_a = cursor.fetchone()[0] or 0
        cursor.execute("SELECT SUM(valor) FROM apostas WHERE evento_id = ? AND opcao = 'B'", (evento_id,))
        total_b = cursor.fetchone()[0] or 0

        pote_total = total_a + total_b
        if pote_total == 0:
            cursor.execute("UPDATE eventos SET status = 'finalizado' WHERE id = ?", (evento_id,))
            conexao.commit()
            embed = criar_embed("🏁 Evento Encerrado", f"O evento `{evento_id}` foi encerrado, mas não houve nenhuma aposta.", 0x3498db)
            await interaction.response.send_message(embed=embed)
            return

        total_vencedor = total_a if vencedor.value == 'A' else total_b
        if total_vencedor == 0:
            cursor.execute("UPDATE eventos SET status = 'finalizado' WHERE id = ?", (evento_id,))
            conexao.commit()
            embed = criar_embed("🏁 Evento Encerrado", f"O vencedor foi a **Opção {vencedor.value}**, mas ninguém apostou nela!\nO pote de **{pote_total}** pontos ficou para a casa.", 0xf1c40f)
            await interaction.response.send_message(embed=embed)
            return

        odd = pote_total / total_vencedor
        cursor.execute("SELECT usuario_id, valor FROM apostas WHERE evento_id = ? AND opcao = ?", (evento_id, vencedor.value))
        ganhadores = cursor.fetchall()
        for user_id, valor_apostado in ganhadores:
            cursor.execute("UPDATE usuarios SET saldo = saldo + ? WHERE id = ?", (int(valor_apostado * odd), user_id))

        cursor.execute("UPDATE eventos SET status = 'finalizado' WHERE id = ?", (evento_id,))
        conexao.commit()

        embed = discord.Embed(title=f"🏁 RESULTADO: {evento[0]}", color=discord.Color(0xf1c40f))
        embed.add_field(name="🏆 Vencedor", value=f"**Opção {vencedor.value}**", inline=False)
        embed.add_field(name="📈 Odd Final", value=f"x{odd:.2f}", inline=True)
        embed.add_field(name="💰 Pote Total", value=f"{pote_total} pontos", inline=True)
        embed.add_field(name="👥 Ganhadores", value=f"{len(ganhadores)} pessoas receberam prêmios.", inline=False)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Apostas(bot))