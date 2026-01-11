import pandas as pd
from typing import Optional, Dict, List, Set
import os
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


# ====== ENUMERACIONES DE ASIGNACIÓN ======
class GrupoAsignacion(Enum):
    """Orden de asignación según Artículo 52"""
    POLITICA_CUOTAS = 1           # 5-10% de la oferta
    VULNERABILIDAD = 2             # Al menos 10%
    MERITO_ACADEMICO = 3           # Al menos 20%
    OTROS_RECONOCIMIENTOS = 4      # Máximo 2%
    BACHILLERES_PUEBLOS = 5        # Máximo 10%
    BACHILLERES_ULTIMO_ANIO = 6    # Al menos 20%
    POBLACION_GENERAL = 7          # Al menos 20%


class EstadoCupo(Enum):
    DISPONIBLE = "DISPONIBLE"
    ASIGNADO = "ASIGNADO"
    ACEPTADO = "ACEPTADO"
    LIBERADO = "LIBERADO"


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
    Cumple con:
    - Orden de segmentos establecido
    - Reasignación a grupos siguientes si no obtiene cupo
    - Liberación de cupos no usados a población general
    - Criterios de desempate (Artículo 54)
    - Bachilleres participan una sola vez en su grupo
    """
    
    # Porcentajes según Artículo 52 (para IES públicas)
    PORCENTAJES_IES = {
        'politica_cuotas': (0.05, 0.10),      # Entre 5% y 10%
        'vulnerabilidad': (0.10, 1.0),         # Al menos 10%
        'merito_academico': (0.20, 1.0),       # Al menos 20%
        'otros_reconocimientos': (0.0, 0.02),  # Máximo 2%
        'bachilleres_pueblos': (0.0, 0.10),    # Máximo 10%
        'bachilleres_ultimo': (0.20, 1.0),     # Al menos 20%
        'poblacion_general': (0.20, 1.0)       # Al menos 20%
    }
    
    # Porcentajes según Artículo 53 (para institutos técnicos/tecnológicos)
    PORCENTAJES_INSTITUTOS = {
        'politica_cuotas': 0.10,       # Art. 53.1: 10%
        'vulnerabilidad': 0.20,         # Art. 53.2: 20%
        'merito_academico': 0.20,       # Art. 53.3: 20%
        'otros_reconocimientos': 0.0,   # Art. 53.4: No aplica
        'bachilleres_pueblos': 0.05,    # Art. 53.5a: 5%
        'bachilleres_ultimo': 0.25,     # Art. 53.5b: 25%
        'poblacion_general': 0.20       # Art. 53.6: al menos 20%
    }
    
    def __init__(self, oferta_df: pd.DataFrame, postulaciones_df: pd.DataFrame, 
                 porcentajes: Dict[str, float] = None, es_instituto: bool = False):
        self.oferta_df = oferta_df
        self.postulaciones_df = postulaciones_df
        self.es_instituto = es_instituto
        
        # Usar porcentajes proporcionados o los predeterminados
        if porcentajes:
            self.porcentajes = porcentajes
        elif es_instituto:
            self.porcentajes = self.PORCENTAJES_INSTITUTOS.copy()
        else:
            # Porcentajes por defecto para IES (usar valores intermedios)
            self.porcentajes = {
                'politica_cuotas': 0.10,
                'vulnerabilidad': 0.10,
                'merito_academico': 0.20,
                'otros_reconocimientos': 0.02,
                'bachilleres_pueblos': 0.10,
                'bachilleres_ultimo': 0.20,
                'poblacion_general': 0.20
            }
        
        self.asignaciones = []
        self.cupos_por_carrera: Dict[str, Dict[GrupoAsignacion, int]] = {}
        self.cupos_originales_por_carrera: Dict[str, Dict[GrupoAsignacion, int]] = {}
        self.ofa_id_por_carrera: Dict[str, str] = {}
        self.carrera_por_cus: Dict[str, str] = {}
        
        # Tracking de postulantes
        self.postulantes_asignados: Set[str] = set()
        self.bachilleres_participaron: Set[str] = set()  # Art. 52 numeral 5
        self.postulantes_por_grupo: Dict[str, List[GrupoAsignacion]] = {}
    
    def validar_porcentajes(self) -> bool:
        """
        Valida que los porcentajes cumplan con los límites del Artículo 52 y 53.
        Retorna True si son válidos, False si hay errores.
        """
        errores = []
        advertencias = []
        
        # Validar límites según Art. 52 (IES públicas)
        if not self.es_instituto:
            # Política de cuotas: entre 5% y 10%
            if not (0.05 <= self.porcentajes.get('politica_cuotas', 0) <= 0.10):
                advertencias.append("Política de cuotas debe estar entre 5% y 10%")
            
            # Vulnerabilidad: al menos 10%
            if self.porcentajes.get('vulnerabilidad', 0) < 0.10:
                advertencias.append("Vulnerabilidad debe ser al menos 10%")
            
            # Mérito académico: al menos 20%
            if self.porcentajes.get('merito_academico', 0) < 0.20:
                advertencias.append("Mérito académico debe ser al menos 20%")
            
            # Otros reconocimientos: máximo 2%
            if self.porcentajes.get('otros_reconocimientos', 0) > 0.02:
                advertencias.append("Otros reconocimientos no debe exceder 2%")
            
            # Bachilleres pueblos: máximo 10%
            if self.porcentajes.get('bachilleres_pueblos', 0) > 0.10:
                advertencias.append("Bachilleres pueblos no debe exceder 10%")
            
            # Bachilleres último año: al menos 20%
            if self.porcentajes.get('bachilleres_ultimo', 0) < 0.20:
                advertencias.append("Bachilleres último año debe ser al menos 20%")
            
            # Población general: al menos 20%
            if self.porcentajes.get('poblacion_general', 0) < 0.20:
                advertencias.append("Población general debe ser al menos 20%")
        
        # Los porcentajes deben sumar aproximadamente 100%
        total = sum(self.porcentajes.values())
        if total < 0.90 or total > 1.10:
            advertencias.append(f"Los porcentajes suman {total*100:.1f}%, deberían sumar ~100%")
        
        # Mostrar advertencias
        for adv in advertencias:
            print(f"Advertencia Art. 52/53: {adv}")
        
        return len(errores) == 0
    
    def segmentar_oferta(self):
        """Segmenta la oferta de cupos según los porcentajes establecidos"""
        for _, oferta in self.oferta_df.iterrows():
            ofa_id = str(oferta.get('OFA_ID', ''))
            cus_id = str(oferta.get('CUS_ID', ''))
            carrera = str(oferta.get('CAR_NOMBRE_CARRERA', ''))
            total_cupos = int(oferta.get('CUS_TOTAL_CUPOS', 0))
            
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
            
            self.cupos_por_carrera[cus_id] = cupos_segmentados.copy()
            self.cupos_originales_por_carrera[cus_id] = cupos_segmentados.copy()
            self.ofa_id_por_carrera[cus_id] = ofa_id
            self.carrera_por_cus[cus_id] = carrera
    
    def clasificar_postulante(self, postulante: Dict) -> List[GrupoAsignacion]:
        """
        Clasifica al postulante en los grupos a los que pertenece.
        Según Art. 52: participa inicialmente en el grupo que más le favorece.
        Si no obtiene cupo, será reasignado a los siguientes grupos.
        """
        grupos = []
        identificacion = str(postulante.get('IDENTIFICACIÓN', ''))
        
        # Art. 52: Si tiene título de tercer nivel, solo población general
        if postulante.get('TIENE_TITULO_TERCER_NIVEL') == 'SI':
            return [GrupoAsignacion.POBLACION_GENERAL]
        
        # 1. Política de cuotas (grupos históricamente excluidos)
        if postulante.get('SEGMENTO_ASPIRANTE') == 2:
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
        # Art. 52 numeral 5: Bachilleres participan una sola vez en su grupo
        es_bachiller_ultimo = postulante.get('BACHILLER_ULTIMO_ANIO') == 'SI'
        es_pueblos_nacionalidades = postulante.get('PUEBLOS_NACIONALIDADES') == 'SI'
        
        if es_bachiller_ultimo and identificacion not in self.bachilleres_participaron:
            # Art. 52.5a: La asignación inicia por pueblos y nacionalidades
            if es_pueblos_nacionalidades:
                grupos.append(GrupoAsignacion.BACHILLERES_PUEBLOS)
            # Art. 52.5b: Continúa con los demás bachilleres
            # Todos los bachilleres del último año participan en este grupo
            grupos.append(GrupoAsignacion.BACHILLERES_ULTIMO_ANIO)
        
        # 6. Siempre puede participar en población general
        grupos.append(GrupoAsignacion.POBLACION_GENERAL)
        
        return grupos
    
    def obtener_grupo_mas_favorable(self, grupos: List[GrupoAsignacion]) -> GrupoAsignacion:
        """
        Determina el grupo más favorable para el postulante.
        El orden de prioridad está dado por el valor del enum (menor = más favorable).
        """
        if not grupos:
            return GrupoAsignacion.POBLACION_GENERAL
        return min(grupos, key=lambda g: g.value)
    
    def resolver_empate(self, postulantes: pd.DataFrame) -> pd.DataFrame:
        """
        Resuelve empates según Artículo 54:
        1. Índice de vulnerabilidad (menor a mayor)
        2. Fecha de inscripción (más antigua a más reciente)
        """
        # Ordenar por puntaje (desc), luego vulnerabilidad (asc), luego fecha (asc)
        columnas_orden = ['PUNTAJE_POSTULACION']
        orden_asc = [False]
        
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
    
    def obtener_postulantes_grupo(self, grupo: GrupoAsignacion) -> pd.DataFrame:
        """Obtiene los postulantes que pertenecen a un grupo específico"""
        postulantes_grupo = []
        
        for _, postulante in self.postulaciones_df.iterrows():
            identificacion = str(postulante['IDENTIFICACIÓN'])
            
            # Saltar si ya está asignado
            if identificacion in self.postulantes_asignados:
                continue
            
            # Clasificar si no se ha hecho antes
            if identificacion not in self.postulantes_por_grupo:
                grupos = self.clasificar_postulante(postulante.to_dict())
                self.postulantes_por_grupo[identificacion] = grupos
            
            grupos_postulante = self.postulantes_por_grupo[identificacion]
            
            # Verificar si pertenece al grupo actual
            if grupo in grupos_postulante:
                # Verificar si este es el grupo más favorable que aún puede usar
                grupos_disponibles = [g for g in grupos_postulante if g.value >= grupo.value]
                if grupos_disponibles and min(grupos_disponibles, key=lambda g: g.value) == grupo:
                    postulantes_grupo.append(postulante)
        
        if not postulantes_grupo:
            return pd.DataFrame()
        
        return pd.DataFrame(postulantes_grupo)
    
    def asignar_por_grupo(self, grupo: GrupoAsignacion):
        """Asigna cupos a los postulantes de un grupo específico"""
        postulantes_df = self.obtener_postulantes_grupo(grupo)
        
        if postulantes_df.empty:
            return
        
        # Ordenar por puntaje y resolver empates
        postulantes_ordenados = self.resolver_empate(postulantes_df)
        
        for _, postulante in postulantes_ordenados.iterrows():
            identificacion = str(postulante['IDENTIFICACIÓN'])
            
            # Verificar si ya tiene asignación (doble check)
            if identificacion in self.postulantes_asignados:
                continue
            
            # Obtener postulaciones ordenadas por prioridad
            postulaciones_postulante = self.postulaciones_df[
                self.postulaciones_df['IDENTIFICACIÓN'].astype(str) == identificacion
            ].sort_values('PRIORIDAD_ELECCION_CARRERA')
            
            # Intentar asignar según prioridad de elección de carrera
            asignado = False
            for _, postulacion in postulaciones_postulante.iterrows():
                cus_id = str(postulacion['CUS_ID'])
                
                if cus_id not in self.cupos_por_carrera:
                    continue
                
                # Verificar si hay cupos disponibles en este grupo
                if self.cupos_por_carrera[cus_id].get(grupo, 0) > 0:
                    ofa_id = self.ofa_id_por_carrera.get(cus_id, str(postulacion.get('OFA_ID', '')))
                    carrera = self.carrera_por_cus.get(cus_id, str(postulacion.get('NOMBRE_CARRERA', '')))
                    
                    # Registrar asignación
                    self.asignaciones.append({
                        'identificacion': identificacion,
                        'cus_id': cus_id,
                        'ofa_id': ofa_id,
                        'carrera': carrera,
                        'puntaje': float(postulante['PUNTAJE_POSTULACION']),
                        'grupo': grupo.name,
                        'prioridad': int(postulacion['PRIORIDAD_ELECCION_CARRERA']),
                        'fecha_asignacion': datetime.now().strftime("%d/%m/%Y %H:%M"),
                        'estado': 'ASIGNADO'
                    })
                    
                    # Actualizar estado
                    self.cupos_por_carrera[cus_id][grupo] -= 1
                    self.postulantes_asignados.add(identificacion)
                    
                    # Marcar bachiller como participado (Art. 52 numeral 5)
                    if grupo in [GrupoAsignacion.BACHILLERES_PUEBLOS, GrupoAsignacion.BACHILLERES_ULTIMO_ANIO]:
                        self.bachilleres_participaron.add(identificacion)
                    
                    asignado = True
                    break
            
            # Si no se asignó, el postulante participará en el siguiente grupo
            if not asignado:
                # Marcar bachiller como participado aunque no haya obtenido cupo
                if grupo in [GrupoAsignacion.BACHILLERES_PUEBLOS, GrupoAsignacion.BACHILLERES_ULTIMO_ANIO]:
                    self.bachilleres_participaron.add(identificacion)
    
    def liberar_cupos_no_usados(self):
        """
        Libera cupos no usados y los pasa a población general.
        Según Art. 52: si no se cumple el porcentaje por falta de demanda,
        los cupos se liberan a población general.
        """
        for cus_id in self.cupos_por_carrera:
            cupos_liberados = 0
            
            for grupo in GrupoAsignacion:
                if grupo == GrupoAsignacion.POBLACION_GENERAL:
                    continue
                
                cupos_restantes = self.cupos_por_carrera[cus_id].get(grupo, 0)
                if cupos_restantes > 0:
                    cupos_liberados += cupos_restantes
                    self.cupos_por_carrera[cus_id][grupo] = 0
            
            # Agregar cupos liberados a población general
            if cupos_liberados > 0:
                self.cupos_por_carrera[cus_id][GrupoAsignacion.POBLACION_GENERAL] += cupos_liberados
    
    def ejecutar_asignacion(self) -> pd.DataFrame:
        """
        Ejecuta el proceso completo de asignación siguiendo el orden
        establecido en el Artículo 52.
        
        Proceso:
        1. Segmentar oferta según porcentajes
        2. Asignar por grupos en orden (1-6)
        3. Liberar cupos no usados a población general
        4. Asignar población general
        5. Retornar resultados
        """
        # Validar porcentajes
        self.validar_porcentajes()
        
        # 1. Segmentar la oferta
        self.segmentar_oferta()
        
        # 2. Orden de asignación según Artículo 52
        orden_grupos = [
            GrupoAsignacion.POLITICA_CUOTAS,
            GrupoAsignacion.VULNERABILIDAD,
            GrupoAsignacion.MERITO_ACADEMICO,
            GrupoAsignacion.OTROS_RECONOCIMIENTOS,
            GrupoAsignacion.BACHILLERES_PUEBLOS,
            GrupoAsignacion.BACHILLERES_ULTIMO_ANIO,
        ]
        
        # 3. Asignar por cada grupo (excepto población general)
        for grupo in orden_grupos:
            self.asignar_por_grupo(grupo)
        
        # 4. Liberar cupos no usados a población general
        self.liberar_cupos_no_usados()
        
        # 5. Asignar población general (incluye cupos liberados)
        self.asignar_por_grupo(GrupoAsignacion.POBLACION_GENERAL)
        
        # 6. Retornar DataFrame con asignaciones
        return pd.DataFrame(self.asignaciones)
    
    def obtener_estadisticas(self) -> Dict:
        """Retorna estadísticas del proceso de asignación"""
        df = pd.DataFrame(self.asignaciones)
        
        if df.empty:
            return {'total_asignados': 0}
        
        return {
            'total_asignados': len(df),
            'por_grupo': df['grupo'].value_counts().to_dict(),
            'por_carrera': df['carrera'].value_counts().to_dict(),
            'cupos_restantes': {
                cus_id: sum(cupos.values()) 
                for cus_id, cupos in self.cupos_por_carrera.items()
            }
        }


# ====== CLASE REPORTE ======
class Reporte:
    """Genera reportes del proceso de asignación en formato Excel"""
    
    def __init__(self, carpeta_reportes: str = "Reportes"):
        self.carpeta_reportes = carpeta_reportes
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
            archivo = os.path.join(self.carpeta_reportes, f"Reporte_Todas_Carreras_{fecha_hora}.xlsx")
            reporte = {'carreras': {}}
            
            if guardar_excel:
                with pd.ExcelWriter(archivo, engine='openpyxl') as writer:
                    carreras_unicas = asignaciones_df['carrera'].unique()
                    
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
                    
                    for i, carr in enumerate(carreras_unicas[:30]):
                        df_carr = asignaciones_df[asignaciones_df['carrera'] == carr]
                        nombre_hoja = carr[:31].replace('/', '-').replace('\\', '-')
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
                
                for grupo in grupos_unicos:
                    df_grupo = asignaciones_df[asignaciones_df['grupo'] == grupo]
                    nombre_hoja = grupo[:31]
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
    """
    Gestiona el proceso de aceptación de cupos según Artículo 56.
    - El cupo aceptado no puede ser modificado ni anulado
    - No se puede renunciar al cupo
    - Solo se puede aceptar un único cupo
    """
    
    def __init__(self, archivo_asignaciones="Asignaciones.xlsx"):
        self.archivo = archivo_asignaciones
    
    def registrar_aceptacion(self, identificacion: str, cus_id: str, fecha_aceptacion: str) -> bool:
        """Registra la aceptación de un cupo (Art. 56)"""
        try:
            df = pd.read_excel(self.archivo)
            
            # Verificar que no tenga otro cupo aceptado (Art. 56)
            cupos_aceptados = df[
                (df['identificacion'] == identificacion) & 
                (df['estado'] == 'ACEPTADO')
            ]
            
            if not cupos_aceptados.empty:
                print(f"El postulante {identificacion} ya tiene un cupo aceptado")
                return False
            
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
    
    def liberar_cupos_no_aceptados(self, fecha_limite: datetime) -> int:
        """
        Libera automáticamente cupos no aceptados (Art. 56).
        Retorna el número de cupos liberados.
        """
        try:
            df = pd.read_excel(self.archivo)
            
            # Convertir fecha de asignación a datetime
            df['fecha_asignacion_dt'] = pd.to_datetime(df['fecha_asignacion'], format='%d/%m/%Y %H:%M')
            
            # Encontrar cupos no aceptados pasada la fecha límite
            mask = (df['estado'] == 'ASIGNADO') & (df['fecha_asignacion_dt'] < fecha_limite)
            cupos_liberados = mask.sum()
            
            # Actualizar estado
            df.loc[mask, 'estado'] = 'LIBERADO'
            df.loc[mask, 'fecha_liberacion'] = datetime.now().strftime("%d/%m/%Y %H:%M")
            
            # Guardar cambios
            df.drop(columns=['fecha_asignacion_dt'], inplace=True)
            df.to_excel(self.archivo, index=False)
            
            return cupos_liberados
        except Exception as e:
            print(f"Error al liberar cupos: {e}")
            return 0
    
    def puede_participar_siguiente_proceso(self, identificacion: str) -> bool:
        """
        Verifica si el postulante puede participar en el siguiente proceso.
        Art. 56: quienes acepten cupo no pueden participar en el siguiente proceso.
        """
        try:
            df = pd.read_excel(self.archivo)
            tiene_cupo_aceptado = df[
                (df['identificacion'] == identificacion) & 
                (df['estado'] == 'ACEPTADO')
            ]
            
            return tiene_cupo_aceptado.empty
        except Exception as e:
            print(f"Error al verificar participación: {e}")
            return True
