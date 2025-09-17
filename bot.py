# Archivo: bot.py
# Punto de entrada principal para el Bot de Neurocogniciones.

import os
import discord
from discord.ext import commands
import asyncio
import traceback

# Importa las configuraciones
import config

# --- CONFIGURACIÓN DE INTENTS (PERMISOS) ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

# Inicializa el bot
bot = commands.Bot(command_prefix='&', intents=intents)

# --- FUNCIÓN PARA CARGAR LOS COGS ---
async def load_all_cogs():
    """Carga todas las extensiones de cogs."""
    cogs_to_load = [
        'cogs.events',
        'cogs.commands',
        'cogs.ticket_management',
        'cogs.human_interaction',
        'cogs.resources',
        'cogs.bug_info',
        'cogs.scheduled_message_task'
    ]
    print("ℹ️ Cargando cogs...")
    for cog in cogs_to_load:
        try:
            await bot.load_extension(cog)
            print(f"  -> Cog '{cog}' cargado.")
        except Exception as e:
            print(f"❌ Error al cargar el cog {cog}: {e}")
    print("✅ Cogs cargados exitosamente.")


# --- FUNCIÓN PRINCIPAL DE INICIO ---
async def main():
    """Función principal que carga los cogs y luego inicia el bot."""
    if not config.TOKEN:
        print("❌ No se encontró el TOKEN del bot. Asegúrate de que está configurado en tu archivo .env.")
        return

    # El context manager `async with bot` maneja la conexión y la limpieza.
    async with bot:
        # Cargamos los cogs antes de iniciar el bot
        await load_all_cogs()
        # Iniciamos el bot
        await bot.start(config.TOKEN)

# --- PUNTO DE ENTRADA ---
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("ℹ️ Bot desconectado manualmente.")
    except Exception as e:
        print(f"❌ Ocurrió un error inesperado: {e}")
        traceback.print_exc()
