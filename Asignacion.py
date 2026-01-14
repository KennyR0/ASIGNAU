import pandas as pd
from typing import Optional, Dict, List, Set
from datetime import datetime
from Estrategias import (GrupoAsignacion, EstrategiaClasificacion,EstrategiaDesempate, 
    EstrategiaSegmentacion,
    ClasificacionSENESCYT,
    DesempateSENESCYT,
    SegmentacionPorcentual,
    SegmentacionInstitutos
)
from Observadores import ObservadorAsignacion

# MOTOR DE ASIGNACIÓN (Strategy + Observer + Dependency Inversion)
class MotorAsignacion:
    """
    Motor de asignación de cupos    

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
                 porcentajes: Dict[str, float] = None, es_instituto: bool = False,
                 estrategia_clasificacion: EstrategiaClasificacion = None,
                 estrategia_desempate: EstrategiaDesempate = None,
                 estrategia_segmentacion: EstrategiaSegmentacion = None,
                 observador: ObservadorAsignacion = None):
        """
        Constructor con Inyección de Dependencias .
        """
        self.oferta_df = oferta_df
        self.postulaciones_df = self._normalizar_columnas(postulaciones_df)
        self.es_instituto = es_instituto
        
        # INYECCIÓN DE ESTRATEGIAS (Strategy + DIP) 
        self._estrategia_clasificacion = estrategia_clasificacion or ClasificacionSENESCYT()
        self._estrategia_desempate = estrategia_desempate or DesempateSENESCYT()
        self._estrategia_segmentacion = estrategia_segmentacion or (
            SegmentacionInstitutos() if es_instituto else SegmentacionPorcentual()
        )
        
        #OBSERVER PATTERN 
        self._observadores: List[ObservadorAsignacion] = []
        if observador:
            self._observadores.append(observador)
        
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
    
    #MÉTODOS PARA CAMBIAR ESTRATEGIAS EN RUNTIME
    
    def set_estrategia_clasificacion(self, estrategia: EstrategiaClasificacion):
        """Permite cambiar la estrategia de clasificación en tiempo de ejecución (OCP)"""
        self._estrategia_clasificacion = estrategia
    
    def set_estrategia_desempate(self, estrategia: EstrategiaDesempate):
        """Permite cambiar la estrategia de desempate en tiempo de ejecución (OCP)"""
        self._estrategia_desempate = estrategia
    
    def set_estrategia_segmentacion(self, estrategia: EstrategiaSegmentacion):
        """Permite cambiar la estrategia de segmentación en tiempo de ejecución (OCP)"""
        self._estrategia_segmentacion = estrategia
    
    #MÉTODOS DEL PATRÓN OBSERVER 
    
    def agregar_observador(self, observador: ObservadorAsignacion):
        """Agrega un observador para recibir notificaciones (Observer Pattern)"""
        if observador not in self._observadores:
            self._observadores.append(observador)
    
    def remover_observador(self, observador: ObservadorAsignacion):
        """Remueve un observador de la lista"""
        if observador in self._observadores:
            self._observadores.remove(observador)
    
    def _notificar_inicio(self, total_carreras: int, total_postulantes: int):
        """Notifica a todos los observadores el inicio de la asignación"""
        for obs in self._observadores:
            obs.on_inicio_asignacion(total_carreras, total_postulantes)
    
    def _notificar_grupo(self, grupo: GrupoAsignacion, asignados: int, restantes: int):
        """Notifica a todos los observadores que se procesó un grupo"""
        for obs in self._observadores:
            obs.on_grupo_procesado(grupo, asignados, restantes)
    
    def _notificar_completado(self, total_asignados: int, estadisticas: Dict):
        """Notifica a todos los observadores que la asignación terminó"""
        for obs in self._observadores:
            obs.on_asignacion_completada(total_asignados, estadisticas)
    
    def _notificar_error(self, mensaje: str):
        """Notifica a todos los observadores de un error"""
        for obs in self._observadores:
            obs.on_error(mensaje)
    
    #MÉTODOS AUXILIARES 
    
    def _normalizar_columnas(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normaliza los nombres de columnas para evitar errores por tildes o variaciones.
        """
        if df is None or df.empty:
            return df
        
        # Mapeo de variantes a nombre estándar
        columnas_mapa = {}
        for col in df.columns:
            col_upper = str(col).upper()
            # Buscar coincidencias
            if 'IDENTIFICACI' in col_upper and 'IDENTIFICACIÓN' not in df.columns:
                columnas_mapa[col] = 'IDENTIFICACIÓN'
            elif 'PUNTAJE' in col_upper and 'PUNTAJE_POSTULACION' not in df.columns:
                columnas_mapa[col] = 'PUNTAJE_POSTULACION'
            elif 'PRIORIDAD' in col_upper and 'PRIORIDAD_ELECCION_CARRERA' not in df.columns:
                columnas_mapa[col] = 'PRIORIDAD_ELECCION_CARRERA'
            elif (col_upper == 'CUS_ID' or col_upper == 'CUS') and 'CUS_ID' not in df.columns:
                columnas_mapa[col] = 'CUS_ID'
        
        if columnas_mapa:
            df = df.rename(columns=columnas_mapa)
        
        return df
    
    def validar_porcentajes(self) -> bool:
        """
        Valida que los porcentajes cumplan con los límites del SENESCYT.
        Retorna True si son válidos, False si hay errores.
        """
        # Validar límites según Art. 52 (IES públicas)
        if not self.es_instituto:
            # Política de cuotas: entre 5% y 10%
            if not (0.05 <= self.porcentajes.get('politica_cuotas', 0) <= 0.10):
                return False
            
            # Vulnerabilidad: al menos 10%
            if self.porcentajes.get('vulnerabilidad', 0) < 0.10:
                return False
            
            # Mérito académico: al menos 20%
            if self.porcentajes.get('merito_academico', 0) < 0.20:
                return False
            
            # Otros reconocimientos: máximo 2%
            if self.porcentajes.get('otros_reconocimientos', 0) > 0.02:
                return False
            
            # Bachilleres pueblos: máximo 10%
            if self.porcentajes.get('bachilleres_pueblos', 0) > 0.10:
                return False
            
            # Bachilleres último año: al menos 20%
            if self.porcentajes.get('bachilleres_ultimo', 0) < 0.20:
                return False
            
            # Población general: al menos 20%
            if self.porcentajes.get('poblacion_general', 0) < 0.20:
                return False
        
        return True
    
    def segmentar_oferta(self):
        """
        Segmenta la oferta de cupos según la estrategia de segmentación configurada.
        Utiliza el patrón Strategy para permitir diferentes formas de segmentación.
        """
        # IMPORTANTE: Agrupar por CUS_ID primero para evitar sobrescrituras
        # si hay múltiples filas por carrera
        oferta_agrupada = self.oferta_df.groupby('CUS_ID').agg({
            'OFA_ID': 'first',
            'CAR_NOMBRE_CARRERA': 'first',
            'CUS_TOTAL_CUPOS': 'sum'  # SUMA los cupos si hay múltiples registros
        }).reset_index()
        
        for _, oferta in oferta_agrupada.iterrows():
            ofa_id = str(oferta.get('OFA_ID', ''))
            cus_id = str(oferta.get('CUS_ID', ''))
            carrera = str(oferta.get('CAR_NOMBRE_CARRERA', ''))
            total_cupos = int(oferta.get('CUS_TOTAL_CUPOS', 0))
            
            # USAR ESTRATEGIA DE SEGMENTACIÓN (Strategy Pattern)
            cupos_segmentados = self._estrategia_segmentacion.segmentar(total_cupos, self.porcentajes)
            
            self.cupos_por_carrera[cus_id] = cupos_segmentados.copy()
            self.cupos_originales_por_carrera[cus_id] = cupos_segmentados.copy()
            self.ofa_id_por_carrera[cus_id] = ofa_id
            self.carrera_por_cus[cus_id] = carrera
    
    def clasificar_postulante(self, postulante: Dict) -> List[GrupoAsignacion]:
        """
        Clasifica al postulante usando la estrategia de clasificación configurada.
        Utiliza el patrón Strategy para permitir diferentes criterios de clasificación.
        """
        # USAR ESTRATEGIA DE CLASIFICACIÓN (Strategy Pattern)
        return self._estrategia_clasificacion.clasificar(postulante, self.bachilleres_participaron)
    
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
        Resuelve empates usando la estrategia de desempate configurada.
        Utiliza el patrón Strategy para permitir diferentes criterios de ordenamiento.
        """
        # USAR ESTRATEGIA DE DESEMPATE (Strategy Pattern)
        return self._estrategia_desempate.resolver(postulantes)
    
    def obtener_postulantes_grupo(self, grupo: GrupoAsignacion) -> pd.DataFrame:
        """Obtiene los postulantes que pertenecen a un grupo específico"""
                # VALIDACIÓN: Verificar que tenemos los datos necesarios
        if self.postulaciones_df.empty:
            print("ERROR: DataFrame de postulaciones está vacío")
            return pd.DataFrame()
        
        if 'IDENTIFICACIÓN' not in self.postulaciones_df.columns:
            print(f"ERROR: Columna 'IDENTIFICACIÓN' no encontrada")
            print(f"Columnas disponibles: {list(self.postulaciones_df.columns)}")
            return pd.DataFrame()
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
        
        # Si no hay postulantes para este grupo, salir (es normal)
        if postulantes_df.empty:
            return
        
        # Validar que tenemos la columna IDENTIFICACIÓN
        if 'IDENTIFICACIÓN' not in postulantes_df.columns:
            print(f"ERROR en asignar_por_grupo ({grupo.name}): Columna IDENTIFICACIÓN no encontrada")
            print(f"   Columnas disponibles: {list(postulantes_df.columns)[:5]}...")
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
                
                # VALIDACIÓN CRÍTICA: Verificar que el CUS_ID existe en cupos_por_carrera
                if cus_id not in self.cupos_por_carrera:
                    continue
                
                # VALIDACIÓN CRÍTICA: Verificar que hay cupos disponibles en ESTE grupo específico
                cupos_disponibles = self.cupos_por_carrera[cus_id].get(grupo, 0)
                if cupos_disponibles <= 0:
                    # No hay cupos en este grupo, continuar con la siguiente carrera
                    continue
                
                # VALIDACIÓN: Asegurar que no sobrepasamos los cupos totales
                total_cupos_carrera = sum(self.cupos_por_carrera[cus_id].values())
                if total_cupos_carrera <= 0:
                    # No hay cupos disponibles en esta carrera (total)
                    continue
                
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
                
                # Actualizar estado - CRÍTICO: Descontar del grupo específico
                self.cupos_por_carrera[cus_id][grupo] -= 1
                self.postulantes_asignados.add(identificacion)
                
                # Marcar bachiller como participado (Art. 52 numeral 5)
                if grupo in [GrupoAsignacion.BACHILLERES_PUEBLOS, GrupoAsignacion.BACHILLERES_ULTIMO_AÑO]:
                    self.bachilleres_participaron.add(identificacion)
                
                asignado = True
                break
            
            # Si no se asignó, el postulante participará en el siguiente grupo
            if not asignado:
                # Marcar bachiller como participado aunque no haya obtenido cupo
                if grupo in [GrupoAsignacion.BACHILLERES_PUEBLOS, GrupoAsignacion.BACHILLERES_ULTIMO_AÑO]:
                    self.bachilleres_participaron.add(identificacion)
    
    def liberar_cupos_no_usados(self):
        """
        Libera cupos no usados y los pasa a población general.
        
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
    
    def _asignar_restantes_a_cupos_disponibles(self):
        """
        Asigna postulantes que aún no tienen cupo a cualquier carrera que tenga cupos disponibles.
        Esto asegura que se llenen todos los cupos posibles.
        """
        # Obtener identificaciones únicas de postulantes sin asignación
        todas_identificaciones = set(self.postulaciones_df['IDENTIFICACIÓN'].astype(str).unique())
        identificaciones_sin_asignar = todas_identificaciones - self.postulantes_asignados
        
        if not identificaciones_sin_asignar:
            return
        
        # Para cada postulante sin asignar, obtener su mejor puntaje
        postulantes_info = []
        for ident in identificaciones_sin_asignar:
            postulaciones = self.postulaciones_df[
                self.postulaciones_df['IDENTIFICACIÓN'].astype(str) == ident
            ]
            if not postulaciones.empty and 'PUNTAJE_POSTULACION' in postulaciones.columns:
                puntaje = postulaciones['PUNTAJE_POSTULACION'].max()
                postulantes_info.append((ident, puntaje))
        
        # Ordenar por puntaje descendente
        postulantes_info.sort(key=lambda x: x[1], reverse=True)
        
        asignados_en_ronda = 0
        for identificacion, puntaje in postulantes_info:
            if identificacion in self.postulantes_asignados:
                continue
            
            # Obtener postulaciones de este postulante ordenadas por prioridad
            postulaciones_postulante = self.postulaciones_df[
                self.postulaciones_df['IDENTIFICACIÓN'].astype(str) == identificacion
            ]
            
            if 'PRIORIDAD_ELECCION_CARRERA' in postulaciones_postulante.columns:
                postulaciones_postulante = postulaciones_postulante.sort_values('PRIORIDAD_ELECCION_CARRERA')
            
            # Intentar asignar a cualquier carrera con cupos (revisar TODOS los grupos, no solo población general)
            for _, postulacion in postulaciones_postulante.iterrows():
                cus_id = str(postulacion['CUS_ID'])
                
                if cus_id not in self.cupos_por_carrera:
                    continue
                
                # Verificar cupos disponibles en CUALQUIER grupo
                total_cupos_disponibles = sum(self.cupos_por_carrera[cus_id].values())
                
                if total_cupos_disponibles > 0:
                    # Encontrar el primer grupo con cupos disponibles
                    grupo_asignacion = None
                    for grupo in [GrupoAsignacion.POBLACION_GENERAL] + list(GrupoAsignacion):
                        if self.cupos_por_carrera[cus_id].get(grupo, 0) > 0:
                            grupo_asignacion = grupo
                            break
                    
                    if grupo_asignacion is None:
                        continue
                    
                    ofa_id = self.ofa_id_por_carrera.get(cus_id, str(postulacion.get('OFA_ID', '')))
                    carrera = self.carrera_por_cus.get(cus_id, str(postulacion.get('NOMBRE_CARRERA', '')))
                    
                    self.asignaciones.append({
                        'identificacion': identificacion,
                        'cus_id': cus_id,
                        'ofa_id': ofa_id,
                        'carrera': carrera,
                        'puntaje': float(puntaje),
                        'grupo': grupo_asignacion.name,
                        'prioridad': int(postulacion.get('PRIORIDAD_ELECCION_CARRERA', 1)),
                        'fecha_asignacion': datetime.now().strftime("%d/%m/%Y %H:%M"),
                        'estado': 'ASIGNADO'
                    })
                    
                    self.cupos_por_carrera[cus_id][grupo_asignacion] -= 1
                    self.postulantes_asignados.add(identificacion)
                    asignados_en_ronda += 1
                    break
        
        if asignados_en_ronda > 0:
            print(f"   ✓ Ronda adicional: {asignados_en_ronda} postulantes asignados")
    
    def ejecutar_asignacion(self) -> pd.DataFrame:
        """
        Ejecuta el proceso completo de asignación siguiendo el orden
        establecido por la SENESCYT.
        
        Proceso:
        1. Segmentar oferta según porcentajes
        2. Asignar por grupos en orden (1-6)
        3. Liberar cupos no usados a población general
        4. Asignar población general
        5. Validar que no se asignaron más que los disponibles
        6. Retornar resultados
        """
        # Validar porcentajes - detener si no cumplen límites
        if not self.validar_porcentajes():
            raise ValueError("Porcentajes incorrectos: no cumplen con los limites del SENESCYT")
        
        # 1. Segmentar la oferta
        self.segmentar_oferta()
        
        # 2. Orden de asignación según Artículo 52
        orden_grupos = [
            GrupoAsignacion.POLITICA_CUOTAS,
            GrupoAsignacion.VULNERABILIDAD,
            GrupoAsignacion.MERITO_ACADEMICO,
            GrupoAsignacion.OTROS_RECONOCIMIENTOS,
            GrupoAsignacion.BACHILLERES_PUEBLOS,
            GrupoAsignacion.BACHILLERES_ULTIMO_AÑO,
        ]
        
        # 3. Asignar por cada grupo (excepto población general)
        for grupo in orden_grupos:
            self.asignar_por_grupo(grupo)
        
        # 4. Liberar cupos no usados a población general
        self.liberar_cupos_no_usados()
        
        # 5. Asignar población general (incluye cupos liberados)
        self.asignar_por_grupo(GrupoAsignacion.POBLACION_GENERAL)
        
        # 5.1 SEGUNDA PASADA: Intentar asignar postulantes restantes a cualquier carrera con cupos
        # Esto cubre el caso donde un postulante no obtuvo su primera opción
        self._asignar_restantes_a_cupos_disponibles()
        
        # DIAGNÓSTICO: Mostrar cupos restantes
        cupos_restantes_total = sum(
            sum(cupos.values()) 
            for cupos in self.cupos_por_carrera.values()
        )
        postulantes_sin_asignar = len(set(self.postulaciones_df['IDENTIFICACIÓN'].astype(str).unique()) - self.postulantes_asignados)
        
        if cupos_restantes_total > 0:
            print(f"\nDIAGNÓSTICO DE ASIGNACIÓN:")
            print(f"   Cupos restantes sin usar: {cupos_restantes_total}")
            print(f"   Postulantes sin asignación: {postulantes_sin_asignar}")
            
            if postulantes_sin_asignar > 0 and cupos_restantes_total > 0:
                print(f"   NOTA: Hay cupos disponibles pero los postulantes restantes no postularon a esas carreras")
        
        # 6. VALIDACIÓN CRÍTICA: Verificar que no se asignaron más cupos que disponibles
        df_asignaciones = pd.DataFrame(self.asignaciones)
        
        # Calcular total de cupos disponibles
        total_cupos_ofertados = sum(
            sum(cupos.values()) 
            for cupos in self.cupos_originales_por_carrera.values()
        )
        
        total_asignados = len(df_asignaciones)
        
        if total_asignados > total_cupos_ofertados:
            print(f"\n  ALERTA DE VALIDACIÓN:")
            print(f"   Total cupos ofertados: {total_cupos_ofertados}")
            print(f"   Total asignados: {total_asignados}")
            print(f"   EXCESO: {total_asignados - total_cupos_ofertados}")
            print(f"\n   Se aplicará corrección...")
            
            # Aplicar corrección: eliminar asignaciones excedentes
            # Priorizamos mantener asignaciones de grupos con menores cupos (más selectivos)
            df_asignaciones = self._corregir_asignaciones_excedentes(df_asignaciones, total_cupos_ofertados)
            self.asignaciones = df_asignaciones.to_dict('records')
        
        # 7. Retornar DataFrame con asignaciones
        return pd.DataFrame(self.asignaciones)
    
    def _corregir_asignaciones_excedentes(self, df_asignaciones: pd.DataFrame, total_cupos_permitidos: int) -> pd.DataFrame:
        """
        Corrige las asignaciones eliminando las excedentes de forma controlada.
        Mantiene las asignaciones más antiguas (o de grupos prioritarios) y elimina las más nuevas.
        """
        # Agrupamos por carrera y verificamos excesos
        excedentes_por_carrera = []
        
        for cus_id in self.cupos_originales_por_carrera.keys():
            cus_id_str = str(cus_id)
            df_carrera = df_asignaciones[df_asignaciones['cus_id'] == cus_id_str]
            cupos_disponibles = sum(self.cupos_originales_por_carrera[cus_id].values())
            
            if len(df_carrera) > cupos_disponibles:
                # Hay exceso en esta carrera
                exceso = len(df_carrera) - cupos_disponibles
                
                # Mantener solo los primeros (más antiguos/prioritarios)
                indices_a_eliminar = df_carrera.index[cupos_disponibles:]
                excedentes_por_carrera.extend(indices_a_eliminar.tolist())
        
        # Eliminar las asignaciones excedentes
        df_corregido = df_asignaciones.drop(excedentes_por_carrera)
        
        print(f"   Asignaciones eliminadas: {len(excedentes_por_carrera)}")
        print(f"   Asignaciones finales: {len(df_corregido)}")
        
        return df_corregido
    
    def obtener_estadisticas(self) -> Dict:
        """Retorna estadísticas del proceso de asignación"""
        df = pd.DataFrame(self.asignaciones)
        
        if df.empty:
            return {'total_asignados': 0}
        
        # Calcular total de cupos disponibles
        total_cupos_ofertados = sum(
            sum(cupos.values()) 
            for cupos in self.cupos_originales_por_carrera.values()
        )
        
        return {
            'total_asignados': len(df),
            'total_cupos_ofertados': total_cupos_ofertados,
            'diferencia': total_cupos_ofertados - len(df),
            'por_grupo': df['grupo'].value_counts().to_dict() if not df.empty else {},
            'por_carrera': df['carrera'].value_counts().to_dict() if not df.empty else {},
            'cupos_restantes': {
                cus_id: sum(cupos.values()) 
                for cus_id, cupos in self.cupos_por_carrera.items()
            }
        }


# GESTIÓN DE ACEPTACIÓN DE CUPOS 
class GestorAceptacion:
    """
    Gestiona el proceso de aceptación de cupos.
    """
    
    def __init__(self, archivo_asignaciones=None):
        if archivo_asignaciones:
            self.archivo = archivo_asignaciones
        else:
            # Intentar usar el archivo del periodo activo
            self.archivo = self._obtener_archivo_periodo_activo()
    
    def _obtener_archivo_periodo_activo(self):
        """Obtiene la ruta del archivo de asignaciones del periodo activo"""
        try:
            from PeriodoAsignacion import GestorPeriodos, PeriodoAsignacion
            
            gestor = GestorPeriodos()
            periodo = gestor.obtener_periodo_activo()
            
            if periodo and periodo.archivo_asignaciones:
                return periodo.archivo_asignaciones
            
            # Buscar en periodos disponibles
            periodos = PeriodoAsignacion.listar_periodos()
            for p in periodos:
                if p['estado'] in ['FINALIZADO', 'EN_PROCESO']:
                    periodo_cargado = PeriodoAsignacion.cargar(p['codigo'])
                    if periodo_cargado and periodo_cargado.archivo_asignaciones:
                        return periodo_cargado.archivo_asignaciones
        except:
            pass
        
        # Fallback
        return "Asignaciones.xlsx"
    
    def registrar_aceptacion(self, identificacion: str, cus_id: str, fecha_aceptacion: str) -> bool:
        """Registra la aceptación de un cupo (Art. 56)"""
        try:
            df = pd.read_excel(self.archivo)
            
            # Convertir columnas a string para comparación
            df['identificacion'] = df['identificacion'].astype(str)
            if 'cus_id' in df.columns:
                df['cus_id'] = df['cus_id'].astype(str)
            
            # Verificar que no tenga otro cupo aceptado (Art. 56)
            cupos_aceptados = df[
                (df['identificacion'] == str(identificacion)) & 
                (df['estado'] == 'ACEPTADO')
            ]
            
            if not cupos_aceptados.empty:
                print(f"El postulante {identificacion} ya tiene un cupo aceptado")
                return False
            
            # Buscar la asignación
            # Si cus_id está vacío o es None, buscar solo por identificación
            if cus_id and str(cus_id).strip():
                mask = (df['identificacion'] == str(identificacion)) & (df['cus_id'] == str(cus_id))
            else:
                mask = (df['identificacion'] == str(identificacion))
            
            if mask.any():
                df.loc[mask, 'estado'] = 'ACEPTADO'
                df.loc[mask, 'fecha_aceptacion'] = fecha_aceptacion
                df.to_excel(self.archivo, index=False)
                return True
            
            return False
        except Exception as e:
            print(f"Error al registrar aceptación: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def verificar_aceptacion(self, identificacion: str) -> Optional[Dict]:
        """Verifica si un postulante tiene un cupo aceptado"""
        try:
            df = pd.read_excel(self.archivo)
            # Convertir a string para comparación
            df['identificacion'] = df['identificacion'].astype(str)
            asignacion = df[(df['identificacion'] == str(identificacion)) & 
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
