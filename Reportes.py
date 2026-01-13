import pandas as pd
import os
from datetime import datetime
from typing import Dict, List


class Reporte:
    """
    Genera reportes del proceso de asignación en formato Excel.
    
    Responsabilidades:
    - Generar reportes completos con estadísticas
    - Reportes por carrera
    - Reportes por grupo de asignación
    - Listas de asignados
    
    Principio SRP: Solo se encarga de generar y guardar reportes.
    """
    
    def __init__(self, carpeta_reportes: str = "Reportes"):
        """
        Args:
            carpeta_reportes: Carpeta donde se guardarán los reportes
        """
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
    
    def generar_lista_asignados(self, asignaciones_df: pd.DataFrame, 
                                 guardar_excel: bool = True) -> List[Dict]:
        """
        Genera lista de todos los asignados.
        
        Args:
            asignaciones_df: DataFrame con las asignaciones
            guardar_excel: Si debe guardar el archivo Excel
            
        Returns:
            Lista de diccionarios con los asignados
        """
        if guardar_excel and not asignaciones_df.empty:
            archivo = self._crear_ruta_archivo("Lista_Asignados")
            asignaciones_df.to_excel(archivo, index=False)
        
        return asignaciones_df.to_dict('records')
    
    def generar_reporte_estadistico(self, asignaciones_df: pd.DataFrame,
                                     guardar_excel: bool = True) -> Dict:
        """
        Genera un reporte estadístico detallado.
        
        Returns:
            Dict con estadísticas avanzadas
        """
        if asignaciones_df.empty:
            return {'error': 'No hay datos para estadísticas'}
        
        estadisticas = {
            'total': len(asignaciones_df),
            'puntaje': {
                'promedio': round(asignaciones_df['puntaje'].mean(), 2),
                'mediana': round(asignaciones_df['puntaje'].median(), 2),
                'desviacion': round(asignaciones_df['puntaje'].std(), 2),
                'minimo': asignaciones_df['puntaje'].min(),
                'maximo': asignaciones_df['puntaje'].max(),
            },
            'distribucion_grupos': asignaciones_df['grupo'].value_counts().to_dict(),
            'distribucion_prioridad': asignaciones_df['prioridad'].value_counts().to_dict() 
                if 'prioridad' in asignaciones_df.columns else {},
            'carreras_mas_demandadas': asignaciones_df['carrera'].value_counts().head(10).to_dict()
        }
        
        if guardar_excel:
            archivo = self._crear_ruta_archivo("Reporte_Estadistico")
            
            with pd.ExcelWriter(archivo, engine='openpyxl') as writer:
                # Estadísticas de puntaje
                df_puntaje = pd.DataFrame([estadisticas['puntaje']])
                df_puntaje.to_excel(writer, sheet_name='Estadisticas_Puntaje', index=False)
                
                # Distribución por grupos
                df_grupos = pd.DataFrame(
                    list(estadisticas['distribucion_grupos'].items()),
                    columns=['Grupo', 'Cantidad']
                )
                df_grupos.to_excel(writer, sheet_name='Distribucion_Grupos', index=False)
                
                # Top carreras
                df_top = pd.DataFrame(
                    list(estadisticas['carreras_mas_demandadas'].items()),
                    columns=['Carrera', 'Asignados']
                )
                df_top.to_excel(writer, sheet_name='Top_Carreras', index=False)
            
            estadisticas['archivo_generado'] = archivo
        
        return estadisticas
