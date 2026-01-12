import pandas as pd
from abc import abstractmethod, ABC
from typing import Optional, Dict, Any, List, Tuple
import os
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from Asignacion import (GrupoAsignacion,EstadoCupo,Cupo,MotorAsignacion,Reporte,GestorAceptacion)
from PeriodoAsignacion import (PeriodoAsignacion,EstadoPeriodo,FasePeriodo,ConfiguracionPeriodo,GestorPeriodos)

#ENUMERACIONES 
class SegmentoAspirante(Enum):
    POBLACION_GENERAL = 1
    POLITICA_CUOTAS = 2

#INTERFAZ DE ESTRATEGIA DE BASE DE DATOS 
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
    def cargar_base(self):
        # Intentar cargar desde el periodo activo primero
        gestor = GestorPeriodos()
        periodo = gestor.obtener_periodo_activo()
        
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

#CONTEXTO DE AUTENTICACIÓN 
class IniciarSesion:
    @classmethod
    def Iniciar(cls, intento_identificacion: str, intento_contra: str, bd: Base_Dato):
        datos_usuario = bd.obtener_usuario(intento_identificacion, intento_contra)
        if datos_usuario is not None:
            return True, datos_usuario
        return False, None

#INTERFAZ DE USUARIO 
class Usuario(ABC):
    @abstractmethod
    def mostrar_informacion(self):
        pass

#CLASE ADMINISTRADOR 
@dataclass
class Administrador(Usuario):
    Periodo = "2025 - 2"
    
    identificacion: str = ""
    nombre: str = ""
    cedula: str = ""
    id: int = 0
    
    # Gestor de periodos para el administrador
    _gestor_periodos: GestorPeriodos = None

    @classmethod
    def crear_desde_bd(cls, datos: Dict[str, Any]):
        admin = cls(
            identificacion=str(datos.get("IDENTIFICACIÓN", "")),
            nombre=str(datos.get("NOMBRE", "")),
            cedula=str(datos.get("CEDULA", "")),
            id=int(datos.get("ID", 0))
        )
        admin._gestor_periodos = GestorPeriodos()
        return admin
    
    def mostrar_informacion(self):
        return {
            'tipo': 'Administrador',
            'identificacion': self.identificacion,
            'nombre': self.nombre,
            'cedula': self.cedula,
            'id': self.id,
            'periodo': self.Periodo
        }
    
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
        
    def ejecutar_asignacion(self, oferta_df, postulaciones_df, porcentajes: Dict[str, float] = None, es_instituto: bool = False):
        """Ejecuta la asignación de cupos con los datos proporcionados"""
        motor = MotorAsignacion(oferta_df, postulaciones_df, porcentajes, es_instituto)
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

#  CLASE POSTULANTE 
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

    def ver_puntaje(self):
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

#  FACTORY METHOD PARA USUARIOS 
class SobrecargaUsuario:
    @staticmethod
    def crear_usuario(bd: Base_Dato, datos: Dict[str, Any]):
        if isinstance(bd, BD_ADMIN):
            return Administrador.crear_desde_bd(datos)
        elif isinstance(bd, BD_USUARIO):
            return Postulante.crear_desde_bd(datos)
        return None

#  PATRÓN FACADE 
class SistemaAutenticacion:
    @staticmethod
    def login_postulante(identificacion: str, contraseña: str):
        return SistemaAutenticacion._autenticar(identificacion, contraseña, BD_USUARIO())
    
    @staticmethod
    def login_administrador(identificacion: str, contraseña: str):
        return SistemaAutenticacion._autenticar(identificacion, contraseña, BD_ADMIN())
    
    @staticmethod
    def _autenticar(identificacion: str, contraseña: str, bd: Base_Dato):
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
    def obtener_tipo_usuario(usuario) -> str:
        if isinstance(usuario, Administrador):
            return "administrador"
        elif isinstance(usuario, Postulante):
            return "postulante"
        return "desconocido"