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


# --- CONFIGURACIÓN DE IDs DE USUARIOS PARA CONTACTO HUMANO ---
# IDs de los usuarios que pueden ser contactados a través del menú "Hablar con un Humano".
# Ejemplo en .env: VALERY_USER_ID=111122223333444455
# Ejemplo en .env: BELU_USER_ID=555544443333222211
VALERY_USER_ID = int(os.getenv('VALERY_USER_ID')) if os.getenv('VALERY_USER_ID') else None
BELU_USER_ID = int(os.getenv('BELU_USER_ID')) if os.getenv('BELU_USER_ID') else None


# ID del servidor
SERVER_ID = int(os.getenv('SERVER_ID')) if os.getenv('SERVER_ID') else None

# ID del canal donde se enviarán las notificaciones de nuevos bugs y reportes de cierre.
BUGS_CHANNEL_ID = int(os.getenv('BUGS_CHANNEL_ID')) if os.getenv('BUGS_CHANNEL_ID') else None

# ID del rol de "Operaciones" que debe ser mencionado en los bugs.
OPERECIONES_ROLES_ID = int(os.getenv('OPERECIONES_ROLES_ID')) if os.getenv('OPERECIONES_ROLES_ID') else None

# ID de la categoría general del servidor, donde se pueden crear canales generales.
GENERAL_CATEGORY_ID = int(os.getenv('GENERAL_CATEGORY_ID')) if os.getenv('GENERAL_CATEGORY_ID') else None

# ID de la base de datos de Notion para los mensajes programados.
NOTION_DATABASE_MENSAJES_ID = os.getenv('NOTION_DATABASE_MENSAJES_ID')


# Diccionario para almacenar el estado de las conversaciones de "Hablar con un Humano"
# Formato: {user_id: {'state': int, 'answers': [], 'channel_id': None, 'selected_human': None}}
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

    if VALERY_USER_ID is None:
        print("¡ADVERTENCIA! 'VALERY_USER_ID' no está definido. El botón de Valery no funcionará.")
    if BELU_USER_ID is None:
        print("¡ADVERTENCIA! 'BELU_USER_ID' no está definido. El botón de Belu no funcionará.")
    if SERVER_ID is None:
        print("¡ADVERTENCIA! La variable de entorno 'SERVER_ID' no está definida.")
    if BUGS_CHANNEL_ID is None:
        print("¡ADVERTENCIA! La variable de entorno 'BUGS_CHANNEL_ID' no está definida. La funcionalidad de bugs podría fallar.")
    if OPERECIONES_ROLES_ID is None:
        print("¡ADVERTENCIA! La variable de entorno 'OPERECIONES_ROLES_ID' no está definida. La mención del rol de operaciones podría fallar.")
    if GENERAL_CATEGORY_ID is None:
        print("¡ADVERTENCIA! 'GENERAL_CATEGORY_ID' no está definido. La creación de canales generales podría fallar.")
    if NOTION_DATABASE_MENSAJES_ID is None:
        print("¡ADVERTENCIA! 'NOTION_DATABASE_MENSAJES_ID' no está definido. La funcionalidad de mensajes programados no funcionará.")

# Llama a la función de validación al cargar el módulo
validate_env_variables()
