# Archivo: views/main_menu.py

import discord
import asyncio
import config # Importa la configuración para acceder a user_conversations
# Importamos el DBManager para interactuar con la base de datos de recursos
from database.db_manager import DBManager

# Instancia global del DBManager para ser utilizada por las vistas
db_manager = DBManager()

class CloseTicketView(discord.ui.View):
    """
    Vista que contiene un botón para cerrar un canal de ticket.
    """
    def __init__(self, channel_to_close: discord.TextChannel):
        super().__init__(timeout=300) # 5 minutos de timeout para el botón
        self.channel_to_close = channel_to_close
        self.message = None # Para almacenar el mensaje

    async def on_timeout(self):
        """
        Se ejecuta cuando el tiempo de espera de la vista ha expirado.
        Deshabilita todos los botones.
        """
        for item in self.children:
            item.disabled = True
        if self.message:
            try:
                # No eliminar el mensaje, solo deshabilitar los botones
                await self.message.edit(content="Este mensaje de cierre de ticket ha expirado.", view=self)
            except discord.NotFound:
                print("Mensaje de CloseTicketView no encontrado al intentar editar en timeout.")
            except Exception as e:
                print(f"Error al editar mensaje de CloseTicketView en timeout: {e}")

    @discord.ui.button(label="Cerrar Ticket", style=discord.ButtonStyle.red, custom_id="close_ticket", emoji="❌")
    async def close_ticket_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Cierra el canal de soporte actual cuando se hace clic en el botón.
        """
        await interaction.response.send_message("Cerrando este canal de soporte en 5 segundos...", ephemeral=False)
        # Deshabilita el botón inmediatamente para evitar clics múltiples
        for item in self.children:
            item.disabled = True
        await interaction.message.edit(view=self)

        await asyncio.sleep(5) # Espera 5 segundos antes de eliminar el canal
        try:
            await self.channel_to_close.delete()
        except discord.Forbidden:
            await interaction.followup.send("❌ No tengo permisos para eliminar este canal. Por favor, contacta a un administrador.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Ocurrió un error al intentar cerrar el canal: `{e}`", ephemeral=True)
            print(f"Error al cerrar el canal {self.channel_to_close.name}: {e}")


class ResourceDisplayView(discord.ui.View):
    """
    Vista para mostrar los recursos finales encontrados.
    """
    def __init__(self, resources: list, current_difficulty: str, current_category: str, current_subcategory: str = None):
        super().__init__(timeout=180) # 3 minutos de timeout
        self.resources = resources
        self.current_difficulty = current_difficulty
        self.current_category = current_category
        self.current_subcategory = current_subcategory
        self.message = None # Para almacenar el mensaje

    async def on_timeout(self):
        """
        Se ejecuta cuando el tiempo de espera de la vista ha expirado.
        Deshabilita todos los botones.
        """
        for item in self.children:
            item.disabled = True
        if self.message:
            try:
                # No eliminar el mensaje, solo deshabilitar los botones
                await self.message.edit(content="La interacción de recursos ha expirado.", view=self)
            except discord.NotFound:
                print("Mensaje de ResourceDisplayView no encontrado al intentar editar en timeout.")
            except Exception as e:
                print(f"Error al editar mensaje de ResourceDisplayView en timeout: {e}")

    async def send_resources(self, interaction: discord.Interaction):
        """
        Envía el mensaje con los recursos encontrados.
        """
        if self.resources:
            response_message = f"📚 **Recursos encontrados para '{self.current_category}'"
            if self.current_subcategory:
                response_message += f" (Subcategoría: '{self.current_subcategory}')"
            response_message += f" (Dificultad: '{self.current_difficulty}'):**\n\n"

            for i, res in enumerate(self.resources):
                response_message += (
                    f"**{i+1}. {res['resource_name']}**\n"
                    f"   Enlace: <{res['link']}>\n"
                    f"   Categoría: `{res['category']}`\n"
                )
                if res['subcategory']:
                    response_message += f"   Subcategoría: `{res['subcategory']}`\n"
                response_message += f"   Dificultad: `{res['difficulty']}`\n\n"
            
            # Dividir el mensaje si es demasiado largo para Discord
            if len(response_message) > 2000:
                self.message = await interaction.followup.send(response_message[:1990] + "...\n(Mensaje truncado. Por favor, refina tu búsqueda.)", view=self)
            else:
                self.message = await interaction.followup.send(response_message, view=self)
        else:
            self.message = await interaction.followup.send(
                f"No se encontraron recursos para la dificultad `{self.current_difficulty}`, "
                f"categoría `{self.current_category}`"
                f"{f' y subcategoría `{self.current_subcategory}`' if self.current_subcategory else ''}. "
                "Intenta con otra selección.", ephemeral=False, view=self
            )


class SubcategorySelectionView(discord.ui.View):
    """
    Vista para seleccionar una subcategoría de recursos.
    """
    def __init__(self, bot, difficulty: str, category: str):
        super().__init__(timeout=180)
        self.bot = bot
        self.difficulty = difficulty
        self.category = category
        self.message = None

        self._add_subcategory_buttons()

    async def on_timeout(self):
        """
        Se ejecuta cuando el tiempo de espera de la vista ha expirado.
        Deshabilita todos los botones.
        """
        for item in self.children:
            item.disabled = True
        if self.message:
            try:
                # No eliminar el mensaje, solo deshabilitar los botones
                await self.message.edit(content="La interacción de selección de subcategoría ha expirado.", view=self)
            except discord.NotFound:
                print("Mensaje de SubcategorySelectionView no encontrado al intentar editar en timeout.")
            except Exception as e:
                print(f"Error al editar mensaje de SubcategorySelectionView en timeout: {e}")

    def _add_subcategory_buttons(self):
        """Añade botones para cada subcategoría disponible."""
        if not db_manager.connect():
            print("Error: No se pudo conectar a la base de datos para obtener subcategorías.")
            self.add_item(discord.ui.Button(label="Error de DB", style=discord.ButtonStyle.red, disabled=True))
            return

        subcategories = db_manager.get_distinct_subcategories(difficulty=self.difficulty, category=self.category)
        if not subcategories:
            self.add_item(discord.ui.Button(label="No hay subcategorías disponibles", style=discord.ButtonStyle.grey, disabled=True))
            return

        for subcategory in subcategories:
            # Discord tiene un límite de 25 botones por vista
            if len(self.children) < 25:
                self.add_item(discord.ui.Button(label=subcategory.title(), style=discord.ButtonStyle.secondary, custom_id=f"subcat_{subcategory}"))
            else:
                break # Evitar añadir más de 25 botones

    @discord.ui.button(label="Ver todos los recursos de esta categoría", style=discord.ButtonStyle.primary, custom_id="view_all_in_category", row=4)
    async def view_all_in_category_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Maneja la interacción para ver todos los recursos de la categoría seleccionada
        sin filtrar por subcategoría.
        """
        await interaction.response.defer() # Deferir la respuesta para dar tiempo a la DB
        
        resources = db_manager.get_resources(category=self.category, difficulty=self.difficulty)
        
        for item in self.children:
            item.disabled = True
        await interaction.message.edit(content=f"Mostrando recursos para '{self.category}' (Dificultad: '{self.difficulty}').", view=self)

        resource_view = ResourceDisplayView(resources, self.difficulty, self.category)
        await resource_view.send_resources(interaction)


    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """ Verifica que solo el usuario que inició la interacción pueda usar los botones.
            La lógica para los botones de subcategoría se maneja aquí dinámicamente.
        """
        if interaction.data and interaction.data.get("custom_id", "").startswith("subcat_"):
            selected_subcategory = interaction.data["custom_id"].replace("subcat_", "")
            await interaction.response.defer() # Deferir la respuesta para dar tiempo a la DB
            resources = db_manager.get_resources(
                category=self.category,
                subcategory=selected_subcategory,
                difficulty=self.difficulty
            )
            for item in self.children:
                item.disabled = True
            await interaction.message.edit(content=f"Has seleccionado la subcategoría: **{selected_subcategory.title()}** (Categoría: {self.category.title()}, Dificultad: {self.difficulty.title()}).", view=self)
            
            resource_view = ResourceDisplayView(resources, self.difficulty, self.category, selected_subcategory)
            await resource_view.send_resources(interaction)
            return False # No continuar con otros botones en esta interacción
        return True # Permitir que otros botones se procesen


class CategorySelectionView(discord.ui.View):
    """
    Vista para seleccionar una categoría de recursos.
    """
    def __init__(self, bot, difficulty: str):
        super().__init__(timeout=180)
        self.bot = bot
        self.difficulty = difficulty
        self.message = None

        self._add_category_buttons()

    async def on_timeout(self):
        """
        Se ejecuta cuando el tiempo de espera de la vista ha expirado.
        Deshabilita todos los botones.
        """
        for item in self.children:
            item.disabled = True
        if self.message:
            try:
                # No eliminar el mensaje, solo deshabilitar los botones
                await self.message.edit(content="La interacción de selección de categoría ha expirado.", view=self)
            except discord.NotFound:
                print("Mensaje de CategorySelectionView no encontrado al intentar editar en timeout.")
            except Exception as e:
                print(f"Error al editar mensaje de CategorySelectionView en timeout: {e}")

    def _add_category_buttons(self):
        """Añade botones para cada categoría disponible."""
        if not db_manager.connect():
            print("Error: No se pudo conectar a la base de datos para obtener categorías.")
            self.add_item(discord.ui.Button(label="Error de DB", style=discord.ButtonStyle.red, disabled=True))
            return

        categories = db_manager.get_distinct_categories(difficulty=self.difficulty)
        if not categories:
            self.add_item(discord.ui.Button(label="No hay categorías disponibles", style=discord.ButtonStyle.grey, disabled=True))
            return

        for category in categories:
            if len(self.children) < 25: # Discord tiene un límite de 25 botones por vista
                self.add_item(discord.ui.Button(label=category.title(), style=discord.ButtonStyle.primary, custom_id=f"cat_{category}"))
            else:
                break


    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """ Verifica que solo el usuario que inició la interacción pueda usar los botones.
            La lógica para los botones de categoría se maneja aquí dinámicamente.
        """
        if interaction.data and interaction.data.get("custom_id", "").startswith("cat_"):
            selected_category = interaction.data["custom_id"].replace("cat_", "")
            await interaction.response.defer() # Deferir la respuesta para dar tiempo a la DB
            
            # Deshabilitar los botones de esta vista
            for item in self.children:
                item.disabled = True
            await interaction.message.edit(content=f"Has seleccionado la categoría: **{selected_category.title()}** (Dificultad: {self.difficulty.title()}).", view=self)

            # Obtener subcategorías para la dificultad y categoría seleccionadas
            subcategories = db_manager.get_distinct_subcategories(difficulty=self.difficulty, category=selected_category)
            print(f"Subcategorías encontradas para '{selected_category}': {subcategories}") # DEBUG: Para ver qué devuelve la DB
            if subcategories:
                subcategory_view = SubcategorySelectionView(self.bot, self.difficulty, selected_category)
                await interaction.followup.send("Por favor, selecciona una subcategoría o ver todos:", view=subcategory_view)
                subcategory_view.message = interaction.message # Asignar el mensaje para timeout
                print("Subcategorías encontradas, enviando vista de selección.")
            else:
                # Si no hay subcategorías, ir directamente a mostrar recursos de la categoría
                resources = db_manager.get_resources(category=selected_category, difficulty=self.difficulty)
                resource_view = ResourceDisplayView(resources, self.difficulty, selected_category)
                await resource_view.send_resources(interaction)
                print("No se encontraron subcategorías, mostrando recursos directamente.")
            return False # No continuar con otros botones en esta interacción

        return True # Permitir que otros botones se procesen


class DifficultySelectionView(discord.ui.View):
    """
    Vista para seleccionar la dificultad de los recursos.
    """
    def __init__(self, bot):
        super().__init__(timeout=180) # 3 minutos de timeout
        self.bot = bot
        self.message = None # Para almacenar el mensaje

        self._add_difficulty_buttons()

    async def on_timeout(self):
        """
        Se ejecuta cuando el tiempo de espera de la vista ha expirado.
        Deshabilita todos los botones.
        """
        for item in self.children:
            item.disabled = True
        if self.message:
            try:
                # No eliminar el mensaje, solo deshabilitar los botones
                await self.message.edit(content="La interacción de selección de dificultad ha expirado.", view=self)
            except discord.NotFound:
                print("Mensaje de DifficultySelectionView no encontrado al intentar editar en timeout.")
            except Exception as e:
                print(f"Error al editar mensaje de DifficultySelectionView en timeout: {e}")

    def _add_difficulty_buttons(self):
        """Añade botones para cada dificultad disponible."""
        if not db_manager.connect():
            print("Error: No se pudo conectar a la base de datos para obtener dificultades. Asegúrate de que la DB esté corriendo y las credenciales sean correctas.")
            self.add_item(discord.ui.Button(label="Error de DB", style=discord.ButtonStyle.red, disabled=True))
            return

        difficulties = db_manager.get_distinct_difficulties()
        print(f"Dificultades obtenidas de la DB: {difficulties}") # DEBUG: Para ver qué devuelve la DB
        
        if not difficulties:
            self.add_item(discord.ui.Button(label="No hay dificultades disponibles", style=discord.ButtonStyle.grey, disabled=True))
            return

        for difficulty in difficulties:
            # Discord tiene un límite de 25 botones por vista
            if len(self.children) < 25:
                self.add_item(discord.ui.Button(label=difficulty.title(), style=discord.ButtonStyle.primary, custom_id=f"diff_{difficulty}"))
            else:
                break # Evitar añadir más de 25 botones

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """ Verifica que solo el usuario que inició la interacción pueda usar los botones.
            La lógica para los botones de dificultad se maneja aquí dinámicamente.
        """
        if interaction.data and interaction.data.get("custom_id", "").startswith("diff_"):
            selected_difficulty = interaction.data["custom_id"].replace("diff_", "")
            await interaction.response.defer() # Deferir la respuesta para dar tiempo a la DB
            
            # Deshabilitar los botones de esta vista
            for item in self.children:
                item.disabled = True
            await interaction.message.edit(content=f"Has seleccionado la dificultad: **{selected_difficulty.title()}**.", view=self)

            # Crear y enviar la siguiente vista de selección de categoría
            category_view = CategorySelectionView(self.bot, selected_difficulty)
            await interaction.followup.send("Por favor, selecciona una categoría:", view=category_view)
            category_view.message = interaction.message # Asignar el mensaje para timeout
            return False # No continuar con otros botones en esta interacción

        return True # Permitir que otros botones se procesen


# Nueva clase de vista para la selección de contacto humano
class HumanSelectionView(discord.ui.View):
    """
    Vista para seleccionar a la persona de contacto (Valery o Belu).
    """
    def __init__(self, bot, original_user_id: int):
        super().__init__(timeout=180) # 3 minutos para que el usuario seleccione
        self.bot = bot
        self.original_user_id = original_user_id
        self.selected_human_id = None
        self.message = None # Para almacenar el mensaje original de esta vista

    async def on_timeout(self):
        """
        Se ejecuta cuando el tiempo de espera de la vista ha expirado.
        Deshabilita todos los botones.
        """
        for item in self.children:
            item.disabled = True
        if self.message:
            try:
                await self.message.edit(content="La selección de contacto ha expirado. Puedes usar `&iniciar` para intentarlo de nuevo.", view=self)
            except discord.NotFound:
                print("Mensaje de HumanSelectionView no encontrado al intentar editar en timeout.")
            except Exception as e:
                print(f"Error al editar mensaje de HumanSelectionView en timeout: {e}")

    @discord.ui.button(label="Valery", style=discord.ButtonStyle.secondary, custom_id="select_valery", emoji="👩‍💼")
    async def valery_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Maneja la selección del contacto Valery.
        """
        if interaction.user.id != self.original_user_id:
            await interaction.response.send_message("Solo la persona que inició la conversación puede seleccionar un contacto.", ephemeral=True)
            return

        await self._select_human(interaction, config.VALERY_USER_ID)

    @discord.ui.button(label="Belu", style=discord.ButtonStyle.secondary, custom_id="select_belu", emoji="👩‍💼")
    async def belu_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Maneja la selección del contacto Belu.
        """
        if interaction.user.id != self.original_user_id:
            await interaction.response.send_message("Solo la persona que inició la conversación puede seleccionar un contacto.", ephemeral=True)
            return

        await self._select_human(interaction, config.BELU_USER_ID)

    async def _select_human(self, interaction: discord.Interaction, human_id: int):
        """
        Lógica común para la selección de un contacto humano.
        """
        await interaction.response.defer()

        # Deshabilitar todos los botones de esta vista
        for item in self.children:
            item.disabled = True
        await interaction.message.edit(content=interaction.message.content + f"\n\nHas seleccionado a: <@{human_id}>", view=self)

        self.selected_human_id = human_id
        # Iniciar el estado de la conversación con la primera pregunta
        config.user_conversations[self.original_user_id]['state'] = 1
        config.user_conversations[self.original_user_id]['selected_human'] = self.selected_human_id

        await interaction.followup.send(
            "¡Perfecto! Para poder ayudarte mejor, por favor, responde las preguntas:\n\n"
            "**1. Describe el problema o dificultad que encontraste. Sé específico y da todos los detalles necesarios para que podamos ayudarte mejor.**",
            ephemeral=False
        )


class MainMenuView(discord.ui.View):
    """
    Vista del menú principal del bot, presentando opciones iniciales con botones.
    """
    def __init__(self, bot):
        super().__init__(timeout=180) # 3 minutos de timeout para la interacción
        self.bot = bot
        self.message = None # Para almacenar el mensaje

    async def on_timeout(self):
        """
        Se ejecuta cuando el tiempo de espera de la vista ha expirado.
        Deshabilita todos los botones.
        """
        for item in self.children:
            item.disabled = True
        if self.message:
            try:
                # No eliminar el mensaje, solo deshabilitar los botones
                await self.message.edit(content="La interacción ha expirado. Puedes usar `&iniciar` para mostrarlo de nuevo.", view=self)
            except discord.NotFound:
                print("Mensaje de MainMenuView no encontrado al intentar editar en timeout.")
            except Exception as e:
                print(f"Error al editar mensaje de MainMenuView en timeout: {e}")

    
    @discord.ui.button(label="Ayuda Técnica", style=discord.ButtonStyle.primary, custom_id="technical_help", emoji="🛠️")
    async def technical_help_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Maneja la interacción cuando se hace clic en el botón 'Ayuda Técnica'.
        """
        # 1. Deferir la interacción inmediatamente para evitar el error "Unknown interaction"
        await interaction.response.defer() 

        # 2. Deshabilita los botones del menú principal para esta interacción
        for item in self.children:
            item.disabled = True
        await interaction.message.edit(content="Has seleccionado 'Ayuda Técnica'", view=self) # Actualiza el mensaje original con los botones deshabilitados
        
    

    @discord.ui.button(label="Necesito un Recurso", style=discord.ButtonStyle.success, custom_id="request_resource", emoji="📚")
    async def request_resource_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Maneja la interacción cuando se hace clic en el botón 'Necesito un Recurso'.
        Inicia el flujo de selección de recursos en el mismo canal.
        """
        # Deferir la interacción inmediatamente
        await interaction.response.defer()

        # Deshabilita los botones del menú principal para esta interacción
        for item in self.children:
            item.disabled = True
        await interaction.message.edit(content="Has seleccionado 'Necesito un Recurso'. Iniciando búsqueda...", view=self)

        # Crear y enviar la vista de selección de dificultad en el mismo canal
        difficulty_view = DifficultySelectionView(self.bot)
        # El mensaje se envía a través de `followup` ya que la interacción ya fue diferida
        difficulty_view.message = await interaction.followup.send("Por favor, selecciona la dificultad del recurso:", view=difficulty_view)


    @discord.ui.button(label="Consultores", style=discord.ButtonStyle.danger, custom_id="human_contact", emoji="🙋")
    async def human_contact_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Maneja la interacción cuando se hace clic en el botón 'Hablar con un Humano'.
        Ahora, en lugar de iniciar preguntas, muestra los botones de selección de persona.
        """
        # 1. Deferir la interacción inmediatamente
        await interaction.response.defer()

        # 2. Deshabilita los botones del menú principal para esta interacción
        for item in self.children:
            item.disabled = True
        await interaction.message.edit(content="Has seleccionado 'Consultores'. ¿Con quién te gustaría hablar?", view=self)

        user_id = interaction.user.id
        if user_id in config.user_conversations and config.user_conversations[user_id]['state'] != 0:
            await interaction.followup.send("Ya tienes una conversación en curso para contactar a un humano. Por favor, completa esa conversación o espera.", ephemeral=True)
            return

        # 3. Inicializa el estado de la conversación (state 0) y envía la nueva vista de selección
        config.user_conversations[user_id] = {'state': 0, 'answers': [], 'channel_id': None, 'selected_human': None}
        human_selection_view = HumanSelectionView(self.bot, user_id)
        # Es crucial asignar el mensaje a la vista para que el on_timeout pueda editarlo
        human_selection_view.message = await interaction.followup.send("Por favor, selecciona con quién quieres hablar:", view=human_selection_view)

# Este archivo no necesita una función `setup` porque solo contiene clases de vista,
# que serán instanciadas y utilizadas por los cogs o comandos del bot.
