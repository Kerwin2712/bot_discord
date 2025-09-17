# cogs/scheduled_message_task.py

import discord
from discord.ext import commands, tasks
import datetime
import pytz
from database.db_manager import DBManager

class ScheduledMessageTask(commands.Cog):
    """
    Un cog que revisa periódicamente la base de datos de Notion en busca de mensajes
    programados para enviar a canales específicos de Discord.
    """
    def __init__(self, bot):
        self.bot = bot
        self.db_manager = DBManager()
        self.timezone = pytz.timezone('UTC')
        self.send_scheduled_messages.start()

    def cog_unload(self):
        self.send_scheduled_messages.cancel()

    @tasks.loop(seconds=60)  # Revisa cada 60 segundos
    async def send_scheduled_messages(self):
        """
        Tarea principal que se ejecuta en bucle para buscar y enviar mensajes.
        """
        now_utc = datetime.datetime.now(self.timezone)
        
        try:
            messages_to_send = self.db_manager.get_scheduled_messages()
            if not messages_to_send:
                return

            print(f"\nSe encontraron {len(messages_to_send)} mensajes activos y pendientes.")

            for msg in messages_to_send:
                try:
                    scheduled_time_aware = datetime.datetime.fromisoformat(msg['fecha'])

                    if now_utc >= scheduled_time_aware:
                        print(f"  - Procesando mensaje '{msg['page_id']}' para el canal {msg['canal_id']}")
                        channel = self.bot.get_channel(msg['canal_id'])
                        if channel:
                            await channel.send(msg['cuerpo'])
                            print(f"    ✅ Mensaje enviado al canal '{channel.name}'.")
                            
                            # --- Lógica de Frecuencia ---
                            frecuencia = msg.get("frecuencia", "unico").lower()
                            page_id = msg['page_id']

                            if frecuencia == "diario":
                                new_date = scheduled_time_aware + datetime.timedelta(days=1)
                                print(f"    - Frecuencia: Diario. Reprogramando para {new_date.strftime('%Y-%m-%d')}")
                                self.db_manager.reschedule_message(page_id, new_date)

                            elif frecuencia == "semanal":
                                new_date = scheduled_time_aware + datetime.timedelta(weeks=1)
                                print(f"    - Frecuencia: Semanal. Reprogramando para {new_date.strftime('%Y-%m-%d')}")
                                self.db_manager.reschedule_message(page_id, new_date)

                            else: # "unico" o cualquier otro valor
                                print("    - Frecuencia: Único. Marcando como enviado.")
                                self.db_manager.mark_message_as_sent(page_id)

                        else:
                            print(f"    ❌ Error: No se encontró el canal con ID {msg['canal_id']}.")

                except Exception as e:
                    print(f"❌ Error procesando un mensaje individual (Page ID: {msg.get('page_id', 'N/A')}): {e}")

        except Exception as e:
            print(f"❌ Error general en la tarea de envío de mensajes: {e}")

    @send_scheduled_messages.before_loop
    async def before_task_starts(self):
        """
        Se asegura de que el bot esté listo y el cliente de Notion conectado
        antes de que comience el bucle de la tarea.
        """
        await self.bot.wait_until_ready()
        print("ℹ️ Bot listo. Conectando a Notion para la tarea de mensajes programados...")
        try:
            self.db_manager.connect()
            print("✅ Conexión a Notion establecida para la tarea de mensajes.")
        except Exception as e:
            print(f"❌ Error al conectar con Notion en el inicio de la tarea: {e}")
        print("ℹ️ Tarea de mensajes programados iniciada. Buscando mensajes para enviar...")

async def setup(bot):
    await bot.add_cog(ScheduledMessageTask(bot))