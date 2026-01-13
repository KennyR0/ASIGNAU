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


class ObservadorConsola(ObservadorAsignacion):
    """
    Implementación de Observer que imprime en consola.
    Útil para debugging y monitoreo en terminal.
    """
    
    def on_inicio_asignacion(self, total_carreras: int, total_postulantes: int) -> None:
        print(f"🚀 Iniciando asignación: {total_carreras} carreras, {total_postulantes} postulantes")
    
    def on_grupo_procesado(self, grupo, asignados: int, restantes: int) -> None:
        nombre_grupo = grupo.name if hasattr(grupo, 'name') else str(grupo)
        print(f"  ✓ {nombre_grupo}: {asignados} asignados, {restantes} cupos restantes")
    
    def on_asignacion_completada(self, total_asignados: int, estadisticas: Dict) -> None:
        print(f"✅ Asignación completada: {total_asignados} postulantes asignados")
        if estadisticas:
            print(f"   Estadísticas: {estadisticas.get('por_grupo', {})}")
    
    def on_error(self, mensaje: str) -> None:
        print(f"❌ Error: {mensaje}")


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


class ObservadorLog(ObservadorAsignacion):
    """
    Implementación de Observer que guarda logs en archivo.
    Útil para auditoría y seguimiento del proceso.
    """
    
    def __init__(self, archivo_log: str = "asignacion.log"):
        self._archivo = archivo_log
    
    def _escribir(self, mensaje: str) -> None:
        """Escribe un mensaje al archivo de log"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with open(self._archivo, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] {mensaje}\n")
        except Exception as e:
            print(f"Error escribiendo log: {e}")
    
    def on_inicio_asignacion(self, total_carreras: int, total_postulantes: int) -> None:
        self._escribir(f"INICIO - Carreras: {total_carreras}, Postulantes: {total_postulantes}")
    
    def on_grupo_procesado(self, grupo, asignados: int, restantes: int) -> None:
        nombre_grupo = grupo.name if hasattr(grupo, 'name') else str(grupo)
        self._escribir(f"GRUPO {nombre_grupo} - Asignados: {asignados}, Restantes: {restantes}")
    
    def on_asignacion_completada(self, total_asignados: int, estadisticas: Dict) -> None:
        self._escribir(f"COMPLETADO - Total asignados: {total_asignados}")
        if estadisticas:
            self._escribir(f"ESTADÍSTICAS: {estadisticas}")
    
    def on_error(self, mensaje: str) -> None:
        self._escribir(f"ERROR: {mensaje}")


class ObservadorMultiple(ObservadorAsignacion):
    """
    Composite Observer: Agrupa múltiples observadores.
    Permite notificar a varios observadores con una sola instancia.
    
    Ejemplo:
        obs_multiple = ObservadorMultiple([
            ObservadorConsola(),
            ObservadorLog("proceso.log"),
            ObservadorCallback(mi_callback)
        ])
        motor.agregar_observador(obs_multiple)
    """
    
    def __init__(self, observadores: list = None):
        self._observadores = observadores or []
    
    def agregar(self, observador: ObservadorAsignacion) -> None:
        """Agrega un observador a la lista"""
        if observador not in self._observadores:
            self._observadores.append(observador)
    
    def remover(self, observador: ObservadorAsignacion) -> None:
        """Remueve un observador de la lista"""
        if observador in self._observadores:
            self._observadores.remove(observador)
    
    def on_inicio_asignacion(self, total_carreras: int, total_postulantes: int) -> None:
        for obs in self._observadores:
            obs.on_inicio_asignacion(total_carreras, total_postulantes)
    
    def on_grupo_procesado(self, grupo, asignados: int, restantes: int) -> None:
        for obs in self._observadores:
            obs.on_grupo_procesado(grupo, asignados, restantes)
    
    def on_asignacion_completada(self, total_asignados: int, estadisticas: Dict) -> None:
        for obs in self._observadores:
            obs.on_asignacion_completada(total_asignados, estadisticas)
    
    def on_error(self, mensaje: str) -> None:
        for obs in self._observadores:
            obs.on_error(mensaje)
