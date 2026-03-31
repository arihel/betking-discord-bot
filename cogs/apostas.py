import discord
from discord.ext import commands
from discord import app_commands
import time
from database import cursor, conexao

def criar_embed(titulo, descricao, cor):
    return discord.Embed(title=titulo, description=descricao, color=discord.Color(cor))

class Apostas(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="criar_evento", description="[ADMIN] Abre um novo evento de apostas manual.")
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
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        embed = discord.Embed(title="🏆 Eventos Disponíveis para Apostas", color=discord.Color(0x3498db))
        for evento in eventos_ativos:
            ev_id, titulo, op_a, op_b = evento
            cursor.execute("SELECT COUNT(*) FROM apostas WHERE evento_id = ?", (ev_id,))
            total_apostas = cursor.fetchone()[0]
            embed.add_field(name=f"🆔 `{ev_id}` - {titulo}", value=f"A: {op_a} | B: {op_b}\n👥 Apostas: **{total_apostas}**", inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="editar_evento", description="[ADMIN] Altera os detalhes de um evento existente.")
    @app_commands.default_permissions(administrator=True)
    async def editar_evento(self, interaction: discord.Interaction, evento_id: int, titulo: str = None, opcao_a: str = None, opcao_b: str = None):
        cursor.execute("SELECT id FROM eventos WHERE id = ?", (evento_id,))
        if not cursor.fetchone():
            return await interaction.response.send_message("❌ Evento não encontrado.", ephemeral=True)
            
        if titulo: cursor.execute("UPDATE eventos SET titulo = ? WHERE id = ?", (titulo, evento_id))
        if opcao_a: cursor.execute("UPDATE eventos SET opcao_a = ? WHERE id = ?", (opcao_a, evento_id))
        if opcao_b: cursor.execute("UPDATE eventos SET opcao_b = ? WHERE id = ?", (opcao_b, evento_id))
        conexao.commit()
        await interaction.response.send_message(f"✅ Evento `{evento_id}` atualizado com sucesso!")

    @app_commands.command(name="excluir_evento", description="[ADMIN] Remove evento e estorna os pontos para os usuários.")
    @app_commands.default_permissions(administrator=True)
    async def excluir_evento(self, interaction: discord.Interaction, evento_id: int):
        cursor.execute("SELECT titulo FROM eventos WHERE id = ?", (evento_id,))
        evento = cursor.fetchone()
        if not evento:
            return await interaction.response.send_message("❌ Evento não encontrado.", ephemeral=True)

        cursor.execute("SELECT usuario_id, valor FROM apostas WHERE evento_id = ?", (evento_id,))
        apostas = cursor.fetchall()
        for usuario_id, valor in apostas:
            cursor.execute("UPDATE usuarios SET saldo = saldo + ? WHERE id = ?", (valor, usuario_id))

        cursor.execute("DELETE FROM apostas WHERE evento_id = ?", (evento_id,))
        cursor.execute("DELETE FROM eventos WHERE id = ?", (evento_id,))
        conexao.commit()
        await interaction.response.send_message(f"🗑️ O evento **{evento[0]}** foi removido. **{len(apostas)}** apostas estornadas.")

    @app_commands.command(name="apostar", description="Faça sua aposta em um evento aberto.")
    @app_commands.describe(evento_id="O número do evento", escolha="Selecione A (Casa), B (Fora) ou C (Empate)", valor="Valor da aposta")
    @app_commands.choices(escolha=[
        app_commands.Choice(name="A - Time da Casa", value="A"),
        app_commands.Choice(name="B - Time de Fora", value="B"),
        app_commands.Choice(name="C - Empate", value="C")
    ])
    async def apostar(self, interaction: discord.Interaction, evento_id: int, escolha: app_commands.Choice[str], valor: int):
        user_id = interaction.user.id
        
        cursor.execute("SELECT saldo FROM usuarios WHERE id = ?", (user_id,))
        usuario = cursor.fetchone()
        if not usuario: return await interaction.response.send_message("❌ Use `/registrar` primeiro.", ephemeral=True)
        
        saldo_atual = usuario[0]
        if valor <= 0: return await interaction.response.send_message("❌ Valor inválido.", ephemeral=True)
        if valor > saldo_atual: return await interaction.response.send_message("❌ Saldo insuficiente.", ephemeral=True)

        cursor.execute("SELECT titulo, opcao_a, opcao_b, status, data_hora FROM eventos WHERE id = ?", (evento_id,))
        evento = cursor.fetchone()

        if not evento: return await interaction.response.send_message("❌ Evento não encontrado.", ephemeral=True)
        
        titulo, time_a, time_b, status, data_hora = evento

        if status != 'aberto':
            return await interaction.response.send_message("❌ Este evento já foi encerrado para apostas.", ephemeral=True)

        agora_timestamp = int(time.time())
        if data_hora and agora_timestamp >= data_hora:
            cursor.execute("UPDATE eventos SET status = 'fechado' WHERE id = ?", (evento_id,))
            conexao.commit()
            return await interaction.response.send_message("⏰ **Apostas Fechadas!** A bola já rolou para este jogo.", ephemeral=True)

        opcao_selecionada = escolha.value
        if opcao_selecionada == 'A': escolha_final = time_a
        elif opcao_selecionada == 'B': escolha_final = time_b
        elif opcao_selecionada == 'C': escolha_final = "Empate"

        try:
            cursor.execute("UPDATE usuarios SET saldo = saldo - ? WHERE id = ?", (valor, user_id))
            cursor.execute("INSERT INTO apostas (usuario_id, evento_id, escolha, valor) VALUES (?, ?, ?, ?)", 
                           (user_id, evento_id, escolha_final, valor))
            conexao.commit()

            embed = discord.Embed(title="✅ Aposta Confirmada!", description=f"Você apostou no jogo **{titulo}**.", color=0x2ecc71)
            embed.add_field(name="Sua Escolha", value=f"🏆 **{escolha_final}**", inline=True)
            embed.add_field(name="Valor", value=f"💰 **R$ {valor}**", inline=True)
            await interaction.response.send_message(embed=embed)

        except Exception as e:
            conexao.rollback()
            await interaction.response.send_message(f"❌ Erro: {e}", ephemeral=True)

    @app_commands.command(name="finalizar_evento", description="[ADMIN] Encerra um evento manualmente e paga os apostadores.")
    @app_commands.describe(evento_id="ID do evento", vencedor="Escolha o resultado final")
    @app_commands.choices(vencedor=[
        app_commands.Choice(name="A - Time da Casa", value="A"),
        app_commands.Choice(name="B - Time de Fora", value="B"),
        app_commands.Choice(name="C - Empate", value="C")
    ])
    @app_commands.default_permissions(administrator=True)
    async def finalizar_evento(self, interaction: discord.Interaction, evento_id: int, vencedor: app_commands.Choice[str]):
        await interaction.response.defer()

        cursor.execute("SELECT titulo, opcao_a, opcao_b, status FROM eventos WHERE id = ?", (evento_id,))
        evento = cursor.fetchone()

        if not evento or evento[3] != 'aberto':
            return await interaction.followup.send("❌ Evento não encontrado ou já finalizado.")

        titulo, time_a, time_b, _ = evento

        if vencedor.value == 'A': escolha_vencedora = time_a
        elif vencedor.value == 'B': escolha_vencedora = time_b
        else: escolha_vencedora = "Empate"

        try:
            cursor.execute("SELECT usuario_id, valor, escolha FROM apostas WHERE evento_id = ?", (evento_id,))
            todas_apostas = cursor.fetchall()

            qtd_ganhadores = 0
            total_pago = 0

            for user_id, valor, escolha_feita in todas_apostas:
                if escolha_feita == escolha_vencedora:
                    premio = valor * 2
                    cursor.execute("UPDATE usuarios SET saldo = saldo + ? WHERE id = ?", (premio, user_id))
                    qtd_ganhadores += 1
                    total_pago += premio

            cursor.execute("UPDATE eventos SET status = 'fechado', resultado = ? WHERE id = ?", (escolha_vencedora, evento_id))
            conexao.commit()

            embed = discord.Embed(
                title=f"🏁 FINALIZADO MANUALMENTE: {titulo}",
                description=f"O administrador definiu o resultado como: **{escolha_vencedora}**",
                color=0xf1c40f
            )
            embed.add_field(name="📊 Estatísticas", value=f"👥 Ganhadores: **{qtd_ganhadores}**\n💰 Total Pago: **R$ {total_pago}**")
            
            await interaction.followup.send(embed=embed)

        except Exception as e:
            conexao.rollback()
            await interaction.followup.send(f"❌ Erro crítico ao finalizar: {e}")

async def setup(bot):
    await bot.add_cog(Apostas(bot))