import pandas as pd
import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, List, Any, Tuple
import shutil
from Asignacion import MotorAsignacion, Reporte


class EstadoPeriodo(Enum):
    """Estados posibles de un periodo de asignación"""
    NO_INICIADO = "NO_INICIADO"       # Periodo creado pero sin datos
    DATOS_CARGADOS = "DATOS_CARGADOS"  # Archivos cargados, listo para asignar
    EN_PROCESO = "EN_PROCESO"          # Asignación en progreso
    FINALIZADO = "FINALIZADO"          # Asignación completada
    CERRADO = "CERRADO"                # Periodo cerrado definitivamente


class FasePeriodo(Enum):
    """Fases del proceso de asignación dentro de un periodo"""
    CONFIGURACION = 1      # Configurando porcentajes
    CARGA_DATOS = 2        # Cargando archivos
    ASIGNACION = 3         # Ejecutando asignación
    ACEPTACION = 4         # Periodo de aceptación de cupos
    REASIGNACION = 5       # Reasignación de cupos liberados
    CIERRE = 6             # Cierre del periodo


@dataclass
class ConfiguracionPeriodo:
    """Configuración de un periodo de asignación"""
    porcentajes: Dict[str, float] = field(default_factory=dict)
    es_instituto: bool = False
    max_vueltas_asignacion: int = 3
    dias_aceptacion: int = 5
    
    def __post_init__(self):
        if not self.porcentajes:
            # Porcentajes por defecto según Art. 52
            self.porcentajes = {
                'politica_cuotas': 0.10,
                'vulnerabilidad': 0.10,
                'merito_academico': 0.20,
                'otros_reconocimientos': 0.02,
                'bachilleres_pueblos': 0.10,
                'bachilleres_ultimo': 0.20,
                'poblacion_general': 0.20
            }


@dataclass
class VueltaAsignacion:
    """Representa una vuelta de asignación dentro del periodo"""
    numero_vuelta: int
    fecha_inicio: str
    fecha_fin: Optional[str] = None
    total_asignados: int = 0
    cupos_liberados: int = 0
    estadisticas: Dict[str, Any] = field(default_factory=dict)
    completada: bool = False


@dataclass 
class PeriodoAsignacion:
    """
    Clase principal que gestiona un periodo de asignación.
    Engloba todo el proceso desde la configuración hasta el cierre.
    """
    codigo: str                                    # Ej: "2025-2"
    nombre: str = ""                               # Ej: "Periodo Académico 2025-2"
    estado: EstadoPeriodo = EstadoPeriodo.NO_INICIADO
    fase: FasePeriodo = FasePeriodo.CONFIGURACION
    
    fecha_creacion: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    fecha_inicio_asignacion: Optional[str] = None
    fecha_fin_asignacion: Optional[str] = None
    fecha_cierre: Optional[str] = None
    
    configuracion: ConfiguracionPeriodo = field(default_factory=ConfiguracionPeriodo)
    vueltas: List[VueltaAsignacion] = field(default_factory=list)
    
    # Rutas de archivos cargados
    archivo_oferta: Optional[str] = None
    archivo_postulantes: Optional[str] = None
    archivo_asignaciones: Optional[str] = None
    
    # Estadísticas globales
    total_cupos_ofertados: int = 0
    total_postulantes: int = 0
    total_asignados: int = 0
    total_no_asignados: int = 0
    
    # DataFrames (no se serializan)
    _oferta_df: Optional[pd.DataFrame] = field(default=None, repr=False)
    _postulantes_df: Optional[pd.DataFrame] = field(default=None, repr=False)
    _asignaciones_df: Optional[pd.DataFrame] = field(default=None, repr=False)
    
    # Carpeta de almacenamiento
    CARPETA_PERIODOS = "Periodos"
    
    def __post_init__(self):
        if not self.nombre:
            self.nombre = f"Periodo Académico {self.codigo}"
        self._crear_carpeta_periodo()
    
    def _crear_carpeta_periodo(self):
        """Crea la carpeta para almacenar datos del periodo"""
        carpeta = os.path.join(self.CARPETA_PERIODOS, self.codigo.replace("-", "_"))
        if not os.path.exists(carpeta):
            os.makedirs(carpeta)
        self._carpeta = carpeta
    
    #GESTIÓN DE ESTADO 
    
    def puede_asignar(self) -> Tuple[bool, str]:
        """Verifica si se puede ejecutar la asignación"""
        if self.estado == EstadoPeriodo.CERRADO:
            return False, "El periodo está cerrado. No se pueden realizar más asignaciones."
        
        if self.estado == EstadoPeriodo.FINALIZADO:
            return False, "La asignación ya fue completada para este periodo."
        
        if self.estado == EstadoPeriodo.NO_INICIADO:
            return False, "Debe cargar los archivos de Oferta Académica y Postulantes primero."
        
        if self._oferta_df is None or self._postulantes_df is None:
            return False, "Faltan datos. Cargue los archivos necesarios."
        
        return True, "Listo para ejecutar asignación."
    
    def puede_cargar_archivos(self) -> Tuple[bool, str]:
        """Verifica si se pueden cargar archivos"""
        if self.estado in [EstadoPeriodo.CERRADO, EstadoPeriodo.FINALIZADO]:
            return False, "No se pueden modificar archivos en un periodo cerrado o finalizado."
        
        if self.estado == EstadoPeriodo.EN_PROCESO:
            return False, "Hay una asignación en proceso. Espere a que termine."
        
        return True, "Puede cargar archivos."
    
    #CARGA DE ARCHIVOS
    
    def cargar_oferta_academica(self, ruta_archivo: str) -> Tuple[bool, str]:
        """
        Carga el archivo de Oferta Académica.
        El archivo debe contener: OFA_ID, CUS_ID, CAR_NOMBRE_CARRERA, CUS_TOTAL_CUPOS
        """
        puede, mensaje = self.puede_cargar_archivos()
        if not puede:
            return False, mensaje
        
        try:
            if not os.path.exists(ruta_archivo):
                return False, f"El archivo no existe: {ruta_archivo}"
            
            # Intentar leer el archivo
            df = pd.read_excel(ruta_archivo, sheet_name=0, skiprows=1)
            
            # Validar columnas requeridas
            columnas_requeridas = ['OFA_ID', 'CUS_ID', 'CAR_NOMBRE_CARRERA', 'CUS_TOTAL_CUPOS']
            columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
            
            if columnas_faltantes:
                # Intentar sin skiprows
                df = pd.read_excel(ruta_archivo, sheet_name=0)
                columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
                
                if columnas_faltantes:
                    return False, f"Columnas faltantes en el archivo: {', '.join(columnas_faltantes)}"
            
            # Copiar archivo a carpeta del periodo
            nombre_destino = os.path.join(self._carpeta, "Oferta_Academica.xlsx")
            shutil.copy(ruta_archivo, nombre_destino)
            
            self._oferta_df = df
            self.archivo_oferta = nombre_destino
            self.total_cupos_ofertados = int(df['CUS_TOTAL_CUPOS'].sum())
            
            self._actualizar_estado_carga()
            self.guardar()
            
            return True, f"Oferta Académica cargada: {len(df)} carreras, {self.total_cupos_ofertados} cupos totales"
            
        except Exception as e:
            return False, f"Error al cargar Oferta Académica: {str(e)}"
    
    def cargar_postulantes(self, ruta_archivo: str) -> Tuple[bool, str]:
        """
        Carga el archivo de Postulantes.
        El archivo debe contener: IDENTIFICACIÓN, PUNTAJE_POSTULACION, CUS_ID, etc.
        """
        puede, mensaje = self.puede_cargar_archivos()
        if not puede:
            return False, mensaje
        
        try:
            if not os.path.exists(ruta_archivo):
                return False, f"El archivo no existe: {ruta_archivo}"
            
            # Intentar leer el archivo
            df = pd.read_excel(ruta_archivo, sheet_name=0, skiprows=1)
            
            # Validar columnas requeridas
            columnas_requeridas = ['IDENTIFICACIÓN', 'PUNTAJE_POSTULACION', 'CUS_ID']
            columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
            
            if columnas_faltantes:
                # Intentar otras hojas o sin skiprows
                df = pd.read_excel(ruta_archivo, sheet_name=0)
                columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
                
                if columnas_faltantes:
                    # Intentar hoja de postulantes (índice 5 como estaba antes)
                    try:
                        df = pd.read_excel(ruta_archivo, sheet_name=5, skiprows=1)
                        columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
                    except:
                        pass
                
                if columnas_faltantes:
                    return False, f"Columnas faltantes en el archivo: {', '.join(columnas_faltantes)}"
            
            # Copiar archivo a carpeta del periodo
            nombre_destino = os.path.join(self._carpeta, "Postulantes.xlsx")
            shutil.copy(ruta_archivo, nombre_destino)
            
            self._postulantes_df = df
            self.archivo_postulantes = nombre_destino
            self.total_postulantes = len(df['IDENTIFICACIÓN'].unique())
            
            self._actualizar_estado_carga()
            self.guardar()
            
            return True, f"Postulantes cargados: {self.total_postulantes} postulantes únicos"
            
        except Exception as e:
            return False, f"Error al cargar Postulantes: {str(e)}"
    
    def _actualizar_estado_carga(self):
        """Actualiza el estado basado en los archivos cargados"""
        if self._oferta_df is not None and self._postulantes_df is not None:
            self.estado = EstadoPeriodo.DATOS_CARGADOS
            self.fase = FasePeriodo.ASIGNACION
        elif self._oferta_df is not None or self._postulantes_df is not None:
            self.fase = FasePeriodo.CARGA_DATOS
    
    #PROCESO DE ASIGNACIÓN
    
    def ejecutar_asignacion_completa(self, callback_progreso=None) -> Tuple[bool, str, Dict]:
        """
        Ejecuta el proceso completo de asignación.
        
        Este método:
        1. Ejecuta todas las vueltas de asignación permitidas
        2. Actualiza el estado del periodo
        3. Guarda los resultados en archivos

        """
        puede, mensaje = self.puede_asignar()
        if not puede:
            return False, mensaje, {}
        
        try:
            self.estado = EstadoPeriodo.EN_PROCESO
            self.fecha_inicio_asignacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.guardar()
            
            if callback_progreso:
                callback_progreso("Iniciando proceso de asignación...")
            
            estadisticas_totales = {
                'vueltas_ejecutadas': 0,
                'asignados_por_vuelta': [],
                'total_asignados': 0,
                'por_grupo': {},
                'por_carrera': {}
            }
            
            asignaciones_acumuladas = []
            postulantes_asignados = set()
            
            # Ejecutar vueltas de asignación
            for num_vuelta in range(1, self.configuracion.max_vueltas_asignacion + 1):
                if callback_progreso:
                    callback_progreso(f"\n=== VUELTA {num_vuelta} DE ASIGNACIÓN ===")
                
                vuelta = VueltaAsignacion(
                    numero_vuelta=num_vuelta,
                    fecha_inicio=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )
                
                # Filtrar postulantes que ya tienen asignación
                postulantes_disponibles = self._postulantes_df[
                    ~self._postulantes_df['IDENTIFICACIÓN'].astype(str).isin(postulantes_asignados)
                ].copy()
                
                if postulantes_disponibles.empty:
                    if callback_progreso:
                        callback_progreso("No hay más postulantes disponibles.")
                    vuelta.fecha_fin = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    vuelta.completada = True
                    self.vueltas.append(vuelta)
                    break
                
                # Crear motor de asignación
                motor = MotorAsignacion(
                    self._oferta_df,
                    postulantes_disponibles,
                    self.configuracion.porcentajes,
                    self.configuracion.es_instituto
                )
                
                # Ejecutar asignación
                df_asignaciones = motor.ejecutar_asignacion()
                
                if df_asignaciones.empty:
                    if callback_progreso:
                        callback_progreso("No se realizaron asignaciones en esta vuelta.")
                    vuelta.fecha_fin = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    vuelta.completada = True
                    self.vueltas.append(vuelta)
                    break
                
                # Registrar asignaciones
                nuevos_asignados = len(df_asignaciones)
                asignaciones_acumuladas.append(df_asignaciones)
                
                # Actualizar postulantes asignados
                postulantes_asignados.update(df_asignaciones['identificacion'].astype(str).tolist())
                
                # Actualizar vuelta
                vuelta.total_asignados = nuevos_asignados
                vuelta.estadisticas = motor.obtener_estadisticas()
                vuelta.fecha_fin = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                vuelta.completada = True
                
                self.vueltas.append(vuelta)
                
                # Actualizar estadísticas
                estadisticas_totales['vueltas_ejecutadas'] += 1
                estadisticas_totales['asignados_por_vuelta'].append(nuevos_asignados)
                estadisticas_totales['total_asignados'] += nuevos_asignados
                
                if callback_progreso:
                    callback_progreso(f"Vuelta {num_vuelta}: {nuevos_asignados} postulantes asignados")
                
                # Verificar si se asignaron todos o no hubo cambios significativos
                if nuevos_asignados == 0:
                    break
            
            # Consolidar asignaciones
            if asignaciones_acumuladas:
                self._asignaciones_df = pd.concat(asignaciones_acumuladas, ignore_index=True)
                
                # Agregar número de vuelta a cada asignación
                vuelta_idx = 0
                start_idx = 0
                for v in self.vueltas:
                    if v.total_asignados > 0:
                        end_idx = start_idx + v.total_asignados
                        self._asignaciones_df.loc[start_idx:end_idx-1, 'vuelta'] = v.numero_vuelta
                        start_idx = end_idx
                
                # Guardar archivo de asignaciones
                self.archivo_asignaciones = os.path.join(self._carpeta, "Asignaciones.xlsx")
                self._asignaciones_df.to_excel(self.archivo_asignaciones, index=False)
                
                # También guardar en la raíz para compatibilidad
                self._asignaciones_df.to_excel("Asignaciones.xlsx", index=False)
                
                # Calcular estadísticas por grupo
                for grupo in self._asignaciones_df['grupo'].unique():
                    estadisticas_totales['por_grupo'][grupo] = int(
                        self._asignaciones_df[self._asignaciones_df['grupo'] == grupo].shape[0]
                    )
                
                # Calcular estadísticas por carrera
                for carrera in self._asignaciones_df['carrera'].unique():
                    estadisticas_totales['por_carrera'][str(carrera)] = int(
                        self._asignaciones_df[self._asignaciones_df['carrera'] == carrera].shape[0]
                    )
            
            # Actualizar estado del periodo
            self.total_asignados = estadisticas_totales['total_asignados']
            self.total_no_asignados = self.total_postulantes - self.total_asignados
            self.estado = EstadoPeriodo.FINALIZADO
            self.fase = FasePeriodo.ACEPTACION
            self.fecha_fin_asignacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.guardar()
            
            mensaje_final = (
                f"Asignación completada exitosamente.\n"
                f"Vueltas ejecutadas: {estadisticas_totales['vueltas_ejecutadas']}\n"
                f"Total asignados: {self.total_asignados}/{self.total_postulantes}\n"
                f"Sin asignación: {self.total_no_asignados}"
            )
            
            if callback_progreso:
                callback_progreso(f"\n{mensaje_final}")
            
            return True, mensaje_final, estadisticas_totales
            
        except Exception as e:
            self.estado = EstadoPeriodo.DATOS_CARGADOS  # Permitir reintentar
            self.guardar()
            return False, f"Error durante la asignación: {str(e)}", {}
    
    #CIERRE DE PERIODO 
    
    def cerrar_periodo(self) -> Tuple[bool, str]:
        """
        Cierra definitivamente el periodo de asignación.
        Una vez cerrado, no se pueden realizar más operaciones.
        """
        if self.estado == EstadoPeriodo.CERRADO:
            return False, "El periodo ya está cerrado."
        
        if self.estado not in [EstadoPeriodo.FINALIZADO]:
            return False, "El periodo debe estar finalizado antes de cerrarlo."
        
        self.estado = EstadoPeriodo.CERRADO
        self.fase = FasePeriodo.CIERRE
        self.fecha_cierre = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.guardar()
        
        return True, f"Periodo {self.codigo} cerrado exitosamente."
    
    #PERSISTENCIA
    
    def guardar(self):
        """Guarda el estado del periodo en un archivo JSON"""
        datos = {
            'codigo': self.codigo,
            'nombre': self.nombre,
            'estado': self.estado.value,
            'fase': self.fase.value,
            'fecha_creacion': self.fecha_creacion,
            'fecha_inicio_asignacion': self.fecha_inicio_asignacion,
            'fecha_fin_asignacion': self.fecha_fin_asignacion,
            'fecha_cierre': self.fecha_cierre,
            'configuracion': {
                'porcentajes': self.configuracion.porcentajes,
                'es_instituto': self.configuracion.es_instituto,
                'max_vueltas_asignacion': self.configuracion.max_vueltas_asignacion,
                'dias_aceptacion': self.configuracion.dias_aceptacion
            },
            'vueltas': [
                {
                    'numero_vuelta': v.numero_vuelta,
                    'fecha_inicio': v.fecha_inicio,
                    'fecha_fin': v.fecha_fin,
                    'total_asignados': v.total_asignados,
                    'cupos_liberados': v.cupos_liberados,
                    'estadisticas': v.estadisticas,
                    'completada': v.completada
                }
                for v in self.vueltas
            ],
            'archivo_oferta': self.archivo_oferta,
            'archivo_postulantes': self.archivo_postulantes,
            'archivo_asignaciones': self.archivo_asignaciones,
            'total_cupos_ofertados': self.total_cupos_ofertados,
            'total_postulantes': self.total_postulantes,
            'total_asignados': self.total_asignados,
            'total_no_asignados': self.total_no_asignados
        }
        
        ruta_json = os.path.join(self._carpeta, "periodo.json")
        with open(ruta_json, 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
    
    @classmethod
    def cargar(cls, codigo: str) -> Optional['PeriodoAsignacion']:
        """Carga un periodo desde su archivo JSON"""
        carpeta = os.path.join(cls.CARPETA_PERIODOS, codigo.replace("-", "_"))
        ruta_json = os.path.join(carpeta, "periodo.json")
        
        if not os.path.exists(ruta_json):
            return None
        
        try:
            with open(ruta_json, 'r', encoding='utf-8') as f:
                datos = json.load(f)
            
            config = ConfiguracionPeriodo(
                porcentajes=datos['configuracion']['porcentajes'],
                es_instituto=datos['configuracion']['es_instituto'],
                max_vueltas_asignacion=datos['configuracion']['max_vueltas_asignacion'],
                dias_aceptacion=datos['configuracion']['dias_aceptacion']
            )
            
            vueltas = [
                VueltaAsignacion(
                    numero_vuelta=v['numero_vuelta'],
                    fecha_inicio=v['fecha_inicio'],
                    fecha_fin=v['fecha_fin'],
                    total_asignados=v['total_asignados'],
                    cupos_liberados=v['cupos_liberados'],
                    estadisticas=v['estadisticas'],
                    completada=v['completada']
                )
                for v in datos['vueltas']
            ]
            
            periodo = cls(
                codigo=datos['codigo'],
                nombre=datos['nombre'],
                estado=EstadoPeriodo(datos['estado']),
                fase=FasePeriodo(datos['fase']),
                fecha_creacion=datos['fecha_creacion'],
                fecha_inicio_asignacion=datos['fecha_inicio_asignacion'],
                fecha_fin_asignacion=datos['fecha_fin_asignacion'],
                fecha_cierre=datos['fecha_cierre'],
                configuracion=config,
                vueltas=vueltas,
                archivo_oferta=datos['archivo_oferta'],
                archivo_postulantes=datos['archivo_postulantes'],
                archivo_asignaciones=datos['archivo_asignaciones'],
                total_cupos_ofertados=datos['total_cupos_ofertados'],
                total_postulantes=datos['total_postulantes'],
                total_asignados=datos['total_asignados'],
                total_no_asignados=datos['total_no_asignados']
            )
            
            # Cargar DataFrames si existen los archivos
            if periodo.archivo_oferta and os.path.exists(periodo.archivo_oferta):
                periodo._oferta_df = pd.read_excel(periodo.archivo_oferta)
            if periodo.archivo_postulantes and os.path.exists(periodo.archivo_postulantes):
                periodo._postulantes_df = pd.read_excel(periodo.archivo_postulantes)
            if periodo.archivo_asignaciones and os.path.exists(periodo.archivo_asignaciones):
                periodo._asignaciones_df = pd.read_excel(periodo.archivo_asignaciones)
            
            return periodo
            
        except Exception as e:
            print(f"Error al cargar periodo: {e}")
            return None
    
    @classmethod
    def listar_periodos(cls) -> List[Dict]:
        """Lista todos los periodos disponibles"""
        periodos = []
        
        if not os.path.exists(cls.CARPETA_PERIODOS):
            return periodos
        
        for carpeta in os.listdir(cls.CARPETA_PERIODOS):
            ruta_json = os.path.join(cls.CARPETA_PERIODOS, carpeta, "periodo.json")
            if os.path.exists(ruta_json):
                try:
                    with open(ruta_json, 'r', encoding='utf-8') as f:
                        datos = json.load(f)
                    periodos.append({
                        'codigo': datos['codigo'],
                        'nombre': datos['nombre'],
                        'estado': datos['estado'],
                        'fecha_creacion': datos['fecha_creacion'],
                        'total_asignados': datos.get('total_asignados', 0)
                    })
                except:
                    pass
        
        # Ordenar por fecha de creación (más reciente primero)
        periodos.sort(key=lambda x: x['fecha_creacion'], reverse=True)
        return periodos
    
    #CONSULTAS
    
    def obtener_resumen(self) -> Dict:
        """Obtiene un resumen del estado del periodo"""
        return {
            'codigo': self.codigo,
            'nombre': self.nombre,
            'estado': self.estado.value,
            'fase': self.fase.name,
            'fecha_creacion': self.fecha_creacion,
            'fecha_inicio_asignacion': self.fecha_inicio_asignacion,
            'fecha_fin_asignacion': self.fecha_fin_asignacion,
            'fecha_cierre': self.fecha_cierre,
            'total_cupos_ofertados': self.total_cupos_ofertados,
            'total_postulantes': self.total_postulantes,
            'total_asignados': self.total_asignados,
            'total_no_asignados': self.total_no_asignados,
            'vueltas_ejecutadas': len(self.vueltas),
            'archivos_cargados': {
                'oferta': self.archivo_oferta is not None,
                'postulantes': self.archivo_postulantes is not None,
                'asignaciones': self.archivo_asignaciones is not None
            }
        }
    
    def obtener_asignaciones(self) -> Optional[pd.DataFrame]:
        """Retorna el DataFrame de asignaciones"""
        return self._asignaciones_df
    
    def obtener_oferta(self) -> Optional[pd.DataFrame]:
        """Retorna el DataFrame de oferta académica"""
        return self._oferta_df
    
    def obtener_postulantes(self) -> Optional[pd.DataFrame]:
        """Retorna el DataFrame de postulantes"""
        return self._postulantes_df


#GESTOR DE PERIODOS

class GestorPeriodos:
    """
    Gestiona los periodos de asignación del sistema.
    Singleton pattern para acceso global.
    """
    _instance = None
    _periodo_activo: Optional[PeriodoAsignacion] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def crear_periodo(self, codigo: str, nombre: str = "") -> Tuple[bool, str, Optional[PeriodoAsignacion]]:
        """Crea un nuevo periodo de asignación"""
        # Verificar si ya existe
        periodo_existente = PeriodoAsignacion.cargar(codigo)
        if periodo_existente:
            return False, f"Ya existe un periodo con el código {codigo}", None
        
        # Crear nuevo periodo
        periodo = PeriodoAsignacion(codigo=codigo, nombre=nombre)
        periodo.guardar()
        
        self._periodo_activo = periodo
        return True, f"Periodo {codigo} creado exitosamente", periodo
    
    def abrir_periodo(self, codigo: str) -> Tuple[bool, str, Optional[PeriodoAsignacion]]:
        """Abre un periodo existente"""
        periodo = PeriodoAsignacion.cargar(codigo)
        if not periodo:
            return False, f"No se encontró el periodo {codigo}", None
        
        self._periodo_activo = periodo
        return True, f"Periodo {codigo} abierto", periodo
    
    def obtener_periodo_activo(self) -> Optional[PeriodoAsignacion]:
        """Retorna el periodo activo actual"""
        return self._periodo_activo
    
    def establecer_periodo_activo(self, periodo: PeriodoAsignacion):
        """Establece el periodo activo"""
        self._periodo_activo = periodo
    
    def listar_periodos(self) -> List[Dict]:
        """Lista todos los periodos disponibles"""
        return PeriodoAsignacion.listar_periodos()
    
    def obtener_ultimo_periodo_abierto(self) -> Optional[PeriodoAsignacion]:
        """Obtiene el último periodo que no esté cerrado"""
        periodos = self.listar_periodos()
        for p in periodos:
            if p['estado'] != EstadoPeriodo.CERRADO.value:
                return PeriodoAsignacion.cargar(p['codigo'])
        return None
