"""
Interfaz principal de usuario con NiceGUI.
Diseño profesional y moderno con estilos personalizados.
PARTE 1 DE 2 - CORREGIDO
"""

from nicegui import ui
from database.db_handler import DatabaseHandler
from models.robot import Robot, EstadoRobot, ModoOperacion
from models.receta import Receta, Ingrediente
from models.tarea import (
    crear_picar, crear_trocear, crear_amasar,
    crear_sofreir, crear_hervir, crear_vapor
)
from ui.components import (
    StatusIndicator, ProgressBar, RecipeCard,
    ParameterPanel, TaskInfoCard, RecipeStepIndicator
)
from ui.custom_styles import inject_custom_styles
from utils.exceptions import RobotApagadoError, TareaInvalidaError
import asyncio
from typing import Optional


class MainInterface:
    """Interfaz principal de la aplicación."""
    
    def __init__(self, db: DatabaseHandler):
        self.db = db
        self.robot = Robot()
        
        # Referencias a componentes UI
        self.status_indicator: Optional[StatusIndicator] = None
        self.progress_bar: Optional[ProgressBar] = None
        self.parameter_panel: Optional[ParameterPanel] = None
        self.task_info: Optional[TaskInfoCard] = None
        self.step_indicator: Optional[RecipeStepIndicator] = None
        
        # Registrar callbacks del robot
        self.robot.registrar_callback_estado(self._on_estado_changed)
        self.robot.registrar_callback_progreso(self._on_progreso_changed)
    
    def create_ui(self):
        """Crea la interfaz de usuario completa."""
        # Inyectar estilos personalizados
        inject_custom_styles()
        
        # Configuración de colores
        ui.colors(primary='#667eea', secondary='#764ba2', accent='#f093fb', 
                  positive='#00f2fe', negative='#f5576c', info='#4facfe', 
                  warning='#fee140')
        
        # Header con gradiente
        with ui.header(elevated=True).classes('glass-dark'):
            with ui.row().classes('w-full items-center justify-between px-6'):
                with ui.row().classes('items-center gap-4 fade-in'):
                    ui.icon('restaurant', size='xl').classes('text-white')
                    with ui.column().classes('gap-0'):
                        ui.label('Robot de Cocina').classes('text-h4 text-white font-bold')
                        ui.label('Sistema Profesional de Control').classes('text-caption text-white opacity-80')
                
                with ui.row().classes('items-center gap-3 fade-in'):
                    self.modo_badge = ui.badge('Manual', color='white', text_color='primary').classes('text-sm px-4 py-2 font-bold')
                    ui.badge('v1.0', color='accent').classes('text-xs')
        
        # Contenido principal con fondo degradado
        ui.add_head_html('''
            <style>
                body { 
                    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                    min-height: 100vh;
                }
            </style>
        ''')
        
        with ui.column().classes('w-full p-6 gap-6'):
            # Panel de estado y control
            with ui.row().classes('w-full gap-6'):
                # Columna izquierda: Control (40%)
                with ui.column().classes('w-2/5 gap-6'):
                    self._create_control_panel()
                    self._create_manual_control_panel()
                
                # Columna derecha: Estado y parámetros (60%)
                with ui.column().classes('w-3/5 gap-6'):
                    self._create_status_panel()
                    self._create_parameters_panel()
            
            # Separador elegante
            ui.separator().classes('my-4')
            
            # Tabs con estilo mejorado
            with ui.tabs().classes('w-full shadow-lg') as tabs:
                ui.tab('manual', label='🎮 Modo Manual').classes('text-lg font-semibold')
                ui.tab('guiada', label='📖 Cocina Guiada').classes('text-lg font-semibold')
                ui.tab('recetas', label='📚 Mis Recetas').classes('text-lg font-semibold')
            
            with ui.tab_panels(tabs, value='manual').classes('w-full'):
                with ui.tab_panel('manual').classes('fade-in'):
                    self._create_manual_operations_panel()
                
                with ui.tab_panel('guiada').classes('fade-in'):
                    self._create_guided_cooking_panel()
                
                with ui.tab_panel('recetas').classes('fade-in'):
                    self._create_recipe_management_panel()
        
        # Footer profesional
        with ui.footer().classes('glass-dark'):
            with ui.row().classes('w-full items-center justify-between px-6 py-3'):
                with ui.row().classes('items-center gap-2'):
                    ui.icon('code', size='sm').classes('text-white')
                    ui.label('Desarrollo Orientado a Objetos').classes('text-sm text-white font-medium')
                
                with ui.row().classes('items-center gap-4 text-xs text-white opacity-80'):
                    ui.label('Abstracción')
                    ui.label('•')
                    ui.label('Herencia')
                    ui.label('•')
                    ui.label('Polimorfismo')
                    ui.label('•')
                    ui.label('Encapsulamiento')
    
    def _create_control_panel(self):
        """Crea el panel de control principal."""
        with ui.card().classes('w-full hover-lift fade-in'):
            with ui.row().classes('items-center gap-3 mb-4'):
                ui.icon('settings', size='md').classes('text-primary')
                ui.label('Control Principal').classes('text-h6 font-bold text-gradient')
            
            with ui.grid(columns=2).classes('w-full gap-3'):
                # Botón Encender
                self.btn_encender = ui.button(
                    'Encender',
                    icon='power_settings_new',
                    on_click=self._encender_robot
                ).classes('btn-gradient-success')
                
                # Botón Apagar
                self.btn_apagar = ui.button(
                    'Apagar',
                    icon='power_off',
                    color='red',
                    on_click=self._apagar_robot
                )
                self.btn_apagar.props('disabled')
                
                # Botón Pausar
                self.btn_pausar = ui.button(
                    'Pausar',
                    icon='pause',
                    color='orange',
                    on_click=self._pausar_robot
                )
                self.btn_pausar.props('disabled')
                
                # Botón Reanudar
                self.btn_reanudar = ui.button(
                    'Reanudar',
                    icon='play_arrow',
                    on_click=self._reanudar_robot
                ).classes('btn-gradient-primary')
                self.btn_reanudar.props('disabled')
            
            ui.separator().classes('my-3')
            
            # Botón Parada de Emergencia
            self.btn_emergencia = ui.button(
                '⚠️ PARADA DE EMERGENCIA',
                color='negative',
                on_click=self._parada_emergencia
            ).classes('w-full emergency-btn').props('size=lg')
    
    def _create_manual_control_panel(self):
        """Panel de control de modo."""
        with ui.card().classes('w-full hover-lift fade-in'):
            with ui.row().classes('items-center gap-3 mb-3'):
                ui.icon('tune', size='md').classes('text-secondary')
                ui.label('Modo de Operación').classes('text-subtitle1 font-bold')
            
            with ui.grid(columns=2).classes('w-full gap-3'):
                self.btn_modo_manual = ui.button(
                    'Manual',
                    icon='touch_app',
                    on_click=lambda: self._cambiar_modo(ModoOperacion.MANUAL)
                ).classes('btn-gradient-primary')
                
                self.btn_modo_guiada = ui.button(
                    'Cocina Guiada',
                    icon='menu_book',
                    color='grey',
                    on_click=lambda: self._cambiar_modo(ModoOperacion.COCINA_GUIADA)
                )
    
    def _create_status_panel(self):
        """Crea el panel de estado del robot."""
        with ui.column().classes('w-full gap-4'):
            # Grid de información principal
            with ui.grid(columns=2).classes('w-full gap-4 fade-in'):
                # Indicador de estado
                self.status_indicator = StatusIndicator(self.robot.estado)
                
                # Información de tarea
                self.task_info = TaskInfoCard()
            
            # Indicador de pasos (para recetas)
            self.step_indicator = RecipeStepIndicator()
            
            # Barra de progreso
            self.progress_bar = ProgressBar("Progreso de Tarea")
    
    def _create_parameters_panel(self):
        """Crea el panel de parámetros."""
        self.parameter_panel = ParameterPanel()
    
    def _create_manual_operations_panel(self):
        """Panel de operaciones manuales."""
        with ui.column().classes('w-full gap-4'):
            # Título con icono
            with ui.row().classes('items-center gap-3 mb-2'):
                ui.icon('construction', size='lg').classes('text-primary')
                with ui.column().classes('gap-1'):
                    ui.label('Operaciones Manuales').classes('text-h5 font-bold text-gradient')
                    ui.label('Seleccione una operación para ejecutar de forma individual').classes('text-body2 text-grey-7')
            
            # Grid de operaciones
            with ui.grid(columns=3).classes('w-full gap-5'):
                # Operaciones de corte
                self._create_operation_card('picar', 'content_cut', 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', 'Picar', 'Corte fino y preciso', '⚡')
                self._create_operation_card('trocear', 'call_split', 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)', 'Trocear', 'Cubos medianos', '🔪')
                self._create_operation_card('amasar', 'sync', 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)', 'Amasar', 'Movimiento rotatorio', '🌀')
                
                # Operaciones de temperatura
                self._create_operation_card('sofreir', 'local_fire_department', 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)', 'Sofreír', 'Temperatura 120°C', '🔥')
                self._create_operation_card('hervir', 'whatshot', 'linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%)', 'Hervir', 'Temperatura 100°C', '💧')
                self._create_operation_card('vapor', 'cloud', 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)', 'Vapor', 'Cocción saludable', '☁️')
    
    def _create_operation_card(self, operation_id, icon, gradient, title, subtitle, emoji):
        """Crea una tarjeta de operación con estilo profesional."""
        with ui.card().classes('operation-card hover-lift cursor-pointer').style(f'background: {gradient}; color: white; min-height: 180px;'):
            with ui.column().classes('items-center justify-center h-full p-6 gap-3').on('click', lambda op=operation_id: asyncio.create_task(self._ejecutar_operacion_manual(op))):
                ui.label(emoji).classes('text-5xl')
                ui.icon(icon, size='xl').classes('text-white')
                ui.label(title).classes('text-h6 font-bold text-white')
                ui.label(subtitle).classes('text-caption text-white opacity-90')


    def _create_guided_cooking_panel(self):
        """Panel de cocina guiada con recetas."""
        with ui.column().classes('w-full gap-4'):
            # Título
            with ui.row().classes('items-center gap-3 mb-2'):
                ui.icon('restaurant_menu', size='lg').classes('text-primary')
                with ui.column().classes('gap-1'):
                    ui.label('Cocina Guiada').classes('text-h5 font-bold text-gradient')
                    ui.label('Seleccione una receta para cocinar paso a paso de forma automática').classes('text-body2 text-grey-7')
            
            # Contenedor de recetas
            self.recipe_container = ui.column().classes('w-full gap-4')
            self._cargar_recetas_en_panel()
    
    def _cargar_recetas_en_panel(self):
        """Carga las recetas en el panel de cocina guiada."""
        self.recipe_container.clear()
        
        with self.recipe_container:
            recetas = self.db.get_all_recipes()
            
            if not recetas:
                with ui.card().classes('w-full p-12 text-center glass'):
                    ui.icon('restaurant_menu', size='xl').classes('text-grey-4 mb-4')
                    ui.label('No hay recetas disponibles').classes('text-h6 text-grey-7')
                return
            
            with ui.grid(columns=2).classes('w-full gap-5'):
                for receta in recetas:
                    RecipeCard(receta, lambda r=receta: self._ejecutar_receta(r), None)
    
    def _create_recipe_management_panel(self):
        """Panel de gestión de recetas."""
        with ui.column().classes('w-full gap-4'):
            # Header
            with ui.row().classes('w-full items-center justify-between mb-4'):
                with ui.row().classes('items-center gap-3'):
                    ui.icon('library_books', size='lg').classes('text-primary')
                    with ui.column().classes('gap-1'):
                        ui.label('Gestión de Recetas').classes('text-h5 font-bold text-gradient')
                        ui.label('Crea, edita y organiza tus recetas personalizadas').classes('text-body2 text-grey-7')
                
                with ui.row().classes('gap-3'):
                    ui.button(
                        'Nueva Receta',
                        icon='add_circle',
                        on_click=self._mostrar_dialogo_nueva_receta
                    ).classes('btn-gradient-success')
                    
                    ui.button(
                        'Factory Reset',
                        icon='restore',
                        color='negative',
                        on_click=self._factory_reset
                    ).props('outline')
            
            # Contenedor de recetas
            self.recipe_management_container = ui.column().classes('w-full gap-4')
            self._cargar_recetas_gestion()
    
    def _cargar_recetas_gestion(self):
        """Carga las recetas en el panel de gestión."""
        self.recipe_management_container.clear()
        
        with self.recipe_management_container:
            recetas = self.db.get_all_recipes()
            
            if not recetas:
                with ui.card().classes('w-full p-12 text-center glass'):
                    ui.icon('restaurant_menu', size='xl').classes('text-grey-4 mb-4')
                    ui.label('No hay recetas disponibles').classes('text-h6 text-grey-7 mb-2')
                    ui.label('Crea tu primera receta personalizada usando el botón "Nueva Receta"').classes('text-caption text-grey-6')
                return
            
            # Separar por tipo
            recetas_fabrica = [r for r in recetas if r.es_fabrica]
            recetas_usuario = [r for r in recetas if not r.es_fabrica]
            
            if recetas_fabrica:
                with ui.row().classes('items-center gap-2 mb-3 mt-4'):
                    ui.icon('factory', size='md').classes('text-blue-6')
                    ui.label('Recetas de Fábrica').classes('text-h6 font-bold')
                    ui.badge(f'{len(recetas_fabrica)}', color='blue')
                
                with ui.grid(columns=2).classes('w-full gap-5'):
                    for receta in recetas_fabrica:
                        RecipeCard(receta, lambda r=receta: self._ver_detalle_receta(r), None)
            
            if recetas_usuario:
                with ui.row().classes('items-center gap-2 mb-3 mt-6'):
                    ui.icon('person', size='md').classes('text-purple-6')
                    ui.label('Mis Recetas Personalizadas').classes('text-h6 font-bold')
                    ui.badge(f'{len(recetas_usuario)}', color='purple')
                
                with ui.grid(columns=2).classes('w-full gap-5'):
                    for receta in recetas_usuario:
                        RecipeCard(receta, lambda r=receta: self._ver_detalle_receta(r), lambda r=receta: self._eliminar_receta(r))
    
    def _encender_robot(self):
        if self.robot.encender():
            ui.notify('✓ Robot encendido correctamente', type='positive', icon='check_circle', position='top')
            self._actualizar_botones()
    
    def _apagar_robot(self):
        try:
            if self.robot.apagar():
                ui.notify('✓ Robot apagado correctamente', type='positive', icon='power_off', position='top')
                self._actualizar_botones()
        except TareaInvalidaError as e:
            ui.notify(str(e), type='negative', icon='error', position='top')
    
    def _pausar_robot(self):
        if self.robot.pausar():
            ui.notify('⏸️ Operación pausada', type='info', icon='pause', position='top')
            self._actualizar_botones()
    
    def _reanudar_robot(self):
        if self.robot.reanudar():
            ui.notify('▶️ Operación reanudada', type='info', icon='play_arrow', position='top')
            self._actualizar_botones()
    
    def _parada_emergencia(self):
        self.robot.parada_emergencia()
        ui.notify('⚠️ PARADA DE EMERGENCIA ACTIVADA', type='negative', icon='warning', position='center', timeout=3000)
        self._actualizar_botones()
    
    def _cambiar_modo(self, modo: ModoOperacion):
        try:
            if self.robot.cambiar_modo(modo):
                self.modo_badge.text = modo.value.replace('_', ' ').title()
                if modo == ModoOperacion.MANUAL:
                    self.btn_modo_manual.props(remove='color').classes('btn-gradient-primary')
                    self.btn_modo_guiada.props('color=grey').classes(remove='btn-gradient-primary')
                else:
                    self.btn_modo_manual.props('color=grey').classes(remove='btn-gradient-primary')
                    self.btn_modo_guiada.props(remove='color').classes('btn-gradient-primary')
                ui.notify(f'🔄 Modo: {modo.value.replace("_", " ").title()}', type='info', icon='swap_horiz', position='top')
        except TareaInvalidaError as e:
            ui.notify(str(e), type='negative', icon='error', position='top')
    
    async def _ejecutar_operacion_manual(self, tipo: str):
        try:
            tarea_map = {
                'picar': crear_picar(),
                'trocear': crear_trocear(),
                'amasar': crear_amasar(),
                'sofreir': crear_sofreir(),
                'hervir': crear_hervir(),
                'vapor': crear_vapor(),
            }
            
            tarea = tarea_map.get(tipo)
            if not tarea:
                ui.notify('Operación no reconocida', type='negative', position='top')
                return
            
            self.task_info.actualizar(tarea.nombre, tarea.descripcion)
            self._actualizar_botones()
            
            resultado = await self.robot.ejecutar_tarea(tarea)
            
            if resultado:
                ui.notify(f'✅ {tarea.nombre} completado exitosamente', type='positive', icon='check_circle', position='top')
            else:
                ui.notify(f'⏹️ {tarea.nombre} detenido', type='warning', icon='stop', position='top')
            
            self.task_info.limpiar()
            self.progress_bar.reiniciar()
            self._actualizar_botones()
            
        except (RobotApagadoError, TareaInvalidaError) as e:
            ui.notify(str(e), type='negative', icon='error', position='top')
    
    def _ejecutar_receta(self, receta: Receta):
        with ui.dialog() as dialog, ui.card().classes('min-w-96 glass'):
            with ui.row().classes('items-center gap-3 mb-4'):
                ui.icon('restaurant', size='lg').classes('text-primary')
                ui.label(f'Iniciar: {receta.nombre}').classes('text-h6 font-bold')
            
            ui.separator()
            
            with ui.column().classes('gap-3 my-4'):
                ui.label(receta.descripcion).classes('text-body2')
                with ui.grid(columns=3).classes('w-full gap-2 my-2'):
                    with ui.row().classes('items-center gap-1'):
                        ui.icon('schedule', size='sm').classes('text-primary')
                        ui.label(receta.tiempo_str).classes('text-body2 font-medium')
                    with ui.row().classes('items-center gap-1'):
                        ui.icon('people', size='sm').classes('text-primary')
                        ui.label(f'{receta.porciones} porciones').classes('text-body2 font-medium')
                    with ui.row().classes('items-center gap-1'):
                        ui.icon('bar_chart', size='sm').classes('text-primary')
                        ui.label(receta.dificultad).classes('text-body2 font-medium')
            
            with ui.expansion('Ver ingredientes', icon='shopping_basket').classes('w-full'):
                for ing in receta.ingredientes:
                    with ui.row().classes('items-center gap-2'):
                        ui.icon('check_circle', size='sm').classes('text-positive')
                        ui.label(f'{ing}').classes('text-body2')
            
            with ui.row().classes('w-full justify-end gap-3 mt-6'):
                ui.button('Cancelar', on_click=dialog.close).props('flat')
                ui.button('Iniciar Receta', icon='play_circle', 
                         on_click=lambda r=receta: (dialog.close(), asyncio.create_task(self._iniciar_receta(r)))
                ).classes('btn-gradient-success')
        
        dialog.open()
    
    async def _iniciar_receta(self, receta: Receta):
        try:
            self.step_indicator.establecer_total_pasos(receta.num_pasos)
            self._actualizar_botones()
            
            resultado = await self.robot.ejecutar_receta(receta)
            
            if resultado:
                ui.notify(f'🎉 ¡Receta "{receta.nombre}" completada con éxito!', 
                         type='positive', icon='celebration', position='center', timeout=5000)
            else:
                ui.notify(f'⏹️ Receta "{receta.nombre}" detenida', 
                         type='warning', icon='stop', position='top')
            
            self.step_indicator.limpiar()
            self.task_info.limpiar()
            self.progress_bar.reiniciar()
            self._actualizar_botones()
            
        except (RobotApagadoError, TareaInvalidaError) as e:
            ui.notify(str(e), type='negative', icon='error', position='top')
            self._actualizar_botones()
    
    def _mostrar_dialogo_nueva_receta(self):
        ui.notify('Función de crear recetas próximamente', type='info', position='top')
    
    def _ver_detalle_receta(self, receta: Receta):
        with ui.dialog() as dialog, ui.card().classes('min-w-[500px] max-h-[80vh] overflow-auto glass'):
            with ui.row().classes('items-center justify-between w-full mb-4'):
                with ui.row().classes('items-center gap-2'):
                    ui.icon('restaurant_menu', size='lg').classes('text-primary')
                    ui.label(receta.nombre).classes('text-h5 font-bold')
                if receta.es_fabrica:
                    ui.badge('Fábrica', color='blue')
            
            ui.label(receta.descripcion).classes('text-body1 mb-4')
            
            with ui.grid(columns=3).classes('w-full gap-4 mb-4'):
                with ui.card().classes('p-3'):
                    ui.icon('schedule', size='md').classes('text-grey-6')
                    ui.label(receta.tiempo_str).classes('text-h6 font-bold')
                    ui.label('Tiempo').classes('text-caption text-grey-6')
                
                with ui.card().classes('p-3'):
                    ui.icon('people', size='md').classes('text-grey-6')
                    ui.label(f'{receta.porciones}').classes('text-h6 font-bold')
                    ui.label('Porciones').classes('text-caption text-grey-6')
                
                with ui.card().classes('p-3'):
                    ui.icon('bar_chart', size='md').classes('text-grey-6')
                    ui.label(receta.dificultad).classes('text-h6 font-bold')
                    ui.label('Dificultad').classes('text-caption text-grey-6')
            
            ui.separator()
            
            ui.label('Ingredientes').classes('text-h6 font-bold mt-4 mb-2')
            for ing in receta.ingredientes:
                with ui.row().classes('items-center gap-2'):
                    ui.icon('check_circle', size='sm').classes('text-green-6')
                    ui.label(str(ing)).classes('text-body2')
            
            ui.separator().classes('my-4')
            
            ui.label('Pasos').classes('text-h6 font-bold mb-2')
            for i, paso in enumerate(receta.pasos, 1):
                with ui.card().classes('w-full mb-2'):
                    ui.label(f'Paso {i}').classes('text-subtitle2 font-bold text-primary')
                    ui.label(f'{paso["operacion"].title()} - {paso["duracion"]}s').classes('text-body2')
                    if paso.get('descripcion'):
                        ui.label(paso['descripcion']).classes('text-caption text-grey-7')
            
            ui.button('Cerrar', on_click=dialog.close).classes('w-full mt-4')
        
        dialog.open()
    
    def _eliminar_receta(self, receta: Receta):
        try:
            if self.db.delete_user_recipe(receta.id):
                ui.notify(f'🗑️ Receta "{receta.nombre}" eliminada', type='positive', icon='delete', position='top')
                self._cargar_recetas_gestion()
                self._cargar_recetas_en_panel()
            else:
                ui.notify('No se pudo eliminar la receta', type='negative', position='top')
        except Exception as e:
            ui.notify(f'Error: {str(e)}', type='negative', position='top')
    
    def _factory_reset(self):
        with ui.dialog() as dialog, ui.card().classes('glass'):
            with ui.row().classes('items-center gap-3 mb-4'):
                ui.icon('warning', size='lg').classes('text-negative')
                ui.label('⚠️ Factory Reset').classes('text-h6 font-bold text-negative')
            
            ui.label('Esta acción eliminará TODAS las recetas de usuario creadas.').classes('text-body2 mt-2')
            ui.label('Las recetas de fábrica se mantendrán intactas.').classes('text-body2 text-grey-7')
            
            with ui.row().classes('w-full justify-end gap-3 mt-6'):
                ui.button('Cancelar', on_click=dialog.close).props('flat')
                ui.button('Confirmar Reset', color='negative', on_click=lambda: self._confirmar_factory_reset(dialog))
        
        dialog.open()
    
    def _confirmar_factory_reset(self, dialog):
        try:
            count = self.db.factory_reset()
            ui.notify(f'✓ Factory reset completado. {count} recetas eliminadas.', type='positive', icon='restore', position='top')
            dialog.close()
            self._cargar_recetas_gestion()
            self._cargar_recetas_en_panel()
        except Exception as e:
            ui.notify(f'Error: {str(e)}', type='negative', position='top')
    
    def _on_estado_changed(self, nuevo_estado: EstadoRobot):
        if self.status_indicator:
            self.status_indicator.actualizar(nuevo_estado)
        
        ui.timer(0.1, lambda: self._actualizar_botones(), once=True)
        
        if self.parameter_panel:
            estado = self.robot.get_estado_completo()
            self.parameter_panel.actualizar(estado['temperatura'], estado['velocidad'])
        
        if self.step_indicator and self.robot.receta_actual:
            self.step_indicator.actualizar(self.robot.paso_actual, self.robot.receta_actual.nombre)
    
    def _on_progreso_changed(self, progreso: int):
        if self.progress_bar:
            tiempo_restante = 0
            if self.robot.tarea_actual:
                duracion = self.robot.tarea_actual.duracion
                tiempo_transcurrido = int((progreso / 100) * duracion)
                tiempo_restante = duracion - tiempo_transcurrido
            
            self.progress_bar.actualizar(progreso, tiempo_restante)
    
    def _actualizar_botones(self):
        estado = self.robot.estado
        
        if estado == EstadoRobot.APAGADO:
            self.btn_encender.props(remove='disabled')
            self.btn_apagar.props('disabled')
            self.btn_pausar.props('disabled')
            self.btn_reanudar.props('disabled')
        elif estado == EstadoRobot.ENCENDIDO:
            self.btn_encender.props('disabled')
            self.btn_apagar.props(remove='disabled')
            self.btn_pausar.props('disabled')
            self.btn_reanudar.props('disabled')
        elif estado == EstadoRobot.COCINANDO:
            self.btn_encender.props('disabled')
            self.btn_apagar.props('disabled')
            self.btn_pausar.props(remove='disabled')
            self.btn_reanudar.props('disabled')
        elif estado == EstadoRobot.PAUSADO:
            self.btn_encender.props('disabled')
            self.btn_apagar.props('disabled')
            self.btn_pausar.props('disabled')
            self.btn_reanudar.props(remove='disabled')