import os
from dotenv import load_dotenv
from notion_client import Client
from notion_client.helpers import collect_paginated_api
import unicodedata
import datetime

load_dotenv()

class DBManager:
    def __init__(self):
        self.notion_token = os.getenv('NOTION_TOKEN')
        self.notion_database_id = os.getenv('NOTION_DATABASE_ID')
        self.notion_database_mensajes_id = os.getenv('NOTION_DATABASE_MENSAJES_ID')
        self.notion = None

        if not self.notion_token:
            print("¡ADVERTENCIA! La variable de entorno de Notion 'NOTION_TOKEN' no está configurada.")
        if not self.notion_database_id:
            print("¡ADVERTENCIA! La variable de entorno de Notion 'NOTION_DATABASE_ID' (para recursos) no está configurada.")
        if not self.notion_database_mensajes_id:
            print("¡ADVERTENCIA! La variable de entorno de Notion 'NOTION_DATABASE_MENSAJES_ID' (para mensajes) no está configurada.")

    def _normalize_string(self, text: str) -> str:
        if text is None:
            return None
        normalized_text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
        return normalized_text.lower()

    def connect(self):
        if self.notion is None:
            try:
                self.notion = Client(auth=self.notion_token)
                print("Cliente de Notion inicializado exitosamente.")
            except Exception as e:
                print(f"Error al inicializar el cliente de Notion: {e}")
                self.notion = None
        return self.notion

    def close(self):
        self.notion = None
        print("Cliente de Notion 'cerrado' (desreferenciado).")

    def get_scheduled_messages(self):
        if not self.notion:
            self.connect()
        if not self.notion or not self.notion_database_mensajes_id:
            return []

        try:
            # Filtro compuesto: activo=True Y enviado=False
            query_filter = {
                "and": [
                    {
                        "property": "activo",
                        "checkbox": {"equals": True}
                    },
                    {
                        "property": "enviado",
                        "checkbox": {"equals": False}
                    }
                ]
            }
            pages = collect_paginated_api(
                self.notion.databases.query,
                database_id=self.notion_database_mensajes_id,
                filter=query_filter
            )
            
            messages = []
            for page in pages:
                props = page.get("properties", {})
                
                cuerpo_prop = props.get("cuerpo", {})
                cuerpo_content = []
                if "title" in cuerpo_prop:
                    cuerpo_content = cuerpo_prop.get("title", [])
                elif "rich_text" in cuerpo_prop:
                    cuerpo_content = cuerpo_prop.get("rich_text", [])
                cuerpo = "".join([text.get("plain_text", "") for text in cuerpo_content])

                fecha_data = props.get("fecha", {}).get("date")
                fecha = fecha_data.get("start") if fecha_data else None
                
                canal_rich_text = props.get("canal", {}).get("rich_text", [])
                canal_id_str = "".join([text.get("plain_text", "") for text in canal_rich_text]).strip()
                
                frecuencia_data = props.get("frecuencia", {}).get("select")
                frecuencia = frecuencia_data.get("name") if frecuencia_data else "unico" # Default a 'unico'

                if cuerpo and fecha and canal_id_str:
                    try:
                        canal_id = int(canal_id_str)
                        messages.append({
                            "page_id": page["id"],
                            "cuerpo": cuerpo,
                            "fecha": fecha,
                            "canal_id": canal_id,
                            "frecuencia": frecuencia
                        })
                    except ValueError:
                        print(f"ADVERTENCIA: No se pudo convertir el ID del canal '{canal_id_str}' a un número para la página '{page['id']}'.")
            return messages
        except Exception as e:
            print(f"Error al obtener mensajes programados de Notion: {e}")
            return []

    def mark_message_as_sent(self, page_id: str):
        if not self.notion:
            self.connect()
        if not self.notion:
            return False
        try:
            self.notion.pages.update(
                page_id=page_id,
                properties={"enviado": {"checkbox": True}}
            )
            print(f"Mensaje '{page_id}' marcado como enviado.")
            return True
        except Exception as e:
            print(f"Error al marcar el mensaje '{page_id}' como enviado: {e}")
            return False

    def reschedule_message(self, page_id: str, new_date: datetime.datetime):
        if not self.notion:
            self.connect()
        if not self.notion:
            return False
        try:
            # Formatear la nueva fecha a ISO 8601 para la API de Notion
            new_date_iso = new_date.isoformat()
            self.notion.pages.update(
                page_id=page_id,
                properties={
                    "fecha": {"date": {"start": new_date_iso}},
                    "enviado": {"checkbox": False} # Desmarcar para el próximo ciclo
                }
            )
            print(f"Mensaje '{page_id}' reprogramado para {new_date_iso}.")
            return True
        except Exception as e:
            print(f"Error al reprogramar el mensaje '{page_id}': {e}")
            return False

    def insert_resource(self, resource_name: str, link: str, category: str, difficulty: str, subcategory: str = None):
        if not self.notion:
            self.connect()
        if not self.notion:
            return False
        try:
            normalized_resource_name = self._normalize_string(resource_name)
            normalized_category = self._normalize_string(category)
            normalized_subcategory = self._normalize_string(subcategory)
            normalized_difficulty = self._normalize_string(difficulty)
            properties = {
                "resource_name": {"title": [{"text": {"content": normalized_resource_name}}]},
                "link": {"url": link},
                "category": {"select": {"name": normalized_category}},
                "difficulty": {"select": {"name": normalized_difficulty}}
            }
            if normalized_subcategory:
                properties["subcategory"] = {"select": {"name": normalized_subcategory}}
            self.notion.pages.create(
                parent={"database_id": self.notion_database_id},
                properties=properties
            )
            print(f"Recurso '{resource_name}' insertado en Notion.")
            return True
        except Exception as e:
            print(f"Error al insertar el recurso '{resource_name}' en Notion: {e}")
            return False

    def get_resources(self, category: str = None, subcategory: str = None, difficulty: str = None):
        if not self.notion:
            self.connect()
        if not self.notion:
            return []
        filter_conditions = []
        normalized_category = self._normalize_string(category)
        normalized_subcategory = self._normalize_string(subcategory)
        normalized_difficulty = self._normalize_string(difficulty)
        if normalized_category:
            filter_conditions.append({
                "property": "category",
                "select": {"equals": category}
            })
        if normalized_subcategory:
            filter_conditions.append({
                "property": "subcategory",
                "select": {"equals": subcategory}
            })
        if normalized_difficulty:
            filter_conditions.append({
                "property": "difficulty",
                "select": {"equals": difficulty}
            })
        query_filter = {}
        if filter_conditions:
            if len(filter_conditions) == 1:
                query_filter = filter_conditions[0]
            else:
                query_filter["and"] = filter_conditions
        resources = []
        try:
            pages = collect_paginated_api(
                self.notion.databases.query,
                database_id=self.notion_database_id,
                filter=query_filter
            )
            for page in pages:
                props = page["properties"]
                resource = {
                    "resource_name": props.get("resource_name", {}).get("title", [{}])[0].get("plain_text") if props.get("resource_name") else None,
                    "link": props.get("link", {}).get("url"),
                    "category": props.get("category", {}).get("select", {}).get("name"),
                    "subcategory": props.get("subcategory", {}).get("select", {}).get("name"),
                    "difficulty": props.get("difficulty", {}).get("select", {}).get("name"),
                }
                resources.append(resource)
            print(f"Recursos encontrados en Notion: {len(resources)}")
        except Exception as e:
            print(f"Error al obtener recursos de Notion: {e}")
        return resources

    def get_distinct_difficulties(self):
        if not self.notion:
            self.connect()
        if not self.notion:
            return []
        difficulties = set()
        try:
            pages = collect_paginated_api(
                self.notion.databases.query,
                database_id=self.notion_database_id
            )
            for page in pages:
                difficulty = page["properties"].get("difficulty", {}).get("select", {}).get("name")
                if difficulty:
                    difficulties.add(difficulty)
        except Exception as e:
            print(f"Error al obtener dificultades distintas de Notion: {e}")
        return sorted(list(difficulties))

    def get_distinct_categories(self, difficulty: str = None):
        if not self.notion:
            self.connect()
        if not self.notion:
            return []
        categories = set()
        filter_conditions = []
        if difficulty:
            filter_conditions.append({
                "property": "difficulty",
                "select": {"equals": self._normalize_string(difficulty)}
            })
        query_filter = {}
        if filter_conditions:
            query_filter["and"] = filter_conditions
        try:
            pages = collect_paginated_api(
                self.notion.databases.query,
                database_id=self.notion_database_id,
                filter=query_filter
            )
            for page in pages:
                category = page["properties"].get("category", {}).get("select", {}).get("name")
                if category:
                    categories.add(category)
        except Exception as e:
            print(f"Error al obtener categorías distintas de Notion: {e}")
        return sorted(list(categories))

    def get_distinct_subcategories(self, difficulty: str = None, category: str = None):
        if not self.notion:
            self.connect()
            print("Conectando a Notion para obtener subcategorías...")
        if not self.notion:
            print("No se pudo conectar a Notion para obtener subcategorías.")
            print("Asegúrate de que el cliente de Notion esté inicializado correctamente.")
            return []
        subcategories = set()
        filter_conditions = []
        if difficulty:
            filter_conditions.append({
                "property": "difficulty",
                "select": {"equals": self._normalize_string(difficulty)}
            })
            print(f"Filtrando por dificultad: {difficulty}")
        if category:
            filter_conditions.append({
                "property": "category",
                "select": {"equals": category}
            })
            print(f"Filtrando por categoría: {category}")
        query_filter = {}
        if filter_conditions:
            query_filter["and"] = filter_conditions
            print(f"Condiciones de filtro aplicadas: {query_filter}")
        try:
            pages = collect_paginated_api(
                self.notion.databases.query,
                database_id=self.notion_database_id,
                filter=query_filter
            )
            for page in pages:
                subcategory = page["properties"].get("subcategory", {}).get("select", {}).get("name")
                if subcategory:
                    print(f"Subcategoría encontrada: {subcategory}")
                    subcategories.add(subcategory)
        except Exception as e:
            print(f"Error al obtener subcategorías distintas de Notion: {e}")
        return sorted(list(subcategories))