import pandas as pd
from typing import Dict, List, Set
from abc import ABC, abstractmethod
from enum import Enum



# ENUMERACIÓN DE GRUPOS (Necesaria para las estrategias)

class GrupoAsignacion(Enum):
    """
    Grupos de asignación según normativa SENESCYT.
    El valor numérico determina el orden de prioridad.
    """
    POLITICA_CUOTAS = 1           # 5-10% de la oferta
    VULNERABILIDAD = 2             # Al menos 10%
    MERITO_ACADEMICO = 3           # Al menos 20%
    OTROS_RECONOCIMIENTOS = 4      # Máximo 2%
    BACHILLERES_PUEBLOS = 5        # Máximo 10%
    BACHILLERES_ULTIMO_ANIO = 6    # Al menos 20%
    POBLACION_GENERAL = 7          # Al menos 20%


# INTERFACES DE ESTRATEGIA (Clases Abstractas)

class EstrategiaClasificacion(ABC):
    """
    Strategy Interface: Define cómo clasificar postulantes en grupos.
    
    Permite implementar diferentes criterios de clasificación:
    - SENESCYT (oficial)
    - Solo mérito
    - Personalizada
    """
    
    @abstractmethod
    def clasificar(self, postulante: Dict, bachilleres_participaron: Set[str]) -> List[GrupoAsignacion]:
        """
        Clasifica al postulante en los grupos a los que pertenece.
        
        Args:
            postulante: Diccionario con datos del postulante
            bachilleres_participaron: Set de IDs de bachilleres que ya participaron
            
        Returns:
            Lista de GrupoAsignacion a los que pertenece
        """
        pass


class EstrategiaDesempate(ABC):
    """
    Strategy Interface: Define cómo resolver empates entre postulantes.
    
    Permite implementar diferentes criterios de ordenamiento:
    - SENESCYT (puntaje, vulnerabilidad, fecha)
    - Solo puntaje
    - Personalizada
    """
    
    @abstractmethod
    def resolver(self, postulantes: pd.DataFrame) -> pd.DataFrame:
        """
        Ordena los postulantes resolviendo empates.
        
        Args:
            postulantes: DataFrame con postulantes a ordenar
            
        Returns:
            DataFrame ordenado según criterios de desempate
        """
        pass


class EstrategiaSegmentacion(ABC):
    """
    Strategy Interface: Define cómo segmentar los cupos por grupo.
    
    Permite implementar diferentes distribuciones:
    - Porcentual (configurable)
    - Institutos (fija según Art. 53)
    - Personalizada
    """
    
    @abstractmethod
    def segmentar(self, total_cupos: int, porcentajes: Dict[str, float]) -> Dict[GrupoAsignacion, int]:
        """
        Segmenta los cupos totales según los porcentajes.
        
        Args:
            total_cupos: Total de cupos a distribuir
            porcentajes: Diccionario con porcentajes por grupo
            
        Returns:
            Diccionario con cupos por GrupoAsignacion
        """
        pass


# 
# IMPLEMENTACIONES DE CLASIFICACIÓN
# 

class ClasificacionSENESCYT(EstrategiaClasificacion):
    """
    Clasificación oficial según normativa SENESCYT (Art. 52).
    
    Evalúa múltiples criterios para determinar a qué grupos
    pertenece cada postulante.
    """
    
    def clasificar(self, postulante: Dict, bachilleres_participaron: Set[str]) -> List[GrupoAsignacion]:
        grupos = []
        identificacion = str(postulante.get('IDENTIFICACIÓN', ''))
        
        # 1. Política de cuotas (grupos históricamente excluidos)
        segmento = postulante.get('SEGMENTO_ASPIRANTE')
        if segmento == 2 or str(segmento) == '2':
            grupos.append(GrupoAsignacion.POLITICA_CUOTAS)
        
        # 2. Vulnerabilidad socioeconómica
        if postulante.get('VULNERABILIDAD_SOCIOECONOMICA') == 'SI':
            grupos.append(GrupoAsignacion.VULNERABILIDAD)
        
        # 3. Mérito académico (cuadro de honor)
        if postulante.get('CUADRO_HONOR') == 'SI' or postulante.get('MERITO_ACADEMICO') == 'SI':
            grupos.append(GrupoAsignacion.MERITO_ACADEMICO)
        
        # 4. Otros reconocimientos al mérito
        if postulante.get('OTROS_RECONOCIMIENTOS') == 'SI':
            grupos.append(GrupoAsignacion.OTROS_RECONOCIMIENTOS)
        
        # 5. Bachilleres del último régimen escolar
        es_bachiller_ultimo = postulante.get('BACHILLER_ULTIMO_ANIO') == 'SI'
        es_pueblos_nacionalidades = postulante.get('PUEBLOS_NACIONALIDADES') == 'SI'
        
        if es_bachiller_ultimo and identificacion not in bachilleres_participaron:
            if es_pueblos_nacionalidades:
                grupos.append(GrupoAsignacion.BACHILLERES_PUEBLOS)
            grupos.append(GrupoAsignacion.BACHILLERES_ULTIMO_ANIO)
        
        # TODOS participan en población general
        grupos.append(GrupoAsignacion.POBLACION_GENERAL)
        
        return grupos


class ClasificacionSoloMerito(EstrategiaClasificacion):
    """
    Clasificación simplificada: Solo por mérito (sin grupos especiales).
    
    Útil para procesos de admisión donde no aplican cuotas
    o para pruebas del sistema.
    """
    
    def clasificar(self, postulante: Dict, bachilleres_participaron: Set[str]) -> List[GrupoAsignacion]:
        # Todos los postulantes van directo a población general
        return [GrupoAsignacion.POBLACION_GENERAL]


class ClasificacionPorSegmento(EstrategiaClasificacion):
    """
    Clasificación basada solo en el segmento del aspirante.
    
    Útil cuando solo se tienen datos básicos de los postulantes.
    """
    
    def clasificar(self, postulante: Dict, bachilleres_participaron: Set[str]) -> List[GrupoAsignacion]:
        grupos = []
        
        segmento = postulante.get('SEGMENTO_ASPIRANTE')
        if segmento == 2 or str(segmento) == '2':
            grupos.append(GrupoAsignacion.POLITICA_CUOTAS)
        
        grupos.append(GrupoAsignacion.POBLACION_GENERAL)
        return grupos



# IMPLEMENTACIONES DE DESEMPATE

class DesempateSENESCYT(EstrategiaDesempate):
    """
    Desempate oficial según Art. 54 SENESCYT.
    
    Orden de criterios:
    1. Puntaje (mayor a menor)
    2. Índice de vulnerabilidad (menor a mayor)
    3. Fecha de inscripción (más antigua primero)
    """
    
    def resolver(self, postulantes: pd.DataFrame) -> pd.DataFrame:
        if postulantes.empty:
            return postulantes
        
        columnas_orden = ['PUNTAJE_POSTULACION']
        orden_asc = [False]  # Mayor puntaje primero
        
        if 'INDICE_VULNERABILIDAD' in postulantes.columns:
            columnas_orden.append('INDICE_VULNERABILIDAD')
            orden_asc.append(True)  # Menor vulnerabilidad primero
        
        if 'FECHA_INSCRIPCION' in postulantes.columns:
            columnas_orden.append('FECHA_INSCRIPCION')
            orden_asc.append(True)  # Más antigua primero
        elif 'FECHA_POSTULACION' in postulantes.columns:
            columnas_orden.append('FECHA_POSTULACION')
            orden_asc.append(True)
        
        return postulantes.sort_values(columnas_orden, ascending=orden_asc)


class DesempatePorPuntaje(EstrategiaDesempate):
    """
    Desempate simple: Solo ordena por puntaje.
    
    Útil para procesos simplificados o cuando no hay
    datos adicionales de desempate.
    """
    
    def resolver(self, postulantes: pd.DataFrame) -> pd.DataFrame:
        if postulantes.empty:
            return postulantes
        return postulantes.sort_values('PUNTAJE_POSTULACION', ascending=False)


class DesempatePorPrioridad(EstrategiaDesempate):
    """
    Desempate considerando la prioridad de elección.
    
    Orden de criterios:
    1. Puntaje (mayor a menor)
    2. Prioridad de elección (menor a mayor, 1 = primera opción)
    """
    
    def resolver(self, postulantes: pd.DataFrame) -> pd.DataFrame:
        if postulantes.empty:
            return postulantes
        
        columnas = ['PUNTAJE_POSTULACION']
        orden = [False]
        
        if 'PRIORIDAD_ELECCION_CARRERA' in postulantes.columns:
            columnas.append('PRIORIDAD_ELECCION_CARRERA')
            orden.append(True)  # Menor prioridad primero (1 es mejor)
        
        return postulantes.sort_values(columnas, ascending=orden)


# IMPLEMENTACIONES DE SEGMENTACIÓN

class SegmentacionPorcentual(EstrategiaSegmentacion):
    """
    Segmentación estándar: Distribuye cupos según porcentajes.
    
    Los cupos restantes (por redondeo) van a población general.
    """
    
    def segmentar(self, total_cupos: int, porcentajes: Dict[str, float]) -> Dict[GrupoAsignacion, int]:
        cupos_segmentados = {
            GrupoAsignacion.POLITICA_CUOTAS: int(total_cupos * porcentajes.get('politica_cuotas', 0)),
            GrupoAsignacion.VULNERABILIDAD: int(total_cupos * porcentajes.get('vulnerabilidad', 0)),
            GrupoAsignacion.MERITO_ACADEMICO: int(total_cupos * porcentajes.get('merito_academico', 0)),
            GrupoAsignacion.OTROS_RECONOCIMIENTOS: int(total_cupos * porcentajes.get('otros_reconocimientos', 0)),
            GrupoAsignacion.BACHILLERES_PUEBLOS: int(total_cupos * porcentajes.get('bachilleres_pueblos', 0)),
            GrupoAsignacion.BACHILLERES_ULTIMO_ANIO: int(total_cupos * porcentajes.get('bachilleres_ultimo', 0)),
            GrupoAsignacion.POBLACION_GENERAL: int(total_cupos * porcentajes.get('poblacion_general', 0))
        }
        
        # Ajustar cupos restantes a población general
        cupos_asignados = sum(cupos_segmentados.values())
        if cupos_asignados < total_cupos:
            cupos_segmentados[GrupoAsignacion.POBLACION_GENERAL] += (total_cupos - cupos_asignados)
        
        return cupos_segmentados


class SegmentacionInstitutos(EstrategiaSegmentacion):
    """
    Segmentación para Institutos Técnicos/Tecnológicos (Art. 53).
    
    Usa porcentajes fijos según normativa, ignorando los
    porcentajes proporcionados.
    """
    
    PORCENTAJES_FIJOS = {
        'politica_cuotas': 0.10,       # 10%
        'vulnerabilidad': 0.20,         # 20%
        'merito_academico': 0.20,       # 20%
        'otros_reconocimientos': 0.0,   # No aplica
        'bachilleres_pueblos': 0.05,    # 5%
        'bachilleres_ultimo': 0.25,     # 25%
        'poblacion_general': 0.20       # 20%
    }
    
    def segmentar(self, total_cupos: int, porcentajes: Dict[str, float] = None) -> Dict[GrupoAsignacion, int]:
        # Ignora porcentajes recibidos y usa los fijos del Art. 53
        return SegmentacionPorcentual().segmentar(total_cupos, self.PORCENTAJES_FIJOS)


class SegmentacionEquitativa(EstrategiaSegmentacion):
    """
    Segmentación equitativa: Distribuye cupos de forma igual.
    
    Útil para pruebas o procesos donde todos los grupos
    tienen igual importancia.
    """
    
    def segmentar(self, total_cupos: int, porcentajes: Dict[str, float] = None) -> Dict[GrupoAsignacion, int]:
        grupos = list(GrupoAsignacion)
        cupos_por_grupo = total_cupos // len(grupos)
        cupos_restantes = total_cupos % len(grupos)
        
        resultado = {grupo: cupos_por_grupo for grupo in grupos}
        
        # Los restantes van a población general
        resultado[GrupoAsignacion.POBLACION_GENERAL] += cupos_restantes
        
        return resultado


class SegmentacionSoloPoblacionGeneral(EstrategiaSegmentacion):
    """
    Segmentación simple: Todo a población general.
    
    Útil cuando no se aplican cuotas especiales.
    """
    
    def segmentar(self, total_cupos: int, porcentajes: Dict[str, float] = None) -> Dict[GrupoAsignacion, int]:
        return {
            GrupoAsignacion.POLITICA_CUOTAS: 0,
            GrupoAsignacion.VULNERABILIDAD: 0,
            GrupoAsignacion.MERITO_ACADEMICO: 0,
            GrupoAsignacion.OTROS_RECONOCIMIENTOS: 0,
            GrupoAsignacion.BACHILLERES_PUEBLOS: 0,
            GrupoAsignacion.BACHILLERES_ULTIMO_ANIO: 0,
            GrupoAsignacion.POBLACION_GENERAL: total_cupos
        }
