from Backend_Completo import Postulante
from Asignacion import GestorAceptacion
import tkinter as tk
from tkinter import messagebox, ttk, scrolledtext
import pandas as pd
import os
from datetime import datetime

class VentanaPostulante:
    """Ventana completa para el postulante"""
    
    def __init__(self, ventana, postulante: Postulante, ventana_principal):
        self.ventana = ventana
        self.postulante = postulante
        self.ventana_principal = ventana_principal
        self.gestor_aceptacion = GestorAceptacion()
        
        self.ventana.title("Panel de Postulante - ASIGNAU")
        self.ventana.geometry("900x700")
        
        # Verificar si tiene cupo asignado
        self.verificar_asignacion()
        
        # Barra superior
        self.crear_barra_superior()
        
        # Notebook para pestañas
        self.notebook = ttk.Notebook(ventana)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Crear pestañas
        self.crear_pestana_inicio()
        self.crear_pestana_postulaciones()
        self.crear_pestana_resultados()
        self.crear_pestana_perfil()
        
        # Botón cerrar sesión
        frame_inferior = tk.Frame(ventana, bg="white")
        frame_inferior.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Button(frame_inferior, text="Cerrar Sesión", 
                 font=("Arial", 12), bg="#f44336", fg="white",
                 width=20, command=self.cerrar_sesion).pack(side=tk.RIGHT)
    
    def crear_barra_superior(self):
        """Crea la barra superior con información del postulante"""
        barra_superior = tk.Frame(self.ventana, bg="#00af09", height=80)
        barra_superior.pack(fill=tk.X, side=tk.TOP)
        
        titulo = tk.Label(barra_superior, 
                         text=f"Bienvenido Postulante: {self.postulante.identificacion}", 
                         font=("Arial", 16, "bold"), 
                         bg="#00af09", 
                         fg="white")
        titulo.pack(pady=10)
        
        estado = "Cupo Asignado" if self.postulante.cupo_asignado else "Sin Cupo Asignado"
        info = tk.Label(barra_superior, 
                       text=f"Puntaje: {self.postulante.puntaje_postulacion} | Segmento: {self.postulante.segmento_aspirante} | Estado: {estado}", 
                       font=("Arial", 10), 
                       bg="#00af09", 
                       fg="white")
        info.pack()
    
    def verificar_asignacion(self):
        """Verifica si el postulante tiene un cupo asignado"""
        try:
            from PeriodoAsignacion import GestorPeriodos, PeriodoAsignacion
            
            # Intentar cargar desde periodo activo primero
            gestor = GestorPeriodos()
            periodo = gestor.obtener_periodo_activo()
            
            asignaciones = None
            
            if periodo and periodo.archivo_asignaciones:
                archivo = periodo.archivo_asignaciones
                if os.path.exists(archivo):
                    asignaciones = pd.read_excel(archivo)
            
            # Si no hay periodo activo, buscar en periodos disponibles
            if asignaciones is None:
                periodos = PeriodoAsignacion.listar_periodos()
                for p in periodos:
                    if p['estado'] in ['FINALIZADO', 'EN_PROCESO']:
                        periodo_cargado = PeriodoAsignacion.cargar(p['codigo'])
                        if periodo_cargado and periodo_cargado.archivo_asignaciones:
                            archivo = periodo_cargado.archivo_asignaciones
                            if os.path.exists(archivo):
                                asignaciones = pd.read_excel(archivo)
                                break
            
            # Fallback: archivo en la raíz
            if asignaciones is None and os.path.exists("Asignaciones.xlsx"):
                asignaciones = pd.read_excel("Asignaciones.xlsx")
            
            if asignaciones is not None:
                # Convertir ambos a string para la comparación
                resultado = asignaciones[asignaciones['identificacion'].astype(str) == str(self.postulante.identificacion)]
                
                if not resultado.empty:
                    self.postulante.cupo_asignado = True
                    self.postulante.estado_cupo = resultado.iloc[0]['estado']
                    self.postulante.nombre_carrera = resultado.iloc[0]['carrera']
                    self.postulante.cus_id = str(resultado.iloc[0]['cus_id'])
                    self.postulante.ofa_id = str(resultado.iloc[0]['ofa_id'])
                    self.info_asignacion = resultado.iloc[0].to_dict()
                else:
                    self.postulante.cupo_asignado = False
                    self.info_asignacion = None
            else:
                self.postulante.cupo_asignado = False
                self.info_asignacion = None
        except Exception as e:
            print(f"Error al verificar asignación: {e}")
            import traceback
            traceback.print_exc()
            self.postulante.cupo_asignado = False
            self.info_asignacion = None
    
    def crear_pestana_inicio(self):
        """Pestaña de inicio con resumen"""
        frame = tk.Frame(self.notebook, bg="white")
        self.notebook.add(frame, text="Inicio")
        
        tk.Label(frame, text="Mi Panel - ASIGNAU", 
                font=("Arial", 18, "bold"), bg="white").pack(pady=20)
        
        # Estado de la postulación
        estado_frame = tk.LabelFrame(frame, text="Estado de mi Postulación", 
                                    font=("Arial", 14, "bold"), bg="white")
        estado_frame.pack(pady=20, padx=40, fill=tk.BOTH)
        
        if self.postulante.cupo_asignado:
            # Mostrar información del cupo asignado
            tk.Label(estado_frame, 
                    text="¡Felicitaciones! Tienes un cupo asignado", 
                    font=("Arial", 14, "bold"), 
                    bg="white", fg="#4CAF50").pack(pady=15)
            
            info_labels = [
                f"Carrera: {self.postulante.nombre_carrera}",
                f"Puntaje: {self.postulante.puntaje_postulacion}",
                f"Estado: {self.postulante.estado_cupo}"
            ]
            
            for texto in info_labels:
                tk.Label(estado_frame, text=texto, 
                        font=("Arial", 12), bg="white").pack(pady=5)
            
            # Botón para aceptar cupo si aún no está aceptado
            if self.postulante.estado_cupo == "ASIGNADO":
                tk.Button(estado_frame, text="Aceptar Cupo", 
                         font=("Arial", 13, "bold"), bg="#4CAF50", fg="white",
                         width=20, height=2, 
                         command=self.aceptar_cupo).pack(pady=20)
            else:
                tk.Label(estado_frame, 
                        text="✓ Cupo Aceptado", 
                        font=("Arial", 13, "bold"), 
                        bg="white", fg="#4CAF50").pack(pady=20)
        else:
            tk.Label(estado_frame, 
                    text="Aún no tienes un cupo asignado", 
                    font=("Arial", 14), 
                    bg="white", fg="#FF9800").pack(pady=15)
            
            tk.Label(estado_frame, 
                    text="Por favor espera los resultados del proceso de asignación", 
                    font=("Arial", 11), 
                    bg="white").pack(pady=10)
        
        # Accesos rápidos
        accesos_frame = tk.LabelFrame(frame, text="Accesos Rápidos", 
                                     font=("Arial", 12, "bold"), bg="white")
        accesos_frame.pack(pady=20, padx=40, fill=tk.BOTH, expand=True)
        
        botones = [
            ("Ver mis Postulaciones", self.ir_a_postulaciones, "#2196F3"),
            ("Ver Resultados Detallados", self.ir_a_resultados, "#FF9800"),
            ("Mi Perfil", self.ir_a_perfil, "#9C27B0")
        ]
        
        for texto, comando, color in botones:
            tk.Button(accesos_frame, text=texto, font=("Arial", 11), 
                     bg=color, fg="white", width=30, height=2,
                     command=comando).pack(pady=10)
    
    def crear_pestana_postulaciones(self):
        """Pestaña con información de postulaciones"""
        frame = tk.Frame(self.notebook, bg="white")
        self.notebook.add(frame, text="Mis Postulaciones")
        
        tk.Label(frame, text="Mis Postulaciones", 
                font=("Arial", 16, "bold"), bg="white").pack(pady=20)
        
        # Información de postulación
        post_frame = tk.LabelFrame(frame, text="Detalles de Postulación", 
                                  font=("Arial", 12, "bold"), bg="white")
        post_frame.pack(pady=10, padx=40, fill=tk.BOTH, expand=True)
        
        postulaciones = self.postulante.obtener_postulaciones()
        
        campos = [
            ("Carrera:", postulaciones['carrera']),
            ("Prioridad:", postulaciones['prioridad']),
            ("Puntaje:", postulaciones['puntaje']),
            ("Segmento:", "Política de Cuotas" if postulaciones['segmento'] == 2 else "Población General"),
            ("Estado:", postulaciones['estado'] if postulaciones['estado'] else "En proceso")
        ]
        
        for i, (label, valor) in enumerate(campos):
            frame_campo = tk.Frame(post_frame, bg="white")
            frame_campo.pack(fill=tk.X, padx=20, pady=10)
            
            tk.Label(frame_campo, text=label, font=("Arial", 11, "bold"), 
                    bg="white", width=15, anchor="w").pack(side=tk.LEFT)
            tk.Label(frame_campo, text=str(valor), font=("Arial", 11), 
                    bg="white", anchor="w").pack(side=tk.LEFT, padx=10)
        
        # Botón para actualizar información
        tk.Button(frame, text="Actualizar Información", 
                 font=("Arial", 11), bg="#2196F3", fg="white",
                 width=25, height=2, 
                 command=self.actualizar_postulaciones).pack(pady=20)
    
    def crear_pestana_resultados(self):
        """Pestaña con resultados detallados"""
        frame = tk.Frame(self.notebook, bg="white")
        self.notebook.add(frame, text="Resultados")
        
        tk.Label(frame, text="Resultados de Asignación", 
                font=("Arial", 16, "bold"), bg="white").pack(pady=20)
        
        # Área de resultados
        resultado_frame = tk.LabelFrame(frame, text="Información Detallada", 
                                       font=("Arial", 12, "bold"), bg="white")
        resultado_frame.pack(pady=10, padx=40, fill=tk.BOTH, expand=True)
        
        self.texto_resultados = scrolledtext.ScrolledText(resultado_frame, 
                                                          font=("Courier", 10), 
                                                          height=25)
        self.texto_resultados.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Cargar resultados
        self.cargar_resultados()
        
        # Botones
        botones_frame = tk.Frame(frame, bg="white")
        botones_frame.pack(pady=10)
        
        tk.Button(botones_frame, text="Actualizar Resultados", 
                 font=("Arial", 11), bg="#2196F3", fg="white",
                 width=20, command=self.cargar_resultados).grid(row=0, column=0, padx=10)
        
        if self.postulante.cupo_asignado and self.postulante.estado_cupo == "ASIGNADO":
            tk.Button(botones_frame, text="Aceptar Cupo", 
                     font=("Arial", 11), bg="#4CAF50", fg="white",
                     width=20, command=self.aceptar_cupo).grid(row=0, column=1, padx=10)
    
    def crear_pestana_perfil(self):
        """Pestaña con información del perfil"""
        frame = tk.Frame(self.notebook, bg="white")
        self.notebook.add(frame, text="Mi Perfil")
        
        tk.Label(frame, text="Mi Perfil", 
                font=("Arial", 16, "bold"), bg="white").pack(pady=20)
        
        # Información personal
        perfil_frame = tk.LabelFrame(frame, text="Información Personal", 
                                    font=("Arial", 12, "bold"), bg="white")
        perfil_frame.pack(pady=10, padx=40, fill=tk.BOTH)
        
        info = self.postulante.mostrar_informacion()
        
        for clave, valor in info.items():
            frame_campo = tk.Frame(perfil_frame, bg="white")
            frame_campo.pack(fill=tk.X, padx=20, pady=8)
            
            tk.Label(frame_campo, text=f"{clave.title()}:", 
                    font=("Arial", 11, "bold"), 
                    bg="white", width=20, anchor="w").pack(side=tk.LEFT)
            tk.Label(frame_campo, text=str(valor), 
                    font=("Arial", 11), 
                    bg="white", anchor="w").pack(side=tk.LEFT, padx=10)
        
        # Opciones de perfil
        opciones_frame = tk.LabelFrame(frame, text="Opciones", 
                                      font=("Arial", 12, "bold"), bg="white")
        opciones_frame.pack(pady=20, padx=40, fill=tk.BOTH, expand=True)
        
        tk.Button(opciones_frame, text="Cambiar Contraseña", 
                 font=("Arial", 11), bg="#FF9800", fg="white",
                 width=25, height=2, 
                 command=self.cambiar_contrasena).pack(pady=10)
        
        tk.Button(opciones_frame, text="Ver Historial de Postulaciones", 
                 font=("Arial", 11), bg="#2196F3", fg="white",
                 width=25, height=2, 
                 command=self.ver_historial).pack(pady=10)
    
    # Métodos de funcionalidad
    def aceptar_cupo(self):
        """Acepta el cupo asignado"""
        if not self.postulante.cupo_asignado:
            messagebox.showwarning("Advertencia", "No tienes un cupo asignado")
            return
        
        if self.postulante.estado_cupo == "ACEPTADO":
            messagebox.showinfo("Información", "Ya has aceptado tu cupo")
            return
        
        respuesta = messagebox.askyesno(
            "Confirmar Aceptación",
            f"¿Estás seguro de aceptar el cupo en la carrera:\n{self.postulante.nombre_carrera}?\n\n"
            "Esta acción no puede deshacerse."
        )
        
        if respuesta:
            # Registrar aceptación
            fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")
            exito = self.gestor_aceptacion.registrar_aceptacion(
                self.postulante.identificacion,
                self.postulante.cus_id,
                fecha_actual
            )
            
            if exito:
                self.postulante.estado_cupo = "ACEPTADO"
                messagebox.showinfo(
                    "¡Felicitaciones!",
                    f"Has aceptado exitosamente tu cupo en:\n{self.postulante.nombre_carrera}\n\n"
                    "Pronto recibirás información sobre el proceso de matrícula."
                )
                # Actualizar ventana
                self.verificar_asignacion()
                self.cargar_resultados()
            else:
                messagebox.showerror("Error", "No se pudo registrar la aceptación")
    
    def cargar_resultados(self):
        """Carga los resultados de la asignación"""
        self.texto_resultados.delete('1.0', tk.END)
        
        try:
            from PeriodoAsignacion import GestorPeriodos, PeriodoAsignacion
            
            # Intentar cargar desde periodo activo primero
            gestor = GestorPeriodos()
            periodo = gestor.obtener_periodo_activo()
            
            asignaciones = None
            
            if periodo and periodo.archivo_asignaciones:
                archivo = periodo.archivo_asignaciones
                if os.path.exists(archivo):
                    asignaciones = pd.read_excel(archivo)
            
            # Si no hay periodo activo, buscar en periodos disponibles
            if asignaciones is None:
                periodos = PeriodoAsignacion.listar_periodos()
                for p in periodos:
                    if p['estado'] in ['FINALIZADO', 'EN_PROCESO']:
                        periodo_cargado = PeriodoAsignacion.cargar(p['codigo'])
                        if periodo_cargado and periodo_cargado.archivo_asignaciones:
                            archivo = periodo_cargado.archivo_asignaciones
                            if os.path.exists(archivo):
                                asignaciones = pd.read_excel(archivo)
                                break
            
            # Fallback: archivo en la raíz
            if asignaciones is None and os.path.exists("Asignaciones.xlsx"):
                asignaciones = pd.read_excel("Asignaciones.xlsx")
            
            if asignaciones is not None:
                # Convertir ambos a string para la comparación
                resultado = asignaciones[asignaciones['identificacion'].astype(str) == str(self.postulante.identificacion)]
                
                if not resultado.empty:
                    info = resultado.iloc[0]
                    texto = f"""
╔══════════════════════════════════════════════════════════════╗
║           RESULTADOS DE ASIGNACIÓN - ASIGNAU                ║
╚══════════════════════════════════════════════════════════════╝

IDENTIFICACIÓN: {info['identificacion']}
CARRERA ASIGNADA: {info['carrera']}
PUNTAJE: {info['puntaje']}
GRUPO: {info['grupo']}
ESTADO: {info['estado']}
VUELTA: {info['vuelta']}

{'='*60}
                    """
                    self.texto_resultados.insert('1.0', texto)
                    
                    # Actualizar el estado del postulante después de cargar resultados
                    self.postulante.cupo_asignado = True
                    self.postulante.estado_cupo = info['estado']
                    self.postulante.nombre_carrera = info['carrera']
                else:
                    self.texto_resultados.insert('1.0', 
                        "No se encontraron resultados de asignación para tu identificación.\n"
                        "Por favor verifica que el proceso de asignación haya finalizado.")
            else:
                self.texto_resultados.insert('1.0', 
                    "Aún no se han generado resultados de asignación.\n"
                    "Por favor espera a que el administrador ejecute el proceso.")
        except FileNotFoundError:
            self.texto_resultados.insert('1.0', 
                "Aún no se han generado resultados de asignación.\n"
                "Por favor espera a que el administrador ejecute el proceso.")
        except Exception as e:
            self.texto_resultados.insert('1.0', 
                f"Error al cargar resultados: {e}")
            import traceback
            traceback.print_exc()
    
    def actualizar_postulaciones(self):
        """Actualiza la información de postulaciones"""
        # Verificar si hay nuevas asignaciones
        self.verificar_asignacion()
        
        # Actualizar la carga de resultados
        self.cargar_resultados()
        
        # Mostrar mensaje
        messagebox.showinfo("Actualizado", "Información actualizada correctamente")
        
        # Recrear pestañas para reflejar cambios
        for widget in self.notebook.winfo_children():
            widget.destroy()
        
        # Recrear todas las pestañas
        self.crear_pestana_inicio()
        self.crear_pestana_postulaciones()
        self.crear_pestana_resultados()
        self.crear_pestana_perfil()
    
    def cambiar_contrasena(self):
        """Cambia la contraseña del postulante"""
        messagebox.showinfo("Información", "Funcionalidad en desarrollo")
    
    def ver_historial(self):
        """Muestra el historial de postulaciones"""
        messagebox.showinfo("Información", "Funcionalidad en desarrollo")
    
    # Métodos de navegación
    def ir_a_postulaciones(self):
        self.notebook.select(1)
    
    def ir_a_resultados(self):
        self.notebook.select(2)
    
    def ir_a_perfil(self):
        self.notebook.select(3)
    
    def cerrar_sesion(self):
        """Cierra la sesión y vuelve a la ventana principal"""
        self.ventana.destroy()
        self.ventana_principal.deiconify()