import pandas as pd
from abc import abstractmethod, ABC
from typing import Optional, Dict, Any, List, Tuple
import os
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

# ====== ENUMERACIONES ======
class SegmentoAspirante(Enum):
    POBLACION_GENERAL = 1
    POLITICA_CUOTAS = 2

class GrupoAsignacion(Enum):
    POLITICA_CUOTAS = 1
    VULNERABILIDAD = 2
    MERITO_ACADEMICO = 3
    OTROS_RECONOCIMIENTOS = 4
    BACHILLERES_PUEBLOS = 5
    BACHILLERES_ULTIMO_ANIO = 6
    POBLACION_GENERAL = 7

class EstadoCupo(Enum):
    DISPONIBLE = "DISPONIBLE"
    ASIGNADO = "ASIGNADO"
    ACEPTADO = "ACEPTADO"
    LIBERADO = "LIBERADO"

# ====== INTERFAZ DE ESTRATEGIA DE BASE DE DATOS ======
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
        excel = "Postulantes.xlsx"
        if os.path.exists(excel):
            return pd.read_excel(excel, sheet_name=5, skiprows=1)
        return None
    
    @staticmethod
    def cargar_oferta_academica():
        excel = "Oferta_Academica.xlsx"
        if os.path.exists(excel):
            return pd.read_excel(excel, sheet_name=0, skiprows=1)
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

# ====== CONTEXTO DE AUTENTICACIÓN ======
class IniciarSesion:
    @classmethod
    def Iniciar(cls, intento_identificacion: str, intento_contra: str, bd: Base_Dato):
        datos_usuario = bd.obtener_usuario(intento_identificacion, intento_contra)
        if datos_usuario is not None:
            return True, datos_usuario
        return False, None

# ====== INTERFAZ DE USUARIO ======
class Usuario(ABC):
    @abstractmethod
    def mostrar_informacion(self):
        pass

# ====== CLASE ADMINISTRADOR ======
@dataclass
class Administrador(Usuario):
    Periodo = "2025 - 2"
    
    identificacion: str = ""
    nombre: str = ""
    cedula: str = ""
    id: int = 0

    @classmethod
    def crear_desde_bd(cls, datos: Dict[str, Any]):
        return cls(
            identificacion=str(datos.get("IDENTIFICACIÓN", "")),
            nombre=str(datos.get("NOMBRE", "")),
            cedula=str(datos.get("CEDULA", "")),
            id=int(datos.get("ID", 0))
        )
    
    def mostrar_informacion(self):
        return {
            'tipo': 'Administrador',
            'identificacion': self.identificacion,
            'nombre': self.nombre,
            'cedula': self.cedula,
            'id': self.id,
            'periodo': self.Periodo
        }
        
    def ejecutar_asignacion(self, oferta_df, postulaciones_df, porcentajes: Dict[str, float] = None):
        """Ejecuta el proceso de asignación de cupos"""
        motor = MotorAsignacion(oferta_df, postulaciones_df, porcentajes)
        return motor.ejecutar_asignacion()
    
    def generar_reporte(self, asignaciones_df):
        """Genera un reporte de las asignaciones"""
        reporte = Reporte()
        return reporte.generar_reporte_completo(asignaciones_df)

# ====== CLASE POSTULANTE ======
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

# ====== FACTORY METHOD PARA USUARIOS ======
class SobrecargaUsuario:
    @staticmethod
    def crear_usuario(bd: Base_Dato, datos: Dict[str, Any]):
        if isinstance(bd, BD_ADMIN):
            return Administrador.crear_desde_bd(datos)
        elif isinstance(bd, BD_USUARIO):
            return Postulante.crear_desde_bd(datos)
        return None

# ====== PATRÓN FACADE ======
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

# ====== CLASE CUPO ======
@dataclass
class Cupo:
    """Representa un cupo disponible en una carrera"""
    id_cupo: str
    ofa_id: str
    cus_id: str
    carrera: str
    total_cupos: int
    grupo: GrupoAsignacion
    estado: EstadoCupo = EstadoCupo.DISPONIBLE
    postulante_asignado: Optional[str] = None
    
    def asignar(self, identificacion_postulante: str):
        """Asigna el cupo a un postulante"""
        if self.estado == EstadoCupo.DISPONIBLE:
            self.estado = EstadoCupo.ASIGNADO
            self.postulante_asignado = identificacion_postulante
            return True
        return False
    
    def liberar(self):
        """Libera el cupo"""
        self.estado = EstadoCupo.DISPONIBLE
        self.postulante_asignado = None
    
    def aceptar(self):
        """Marca el cupo como aceptado"""
        if self.estado == EstadoCupo.ASIGNADO:
            self.estado = EstadoCupo.ACEPTADO
            return True
        return False
    
    def esta_disponible(self):
        return self.estado == EstadoCupo.DISPONIBLE

# ====== MOTOR DE ASIGNACIÓN ======
class MotorAsignacion:
    """
    Implementa el algoritmo de asignación de cupos según el Artículo 52
    """
    
    def __init__(self, oferta_df: pd.DataFrame, postulaciones_df: pd.DataFrame, 
                 porcentajes: Dict[str, float] = None):
        self.oferta_df = oferta_df
        self.postulaciones_df = postulaciones_df
        
        # Porcentajes por defecto según el artículo 52
        self.porcentajes = porcentajes or {
            'politica_cuotas': 0.10,
            'vulnerabilidad': 0.10,
            'merito_academico': 0.20,
            'otros_reconocimientos': 0.02,
            'bachilleres_pueblos': 0.10,
            'bachilleres_ultimo': 0.20,
            'poblacion_general': 0.20
        }
        
        self.asignaciones = []
        self.cupos_por_carrera = {}
        self.ofa_id_por_carrera = {}  # Mapeo CUS_ID -> OFA_ID
        self.carrera_por_cus = {}  # Mapeo CUS_ID -> nombre carrera
    
    def segmentar_oferta(self):
        """Segmenta la oferta de cupos según los porcentajes establecidos"""
        for _, oferta in self.oferta_df.iterrows():
            ofa_id = oferta['OFA_ID']
            cus_id = oferta['CUS_ID']
            carrera = oferta['CAR_NOMBRE_CARRERA']
            total_cupos = oferta['CUS_TOTAL_CUPOS']
            
            cupos_segmentados = {
                GrupoAsignacion.POLITICA_CUOTAS: int(total_cupos * self.porcentajes['politica_cuotas']),
                GrupoAsignacion.VULNERABILIDAD: int(total_cupos * self.porcentajes['vulnerabilidad']),
                GrupoAsignacion.MERITO_ACADEMICO: int(total_cupos * self.porcentajes['merito_academico']),
                GrupoAsignacion.OTROS_RECONOCIMIENTOS: int(total_cupos * self.porcentajes['otros_reconocimientos']),
                GrupoAsignacion.BACHILLERES_PUEBLOS: int(total_cupos * self.porcentajes['bachilleres_pueblos']),
                GrupoAsignacion.BACHILLERES_ULTIMO_ANIO: int(total_cupos * self.porcentajes['bachilleres_ultimo']),
                GrupoAsignacion.POBLACION_GENERAL: int(total_cupos * self.porcentajes['poblacion_general'])
            }
            
            # Ajustar cupos restantes a población general
            cupos_asignados = sum(cupos_segmentados.values())
            if cupos_asignados < total_cupos:
                cupos_segmentados[GrupoAsignacion.POBLACION_GENERAL] += (total_cupos - cupos_asignados)
            
            self.cupos_por_carrera[cus_id] = cupos_segmentados
            self.ofa_id_por_carrera[cus_id] = ofa_id  # Guardar OFA_ID
            self.carrera_por_cus[cus_id] = carrera  # Guardar nombre carrera
    
    def clasificar_postulante(self, postulante: Dict) -> List[GrupoAsignacion]:
        """
        Clasifica al postulante en los grupos a los que pertenece
        Según el artículo: si cumple con más de un criterio, participa en el que más le favorece
        """
        grupos = []
        
        # Verificar si pertenece a política de cuotas
        if postulante.get('SEGMENTO_ASPIRANTE') == 2:
            grupos.append(GrupoAsignacion.POLITICA_CUOTAS)
        
        # Verificar vulnerabilidad (campo hipotético)
        if postulante.get('VULNERABILIDAD_SOCIOECONOMICA') == 'SI':
            grupos.append(GrupoAsignacion.VULNERABILIDAD)
        
        # Verificar mérito académico (campo hipotético)
        if postulante.get('MERITO_ACADEMICO') == 'SI':
            grupos.append(GrupoAsignacion.MERITO_ACADEMICO)
        
        # Verificar otros reconocimientos (campo hipotético)
        if postulante.get('OTROS_RECONOCIMIENTOS') == 'SI':
            grupos.append(GrupoAsignacion.OTROS_RECONOCIMIENTOS)
        
        # Verificar bachilleres de pueblos y nacionalidades
        if postulante.get('PUEBLOS_NACIONALIDADES') == 'SI':
            grupos.append(GrupoAsignacion.BACHILLERES_PUEBLOS)
        
        # Verificar bachiller del último año
        if postulante.get('BACHILLER_ULTIMO_ANIO') == 'SI':
            grupos.append(GrupoAsignacion.BACHILLERES_ULTIMO_ANIO)
        
        # Siempre puede participar en población general
        grupos.append(GrupoAsignacion.POBLACION_GENERAL)
        
        return grupos
    
    def asignar_por_grupo(self, grupo: GrupoAsignacion, postulantes_df: pd.DataFrame):
        """Asigna cupos a los postulantes de un grupo específico"""
        # Ordenar por puntaje (mayor a menor)
        postulantes_ordenados = postulantes_df.sort_values('PUNTAJE_POSTULACION', ascending=False)
        
        for _, postulante in postulantes_ordenados.iterrows():
            identificacion = postulante['IDENTIFICACIÓN']
            
            # Verificar si ya tiene asignación
            if any(a['identificacion'] == identificacion for a in self.asignaciones):
                continue
            
            # Obtener sus postulaciones ordenadas por prioridad
            postulaciones_postulante = self.postulaciones_df[
                self.postulaciones_df['IDENTIFICACIÓN'] == identificacion
            ].sort_values('PRIORIDAD_ELECCION_CARRERA')
            
            # Intentar asignar según prioridad
            for _, postulacion in postulaciones_postulante.iterrows():
                cus_id = postulacion['CUS_ID']
                
                if cus_id not in self.cupos_por_carrera:
                    continue
                
                # Verificar si hay cupos disponibles en este grupo
                if self.cupos_por_carrera[cus_id].get(grupo, 0) > 0:
                    # Obtener OFA_ID desde el mapeo guardado (más confiable)
                    ofa_id = self.ofa_id_por_carrera.get(cus_id, postulacion.get('OFA_ID', ''))
                    carrera = self.carrera_por_cus.get(cus_id, postulacion.get('NOMBRE_CARRERA', ''))
                    
                    # Asignar cupo
                    self.asignaciones.append({
                        'identificacion': identificacion,
                        'cus_id': cus_id,
                        'ofa_id': ofa_id,
                        'carrera': carrera,
                        'puntaje': postulante['PUNTAJE_POSTULACION'],
                        'grupo': grupo.name,
                        'prioridad': postulacion['PRIORIDAD_ELECCION_CARRERA'],
                        'fecha_asignacion': datetime.now().strftime("%d/%m/%Y %H:%M"),
                        'estado': 'ASIGNADO'
                    })
                    
                    # Reducir cupos disponibles
                    self.cupos_por_carrera[cus_id][grupo] -= 1
                    break
    
    def ejecutar_asignacion(self) -> pd.DataFrame:
        """
        Ejecuta el proceso completo de asignación siguiendo el orden establecido
        en el Artículo 52
        """
        # 1. Segmentar la oferta
        self.segmentar_oferta()
        
        # 2. Orden de asignación según el artículo
        orden_grupos = [
            GrupoAsignacion.POLITICA_CUOTAS,
            GrupoAsignacion.VULNERABILIDAD,
            GrupoAsignacion.MERITO_ACADEMICO,
            GrupoAsignacion.OTROS_RECONOCIMIENTOS,
            GrupoAsignacion.BACHILLERES_PUEBLOS,
            GrupoAsignacion.BACHILLERES_ULTIMO_ANIO,
            GrupoAsignacion.POBLACION_GENERAL
        ]
        
        # 3. Asignar por cada grupo
        for grupo in orden_grupos:
            self.asignar_por_grupo(grupo, self.postulaciones_df)
        
        # 4. Retornar DataFrame con asignaciones
        return pd.DataFrame(self.asignaciones)

# ====== CLASE REPORTE ======
class Reporte:
    """Genera reportes del proceso de asignación en formato Excel"""
    
    def __init__(self, carpeta_reportes: str = "Reportes"):
        self.carpeta_reportes = carpeta_reportes
        # Crear carpeta si no existe
        if not os.path.exists(carpeta_reportes):
            os.makedirs(carpeta_reportes)
    
    def generar_reporte_completo(self, asignaciones_df: pd.DataFrame, guardar_excel: bool = True) -> Dict:
        """Genera un reporte completo con estadísticas y lo guarda en Excel"""
        if asignaciones_df.empty:
            return {'error': 'No hay asignaciones para generar reporte'}
        
        reporte = {
            'total_asignaciones': len(asignaciones_df),
            'por_grupo': asignaciones_df['grupo'].value_counts().to_dict(),
            'por_carrera': asignaciones_df['carrera'].value_counts().to_dict(),
            'puntaje_promedio': asignaciones_df['puntaje'].mean(),
            'puntaje_maximo': asignaciones_df['puntaje'].max(),
            'puntaje_minimo': asignaciones_df['puntaje'].min()
        }
        
        if guardar_excel:
            fecha_hora = datetime.now().strftime("%Y%m%d_%H%M%S")
            archivo = os.path.join(self.carpeta_reportes, f"Reporte_General_{fecha_hora}.xlsx")
            
            with pd.ExcelWriter(archivo, engine='openpyxl') as writer:
                # Hoja 1: Resumen general
                resumen_data = {
                    'Métrica': ['Total Asignaciones', 'Puntaje Promedio', 'Puntaje Máximo', 'Puntaje Mínimo'],
                    'Valor': [reporte['total_asignaciones'], 
                             round(reporte['puntaje_promedio'], 2),
                             reporte['puntaje_maximo'], 
                             reporte['puntaje_minimo']]
                }
                pd.DataFrame(resumen_data).to_excel(writer, sheet_name='Resumen', index=False)
                
                # Hoja 2: Asignaciones por grupo
                df_grupos = pd.DataFrame(list(reporte['por_grupo'].items()), 
                                        columns=['Grupo', 'Cantidad'])
                df_grupos.to_excel(writer, sheet_name='Por_Grupo', index=False)
                
                # Hoja 3: Asignaciones por carrera
                df_carreras = pd.DataFrame(list(reporte['por_carrera'].items()), 
                                          columns=['Carrera', 'Cantidad'])
                df_carreras.to_excel(writer, sheet_name='Por_Carrera', index=False)
                
                # Hoja 4: Lista completa de asignaciones
                asignaciones_df.to_excel(writer, sheet_name='Asignaciones_Detalle', index=False)
            
            reporte['archivo_generado'] = archivo
        
        return reporte
    
    def generar_reporte_por_carrera(self, asignaciones_df: pd.DataFrame, carrera: str = None, 
                                    guardar_excel: bool = True) -> Dict:
        """Genera reporte específico de una carrera o todas las carreras en Excel"""
        if asignaciones_df.empty:
            return {'error': 'No hay asignaciones para generar reporte'}
        
        fecha_hora = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if carrera:
            # Reporte de una carrera específica
            df_carrera = asignaciones_df[asignaciones_df['carrera'] == carrera]
            if df_carrera.empty:
                return {'error': f'No hay asignaciones para la carrera: {carrera}'}
            
            reporte = {
                'carrera': carrera,
                'total_asignados': len(df_carrera),
                'por_grupo': df_carrera['grupo'].value_counts().to_dict(),
                'puntaje_promedio': df_carrera['puntaje'].mean()
            }
            
            if guardar_excel:
                archivo = os.path.join(self.carpeta_reportes, f"Reporte_{carrera.replace(' ', '_')}_{fecha_hora}.xlsx")
                with pd.ExcelWriter(archivo, engine='openpyxl') as writer:
                    df_carrera.to_excel(writer, sheet_name='Asignados', index=False)
                    df_grupos = pd.DataFrame(list(reporte['por_grupo'].items()), 
                                            columns=['Grupo', 'Cantidad'])
                    df_grupos.to_excel(writer, sheet_name='Por_Grupo', index=False)
                reporte['archivo_generado'] = archivo
        else:
            # Reporte de todas las carreras en un solo archivo
            archivo = os.path.join(self.carpeta_reportes, f"Reporte_Todas_Carreras_{fecha_hora}.xlsx")
            reporte = {'carreras': {}}
            
            if guardar_excel:
                with pd.ExcelWriter(archivo, engine='openpyxl') as writer:
                    carreras_unicas = asignaciones_df['carrera'].unique()
                    
                    # Hoja resumen
                    resumen_list = []
                    for carr in carreras_unicas:
                        df_carr = asignaciones_df[asignaciones_df['carrera'] == carr]
                        resumen_list.append({
                            'Carrera': carr,
                            'Total_Asignados': len(df_carr),
                            'Puntaje_Promedio': round(df_carr['puntaje'].mean(), 2),
                            'Puntaje_Max': df_carr['puntaje'].max(),
                            'Puntaje_Min': df_carr['puntaje'].min()
                        })
                        reporte['carreras'][carr] = len(df_carr)
                    
                    pd.DataFrame(resumen_list).to_excel(writer, sheet_name='Resumen_Carreras', index=False)
                    
                    # Una hoja por cada carrera (máximo 30 para evitar problemas)
                    for i, carr in enumerate(carreras_unicas[:30]):
                        df_carr = asignaciones_df[asignaciones_df['carrera'] == carr]
                        nombre_hoja = carr[:31].replace('/', '-').replace('\\', '-')  # Límite Excel
                        df_carr.to_excel(writer, sheet_name=nombre_hoja, index=False)
                
                reporte['archivo_generado'] = archivo
        
        return reporte
    
    def generar_reporte_por_grupo(self, asignaciones_df: pd.DataFrame, guardar_excel: bool = True) -> Dict:
        """Genera reporte por grupos de asignación en Excel"""
        if asignaciones_df.empty:
            return {'error': 'No hay asignaciones para generar reporte'}
        
        fecha_hora = datetime.now().strftime("%Y%m%d_%H%M%S")
        archivo = os.path.join(self.carpeta_reportes, f"Reporte_Por_Grupos_{fecha_hora}.xlsx")
        
        reporte = {
            'por_grupo': asignaciones_df['grupo'].value_counts().to_dict(),
            'detalle_por_grupo': {}
        }
        
        if guardar_excel:
            with pd.ExcelWriter(archivo, engine='openpyxl') as writer:
                grupos_unicos = asignaciones_df['grupo'].unique()
                
                # Hoja resumen
                resumen_list = []
                for grupo in grupos_unicos:
                    df_grupo = asignaciones_df[asignaciones_df['grupo'] == grupo]
                    resumen_list.append({
                        'Grupo': grupo,
                        'Total_Asignados': len(df_grupo),
                        'Puntaje_Promedio': round(df_grupo['puntaje'].mean(), 2),
                        'Puntaje_Max': df_grupo['puntaje'].max(),
                        'Puntaje_Min': df_grupo['puntaje'].min()
                    })
                    reporte['detalle_por_grupo'][grupo] = len(df_grupo)
                
                pd.DataFrame(resumen_list).to_excel(writer, sheet_name='Resumen_Grupos', index=False)
                
                # Una hoja por cada grupo
                for grupo in grupos_unicos:
                    df_grupo = asignaciones_df[asignaciones_df['grupo'] == grupo]
                    nombre_hoja = grupo[:31]  # Límite de caracteres en Excel
                    df_grupo.to_excel(writer, sheet_name=nombre_hoja, index=False)
            
            reporte['archivo_generado'] = archivo
        
        return reporte
    
    def generar_lista_asignados(self, asignaciones_df: pd.DataFrame, guardar_excel: bool = True) -> List[Dict]:
        """Genera lista de todos los asignados y la guarda en Excel"""
        if guardar_excel and not asignaciones_df.empty:
            fecha_hora = datetime.now().strftime("%Y%m%d_%H%M%S")
            archivo = os.path.join(self.carpeta_reportes, f"Lista_Asignados_{fecha_hora}.xlsx")
            asignaciones_df.to_excel(archivo, index=False)
        
        return asignaciones_df.to_dict('records')

# ====== GESTIÓN DE ACEPTACIÓN DE CUPOS ======
class GestorAceptacion:
    """Gestiona el proceso de aceptación de cupos"""
    
    def __init__(self, archivo_asignaciones="Asignaciones.xlsx"):
        self.archivo = archivo_asignaciones
    
    def registrar_aceptacion(self, identificacion: str, cus_id: str, fecha_aceptacion: str) -> bool:
        """Registra la aceptación de un cupo"""
        try:
            df = pd.read_excel(self.archivo)
            
            # Buscar la asignación
            mask = (df['identificacion'] == identificacion) & (df['cus_id'] == cus_id)
            
            if mask.any():
                df.loc[mask, 'estado'] = 'ACEPTADO'
                df.loc[mask, 'fecha_aceptacion'] = fecha_aceptacion
                df.to_excel(self.archivo, index=False)
                return True
            
            return False
        except Exception as e:
            print(f"Error al registrar aceptación: {e}")
            return False
    
    def verificar_aceptacion(self, identificacion: str) -> Optional[Dict]:
        """Verifica si un postulante tiene un cupo aceptado"""
        try:
            df = pd.read_excel(self.archivo)
            asignacion = df[(df['identificacion'] == identificacion) & 
                          (df['estado'] == 'ACEPTADO')]
            
            if not asignacion.empty:
                return asignacion.iloc[0].to_dict()
            return None
        except Exception as e:
            print(f"Error al verificar aceptación: {e}")
            return None