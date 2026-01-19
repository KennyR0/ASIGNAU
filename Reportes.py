import pandas as pd
import os
from datetime import datetime
from typing import Dict


class Reporte:
    """
    Genera reportes del proceso en formato Excel.
    
    Responsabilidades:
    - Generar reportes completos con estadísticas
    - Reportes por carrera
    - Reportes por grupo de asignación
    - Listas de asignados
    
    """
    
    def __init__(self, carpeta_reportes: str = "Reportes"):
        self.carpeta_reportes = carpeta_reportes
        if not os.path.exists(carpeta_reportes):
            os.makedirs(carpeta_reportes)
    
    def _obtener_timestamp(self) -> str:
        """Genera un timestamp para nombres de archivo"""
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _crear_ruta_archivo(self, prefijo: str) -> str:
        """Crea la ruta completa para un archivo de reporte"""
        return os.path.join(
            self.carpeta_reportes, 
            f"{prefijo}_{self._obtener_timestamp()}.xlsx"
        )
    
    def generar_reporte_completo(self, asignaciones_df: pd.DataFrame, 
                                  guardar_excel: bool = True) -> Dict:
        """
        Genera un reporte completo con estadísticas y lo guarda en Excel.
        
        Args:
            asignaciones_df: DataFrame con las asignaciones
            guardar_excel: Si debe guardar el archivo Excel
            
        Returns:
            Dict con estadísticas y ruta del archivo generado
        """
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
            archivo = self._crear_ruta_archivo("Reporte_General")
            
            with pd.ExcelWriter(archivo, engine='openpyxl') as writer:
                # Hoja 1: Resumen general
                resumen_data = {
                    'Métrica': [
                        'Total Asignaciones', 
                        'Puntaje Promedio', 
                        'Puntaje Máximo', 
                        'Puntaje Mínimo'
                    ],
                    'Valor': [
                        reporte['total_asignaciones'], 
                        round(reporte['puntaje_promedio'], 2),
                        reporte['puntaje_maximo'], 
                        reporte['puntaje_minimo']
                    ]
                }
                pd.DataFrame(resumen_data).to_excel(
                    writer, sheet_name='Resumen', index=False
                )
                
                # Hoja 2: Asignaciones por grupo
                df_grupos = pd.DataFrame(
                    list(reporte['por_grupo'].items()), 
                    columns=['Grupo', 'Cantidad']
                )
                df_grupos.to_excel(writer, sheet_name='Por_Grupo', index=False)
                
                # Hoja 3: Asignaciones por carrera
                df_carreras = pd.DataFrame(
                    list(reporte['por_carrera'].items()), 
                    columns=['Carrera', 'Cantidad']
                )
                df_carreras.to_excel(writer, sheet_name='Por_Carrera', index=False)
                
                # Hoja 4: Lista completa de asignaciones
                asignaciones_df.to_excel(
                    writer, sheet_name='Asignaciones_Detalle', index=False
                )
            
            reporte['archivo_generado'] = archivo
        
        return reporte
    
    def generar_reporte_por_carrera(self, asignaciones_df: pd.DataFrame, 
                                     carrera: str = None, 
                                     guardar_excel: bool = True) -> Dict:
        """
        Genera reporte específico de una carrera o todas las carreras.
        
        Args:
            asignaciones_df: DataFrame con las asignaciones
            carrera: Nombre de la carrera específica (None para todas)
            guardar_excel: Si debe guardar el archivo Excel
            
        Returns:
            Dict con estadísticas y ruta del archivo generado
        """
        if asignaciones_df.empty:
            return {'error': 'No hay asignaciones para generar reporte'}
        
        if carrera:
            return self._reporte_carrera_especifica(
                asignaciones_df, carrera, guardar_excel
            )
        else:
            return self._reporte_todas_carreras(asignaciones_df, guardar_excel)
    
    def _reporte_carrera_especifica(self, asignaciones_df: pd.DataFrame, 
                                     carrera: str, 
                                     guardar_excel: bool) -> Dict:
        """Genera reporte para una carrera específica"""
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
            nombre_archivo = carrera.replace(' ', '_').replace('/', '-')[:30]
            archivo = self._crear_ruta_archivo(f"Reporte_{nombre_archivo}")
            
            with pd.ExcelWriter(archivo, engine='openpyxl') as writer:
                df_carrera.to_excel(writer, sheet_name='Asignados', index=False)
                df_grupos = pd.DataFrame(
                    list(reporte['por_grupo'].items()), 
                    columns=['Grupo', 'Cantidad']
                )
                df_grupos.to_excel(writer, sheet_name='Por_Grupo', index=False)
            
            reporte['archivo_generado'] = archivo
        
        return reporte
    
    def _reporte_todas_carreras(self, asignaciones_df: pd.DataFrame, 
                                 guardar_excel: bool) -> Dict:
        """Genera reporte para todas las carreras"""
        reporte = {'carreras': {}}
        
        if guardar_excel:
            archivo = self._crear_ruta_archivo("Reporte_Todas_Carreras")
            
            with pd.ExcelWriter(archivo, engine='openpyxl') as writer:
                carreras_unicas = asignaciones_df['carrera'].unique()
                
                # Crear resumen
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
                
                pd.DataFrame(resumen_list).to_excel(
                    writer, sheet_name='Resumen_Carreras', index=False
                )
                
                # Hojas por carrera (máximo 30 para evitar límites de Excel)
                for i, carr in enumerate(carreras_unicas[:30]):
                    df_carr = asignaciones_df[asignaciones_df['carrera'] == carr]
                    nombre_hoja = carr[:31].replace('/', '-').replace('\\', '-')
                    df_carr.to_excel(writer, sheet_name=nombre_hoja, index=False)
            
            reporte['archivo_generado'] = archivo
        
        return reporte
    
    def generar_reporte_por_grupo(self, asignaciones_df: pd.DataFrame, 
                                   guardar_excel: bool = True) -> Dict:
        """
        Genera reporte por grupos de asignación.
        
        Args:
            asignaciones_df: DataFrame con las asignaciones
            guardar_excel: Si debe guardar el archivo Excel
            
        Returns:
            Dict con estadísticas por grupo y ruta del archivo generado
        """
        if asignaciones_df.empty:
            return {'error': 'No hay asignaciones para generar reporte'}
        
        reporte = {
            'por_grupo': asignaciones_df['grupo'].value_counts().to_dict(),
            'detalle_por_grupo': {}
        }
        
        if guardar_excel:
            archivo = self._crear_ruta_archivo("Reporte_Por_Grupos")
            
            with pd.ExcelWriter(archivo, engine='openpyxl') as writer:
                grupos_unicos = asignaciones_df['grupo'].unique()
                
                # Crear resumen
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
                
                pd.DataFrame(resumen_list).to_excel(
                    writer, sheet_name='Resumen_Grupos', index=False
                )
                
                # Hojas por grupo
                for grupo in grupos_unicos:
                    df_grupo = asignaciones_df[asignaciones_df['grupo'] == grupo]
                    nombre_hoja = str(grupo)[:31]
                    df_grupo.to_excel(writer, sheet_name=nombre_hoja, index=False)
            
            reporte['archivo_generado'] = archivo
        
        return reporte

    def generar_matriz_asignacion(self, asignaciones_df: pd.DataFrame,
                                   oferta_df: pd.DataFrame,
                                   postulantes_df: pd.DataFrame,
                                   carpeta_periodo: str = None) -> Dict:
        """
        Genera la matriz de asignación oficial con todos los datos combinados.
        """
        if asignaciones_df.empty:
            return {'error': 'No hay asignaciones para generar matriz', 'archivo': None}
        
        try:
            # Crear copia para no modificar el original
            matriz = asignaciones_df.copy()
            
            # Normalizar tipos de datos para merge
            matriz['cus_id'] = matriz['cus_id'].astype(str)
            matriz['identificacion'] = matriz['identificacion'].astype(str)
            
            if 'CUS_ID' in oferta_df.columns:
                oferta_df = oferta_df.copy()
                oferta_df['CUS_ID'] = oferta_df['CUS_ID'].astype(str)
            
            if 'IDENTIFICACIÓN' in postulantes_df.columns:
                postulantes_df = postulantes_df.copy()
                postulantes_df['IDENTIFICACIÓN'] = postulantes_df['IDENTIFICACIÓN'].astype(str)
            
            # Columnas de la oferta académica a incluir
            columnas_oferta = {
                'AREA_NOMBRE': 'CAMPO_AMPLIO',
                'NIVEL': 'NIVEL',
                'IES_NOMBRE_INSTIT': 'FACULTAD',
                'DESCRIPCION_TIPO_CUPO': 'TIPO_OFERTA',
                'OFA_ID': 'ID_OFERTA_ULEAI',
                'IES_ID_SNIESE': 'ID_OFERTA_SENESCYT',
                'CUS_ID': 'CUS_ID',
                'CUS_TOTAL_CUPOS': 'TOTAL_CUPOS',
                'CAR_NOMBRE_CARRERA': 'CARRERA',
                'MODALIDAD': 'MODALIDAD',
                'JORNADA': 'JORNADA',
                'PRO_NOMBRE': 'PROVINCIA',
                'CAN_NOMBRE': 'CANTON'
            }
            
            # Columnas de postulantes a incluir
            columnas_postulantes = {
                'IDENTIFICACIÓN': 'IDENTIFICACION',
                'PUNTAJE_POSTULACION': 'NOTA_POSTULACION',
                'SEGMENTO_ASPIRANTE': 'SEGMENTO_ASPIRANTE',
                'PRIORIDAD_ELECCION_CARRERA': 'ORDEN_PRIORIDAD',
                'FECHA_POSTULACION': 'FECHA_POSTULACION',
                'INSTANCIA_POSTULACION': 'INSTANCIA_POSTULACION',
                'VULNERABILIDAD_SOCIOECONOMICA': 'VULNERABILIDAD_SOCIOECONOMICA',
                'CUADRO_HONOR': 'MERITO_ACADEMICO',
                'PUEBLOS_NACIONALIDADES': 'BACHILLER_PUEBLOS_NACIONALIDADES',
                'BACHILLER_ULTIMO_ANIO': 'BACHILLER_ULTIMO_ANIO',
                'SEXO': 'SEXO',
                'AUTOIDENTIFICACION': 'AUTOIDENTIFICACION'
            }
            
            # Merge con oferta académica
            cols_oferta_disponibles = [c for c in columnas_oferta.keys() if c in oferta_df.columns]
            if cols_oferta_disponibles and 'CUS_ID' in oferta_df.columns:
                oferta_subset = oferta_df[cols_oferta_disponibles].drop_duplicates(subset=['CUS_ID'])
                matriz = matriz.merge(
                    oferta_subset,
                    left_on='cus_id',
                    right_on='CUS_ID',
                    how='left'
                )
            
            # Merge con postulantes
            cols_post_disponibles = [c for c in columnas_postulantes.keys() if c in postulantes_df.columns]
            if cols_post_disponibles and 'IDENTIFICACIÓN' in postulantes_df.columns:
                # Obtener datos únicos por postulante (tomar el primero si hay duplicados)
                postulantes_unicos = postulantes_df.drop_duplicates(subset=['IDENTIFICACIÓN'])
                postulantes_subset = postulantes_unicos[cols_post_disponibles]
                matriz = matriz.merge(
                    postulantes_subset,
                    left_on='identificacion',
                    right_on='IDENTIFICACIÓN',
                    how='left'
                )
            
            # Renombrar columnas para la matriz final
            rename_map = {}
            for orig, nuevo in columnas_oferta.items():
                if orig in matriz.columns:
                    rename_map[orig] = nuevo
            for orig, nuevo in columnas_postulantes.items():
                if orig in matriz.columns and orig not in rename_map:
                    rename_map[orig] = nuevo
            
            # Renombrar columnas de asignación
            rename_map.update({
                'identificacion': 'IDENTIFICACION_POSTULANTE',
                'cus_id': 'CUS_ID_ASIGNADO',
                'ofa_id': 'OFA_ID_ASIGNADO',
                'carrera': 'CARRERA_ASIGNADA',
                'puntaje': 'PUNTAJE_ASIGNACION',
                'grupo': 'GRUPO_ASIGNACION',
                'prioridad': 'PRIORIDAD_ELECCION',
                'fecha_asignacion': 'FECHA_ASIGNACION',
                'estado': 'ESTADO_ASIGNACION'
            })
            
            matriz = matriz.rename(columns=rename_map)
            
            # Ordenar columnas de forma lógica
            columnas_orden = [
                # Datos de la oferta
                'CAMPO_AMPLIO', 'NIVEL', 'FACULTAD', 'CARRERA', 'MODALIDAD', 'JORNADA',
                'PROVINCIA', 'CANTON', 'TIPO_OFERTA', 'ID_OFERTA_ULEAI', 'ID_OFERTA_SENESCYT',
                'CUS_ID_ASIGNADO', 'TOTAL_CUPOS',
                # Datos de asignación
                'GRUPO_ASIGNACION', 'PUNTAJE_ASIGNACION', 'PRIORIDAD_ELECCION', 
                'FECHA_ASIGNACION', 'ESTADO_ASIGNACION',
                # Datos del postulante
                'IDENTIFICACION_POSTULANTE', 'NOTA_POSTULACION', 'ORDEN_PRIORIDAD',
                'SEGMENTO_ASPIRANTE', 'VULNERABILIDAD_SOCIOECONOMICA', 'MERITO_ACADEMICO',
                'BACHILLER_PUEBLOS_NACIONALIDADES', 'BACHILLER_ULTIMO_ANIO',
                'INSTANCIA_POSTULACION', 'FECHA_POSTULACION', 'AUTOIDENTIFICACION', 'SEXO'
            ]
            
            # Filtrar solo las columnas que existen
            columnas_finales = [c for c in columnas_orden if c in matriz.columns]
            # Agregar columnas que no están en el orden pero existen
            columnas_extra = [c for c in matriz.columns if c not in columnas_finales]
            columnas_finales.extend(columnas_extra)
            
            matriz = matriz[columnas_finales]
            
            # Determinar ruta del archivo
            if carpeta_periodo:
                archivo = os.path.join(carpeta_periodo, f"Matriz_Asignacion_{self._obtener_timestamp()}.xlsx")
            else:
                archivo = self._crear_ruta_archivo("Matriz_Asignacion")
            
            # Guardar archivo Excel
            with pd.ExcelWriter(archivo, engine='openpyxl') as writer:
                matriz.to_excel(writer, sheet_name='Matriz_Asignacion', index=False)
                
                # Hoja de resumen
                resumen = pd.DataFrame({
                    'Métrica': [
                        'Total Asignados',
                        'Puntaje Promedio',
                        'Puntaje Máximo',
                        'Puntaje Mínimo',
                        'Fecha Generación'
                    ],
                    'Valor': [
                        len(matriz),
                        round(matriz['PUNTAJE_ASIGNACION'].mean(), 2) if 'PUNTAJE_ASIGNACION' in matriz.columns else 'N/A',
                        matriz['PUNTAJE_ASIGNACION'].max() if 'PUNTAJE_ASIGNACION' in matriz.columns else 'N/A',
                        matriz['PUNTAJE_ASIGNACION'].min() if 'PUNTAJE_ASIGNACION' in matriz.columns else 'N/A',
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    ]
                })
                resumen.to_excel(writer, sheet_name='Resumen', index=False)
                
                # Distribución por grupo
                if 'GRUPO_ASIGNACION' in matriz.columns:
                    dist_grupo = matriz['GRUPO_ASIGNACION'].value_counts().reset_index()
                    dist_grupo.columns = ['Grupo', 'Cantidad']
                    dist_grupo.to_excel(writer, sheet_name='Por_Grupo', index=False)
                
                # Distribución por carrera
                col_carrera = 'CARRERA' if 'CARRERA' in matriz.columns else 'CARRERA_ASIGNADA'
                if col_carrera in matriz.columns:
                    dist_carrera = matriz[col_carrera].value_counts().reset_index()
                    dist_carrera.columns = ['Carrera', 'Asignados']
                    dist_carrera.to_excel(writer, sheet_name='Por_Carrera', index=False)
            
            return {
                'exito': True,
                'archivo': archivo,
                'total_registros': len(matriz),
                'mensaje': f"Matriz de asignación generada exitosamente con {len(matriz)} registros"
            }
            
        except Exception as e:
            return {
                'exito': False,
                'archivo': None,
                'error': str(e),
                'mensaje': f"Error al generar matriz: {str(e)}"
            }
