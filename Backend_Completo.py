import pandas as pd
from abc import abstractmethod, ABC
from typing import Optional, Dict, Any, List, Tuple, Protocol, runtime_checkable
import os
from dataclasses import dataclass, field
from Asignacion import (MotorAsignacion, Reporte,
                        EstrategiaClasificacion, EstrategiaDesempate, EstrategiaSegmentacion,
                        ClasificacionSENESCYT, DesempateSENESCYT, SegmentacionPorcentual)
from PeriodoAsignacion import (PeriodoAsignacion, EstadoPeriodo, GestorPeriodos)


# INTERFACE PARA GESTIÓN DE PERIODOS (DIP)
@runtime_checkable
class IGestorPeriodos(Protocol):
    """Interface para gestión de periodos (ISP + DIP)"""
    def obtener_periodo_activo(self) -> Optional['PeriodoAsignacion']:
        ...
    def crear_periodo(self, codigo: str, nombre: str) -> Tuple[bool, str, Optional['PeriodoAsignacion']]:
        ...
    def listar_periodos(self) -> List[Dict]:
        ...


# PATRÓN ADAPTER - ESTRATEGIA DE BASE DE DATOS (Open/Closed Principle)
class Base_Dato(ABC):
    @abstractmethod
    def cargar_base(self):
        pass

    @abstractmethod
    def obtener_usuario(self, identificacion: str, contraseña: str):
        pass

class BD_ADMIN(Base_Dato):
    def cargar_base(self):
        excel = "Admin.xlsx"
        if os.path.exists(excel):
            base = pd.read_excel(excel, sheet_name=0, skiprows=1)
            return base
        return None

    def obtener_usuario(self, identificacion: str, contraseña: str):
        datos = self.cargar_base()
        if datos is None:
            return None
        
        usuario = datos[
            (datos["IDENTIFICACIÓN"].astype(str) == identificacion) &
            (datos["CONTRASEÑA"] == contraseña)
        ]
        
        if not usuario.empty:
            return usuario.iloc[0].to_dict()
        return None

class BD_USUARIO(Base_Dato):
    """Adapter para base de datos de usuarios/postulantes (Dependency Inversion)"""
    
    def __init__(self, gestor_periodos: IGestorPeriodos = None):
        # DIP: Dependencia inyectada, no creada internamente
        self._gestor_periodos = gestor_periodos
    
    @property
    def gestor_periodos(self) -> IGestorPeriodos:
        """Lazy initialization con inyección de dependencias"""
        if self._gestor_periodos is None:
            self._gestor_periodos = GestorPeriodos()
        return self._gestor_periodos
    
    def cargar_base(self):
        # Intentar cargar desde el periodo activo primero
        periodo = self.gestor_periodos.obtener_periodo_activo()
        
        if periodo and periodo.archivo_postulantes:
            excel = periodo.archivo_postulantes
            if os.path.exists(excel):
                base = pd.read_excel(excel, sheet_name=5, skiprows=1)
                return base
        
        # Si no hay periodo activo, buscar en el último periodo disponible
        periodos = PeriodoAsignacion.listar_periodos()
        for p in periodos:
            if p['estado'] != 'CERRADO':
                periodo_cargado = PeriodoAsignacion.cargar(p['codigo'])
                if periodo_cargado and periodo_cargado.archivo_postulantes:
                    excel = periodo_cargado.archivo_postulantes
                    if os.path.exists(excel):
                        base = pd.read_excel(excel, sheet_name=5, skiprows=1)
                        return base
        
        excel = "Postulantes.xlsx"
        if os.path.exists(excel):
            base = pd.read_excel(excel, sheet_name=5, skiprows=1)
            return base
        return None
        
    def obtener_usuario(self, identificacion: str, contraseña: str):
        datos = self.cargar_base()
        if datos is None:
            return None
        
        usuario = datos[
            (datos["IDENTIFICACIÓN"].astype(str) == identificacion) &
            (datos["CONTRASEÑA"] == contraseña)
        ]
        
        if not usuario.empty:
            return usuario.iloc[0].to_dict()
        return None

class BD_POSTULACIONES:
    """Maneja la base de datos de postulaciones"""
    
    @staticmethod
    def cargar_postulaciones():
        # Intentar cargar desde el periodo activo primero
        gestor = GestorPeriodos()
        periodo = gestor.obtener_periodo_activo()
        
        if periodo and periodo.archivo_postulantes:
            excel = periodo.archivo_postulantes
            if os.path.exists(excel):
                return pd.read_excel(excel, sheet_name=5, skiprows=1)
        
        # Fallback: archivo en la raíz
        excel = "Postulantes.xlsx"
        if os.path.exists(excel):
            return pd.read_excel(excel, sheet_name=5, skiprows=1)
        return None
    
    @staticmethod
    def cargar_oferta_academica():
        # Intentar cargar desde el periodo activo primero
        gestor = GestorPeriodos()
        periodo = gestor.obtener_periodo_activo()
        
        if periodo and periodo.archivo_oferta:
            excel = periodo.archivo_oferta
            if os.path.exists(excel):
                return pd.read_excel(excel, sheet_name=0, skiprows=1)
        
        # Fallback: archivo en la raíz
        excel = "Oferta_Academica.xlsx"
        if os.path.exists(excel):
            return pd.read_excel(excel, sheet_name=0, skiprows=1)
        return None
    
    @staticmethod
    def cargar_asignaciones():
        """Carga las asignaciones del periodo activo"""
        # Intentar cargar desde el periodo activo primero
        gestor = GestorPeriodos()
        periodo = gestor.obtener_periodo_activo()
        
        if periodo and periodo.archivo_asignaciones:
            excel = periodo.archivo_asignaciones
            if os.path.exists(excel):
                return pd.read_excel(excel)
        
        # Buscar en periodos disponibles
        periodos = PeriodoAsignacion.listar_periodos()
        for p in periodos:
            if p['estado'] in ['FINALIZADO', 'EN_PROCESO']:
                periodo_cargado = PeriodoAsignacion.cargar(p['codigo'])
                if periodo_cargado and periodo_cargado.archivo_asignaciones:
                    excel = periodo_cargado.archivo_asignaciones
                    if os.path.exists(excel):
                        return pd.read_excel(excel)
        
        # Fallback: archivo en la raíz
        excel = "Asignaciones.xlsx"
        if os.path.exists(excel):
            return pd.read_excel(excel)
        return None
    
    @staticmethod
    def guardar_asignaciones(df_asignaciones, archivo="Asignaciones.xlsx"):
        """Guarda las asignaciones en un archivo Excel"""
        try:
            df_asignaciones.to_excel(archivo, index=False)
            return True
        except Exception as e:
            print(f"Error al guardar asignaciones: {e}")
            return False

# CONTEXTO DE AUTENTICACIÓN (Single Responsibility Principle)
class IniciarSesion:
    """Clase con responsabilidad única: validar credenciales (SRP)"""
    
    @classmethod
    def Iniciar(cls, intento_identificacion: str, intento_contra: str, bd: Base_Dato):
        """Valida las credenciales contra la base de datos proporcionada (DIP)"""
        datos_usuario = bd.obtener_usuario(intento_identificacion, intento_contra)
        if datos_usuario is not None:
            return True, datos_usuario
        return False, None

# CLASE BASE USUARIO (Herencia + Polimorfismo + Template Method)
class Usuario(ABC):
    
    @abstractmethod
    def mostrar_informacion(self):
        pass
    
    @abstractmethod
    def obtener_identificacion(self) -> str:
        """Retorna la identificación única del usuario"""
        pass

# CLASE ADMINISTRADOR (Herencia + Polimorfismo + DIP)
@dataclass
class Administrador(Usuario):
    Periodo = "2025 - 2"
    
    identificacion: str = ""
    nombre: str = ""
    cedula: str = ""
    id: int = 0
    
    # DIP: Dependencias inyectadas
    _gestor_periodos: IGestorPeriodos = field(default=None, repr=False)
    _estrategia_clasificacion: EstrategiaClasificacion = field(default=None, repr=False)
    _estrategia_desempate: EstrategiaDesempate = field(default=None, repr=False)
    _estrategia_segmentacion: EstrategiaSegmentacion = field(default=None, repr=False)

    @classmethod
    def crear_desde_bd(cls, datos: Dict[str, Any], 
                       gestor_periodos: IGestorPeriodos = None,
                       estrategia_clasificacion: EstrategiaClasificacion = None,
                       estrategia_desempate: EstrategiaDesempate = None,
                       estrategia_segmentacion: EstrategiaSegmentacion = None):
        """Factory Method con inyección de dependencias"""
        admin = cls(
            identificacion=str(datos.get("IDENTIFICACIÓN", "")),
            nombre=str(datos.get("NOMBRE", "")),
            cedula=str(datos.get("CEDULA", "")),
            id=int(datos.get("ID", 0))
        )
        # DIP: Inyectar dependencias o usar defaults
        admin._gestor_periodos = gestor_periodos or GestorPeriodos()
        admin._estrategia_clasificacion = estrategia_clasificacion or ClasificacionSENESCYT()
        admin._estrategia_desempate = estrategia_desempate or DesempateSENESCYT()
        admin._estrategia_segmentacion = estrategia_segmentacion or SegmentacionPorcentual()
        return admin
    
    def mostrar_informacion(self):
        """Polimorfismo: Implementación específica de Administrador"""
        return {
            'tipo': 'Administrador',
            'identificacion': self.identificacion,
            'nombre': self.nombre,
            'cedula': self.cedula,
            'id': self.id,
            'periodo': self.Periodo
        }
    
    def obtener_identificacion(self) -> str:
        """Implementación de la interfaz Usuario"""
        return self.identificacion
    
    def obtener_gestor_periodos(self) -> GestorPeriodos:
        """Retorna el gestor de periodos"""
        if self._gestor_periodos is None:
            self._gestor_periodos = GestorPeriodos()
        return self._gestor_periodos
    
    def crear_nuevo_periodo(self, codigo: str, nombre: str = "") -> Tuple[bool, str, Optional[PeriodoAsignacion]]:
        """Crea un nuevo periodo de asignación"""
        gestor = self.obtener_gestor_periodos()
        return gestor.crear_periodo(codigo, nombre)
    
    def abrir_periodo(self, codigo: str) -> Tuple[bool, str, Optional[PeriodoAsignacion]]:
        """Abre un periodo existente"""
        gestor = self.obtener_gestor_periodos()
        return gestor.abrir_periodo(codigo)
    
    def obtener_periodo_activo(self) -> Optional[PeriodoAsignacion]:
        """Obtiene el periodo activo actual"""
        gestor = self.obtener_gestor_periodos()
        return gestor.obtener_periodo_activo()
    
    def listar_periodos(self) -> List[Dict]:
        """Lista todos los periodos disponibles"""
        gestor = self.obtener_gestor_periodos()
        return gestor.listar_periodos()
        
    def set_estrategia_clasificacion(self, estrategia: EstrategiaClasificacion):
        """Permite cambiar la estrategia de clasificación (OCP)"""
        self._estrategia_clasificacion = estrategia
    
    def set_estrategia_desempate(self, estrategia: EstrategiaDesempate):
        """Permite cambiar la estrategia de desempate (OCP)"""
        self._estrategia_desempate = estrategia
    
    def set_estrategia_segmentacion(self, estrategia: EstrategiaSegmentacion):
        """Permite cambiar la estrategia de segmentación (OCP)"""
        self._estrategia_segmentacion = estrategia
        
    def ejecutar_asignacion(self, oferta_df, postulaciones_df, 
                            porcentajes: Dict[str, float] = None, 
                            es_instituto: bool = False):
        """
        Ejecuta la asignación de cupos con las estrategias inyectadas (DIP).
        Utiliza Strategy Pattern para permitir diferentes comportamientos.
        """
        motor = MotorAsignacion(
            oferta_df, postulaciones_df, porcentajes, es_instituto,
            estrategia_clasificacion=self._estrategia_clasificacion,
            estrategia_desempate=self._estrategia_desempate,
            estrategia_segmentacion=self._estrategia_segmentacion
        )
        return motor.ejecutar_asignacion()
    
    def ejecutar_asignacion_periodo(self, callback_progreso=None) -> Tuple[bool, str, Dict]:
        """
        Ejecuta la asignación completa para el periodo activo.
        """
        periodo = self.obtener_periodo_activo()
        if not periodo:
            return False, "No hay un periodo activo. Cree o abra un periodo primero.", {}
        
        return periodo.ejecutar_asignacion_completa(callback_progreso)
    
    def cerrar_periodo_activo(self) -> Tuple[bool, str]:
        """Cierra el periodo activo"""
        periodo = self.obtener_periodo_activo()
        if not periodo:
            return False, "No hay un periodo activo."
        
        return periodo.cerrar_periodo()
    
    def generar_reporte(self, asignaciones_df):
        """Genera un reporte de las asignaciones"""
        reporte = Reporte()
        return reporte.generar_reporte_completo(asignaciones_df)

#CLASE POSTULANTE
@dataclass
class Postulante(Usuario):
    identificacion: str = ""
    contraseña: str = ""
    fecha_postulacion: str = ""
    puntaje_postulacion: float = 0.0
    segmento_aspirante: int = 0
    instancia_postulacion: int = 0
    prioridad_carrera: int = 0
    nombre_carrera: str = ""
    ofa_id: str = ""
    cus_id: str = ""
    cupo_asignado: bool = False
    estado_cupo: str = ""
    
    @classmethod
    def crear_desde_bd(cls, datos: Dict[str, Any]):
        """Factory Method para crear Postulante desde datos de BD"""
        return cls(
            identificacion=str(datos.get("IDENTIFICACIÓN", "")),
            contraseña=str(datos.get("CONTRASEÑA", "")),
            fecha_postulacion=str(datos.get("FECHA_POSTULACION", "")),
            puntaje_postulacion=float(datos.get("PUNTAJE_POSTULACION", 0.0)),
            segmento_aspirante=int(datos.get("SEGMENTO_ASPIRANTE", 0)),
            instancia_postulacion=int(datos.get("INSTANCIA_POSTULACION", 0)),
            prioridad_carrera=int(datos.get("PRIORIDAD_ELECCION_CARRERA", 0)),
            nombre_carrera=str(datos.get("NOMBRE_CARRERA", "")),
            ofa_id=str(datos.get("OFA_ID", "")),
            cus_id=str(datos.get("CUS_ID", ""))
        )

    def mostrar_informacion(self):
        """Polimorfismo: Implementación específica de Postulante"""
        return {
            'tipo': 'Postulante',
            'identificacion': self.identificacion,
            'fecha_postulacion': self.fecha_postulacion,
            'puntaje': self.puntaje_postulacion,
            'segmento': self.segmento_aspirante,
            'carrera': self.nombre_carrera,
            'prioridad': self.prioridad_carrera,
            'estado_cupo': self.estado_cupo
        }
    
    def obtener_identificacion(self) -> str:
        """Implementación de la interfaz Usuario (Liskov Substitution)"""
        return self.identificacion

    def ver_puntaje(self) -> float:
        return self.puntaje_postulacion
    
    def obtener_postulaciones(self):
        return {
            'carrera': self.nombre_carrera,
            'prioridad': self.prioridad_carrera,
            'puntaje': self.puntaje_postulacion,
            'segmento': self.segmento_aspirante,
            'cupo_asignado': self.cupo_asignado,
            'estado': self.estado_cupo
        }
    
    def aceptar_cupo(self):
        """Acepta el cupo asignado"""
        if self.cupo_asignado and self.estado_cupo == "ASIGNADO":
            self.estado_cupo = "ACEPTADO"
            return True
        return False

# FACTORY METHOD PARA USUARIOS (Patrón Creacional)
class SobrecargaUsuario:
    """
    Factory Method : Crea el tipo correcto de Usuario según la BD.
    """
    @staticmethod
    def crear_usuario(bd: Base_Dato, datos: Dict[str, Any]) -> Optional[Usuario]:
        if isinstance(bd, BD_ADMIN):
            return Administrador.crear_desde_bd(datos)
        elif isinstance(bd, BD_USUARIO):
            return Postulante.crear_desde_bd(datos)
        return None


# PATRÓN FACADE (Patrón Estructural)

class SistemaAutenticacion:
    
    @staticmethod
    def login_postulante(identificacion: str, contraseña: str, 
                         bd: Base_Dato = None) -> Tuple[bool, Optional[Usuario], str]:
        """Login de postulante con inyección de dependencias opcional"""
        bd = bd or BD_USUARIO()
        return SistemaAutenticacion._autenticar(identificacion, contraseña, bd)
    
    @staticmethod
    def login_administrador(identificacion: str, contraseña: str,
                            bd: Base_Dato = None) -> Tuple[bool, Optional[Usuario], str]:
        """Login de administrador con inyección de dependencias opcional"""
        bd = bd or BD_ADMIN()
        return SistemaAutenticacion._autenticar(identificacion, contraseña, bd)
    
    @staticmethod
    def _autenticar(identificacion: str, contraseña: str, bd: Base_Dato) -> Tuple[bool, Optional[Usuario], str]:
        """Método privado que realiza la autenticación real"""
        try:
            exito, datos_usuario = IniciarSesion.Iniciar(identificacion, contraseña, bd)
            if not exito or datos_usuario is None:
                return False, None, "Credenciales incorrectas"
            
            usuario = SobrecargaUsuario.crear_usuario(bd, datos_usuario)
            if usuario is None:
                return False, None, "Error al crear instancia de usuario"
            
            return True, usuario, "Inicio de sesión exitoso"
        except Exception as e:
            return False, None, f"Error en autenticación: {str(e)}"
    
    @staticmethod
    def obtener_tipo_usuario(usuario: Usuario) -> str:
        """Polimorfismo: Identifica el tipo de usuario"""
        if isinstance(usuario, Administrador):
            return "administrador"
        elif isinstance(usuario, Postulante):
            return "postulante"
        return "desconocido"