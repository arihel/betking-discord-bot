import discord
from discord.ext import commands, tasks
import aiohttp
import os
import datetime
from database import cursor, conexao

class Automacao(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.url_fixtures = "https://v3.football.api-sports.io/fixtures"
        self.headers = {"x-apisports-key": os.getenv("API_SPORTS_KEY")}
        self.ciclo_mestre.start()

    # Deixei com 6 horas. Mude para minutes=1 temporariamente se quiser forçar o teste de novo!
    @tasks.loop(hours=6)
    async def ciclo_mestre(self):
        agora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"🔄 [{agora}] Iniciando ciclo mestre de verificação da API...")
        await self.buscar_novos_jogos()
        await self.verificar_resultados()

    async def buscar_novos_jogos(self):
        print("⚽ Buscando novos jogos importantes para amanhã...")
        data_futura = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        params = {"date": data_futura, "timezone": "America/Sao_Paulo"}

        # IDs das competições VIP (Brasileirão, Libertadores, Champions, etc)
        LIGAS_IMPORTANTES = [71, 73, 13, 2, 1, 4, 9, 10, 34]

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(self.url_fixtures, headers=self.headers, params=params) as resp:
                    if resp.status == 200:
                        dados = await resp.json()
                        todos_os_jogos = dados.get('response', [])
                        
                        # Filtra apenas os jogos VIP
                        jogos_filtrados = [
                            jogo for jogo in todos_os_jogos 
                            if jogo['league']['id'] in LIGAS_IMPORTANTES
                        ]

                        top_20_jogos = jogos_filtrados[:20]

                        jogos_adicionados = 0
                        for jogo in top_20_jogos:
                            api_id = jogo['fixture']['id']
                            timestamp_jogo = jogo['fixture']['timestamp']
                            casa = jogo['teams']['home']['name']
                            fora = jogo['teams']['away']['name']
                            evento_titulo = f"{casa} vs {fora}"

                            try:
                                cursor.execute("""
                                    INSERT OR IGNORE INTO eventos (titulo, opcao_a, opcao_b, status, api_id, data_hora) 
                                    VALUES (?, ?, ?, 'aberto', ?, ?)
                                """, (evento_titulo, casa, fora, api_id, timestamp_jogo))
                                
                                if cursor.rowcount > 0: 
                                    jogos_adicionados += 1
                            except Exception as e:
                                print(f"Erro no banco: {e}")
                        
                        conexao.commit()
                        
                        if jogos_adicionados > 0:
                            print(f"✅ {jogos_adicionados} novos jogos VIP adicionados.")
                            # Chama a função correta passando a variável
                            await self.anunciar_jogos_abertos(jogos_adicionados)
                        else:
                            print("ℹ️ Nenhum jogo das ligas principais encontrado para amanhã.")
            except Exception as e:
                print(f"❌ Erro na API: {e}")

    async def verificar_resultados(self):
        print("🏁 Verificando se há jogos finalizados...")
        cursor.execute("SELECT id, api_id, titulo, opcao_a, opcao_b FROM eventos WHERE status = 'aberto' AND api_id IS NOT NULL")
        eventos_abertos = cursor.fetchall()

        if not eventos_abertos:
            print("▶️ Nenhum jogo em aberto no momento. Ciclo finalizado.")
            return

        # Agrupa IDs para poupar requisições da API
        api_ids = [str(ev[1]) for ev in eventos_abertos]
        chunks = [api_ids[i:i + 20] for i in range(0, len(api_ids), 20)]
        mapa_eventos = {ev[1]: ev for ev in eventos_abertos}

        async with aiohttp.ClientSession() as session:
            for chunk in chunks:
                ids_agrupados = ",".join(chunk)
                params = {"ids": ids_agrupados, "timezone": "America/Sao_Paulo"}
                
                try:
                    async with session.get(self.url_fixtures, headers=self.headers, params=params) as resp:
                        if resp.status == 200:
                            dados = await resp.json()
                            for jogo in dados.get('response', []):
                                status_partida = jogo['fixture']['status']['short']
                                
                                if status_partida in ['FT', 'AET', 'PEN']:
                                    api_id_jogo = jogo['fixture']['id']
                                    ev_id, _, titulo, time_a, time_b = mapa_eventos[api_id_jogo]
                                    
                                    gols_casa = jogo['goals']['home']
                                    gols_fora = jogo['goals']['away']
                                    
                                    vencedor = "Empate"
                                    if gols_casa > gols_fora: vencedor = time_a
                                    elif gols_fora > gols_casa: vencedor = time_b
                                        
                                    placar = f"{gols_casa} x {gols_fora}"
                                    await self.processar_pagamentos(ev_id, titulo, vencedor, placar)
                except Exception as e:
                    print(f"❌ Erro ao checar resultados: {e}")

        print("✅ Verificação concluída com sucesso! Aguardando o próximo ciclo...") # AVISO 2

    async def processar_pagamentos(self, evento_id, titulo, vencedor, placar):
        cursor.execute("SELECT usuario_id, valor FROM apostas WHERE evento_id = ? AND escolha = ?", (evento_id, vencedor))
        ganhadores = cursor.fetchall()

        total_pago = 0
        for user_id, valor in ganhadores:
            premio = valor * 2
            cursor.execute("UPDATE usuarios SET saldo = saldo + ? WHERE id = ?", (premio, user_id))
            total_pago += premio

        cursor.execute("UPDATE eventos SET status = 'fechado', resultado = ? WHERE id = ?", (vencedor, evento_id))
        conexao.commit()
        await self.anunciar_fim_de_jogo(titulo, vencedor, placar, len(ganhadores), total_pago)

    async def anunciar_jogos_abertos(self, jogos_adicionados):
        cursor.execute("SELECT canal_id FROM configuracoes")
        canais = cursor.fetchall()
        if not canais: return

        embed = discord.Embed(title="🔥 Novos Jogos Liberados!", description=f"A casa abriu **{jogos_adicionados} novos eventos VIPs**. Aposte na vitória ou no Empate!", color=0xffa500)
        cursor.execute("SELECT id, titulo FROM eventos WHERE status = 'aberto' ORDER BY id DESC LIMIT ?", (jogos_adicionados,))
        for ev_id, titulo in cursor.fetchall():
            embed.add_field(name=f"🎫 Evento #{ev_id}", value=f"**{titulo}**", inline=False)
        embed.set_footer(text="Use o comando /apostar para participar!")

        for (canal_id,) in canais:
            canal = self.bot.get_channel(canal_id)
            if canal: await canal.send(embed=embed)

    async def anunciar_fim_de_jogo(self, titulo, vencedor, placar, qtd_ganhadores, total_pago):
        cursor.execute("SELECT canal_id FROM configuracoes")
        canais = cursor.fetchall()
        if not canais: return

        embed = discord.Embed(title="🏁 Jogo Encerrado!", description=f"**{titulo}** finalizou em **{placar}**.", color=0x2ecc71)
        embed.add_field(name="Vencedor / Resultado", value=f"🏆 **{vencedor}**", inline=False)
        embed.add_field(name="Resumo", value=f"👥 Ganhadores: **{qtd_ganhadores}**\n💰 Total Pago: **R$ {total_pago}**", inline=False)

        for (canal_id,) in canais:
            canal = self.bot.get_channel(canal_id)
            if canal: await canal.send(embed=embed)

    @ciclo_mestre.before_loop
    async def before_ciclo(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(Automacao(bot))