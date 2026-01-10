from Backend_Completo import Administrador, MotorAsignacion, Reporte, BD_POSTULACIONES
import tkinter as tk
from tkinter import messagebox, ttk, scrolledtext
import pandas as pd

class VentanaAdministrador:
    """Ventana completa para el administrador"""
    
    def __init__(self, ventana, admin: Administrador, ventana_principal):
        self.ventana = ventana
        self.admin = admin
        self.ventana_principal = ventana_principal
        
        self.ventana.title("Panel de Administrador - ASIGNAU")
        self.ventana.geometry("1000x700")
        
        # Barra superior
        self.crear_barra_superior()
        
        # Notebook para pestañas
        self.notebook = ttk.Notebook(ventana)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Crear pestañas
        self.crear_pestana_inicio()
        self.crear_pestana_asignacion()
        self.crear_pestana_reportes()
        self.crear_pestana_consultas()
        
        # Botón cerrar sesión
        frame_inferior = tk.Frame(ventana, bg="white")
        frame_inferior.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Button(frame_inferior, text="Cerrar Sesión", 
                 font=("Arial", 12), bg="#f44336", fg="white",
                 width=20, command=self.cerrar_sesion).pack(side=tk.RIGHT)
    
    def crear_barra_superior(self):
        """Crea la barra superior con información del admin"""
        barra_superior = tk.Frame(self.ventana, bg="#2c3e50", height=80)
        barra_superior.pack(fill=tk.X, side=tk.TOP)
        
        titulo = tk.Label(barra_superior, 
                         text=f"Bienvenido Administrador: {self.admin.nombre}", 
                         font=("Arial", 16, "bold"), 
                         bg="#2c3e50", 
                         fg="white")
        titulo.pack(pady=10)
        
        info = tk.Label(barra_superior, 
                       text=f"ID: {self.admin.id} | Cédula: {self.admin.cedula} | Periodo: {self.admin.Periodo}", 
                       font=("Arial", 10), 
                       bg="#2c3e50", 
                       fg="white")
        info.pack()
    
    def crear_pestana_inicio(self):
        """Pestaña de inicio con resumen"""
        frame = tk.Frame(self.notebook, bg="white")
        self.notebook.add(frame, text="Inicio")
        
        tk.Label(frame, text="Panel de Control - ASIGNAU", 
                font=("Arial", 18, "bold"), bg="white").pack(pady=20)
        
        # Información del periodo
        info_frame = tk.LabelFrame(frame, text="Información del Periodo", 
                                  font=("Arial", 12, "bold"), bg="white")
        info_frame.pack(pady=20, padx=20, fill=tk.BOTH)
        
        tk.Label(info_frame, text=f"Periodo Actual: {self.admin.Periodo}", 
                font=("Arial", 11), bg="white").pack(pady=5, anchor="w", padx=10)
        tk.Label(info_frame, text="Estado: Proceso de Asignación Activo", 
                font=("Arial", 11), bg="white").pack(pady=5, anchor="w", padx=10)
        
        # Accesos rápidos
        accesos_frame = tk.LabelFrame(frame, text="Accesos Rápidos", 
                                     font=("Arial", 12, "bold"), bg="white")
        accesos_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)
        
        botones = [
            ("Ejecutar Asignación de Cupos", self.ir_a_asignacion, "#4CAF50"),
            ("Ver Reportes", self.ir_a_reportes, "#2196F3"),
            ("Consultar Postulantes", self.ir_a_consultas, "#FF9800")
        ]
        
        for texto, comando, color in botones:
            tk.Button(accesos_frame, text=texto, font=("Arial", 11), 
                     bg=color, fg="white", width=30, height=2,
                     command=comando).pack(pady=10)
    
    def crear_pestana_asignacion(self):
        """Pestaña para ejecutar el proceso de asignación"""
        frame = tk.Frame(self.notebook, bg="white")
        self.notebook.add(frame, text="Asignación de Cupos")
        
        tk.Label(frame, text="Proceso de Asignación Automatizada", 
                font=("Arial", 16, "bold"), bg="white").pack(pady=20)
        
        # Configuración de porcentajes
        config_frame = tk.LabelFrame(frame, text="Configuración de Segmentos (%)", 
                                    font=("Arial", 12, "bold"), bg="white")
        config_frame.pack(pady=10, padx=20, fill=tk.X)
        
        self.porcentajes = {}
        campos = [
            ("Política de Cuotas:", 10),
            ("Mayor Vulnerabilidad:", 10),
            ("Mérito Académico:", 20),
            ("Otros Reconocimientos:", 2),
            ("Bachilleres Pueblos:", 10),
            ("Bachilleres Último Año:", 20),
            ("Población General:", 20)
        ]
        
        for i, (label, valor_default) in enumerate(campos):
            tk.Label(config_frame, text=label, font=("Arial", 10), 
                    bg="white").grid(row=i, column=0, padx=10, pady=5, sticky="w")
            
            entry = tk.Entry(config_frame, font=("Arial", 10), width=10)
            entry.insert(0, str(valor_default))
            entry.grid(row=i, column=1, padx=10, pady=5)
            
            self.porcentajes[label] = entry
        
        # Botones de acción
        botones_frame = tk.Frame(frame, bg="white")
        botones_frame.pack(pady=20)
        
        tk.Button(botones_frame, text="Cargar Datos de Postulación", 
                 font=("Arial", 11), bg="#2196F3", fg="white",
                 width=25, height=2, command=self.cargar_datos).grid(row=0, column=0, padx=10)
        
        tk.Button(botones_frame, text="Ejecutar Asignación", 
                 font=("Arial", 11), bg="#4CAF50", fg="white",
                 width=25, height=2, command=self.ejecutar_asignacion).grid(row=0, column=1, padx=10)
        
        # Área de resultados
        resultado_frame = tk.LabelFrame(frame, text="Resultados", 
                                       font=("Arial", 12, "bold"), bg="white")
        resultado_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        self.texto_resultado = scrolledtext.ScrolledText(resultado_frame, 
                                                         font=("Courier", 9), 
                                                         height=15)
        self.texto_resultado.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def crear_pestana_reportes(self):
        """Pestaña para generar reportes"""
        frame = tk.Frame(self.notebook, bg="white")
        self.notebook.add(frame, text="Reportes")
        
        tk.Label(frame, text="Generación de Reportes", 
                font=("Arial", 16, "bold"), bg="white").pack(pady=20)
        
        # Botones de tipos de reportes
        botones_frame = tk.Frame(frame, bg="white")
        botones_frame.pack(pady=20)
        
        tk.Button(botones_frame, text="Reporte General de Asignación", 
                 font=("Arial", 11), bg="#4CAF50", fg="white",
                 width=30, height=2, command=self.generar_reporte_general).pack(pady=10)
        
        tk.Button(botones_frame, text="Reporte por Carrera", 
                 font=("Arial", 11), bg="#2196F3", fg="white",
                 width=30, height=2, command=self.generar_reporte_carrera).pack(pady=10)
        
        tk.Button(botones_frame, text="Reporte por Grupo", 
                 font=("Arial", 11), bg="#FF9800", fg="white",
                 width=30, height=2, command=self.generar_reporte_grupo).pack(pady=10)
        
        # Área de visualización de reportes
        reporte_frame = tk.LabelFrame(frame, text="Visualización de Reporte", 
                                     font=("Arial", 12, "bold"), bg="white")
        reporte_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        self.texto_reporte = scrolledtext.ScrolledText(reporte_frame, 
                                                       font=("Courier", 9), 
                                                       height=20)
        self.texto_reporte.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def crear_pestana_consultas(self):
        """Pestaña para consultas de postulantes"""
        frame = tk.Frame(self.notebook, bg="white")
        self.notebook.add(frame, text="Consultas")
        
        tk.Label(frame, text="Consultar Postulantes", 
                font=("Arial", 16, "bold"), bg="white").pack(pady=20)
        
        # Búsqueda
        busqueda_frame = tk.Frame(frame, bg="white")
        busqueda_frame.pack(pady=10)
        
        tk.Label(busqueda_frame, text="Identificación:", 
                font=("Arial", 11), bg="white").grid(row=0, column=0, padx=10)
        
        self.entry_busqueda = tk.Entry(busqueda_frame, font=("Arial", 11), width=25)
        self.entry_busqueda.grid(row=0, column=1, padx=10)
        
        tk.Button(busqueda_frame, text="Buscar", font=("Arial", 11), 
                 bg="#2196F3", fg="white", width=15,
                 command=self.buscar_postulante).grid(row=0, column=2, padx=10)
        
        # Resultados
        resultado_frame = tk.LabelFrame(frame, text="Resultados de Búsqueda", 
                                       font=("Arial", 12, "bold"), bg="white")
        resultado_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        self.texto_consulta = scrolledtext.ScrolledText(resultado_frame, 
                                                        font=("Courier", 9), 
                                                        height=20)
        self.texto_consulta.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Métodos de funcionalidad
    def cargar_datos(self):
        """Carga los datos de postulación"""
        try:
            postulaciones = BD_POSTULACIONES.cargar_postulaciones()
            if postulaciones is not None:
                self.postulaciones_df = postulaciones
                self.texto_resultado.insert(tk.END, f"Datos cargados correctamente\n")
                self.texto_resultado.insert(tk.END, f"Total de postulaciones: {len(postulaciones)}\n\n")
            else:
                messagebox.showerror("Error", "No se pudo cargar el archivo de postulaciones")
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar datos: {str(e)}")
    
    def ejecutar_asignacion(self):
        """Ejecuta el proceso de asignación"""
        try:
            if not hasattr(self, 'postulaciones_df'):
                messagebox.showwarning("Advertencia", "Primero cargue los datos de postulación")
                return
            
            # Obtener porcentajes configurados
            porcentajes = {
                'politica_cuotas': float(self.porcentajes["Política de Cuotas:"].get()) / 100,
                'vulnerabilidad': float(self.porcentajes["Mayor Vulnerabilidad:"].get()) / 100,
                'merito_academico': float(self.porcentajes["Mérito Académico:"].get()) / 100,
                'otros_reconocimientos': float(self.porcentajes["Otros Reconocimientos:"].get()) / 100,
                'bachilleres_pueblos': float(self.porcentajes["Bachilleres Pueblos:"].get()) / 100,
                'bachilleres_ultimo': float(self.porcentajes["Bachilleres Último Año:"].get()) / 100,
                'poblacion_general': float(self.porcentajes["Población General:"].get()) / 100
            }
            
            # Cargar oferta académica
            oferta = BD_POSTULACIONES.cargar_oferta_academica()
            if oferta is None:
                messagebox.showerror("Error", "No se pudo cargar la oferta académica")
                return
            
            # Ejecutar asignación
            self.texto_resultado.insert(tk.END, "\n=== EJECUTANDO ASIGNACIÓN ===\n")
            self.texto_resultado.insert(tk.END, f"Fecha: {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M')}\n\n")
            
            asignaciones = self.admin.ejecutar_asignacion(oferta, self.postulaciones_df, porcentajes)
            
            # Guardar resultados
            BD_POSTULACIONES.guardar_asignaciones(asignaciones)
            
            self.texto_resultado.insert(tk.END, f"Total de asignaciones realizadas: {len(asignaciones)}\n")
            self.texto_resultado.insert(tk.END, "\nPrimeras 10 asignaciones:\n")
            self.texto_resultado.insert(tk.END, asignaciones.head(10).to_string() + "\n")
            
            messagebox.showinfo("Éxito", "Asignación ejecutada correctamente")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en asignación: {str(e)}")
    
    def generar_reporte_general(self):
        """Genera reporte general y lo guarda en Excel"""
        try:
            asignaciones = pd.read_excel("Asignaciones.xlsx")
            reporte = Reporte().generar_reporte_completo(asignaciones, guardar_excel=True)
            
            if 'error' in reporte:
                messagebox.showerror("Error", reporte['error'])
                return
            
            self.texto_reporte.delete(1.0, tk.END)
            self.texto_reporte.insert(tk.END, "=== REPORTE GENERAL DE ASIGNACIÓN ===\n\n")
            self.texto_reporte.insert(tk.END, f"Total de asignaciones: {reporte['total_asignaciones']}\n\n")
            self.texto_reporte.insert(tk.END, "Asignaciones por Grupo:\n")
            for grupo, cantidad in reporte['por_grupo'].items():
                self.texto_reporte.insert(tk.END, f"  {grupo}: {cantidad}\n")
            
            self.texto_reporte.insert(tk.END, f"\nPuntaje Promedio: {reporte['puntaje_promedio']:.2f}\n")
            self.texto_reporte.insert(tk.END, f"Puntaje Máximo: {reporte['puntaje_maximo']:.2f}\n")
            self.texto_reporte.insert(tk.END, f"Puntaje Mínimo: {reporte['puntaje_minimo']:.2f}\n")
            
            if 'archivo_generado' in reporte:
                self.texto_reporte.insert(tk.END, f"\n✓ Reporte Excel guardado en:\n{reporte['archivo_generado']}\n")
                messagebox.showinfo("Éxito", f"Reporte generado y guardado en:\n{reporte['archivo_generado']}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte: {str(e)}")
    
    def generar_reporte_carrera(self):
        """Genera reporte por carrera y lo guarda en Excel"""
        try:
            asignaciones = pd.read_excel("Asignaciones.xlsx")
            reporte = Reporte().generar_reporte_por_carrera(asignaciones, carrera=None, guardar_excel=True)
            
            if 'error' in reporte:
                messagebox.showerror("Error", reporte['error'])
                return
            
            self.texto_reporte.delete(1.0, tk.END)
            self.texto_reporte.insert(tk.END, "=== REPORTE POR CARRERA ===\n\n")
            
            if 'carreras' in reporte:
                for carrera, cantidad in reporte['carreras'].items():
                    self.texto_reporte.insert(tk.END, f"{carrera}: {cantidad} asignados\n")
            
            if 'archivo_generado' in reporte:
                self.texto_reporte.insert(tk.END, f"\n✓ Reporte Excel guardado en:\n{reporte['archivo_generado']}\n")
                messagebox.showinfo("Éxito", f"Reporte generado y guardado en:\n{reporte['archivo_generado']}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte: {str(e)}")
    
    def generar_reporte_grupo(self):
        """Genera reporte por grupo y lo guarda en Excel"""
        try:
            asignaciones = pd.read_excel("Asignaciones.xlsx")
            reporte = Reporte().generar_reporte_por_grupo(asignaciones, guardar_excel=True)
            
            if 'error' in reporte:
                messagebox.showerror("Error", reporte['error'])
                return
            
            self.texto_reporte.delete(1.0, tk.END)
            self.texto_reporte.insert(tk.END, "=== REPORTE POR GRUPO ===\n\n")
            
            if 'detalle_por_grupo' in reporte:
                for grupo, cantidad in reporte['detalle_por_grupo'].items():
                    self.texto_reporte.insert(tk.END, f"{grupo}: {cantidad} asignados\n")
            
            if 'archivo_generado' in reporte:
                self.texto_reporte.insert(tk.END, f"\n✓ Reporte Excel guardado en:\n{reporte['archivo_generado']}\n")
                messagebox.showinfo("Éxito", f"Reporte generado y guardado en:\n{reporte['archivo_generado']}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte: {str(e)}")
    
    def buscar_postulante(self):
        """Busca información de un postulante"""
        identificacion = self.entry_busqueda.get().strip()
        
        if not identificacion:
            messagebox.showwarning("Advertencia", "Ingrese una identificación")
            return
        
        try:
            asignaciones = pd.read_excel("Asignaciones.xlsx")
            resultado = asignaciones[asignaciones['identificacion'] == identificacion]
            
            self.texto_consulta.delete(1.0, tk.END)
            
            if resultado.empty:
                self.texto_consulta.insert(tk.END, f"No se encontraron asignaciones para: {identificacion}\n")
            else:
                self.texto_consulta.insert(tk.END, f"=== INFORMACIÓN DEL POSTULANTE ===\n\n")
                self.texto_consulta.insert(tk.END, f"Identificación: {identificacion}\n")
                self.texto_consulta.insert(tk.END, f"Carrera: {resultado.iloc[0]['carrera']}\n")
                self.texto_consulta.insert(tk.END, f"Puntaje: {resultado.iloc[0]['puntaje']}\n")
                self.texto_consulta.insert(tk.END, f"Grupo: {resultado.iloc[0]['grupo']}\n")
                self.texto_consulta.insert(tk.END, f"Estado: {resultado.iloc[0]['estado']}\n")
                self.texto_consulta.insert(tk.END, f"Fecha Asignación: {resultado.iloc[0]['fecha_asignacion']}\n")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error en búsqueda: {str(e)}")
    
    # Métodos de navegación
    def ir_a_asignacion(self):
        self.notebook.select(1)
    
    def ir_a_reportes(self):
        self.notebook.select(2)
    
    def ir_a_consultas(self):
        self.notebook.select(3)
    
    def cerrar_sesion(self):
        """Cierra la sesión y vuelve a la ventana principal"""
        self.ventana.destroy()
        self.ventana_principal.deiconify()