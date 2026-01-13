from Backend_Completo import (Administrador, Reporte, EstadoPeriodo)
import tkinter as tk
from tkinter import messagebox, ttk, scrolledtext, filedialog
import pandas as pd
from datetime import datetime


class VentanaAdministrador:
    """Ventana completa para el administrador con sistema de periodos"""
    
    def __init__(self, ventana, admin: Administrador, ventana_principal):
        self.ventana = ventana
        self.admin = admin
        self.ventana_principal = ventana_principal
        
        # Periodo activo
        self.periodo_activo = None
        
        self.ventana.title("Panel de Administrador - ASIGNAU")
        self.ventana.geometry("1100x750")
        
        # Intentar cargar último periodo abierto
        self._cargar_ultimo_periodo()
        
        # Barra superior
        self.crear_barra_superior()
        
        # Notebook para pestañas
        self.notebook = ttk.Notebook(ventana)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Crear pestañas
        self.crear_pestana_inicio()
        self.crear_pestana_periodos()
        self.crear_pestana_asignacion()
        self.crear_pestana_reportes()
        self.crear_pestana_consultas()
        
        # Botón cerrar sesión
        frame_inferior = tk.Frame(ventana, bg="white")
        frame_inferior.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Button(frame_inferior, text="Cerrar Sesión", 
                 font=("Arial", 12), bg="#f44336", fg="white",
                 width=20, command=self.cerrar_sesion).pack(side=tk.RIGHT)
        
        # Actualizar interfaz según estado del periodo
        self._actualizar_estado_interfaz()
    
    def _cargar_ultimo_periodo(self):
        """Intenta cargar el último periodo abierto"""
        gestor = self.admin.obtener_gestor_periodos()
        self.periodo_activo = gestor.obtener_ultimo_periodo_abierto()
        if self.periodo_activo:
            gestor.establecer_periodo_activo(self.periodo_activo)
    
    def crear_barra_superior(self):
        """Crea la barra superior con información del admin"""
        barra_superior = tk.Frame(self.ventana, bg="#2c3e50", height=80)
        barra_superior.pack(fill=tk.X, side=tk.TOP)
        
        titulo = tk.Label(barra_superior, 
                         text=f"Bienvenido Administrador", 
                         font=("Arial", 16, "bold"), 
                         bg="#2c3e50", 
                         fg="white")
        titulo.pack(pady=10)
        
        # Frame para info del periodo
        self.frame_info_periodo = tk.Frame(barra_superior, bg="#2c3e50")
        self.frame_info_periodo.pack()
        
        self.label_periodo_info = tk.Label(
            self.frame_info_periodo, 
            text=self._obtener_texto_periodo(),
            font=("Arial", 10), 
            bg="#2c3e50", 
            fg="white"
        )
        self.label_periodo_info.pack()
    
    def _obtener_texto_periodo(self) -> str:
        """Obtiene el texto descriptivo del periodo actual"""
        if self.periodo_activo:
            estado = self.periodo_activo.estado.value
            return f"Periodo: {self.periodo_activo.codigo} | Estado: {estado}"
        return "Sin periodo activo | Cree o seleccione un periodo para comenzar"
    
    def _actualizar_estado_interfaz(self):
        """Actualiza la interfaz según el estado del periodo"""
        # Actualizar label de periodo
        if hasattr(self, 'label_periodo_info'):
            self.label_periodo_info.config(text=self._obtener_texto_periodo())
        
        # Actualizar botones según estado
        if hasattr(self, 'btn_ejecutar_asignacion'):
            puede_asignar = False
            if self.periodo_activo:
                puede_asignar, _ = self.periodo_activo.puede_asignar()
            
            if puede_asignar:
                self.btn_ejecutar_asignacion.config(state=tk.NORMAL, bg="#4CAF50")
            else:
                self.btn_ejecutar_asignacion.config(state=tk.DISABLED, bg="#cccccc")
        
        # Actualizar información de archivos cargados
        if hasattr(self, 'label_estado_oferta'):
            if self.periodo_activo and self.periodo_activo.archivo_oferta:
                self.label_estado_oferta.config(
                    text=f"✓ Oferta cargada: {self.periodo_activo.total_cupos_ofertados} cupos",
                    fg="green"
                )
            else:
                self.label_estado_oferta.config(text="✗ No cargado", fg="red")
        
        if hasattr(self, 'label_estado_postulantes'):
            if self.periodo_activo and self.periodo_activo.archivo_postulantes:
                self.label_estado_postulantes.config(
                    text=f"✓ Postulantes cargados: {self.periodo_activo.total_postulantes}",
                    fg="green"
                )
            else:
                self.label_estado_postulantes.config(text="✗ No cargado", fg="red")
        
        # Actualizar resumen en pestaña inicio
        if hasattr(self, 'texto_resumen_periodo'):
            self._actualizar_resumen_periodo()
    
    def crear_pestana_inicio(self):
        """Pestaña de inicio con resumen"""
        frame = tk.Frame(self.notebook, bg="white")
        self.notebook.add(frame, text="Inicio")
        
        tk.Label(frame, text="Panel de Control - ASIGNAU", 
                font=("Arial", 18, "bold"), bg="white").pack(pady=20)
        
        # Frame principal con dos columnas
        frame_contenido = tk.Frame(frame, bg="white")
        frame_contenido.pack(fill=tk.BOTH, expand=True, padx=20)
        
        # Columna izquierda - Resumen del periodo
        frame_izq = tk.LabelFrame(frame_contenido, text="Resumen del Periodo Activo", 
                                  font=("Arial", 12, "bold"), bg="white")
        frame_izq.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.texto_resumen_periodo = scrolledtext.ScrolledText(
            frame_izq, font=("Courier", 10), height=20, width=50
        )
        self.texto_resumen_periodo.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Columna derecha - Accesos rápidos
        frame_der = tk.LabelFrame(frame_contenido, text="Acciones Rápidas", 
                                 font=("Arial", 12, "bold"), bg="white")
        frame_der.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10, pady=10)
        
        botones = [
            ("Gestionar Periodos", self.ir_a_periodos, "#9C27B0"),
            ("Cargar Archivos", self.ir_a_asignacion, "#2196F3"),
            ("Ejecutar Asignación", self._ejecutar_desde_inicio, "#4CAF50"),
            ("Ver Reportes", self.ir_a_reportes, "#FF9800"),
            ("Consultar Postulantes", self.ir_a_consultas, "#607D8B")
        ]
        
        for texto, comando, color in botones:
            tk.Button(frame_der, text=texto, font=("Arial", 11), 
                     bg=color, fg="white", width=25, height=2,
                     command=comando).pack(pady=8, padx=10)
        
        self._actualizar_resumen_periodo()
    
    def _actualizar_resumen_periodo(self):
        """Actualiza el resumen del periodo en la pestaña inicio"""
        if not hasattr(self, 'texto_resumen_periodo'):
            return
            
        self.texto_resumen_periodo.config(state=tk.NORMAL)
        self.texto_resumen_periodo.delete(1.0, tk.END)
        
        if not self.periodo_activo:
            self.texto_resumen_periodo.insert(tk.END, "=" * 40 + "\n")
            self.texto_resumen_periodo.insert(tk.END, "  SIN PERIODO ACTIVO\n")
            self.texto_resumen_periodo.insert(tk.END, "=" * 40 + "\n\n")
            self.texto_resumen_periodo.insert(tk.END, "Para comenzar:\n\n")
            self.texto_resumen_periodo.insert(tk.END, "1. Vaya a la pestana 'Periodos'\n")
            self.texto_resumen_periodo.insert(tk.END, "2. Cree un nuevo periodo o seleccione uno existente\n")
            self.texto_resumen_periodo.insert(tk.END, "3. Cargue los archivos necesarios\n")
            self.texto_resumen_periodo.insert(tk.END, "4. Ejecute la asignacion\n")
        else:
            resumen = self.periodo_activo.obtener_resumen()
            
            self.texto_resumen_periodo.insert(tk.END, "=" * 40 + "\n")
            self.texto_resumen_periodo.insert(tk.END, f"  PERIODO: {resumen['codigo']}\n")
            self.texto_resumen_periodo.insert(tk.END, "=" * 40 + "\n\n")
            
            # Estado
            estado_emoji = {
                'NO_INICIADO': '[  ]',
                'DATOS_CARGADOS': '[OK]',
                'EN_PROCESO': '[..]',
                'FINALIZADO': '[OK]',
                'CERRADO': '[XX]'
            }
            emoji = estado_emoji.get(resumen['estado'], '[  ]')
            self.texto_resumen_periodo.insert(tk.END, f"Estado: {emoji} {resumen['estado']}\n")
            self.texto_resumen_periodo.insert(tk.END, f"Fase: {resumen['fase']}\n\n")
            
            # Archivos
            self.texto_resumen_periodo.insert(tk.END, "-" * 40 + "\n")
            self.texto_resumen_periodo.insert(tk.END, "ARCHIVOS:\n")
            self.texto_resumen_periodo.insert(tk.END, "-" * 40 + "\n")
            
            oferta_ok = "[OK]" if resumen['archivos_cargados']['oferta'] else "[  ]"
            post_ok = "[OK]" if resumen['archivos_cargados']['postulantes'] else "[  ]"
            asig_ok = "[OK]" if resumen['archivos_cargados']['asignaciones'] else "[  ]"
            
            self.texto_resumen_periodo.insert(tk.END, f"  {oferta_ok} Oferta Academica\n")
            self.texto_resumen_periodo.insert(tk.END, f"  {post_ok} Postulantes\n")
            self.texto_resumen_periodo.insert(tk.END, f"  {asig_ok} Asignaciones\n\n")
            
            # Estadísticas
            self.texto_resumen_periodo.insert(tk.END, "-" * 40 + "\n")
            self.texto_resumen_periodo.insert(tk.END, "ESTADISTICAS:\n")
            self.texto_resumen_periodo.insert(tk.END, "-" * 40 + "\n")
            self.texto_resumen_periodo.insert(tk.END, f"  Cupos ofertados: {resumen['total_cupos_ofertados']}\n")
            self.texto_resumen_periodo.insert(tk.END, f"  Postulantes: {resumen['total_postulantes']}\n")
            self.texto_resumen_periodo.insert(tk.END, f"  Asignados: {resumen['total_asignados']}\n")
            self.texto_resumen_periodo.insert(tk.END, f"  Sin asignar: {resumen['total_no_asignados']}\n")
            self.texto_resumen_periodo.insert(tk.END, f"  Vueltas ejecutadas: {resumen['vueltas_ejecutadas']}\n\n")
            
            # Fechas
            self.texto_resumen_periodo.insert(tk.END, "-" * 40 + "\n")
            self.texto_resumen_periodo.insert(tk.END, "FECHAS:\n")
            self.texto_resumen_periodo.insert(tk.END, "-" * 40 + "\n")
            self.texto_resumen_periodo.insert(tk.END, f"  Creacion: {resumen['fecha_creacion']}\n")
            if resumen['fecha_inicio_asignacion']:
                self.texto_resumen_periodo.insert(tk.END, f"  Inicio asig.: {resumen['fecha_inicio_asignacion']}\n")
            if resumen['fecha_fin_asignacion']:
                self.texto_resumen_periodo.insert(tk.END, f"  Fin asig.: {resumen['fecha_fin_asignacion']}\n")
            if resumen['fecha_cierre']:
                self.texto_resumen_periodo.insert(tk.END, f"  Cierre: {resumen['fecha_cierre']}\n")
        
        self.texto_resumen_periodo.config(state=tk.DISABLED)
    
    def _ejecutar_desde_inicio(self):
        """Ejecuta asignación desde la pestaña inicio"""
        if not self.periodo_activo:
            messagebox.showwarning("Advertencia", "Primero seleccione o cree un periodo")
            self.ir_a_periodos()
            return
        
        puede, mensaje = self.periodo_activo.puede_asignar()
        if not puede:
            messagebox.showwarning("Advertencia", mensaje)
            self.ir_a_asignacion()
            return
        
        self.ir_a_asignacion()
        self.ejecutar_asignacion()
    
    def crear_pestana_periodos(self):
        """Pestaña para gestionar periodos"""
        frame = tk.Frame(self.notebook, bg="white")
        self.notebook.add(frame, text="Periodos")
        
        tk.Label(frame, text="Gestion de Periodos de Asignacion", 
                font=("Arial", 16, "bold"), bg="white").pack(pady=15)
        
        # Frame principal dividido
        frame_principal = tk.Frame(frame, bg="white")
        frame_principal.pack(fill=tk.BOTH, expand=True, padx=20)
        
        # Columna izquierda - Crear/Abrir periodo
        frame_izq = tk.LabelFrame(frame_principal, text="Nuevo Periodo", 
                                  font=("Arial", 12, "bold"), bg="white")
        frame_izq.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Campos para nuevo periodo
        tk.Label(frame_izq, text="Codigo del Periodo:", 
                font=("Arial", 11), bg="white").pack(pady=5, anchor="w", padx=10)
        
        self.entry_codigo_periodo = tk.Entry(frame_izq, font=("Arial", 11), width=20)
        self.entry_codigo_periodo.pack(padx=10, pady=5)
        self.entry_codigo_periodo.insert(0, "2025-2")
        
        tk.Label(frame_izq, text="Nombre (opcional):", 
                font=("Arial", 11), bg="white").pack(pady=5, anchor="w", padx=10)
        
        self.entry_nombre_periodo = tk.Entry(frame_izq, font=("Arial", 11), width=30)
        self.entry_nombre_periodo.pack(padx=10, pady=5)
        
        tk.Button(frame_izq, text="Crear Nuevo Periodo", 
                 font=("Arial", 11), bg="#4CAF50", fg="white",
                 width=25, height=2, command=self.crear_periodo).pack(pady=15)
        
        # Separador
        ttk.Separator(frame_izq, orient="horizontal").pack(fill=tk.X, padx=10, pady=15)
        
        # Cerrar periodo actual
        tk.Label(frame_izq, text="Periodo Activo:", 
                font=("Arial", 11, "bold"), bg="white").pack(pady=5, anchor="w", padx=10)
        
        self.label_periodo_activo = tk.Label(
            frame_izq, 
            text=self.periodo_activo.codigo if self.periodo_activo else "Ninguno",
            font=("Arial", 11), bg="white", fg="blue"
        )
        self.label_periodo_activo.pack(padx=10, pady=5)
        
        tk.Button(frame_izq, text="Cerrar Periodo Activo", 
                 font=("Arial", 11), bg="#f44336", fg="white",
                 width=25, height=2, command=self.cerrar_periodo).pack(pady=10)
        
        # Columna derecha - Lista de periodos
        frame_der = tk.LabelFrame(frame_principal, text="Periodos Existentes", 
                                 font=("Arial", 12, "bold"), bg="white")
        frame_der.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Treeview para lista de periodos
        columns = ('codigo', 'estado', 'fecha', 'asignados')
        self.tree_periodos = ttk.Treeview(frame_der, columns=columns, show='headings', height=12)
        
        self.tree_periodos.heading('codigo', text='Codigo')
        self.tree_periodos.heading('estado', text='Estado')
        self.tree_periodos.heading('fecha', text='Fecha Creacion')
        self.tree_periodos.heading('asignados', text='Asignados')
        
        self.tree_periodos.column('codigo', width=100)
        self.tree_periodos.column('estado', width=120)
        self.tree_periodos.column('fecha', width=150)
        self.tree_periodos.column('asignados', width=80)
        
        scrollbar = ttk.Scrollbar(frame_der, orient=tk.VERTICAL, command=self.tree_periodos.yview)
        self.tree_periodos.configure(yscrollcommand=scrollbar.set)
        
        self.tree_periodos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botones de acción para periodos existentes
        frame_botones = tk.Frame(frame_der, bg="white")
        frame_botones.pack(fill=tk.X, pady=10)
        
        tk.Button(frame_botones, text="Abrir Periodo", 
                 font=("Arial", 10), bg="#2196F3", fg="white",
                 width=15, command=self.abrir_periodo_seleccionado).pack(side=tk.LEFT, padx=5)
        
        tk.Button(frame_botones, text="Actualizar Lista", 
                 font=("Arial", 10), bg="#607D8B", fg="white",
                 width=15, command=self.actualizar_lista_periodos).pack(side=tk.LEFT, padx=5)
        
        # Cargar lista inicial
        self.actualizar_lista_periodos()
    
    def crear_periodo(self):
        """Crea un nuevo periodo"""
        codigo = self.entry_codigo_periodo.get().strip()
        nombre = self.entry_nombre_periodo.get().strip()
        
        if not codigo:
            messagebox.showerror("Error", "Ingrese un codigo para el periodo")
            return
        
        exito, mensaje, periodo = self.admin.crear_nuevo_periodo(codigo, nombre)
        
        if exito:
            self.periodo_activo = periodo
            self.label_periodo_activo.config(text=codigo)
            messagebox.showinfo("Exito", mensaje)
            self.actualizar_lista_periodos()
            self._actualizar_estado_interfaz()
        else:
            messagebox.showerror("Error", mensaje)
    
    def abrir_periodo_seleccionado(self):
        """Abre el periodo seleccionado en el treeview"""
        seleccion = self.tree_periodos.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un periodo de la lista")
            return
        
        item = self.tree_periodos.item(seleccion[0])
        codigo = item['values'][0]
        
        exito, mensaje, periodo = self.admin.abrir_periodo(codigo)
        
        if exito:
            self.periodo_activo = periodo
            self.label_periodo_activo.config(text=codigo)
            messagebox.showinfo("Exito", f"Periodo {codigo} abierto")
            self._actualizar_estado_interfaz()
        else:
            messagebox.showerror("Error", mensaje)
    
    def cerrar_periodo(self):
        """Cierra el periodo activo"""
        if not self.periodo_activo:
            messagebox.showwarning("Advertencia", "No hay periodo activo")
            return
        
        if self.periodo_activo.estado != EstadoPeriodo.FINALIZADO:
            messagebox.showwarning(
                "Advertencia", 
                "El periodo debe estar FINALIZADO para poder cerrarlo.\n"
                "Ejecute la asignacion primero."
            )
            return
        
        respuesta = messagebox.askyesno(
            "Confirmar Cierre",
            f"Esta seguro de cerrar el periodo {self.periodo_activo.codigo}?\n\n"
            "Esta accion es IRREVERSIBLE.\n"
            "No podra realizar mas asignaciones en este periodo."
        )
        
        if respuesta:
            exito, mensaje = self.periodo_activo.cerrar_periodo()
            if exito:
                messagebox.showinfo("Exito", mensaje)
                self.actualizar_lista_periodos()
                self._actualizar_estado_interfaz()
            else:
                messagebox.showerror("Error", mensaje)
    
    def actualizar_lista_periodos(self):
        """Actualiza la lista de periodos en el treeview"""
        # Limpiar treeview
        for item in self.tree_periodos.get_children():
            self.tree_periodos.delete(item)
        
        # Obtener periodos
        periodos = self.admin.listar_periodos()
        
        for p in periodos:
            self.tree_periodos.insert('', tk.END, values=(
                p['codigo'],
                p['estado'],
                p['fecha_creacion'][:10],
                p.get('total_asignados', 0)
            ))
    
    def crear_pestana_asignacion(self):
        """Pestana para carga de archivos y ejecucion de asignacion"""
        frame = tk.Frame(self.notebook, bg="white")
        self.notebook.add(frame, text="Asignacion")
        
        tk.Label(frame, text="Proceso de Asignacion de Cupos", 
                font=("Arial", 16, "bold"), bg="white").pack(pady=15)
        
        # Frame para carga de archivos
        frame_archivos = tk.LabelFrame(frame, text="1. Carga de Archivos", 
                                       font=("Arial", 12, "bold"), bg="white")
        frame_archivos.pack(pady=10, padx=20, fill=tk.X)
        
        # Oferta Académica
        frame_oferta = tk.Frame(frame_archivos, bg="white")
        frame_oferta.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(frame_oferta, text="Oferta Academica:", 
                font=("Arial", 11), bg="white", width=20, anchor="w").pack(side=tk.LEFT)
        
        tk.Button(frame_oferta, text="Seleccionar Archivo", 
                 font=("Arial", 10), bg="#2196F3", fg="white",
                 command=self.cargar_oferta_academica).pack(side=tk.LEFT, padx=10)
        
        self.label_estado_oferta = tk.Label(frame_oferta, text="X No cargado", 
                                           font=("Arial", 10), bg="white", fg="red")
        self.label_estado_oferta.pack(side=tk.LEFT, padx=10)
        
        # Postulantes
        frame_post = tk.Frame(frame_archivos, bg="white")
        frame_post.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(frame_post, text="Archivo de Postulantes:", 
                font=("Arial", 11), bg="white", width=20, anchor="w").pack(side=tk.LEFT)
        
        tk.Button(frame_post, text="Seleccionar Archivo", 
                 font=("Arial", 10), bg="#2196F3", fg="white",
                 command=self.cargar_postulantes).pack(side=tk.LEFT, padx=10)
        
        self.label_estado_postulantes = tk.Label(frame_post, text="X No cargado", 
                                                 font=("Arial", 10), bg="white", fg="red")
        self.label_estado_postulantes.pack(side=tk.LEFT, padx=10)
        
        # Frame para configuración de porcentajes
        frame_config = tk.LabelFrame(frame, text="2. Configuracion de Porcentajes (%)", 
                                    font=("Arial", 12, "bold"), bg="white")
        frame_config.pack(pady=10, padx=20, fill=tk.X)
        
        self.porcentajes = {}
        campos = [
            ("Politica de Cuotas (5-10%):", 10),
            ("Mayor Vulnerabilidad (min 10%):", 10),
            ("Merito Academico (min 20%):", 20),
            ("Otros Reconocimientos (max 2%):", 2),
            ("Bachilleres Pueblos (max 10%):", 10),
            ("Bachilleres Ultimo Anio (min 20%):", 20),
            ("Poblacion General (min 20%):", 20)
        ]
        
        frame_campos = tk.Frame(frame_config, bg="white")
        frame_campos.pack(pady=10)
        
        for i, (label, valor_default) in enumerate(campos):
            row = i // 2
            col = (i % 2) * 2
            
            tk.Label(frame_campos, text=label, font=("Arial", 10), 
                    bg="white").grid(row=row, column=col, padx=10, pady=5, sticky="e")
            
            entry = tk.Entry(frame_campos, font=("Arial", 10), width=8)
            entry.insert(0, str(valor_default))
            entry.grid(row=row, column=col+1, padx=5, pady=5)
            
            # Guardar referencia sin los paréntesis
            key = label.split("(")[0].strip().rstrip(":")
            self.porcentajes[key] = entry
        
        # Checkbox para instituto
        self.var_es_instituto = tk.BooleanVar(value=False)
        tk.Checkbutton(frame_config, text="Es Instituto Tecnico/Tecnologico (Art. 53)", 
                      variable=self.var_es_instituto, font=("Arial", 10), 
                      bg="white").pack(pady=5)
        
        # Frame para ejecutar asignación
        frame_ejecutar = tk.LabelFrame(frame, text="3. Ejecutar Asignacion", 
                                       font=("Arial", 12, "bold"), bg="white")
        frame_ejecutar.pack(pady=10, padx=20, fill=tk.X)
        
        frame_botones = tk.Frame(frame_ejecutar, bg="white")
        frame_botones.pack(pady=15)
        
        self.btn_ejecutar_asignacion = tk.Button(
            frame_botones, 
            text="EJECUTAR ASIGNACION COMPLETA", 
            font=("Arial", 12, "bold"), 
            bg="#4CAF50", 
            fg="white",
            width=35, 
            height=2, 
            command=self.ejecutar_asignacion
        )
        self.btn_ejecutar_asignacion.pack(pady=10)
        
        # Nota informativa
        tk.Label(frame_ejecutar, 
                text="Este proceso ejecutara todas las vueltas de asignacion segun la normativa\n"
                     "y cerrara automaticamente cuando no haya mas asignaciones posibles.",
                font=("Arial", 9, "italic"), bg="white", fg="#666666").pack(pady=5)
        
        # Área de resultados
        frame_resultado = tk.LabelFrame(frame, text="Resultados del Proceso", 
                                       font=("Arial", 12, "bold"), bg="white")
        frame_resultado.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        self.texto_resultado = scrolledtext.ScrolledText(frame_resultado, 
                                                         font=("Courier", 9), 
                                                         height=12)
        self.texto_resultado.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Actualizar estado inicial
        self._actualizar_estado_interfaz()
    
    def cargar_oferta_academica(self):
        """Abre dialogo para cargar archivo de Oferta Academica"""
        if not self.periodo_activo:
            messagebox.showwarning("Advertencia", "Primero cree o seleccione un periodo")
            self.ir_a_periodos()
            return
        
        puede, mensaje = self.periodo_activo.puede_cargar_archivos()
        if not puede:
            messagebox.showerror("Error", mensaje)
            return
        
        archivo = filedialog.askopenfilename(
            title="Seleccionar Oferta Academica",
            filetypes=[("Archivos Excel", "*.xlsx *.xls"), ("Todos los archivos", "*.*")]
        )
        
        if archivo:
            exito, mensaje = self.periodo_activo.cargar_oferta_academica(archivo)
            
            if exito:
                self.texto_resultado.insert(tk.END, f"[OK] {mensaje}\n")
                self._actualizar_estado_interfaz()
            else:
                messagebox.showerror("Error", mensaje)
    
    def cargar_postulantes(self):
        """Abre dialogo para cargar archivo de Postulantes"""
        if not self.periodo_activo:
            messagebox.showwarning("Advertencia", "Primero cree o seleccione un periodo")
            self.ir_a_periodos()
            return
        
        puede, mensaje = self.periodo_activo.puede_cargar_archivos()
        if not puede:
            messagebox.showerror("Error", mensaje)
            return
        
        archivo = filedialog.askopenfilename(
            title="Seleccionar Archivo de Postulantes",
            filetypes=[("Archivos Excel", "*.xlsx *.xls"), ("Todos los archivos", "*.*")]
        )
        
        if archivo:
            exito, mensaje = self.periodo_activo.cargar_postulantes(archivo)
            
            if exito:
                self.texto_resultado.insert(tk.END, f"[OK] {mensaje}\n")
                self._actualizar_estado_interfaz()
            else:
                messagebox.showerror("Error", mensaje)
    
    def ejecutar_asignacion(self):
        """Ejecuta el proceso completo de asignacion"""
        if not self.periodo_activo:
            messagebox.showwarning("Advertencia", "Primero cree o seleccione un periodo")
            self.ir_a_periodos()
            return
        
        puede, mensaje = self.periodo_activo.puede_asignar()
        if not puede:
            messagebox.showerror("Error", mensaje)
            return
        
        # Confirmar ejecución
        respuesta = messagebox.askyesno(
            "Confirmar Asignacion",
            f"Esta seguro de ejecutar la asignacion para el periodo {self.periodo_activo.codigo}?\n\n"
            "Este proceso:\n"
            "- Ejecutara todas las vueltas de asignacion necesarias\n"
            "- Aplicara la normativa del Art. 52\n"
            "- No se puede deshacer una vez completado"
        )
        
        if not respuesta:
            return
        
        # Configurar porcentajes del periodo
        try:
            porcentajes = {
                'politica_cuotas': float(self.porcentajes["Politica de Cuotas"].get()) / 100,
                'vulnerabilidad': float(self.porcentajes["Mayor Vulnerabilidad"].get()) / 100,
                'merito_academico': float(self.porcentajes["Merito Academico"].get()) / 100,
                'otros_reconocimientos': float(self.porcentajes["Otros Reconocimientos"].get()) / 100,
                'bachilleres_pueblos': float(self.porcentajes["Bachilleres Pueblos"].get()) / 100,
                'bachilleres_ultimo': float(self.porcentajes["Bachilleres Ultimo Anio"].get()) / 100,
                'poblacion_general': float(self.porcentajes["Poblacion General"].get()) / 100
            }
            
            self.periodo_activo.configuracion.porcentajes = porcentajes
            self.periodo_activo.configuracion.es_instituto = self.var_es_instituto.get()
            
        except ValueError as e:
            messagebox.showerror("Error", f"Error en porcentajes: verifique que sean numeros validos")
            return
        
        # Deshabilitar botón durante ejecución
        self.btn_ejecutar_asignacion.config(state=tk.DISABLED, text="PROCESANDO...")
        self.texto_resultado.delete(1.0, tk.END)
        self.texto_resultado.insert(tk.END, "Iniciando proceso de asignacion...\n")
        self.texto_resultado.insert(tk.END, f"Periodo: {self.periodo_activo.codigo}\n")
        self.texto_resultado.insert(tk.END, f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        self.texto_resultado.insert(tk.END, "=" * 50 + "\n\n")
        self.ventana.update()
        
        # Callback para mostrar progreso
        def callback_progreso(mensaje):
            self.texto_resultado.insert(tk.END, mensaje + "\n")
            self.texto_resultado.see(tk.END)
            self.ventana.update()
        
        # Ejecutar asignación
        try:
            exito, mensaje, estadisticas = self.periodo_activo.ejecutar_asignacion_completa(callback_progreso)
            
            if exito:
                self.texto_resultado.insert(tk.END, "\n" + "=" * 50 + "\n")
                self.texto_resultado.insert(tk.END, "[OK] PROCESO COMPLETADO EXITOSAMENTE\n")
                self.texto_resultado.insert(tk.END, "=" * 50 + "\n\n")
                
                # Mostrar estadísticas
                self.texto_resultado.insert(tk.END, "ESTADISTICAS FINALES:\n")
                self.texto_resultado.insert(tk.END, f"  Vueltas ejecutadas: {estadisticas.get('vueltas_ejecutadas', 0)}\n")
                self.texto_resultado.insert(tk.END, f"  Total asignados: {estadisticas.get('total_asignados', 0)}\n")
                
                if 'por_grupo' in estadisticas:
                    self.texto_resultado.insert(tk.END, "\nPor grupo:\n")
                    for grupo, cantidad in estadisticas['por_grupo'].items():
                        self.texto_resultado.insert(tk.END, f"  {grupo}: {cantidad}\n")
                
                messagebox.showinfo("Exito", mensaje)
            else:
                self.texto_resultado.insert(tk.END, f"\n[ERROR] {mensaje}\n")
                messagebox.showerror("Error", mensaje)
                
        except Exception as e:
            self.texto_resultado.insert(tk.END, f"\n[ERROR] {str(e)}\n")
            messagebox.showerror("Error", f"Error durante la asignacion: {str(e)}")
        
        finally:
            # Restaurar botón
            self.btn_ejecutar_asignacion.config(text="EJECUTAR ASIGNACION COMPLETA")
            self._actualizar_estado_interfaz()
    
    def crear_pestana_reportes(self):
        """Pestana para generar reportes"""
        frame = tk.Frame(self.notebook, bg="white")
        self.notebook.add(frame, text="Reportes")
        
        tk.Label(frame, text="Generacion de Reportes", 
                font=("Arial", 16, "bold"), bg="white").pack(pady=20)
        
        # Botones de tipos de reportes
        botones_frame = tk.Frame(frame, bg="white")
        botones_frame.pack(pady=20)
        
        tk.Button(botones_frame, text="Reporte General de Asignacion", 
                 font=("Arial", 11), bg="#4CAF50", fg="white",
                 width=30, height=2, command=self.generar_reporte_general).pack(pady=10)
        
        tk.Button(botones_frame, text="Reporte por Carrera", 
                 font=("Arial", 11), bg="#2196F3", fg="white",
                 width=30, height=2, command=self.generar_reporte_carrera).pack(pady=10)
        
        tk.Button(botones_frame, text="Reporte por Grupo", 
                 font=("Arial", 11), bg="#FF9800", fg="white",
                 width=30, height=2, command=self.generar_reporte_grupo).pack(pady=10)
        
        # Área de visualización de reportes
        reporte_frame = tk.LabelFrame(frame, text="Visualizacion de Reporte", 
                                     font=("Arial", 12, "bold"), bg="white")
        reporte_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        self.texto_reporte = scrolledtext.ScrolledText(reporte_frame, 
                                                       font=("Courier", 9), 
                                                       height=20)
        self.texto_reporte.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def crear_pestana_consultas(self):
        """Pestana para consultas de postulantes"""
        frame = tk.Frame(self.notebook, bg="white")
        self.notebook.add(frame, text="Consultas")
        
        tk.Label(frame, text="Consultar Postulantes", 
                font=("Arial", 16, "bold"), bg="white").pack(pady=20)
        
        # Búsqueda
        busqueda_frame = tk.Frame(frame, bg="white")
        busqueda_frame.pack(pady=10)
        
        tk.Label(busqueda_frame, text="Identificacion:", 
                font=("Arial", 11), bg="white").grid(row=0, column=0, padx=10)
        
        self.entry_busqueda = tk.Entry(busqueda_frame, font=("Arial", 11), width=25)
        self.entry_busqueda.grid(row=0, column=1, padx=10)
        
        tk.Button(busqueda_frame, text="Buscar", font=("Arial", 11), 
                 bg="#2196F3", fg="white", width=15,
                 command=self.buscar_postulante).grid(row=0, column=2, padx=10)
        
        # Resultados
        resultado_frame = tk.LabelFrame(frame, text="Resultados de Busqueda", 
                                       font=("Arial", 12, "bold"), bg="white")
        resultado_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        self.texto_consulta = scrolledtext.ScrolledText(resultado_frame, 
                                                        font=("Courier", 9), 
                                                        height=20)
        self.texto_consulta.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # ============== Metodos de Reportes ==============
    
    def generar_reporte_general(self):
        """Genera reporte general"""
        try:
            df_asignaciones = self._obtener_asignaciones()
            if df_asignaciones is None or df_asignaciones.empty:
                messagebox.showwarning("Advertencia", "No hay asignaciones para generar reporte")
                return
            
            reporte = Reporte().generar_reporte_completo(df_asignaciones, guardar_excel=True)
            
            if 'error' in reporte:
                messagebox.showerror("Error", reporte['error'])
                return
            
            self.texto_reporte.delete(1.0, tk.END)
            self.texto_reporte.insert(tk.END, "=== REPORTE GENERAL DE ASIGNACION ===\n\n")
            self.texto_reporte.insert(tk.END, f"Periodo: {self.periodo_activo.codigo if self.periodo_activo else 'N/A'}\n")
            self.texto_reporte.insert(tk.END, f"Total de asignaciones: {reporte['total_asignaciones']}\n\n")
            self.texto_reporte.insert(tk.END, "Asignaciones por Grupo:\n")
            for grupo, cantidad in reporte.get('por_grupo', {}).items():
                self.texto_reporte.insert(tk.END, f"  {grupo}: {cantidad}\n")
            
            self.texto_reporte.insert(tk.END, f"\nPuntaje Promedio: {reporte.get('puntaje_promedio', 0):.2f}\n")
            self.texto_reporte.insert(tk.END, f"Puntaje Maximo: {reporte.get('puntaje_maximo', 0):.2f}\n")
            self.texto_reporte.insert(tk.END, f"Puntaje Minimo: {reporte.get('puntaje_minimo', 0):.2f}\n")
            
            if 'archivo_generado' in reporte:
                self.texto_reporte.insert(tk.END, f"\n[OK] Reporte guardado en: {reporte['archivo_generado']}\n")
                messagebox.showinfo("Exito", f"Reporte generado")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte: {str(e)}")
    
    def generar_reporte_carrera(self):
        """Genera reporte por carrera"""
        try:
            df_asignaciones = self._obtener_asignaciones()
            if df_asignaciones is None or df_asignaciones.empty:
                messagebox.showwarning("Advertencia", "No hay asignaciones para generar reporte")
                return
            
            reporte = Reporte().generar_reporte_por_carrera(df_asignaciones, carrera=None, guardar_excel=True)
            
            self.texto_reporte.delete(1.0, tk.END)
            self.texto_reporte.insert(tk.END, "=== REPORTE POR CARRERA ===\n\n")
            
            if 'carreras' in reporte:
                for carrera, cantidad in reporte['carreras'].items():
                    self.texto_reporte.insert(tk.END, f"{carrera}: {cantidad} asignados\n")
            
            if 'archivo_generado' in reporte:
                messagebox.showinfo("Exito", "Reporte generado")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte: {str(e)}")
    
    def generar_reporte_grupo(self):
        """Genera reporte por grupo"""
        try:
            df_asignaciones = self._obtener_asignaciones()
            if df_asignaciones is None or df_asignaciones.empty:
                messagebox.showwarning("Advertencia", "No hay asignaciones para generar reporte")
                return
            
            reporte = Reporte().generar_reporte_por_grupo(df_asignaciones, guardar_excel=True)
            
            self.texto_reporte.delete(1.0, tk.END)
            self.texto_reporte.insert(tk.END, "=== REPORTE POR GRUPO ===\n\n")
            
            if 'detalle_por_grupo' in reporte:
                for grupo, cantidad in reporte['detalle_por_grupo'].items():
                    self.texto_reporte.insert(tk.END, f"{grupo}: {cantidad} asignados\n")
            
            if 'archivo_generado' in reporte:
                messagebox.showinfo("Exito", "Reporte generado")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte: {str(e)}")
    
    def _obtener_asignaciones(self):
        """Obtiene el DataFrame de asignaciones del periodo o archivo"""
        if self.periodo_activo:
            df = self.periodo_activo.obtener_asignaciones()
            if df is not None:
                return df
        
        # Intentar leer del archivo
        try:
            return pd.read_excel("Asignaciones.xlsx")
        except:
            return None
    
    def buscar_postulante(self):
        """Busca informacion de un postulante"""
        identificacion = self.entry_busqueda.get().strip()
        
        if not identificacion:
            messagebox.showwarning("Advertencia", "Ingrese una identificacion")
            return
        
        try:
            df_asignaciones = self._obtener_asignaciones()
            
            self.texto_consulta.delete(1.0, tk.END)
            
            if df_asignaciones is None or df_asignaciones.empty:
                self.texto_consulta.insert(tk.END, "No hay datos de asignaciones disponibles\n")
                return
            
            resultado = df_asignaciones[df_asignaciones['identificacion'] == identificacion]
            
            if resultado.empty:
                self.texto_consulta.insert(tk.END, f"No se encontraron asignaciones para: {identificacion}\n")
            else:
                self.texto_consulta.insert(tk.END, f"=== INFORMACION DEL POSTULANTE ===\n\n")
                self.texto_consulta.insert(tk.END, f"Identificacion: {identificacion}\n")
                self.texto_consulta.insert(tk.END, f"Carrera: {resultado.iloc[0]['carrera']}\n")
                self.texto_consulta.insert(tk.END, f"Puntaje: {resultado.iloc[0]['puntaje']}\n")
                self.texto_consulta.insert(tk.END, f"Grupo: {resultado.iloc[0]['grupo']}\n")
                self.texto_consulta.insert(tk.END, f"Estado: {resultado.iloc[0]['estado']}\n")
                self.texto_consulta.insert(tk.END, f"Fecha Asignacion: {resultado.iloc[0]['fecha_asignacion']}\n")
                if 'vuelta' in resultado.columns:
                    self.texto_consulta.insert(tk.END, f"Vuelta de Asignacion: {resultado.iloc[0]['vuelta']}\n")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error en busqueda: {str(e)}")
    
    # ============== Metodos de navegacion ==============
    
    def ir_a_periodos(self):
        self.notebook.select(1)
    
    def ir_a_asignacion(self):
        self.notebook.select(2)
    
    def ir_a_reportes(self):
        self.notebook.select(3)
    
    def ir_a_consultas(self):
        self.notebook.select(4)
    
    def cerrar_sesion(self):
        """Cierra la sesion y vuelve a la ventana principal"""
        self.ventana.destroy()
        self.ventana_principal.deiconify()
