from typing import Dict, Callable, Protocol, runtime_checkable, Any


@runtime_checkable
class ObservadorAsignacion(Protocol):
    """
    Observer Pattern: Interface para observadores del proceso de asignación.
    Permite notificar el progreso sin acoplar el motor a la UI.
    
    Uso:
        class MiObservador:
            def on_inicio_asignacion(self, total_carreras, total_postulantes): ...
            def on_grupo_procesado(self, grupo, asignados, restantes): ...
            def on_asignacion_completada(self, total_asignados, estadisticas): ...
            def on_error(self, mensaje): ...
    """
    
    def on_inicio_asignacion(self, total_carreras: int, total_postulantes: int) -> None:
        """Notifica el inicio del proceso de asignación"""
        ...
    
    def on_grupo_procesado(self, grupo: Any, asignados: int, restantes: int) -> None:
        """Notifica que se procesó un grupo de asignación"""
        ...
    
    def on_asignacion_completada(self, total_asignados: int, estadisticas: Dict) -> None:
        """Notifica que la asignación se completó"""
        ...
    
    def on_error(self, mensaje: str) -> None:
        """Notifica un error en el proceso"""
        ...


class ObservadorCallback(ObservadorAsignacion):
    """
    Implementación de Observer que usa callbacks.
    Útil para integración con interfaces gráficas (Tkinter, etc.)
    
    Ejemplo de uso:
        def mi_callback(evento, datos):
            if evento == "inicio":
                label.config(text=f"Procesando {datos['postulantes']} postulantes...")
            elif evento == "completado":
                messagebox.showinfo("Éxito", f"Asignados: {datos['asignados']}")
        
        observador = ObservadorCallback(mi_callback)
        motor.agregar_observador(observador)
    """
    
    def __init__(self, callback: Callable[[str, Dict], None] = None):
        """
        Args:
            callback: Función que recibe (evento: str, datos: Dict)
                     eventos: "inicio", "grupo", "completado", "error"
        """
        self._callback = callback
    
    def _notificar(self, evento: str, datos: Dict) -> None:
        """Método interno para notificar al callback"""
        if self._callback:
            try:
                self._callback(evento, datos)
            except Exception as e:
                print(f"Error en callback del observador: {e}")
    
    def on_inicio_asignacion(self, total_carreras: int, total_postulantes: int) -> None:
        self._notificar("inicio", {
            "carreras": total_carreras, 
            "postulantes": total_postulantes
        })
    
    def on_grupo_procesado(self, grupo, asignados: int, restantes: int) -> None:
        nombre_grupo = grupo.name if hasattr(grupo, 'name') else str(grupo)
        self._notificar("grupo", {
            "grupo": nombre_grupo, 
            "asignados": asignados, 
            "restantes": restantes
        })
    
    def on_asignacion_completada(self, total_asignados: int, estadisticas: Dict) -> None:
        self._notificar("completado", {
            "asignados": total_asignados, 
            "estadisticas": estadisticas
        })
    
    def on_error(self, mensaje: str) -> None:
        self._notificar("error", {"mensaje": mensaje})
