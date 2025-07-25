import os
from dotenv import load_dotenv

# Carga las variables de entorno desde el archivo .env
load_dotenv()

# --- TOKEN DEL BOT ---
# El token de tu bot de Discord. Es crucial mantenerlo seguro y no compartirlo.
TOKEN = os.getenv('TOKEN')

# --- CONFIGURACIÓN DE IDs DE CANALES, CATEGORÍAS Y ROLES ---
# Estos IDs se obtienen activando el Modo Desarrollador en Discord (Ajustes de Usuario -> Avanzado),
# luego haciendo clic derecho en el canal/categoría/rol y seleccionando "Copiar ID".
# Es fundamental que estos valores se configuren en tu archivo .env.

# ID del canal donde los nuevos miembros recibirán el mensaje de bienvenida.
# Ejemplo en .env: NUEVO_INGRESO_CHANNEL_ID=123456789012345678
NUEVO_INGRESO_CHANNEL_ID = int(os.getenv('NUEVO_INGRESO_CHANNEL_ID')) if os.getenv('NUEVO_INGRESO_CHANNEL_ID') else None

# ID de la categoría donde se crearán los canales de ayuda técnica.
# Ejemplo en .env: AYUDA_TECNICA_CATEGORY_ID=987654321098765432
AYUDA_TECNICA_CATEGORY_ID = int(os.getenv('AYUDA_TECNICA_CATEGORY_ID')) if os.getenv('AYUDA_TECNICA_CATEGORY_ID') else None

# ID de la categoría donde se crearán los canales de atención al cliente (para "Hablar con un Humano").
# Ejemplo en .env: ATENCION_AL_CLIENTE_CATEGORY_ID=112233445566778899
ATENCION_AL_CLIENTE_CATEGORY_ID = int(os.getenv('ATENCION_AL_CLIENTE_CATEGORY_ID')) if os.getenv('ATENCION_AL_CLIENTE_CATEGORY_ID') else None

# ID de la categoría donde se crearán los canales para la búsqueda de recursos.
# Ejemplo en .env: RESOURCES_CATEGORY_ID=223344556677889900
RESOURCES_CATEGORY_ID = int(os.getenv('RESOURCES_CATEGORY_ID')) if os.getenv('RESOURCES_CATEGORY_ID') else None

# ID del rol que será notificado y tendrá acceso a los canales de soporte técnico.
# Ejemplo en .env: SOPORTE_TECNICO_ROLE_ID=123123123123123123
SOPORTE_TECNICO_ROLE_ID = int(os.getenv('SOPORTE_TECNICO_ROLE_ID')) if os.getenv('SOPORTE_TECNICO_ROLE_ID') else None

# ID del rol que será notificado y tendrá acceso a los canales de atención al cliente.
# Ejemplo en .env: ATENCION_AL_CLIENTE_ROLE_ID=456456456456456456
ATENCION_AL_CLIENTE_ROLE_ID = int(os.getenv('ATENCION_AL_CLIENTE_ROLE_ID')) if os.getenv('ATENCION_AL_CLIENTE_ROLE_ID') else None

# Diccionario para almacenar el estado de las conversaciones de "Hablar con un Humano"
# Formato: {user_id: {'state': int, 'answers': [], 'channel_id': None}}
# state: 0 = no en conversación, 1 = esperando respuesta a Pregunta 1, etc.
# Este diccionario se mantendrá aquí por simplicidad, pero en una aplicación más grande
# podría considerarse moverlo a una base de datos o un sistema de caché.
user_conversations = {}

# Verificar que las variables de entorno esenciales estén cargadas
def validate_env_variables():
    """
    Valida que las variables de entorno esenciales estén configuradas.
    Imprime advertencias si alguna variable importante no se encuentra.
    """
    if TOKEN is None:
        print("¡ADVERTENCIA! La variable de entorno 'TOKEN' no está definida. El bot no podrá iniciar sesión.")
    if NUEVO_INGRESO_CHANNEL_ID is None:
        print("¡ADVERTENCIA! 'NUEVO_INGRESO_CHANNEL_ID' no está definido. La bienvenida automática no funcionará.")
    if AYUDA_TECNICA_CATEGORY_ID is None:
        print("¡ADVERTENCIA! 'AYUDA_TECNICA_CATEGORY_ID' no está definido. La creación de canales de ayuda técnica podría fallar.")
    if ATENCION_AL_CLIENTE_CATEGORY_ID is None:
        print("¡ADVERTENCIA! 'ATENCION_AL_CLIENTE_CATEGORY_ID' no está definido. La creación de canales de atención al cliente podría fallar.")
    if RESOURCES_CATEGORY_ID is None:
        print("¡ADVERTENCIA! 'RESOURCES_CATEGORY_ID' no está definido. La creación de canales de búsqueda de recursos podría fallar.")
    if SOPORTE_TECNICO_ROLE_ID is None:
        print("¡ADVERTENCIA! 'SOPORTE_TECNICO_ROLE_ID' no está definido. La asignación de permisos de soporte técnico podría fallar.")
    if ATENCION_AL_CLIENTE_ROLE_ID is None:
        print("¡ADVERTENCIA! 'ATENCION_AL_CLIENTE_ROLE_ID' no está definido. La asignación de permisos de atención al cliente podría fallar.")

# Llama a la función de validación al cargar el módulo
validate_env_variables()
