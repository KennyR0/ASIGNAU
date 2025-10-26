from Backend import Postulante
from front import tk,messagebox

class VentanaPostulante:
    """Ventana para el postulante con sus datos cargados"""
    
    def __init__(self, ventana, postulante: Postulante, ventana_principal):
        self.ventana = ventana
        self.postulante = postulante  # INSTANCIA DE POSTULANTE CON DATOS
        self.ventana_principal = ventana_principal
        
        self.ventana.title("Panel de Postulante")
        self.ventana.geometry("800x600")
        
        # Barra superior con información del postulante
        barra_superior = tk.Frame(ventana, bg="#00af09", height=80)
        barra_superior.pack(fill=tk.X, side=tk.TOP)
        
        titulo = tk.Label(barra_superior, 
                         text=f"Bienvenido Postulante: {self.postulante.identificacion}", 
                         font=("Arial", 16, "bold"), 
                         bg="#00af09", 
                         fg="white")
        titulo.pack(pady=10)
        
        info = tk.Label(barra_superior, 
                       text=f"Puntaje: {self.postulante.puntaje_postulacion} | Segmento: {self.postulante.segmento_aspirante}", 
                       font=("Arial", 10), 
                       bg="#00af09", 
                       fg="white")
        info.pack()

        # Frame principal
        frame_principal = tk.Frame(ventana, bg="white")
        frame_principal.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Mostrar postulaciones
        self.mostrar_postulaciones(frame_principal)

        # Botones de funcionalidad
        frame_botones = tk.Frame(frame_principal, bg="white")
        frame_botones.pack(pady=20)
        
        tk.Button(frame_botones, text="Ver Puntaje Completo", 
                 font=("Arial", 12), width=25, height=2,
                 command=self.mostrar_puntaje).grid(row=0, column=0, padx=10, pady=10)
        
        tk.Button(frame_botones, text="Ver Información Completa", 
                 font=("Arial", 12), width=25, height=2,
                 command=self.mostrar_info).grid(row=0, column=1, padx=10, pady=10)
        
        tk.Button(frame_botones, text="Cambiar Contraseña", 
                 font=("Arial", 12), width=25, height=2,
                 command=None).grid(row=1, column=0, padx=10, pady=10)
        
        tk.Button(frame_botones, text="Cerrar Sesión", 
                 font=("Arial", 12), width=25, height=2,
                 bg="#f44336", fg="white",
                 command=self.cerrar_sesion).grid(row=1, column=1, padx=10, pady=10)

    def mostrar_postulaciones(self, parent):
        """Muestra las postulaciones del usuario"""
        frame_post = tk.LabelFrame(parent, text="Mis Postulaciones", 
                                   font=("Arial", 12, "bold"), bg="white")
        frame_post.pack(pady=20, fill=tk.BOTH, expand=True)
        
        postulaciones = self.postulante.obtener_postulaciones()
        
        tk.Label(frame_post, text=f"Carrera: {postulaciones['carrera']}", 
                font=("Arial", 11), bg="white").pack(pady=5)
        tk.Label(frame_post, text=f"Prioridad: {postulaciones['prioridad']}", 
                font=("Arial", 11), bg="white").pack(pady=5)
        tk.Label(frame_post, text=f"Segmento: {postulaciones['segmento']}", 
                font=("Arial", 11), bg="white").pack(pady=5)

    def mostrar_puntaje(self):
        """Muestra el puntaje del postulante"""
        puntaje = self.postulante.ver_puntaje()
        messagebox.showinfo("Mi Puntaje", 
                           f"Tu puntaje de postulación es: {puntaje}")

    def mostrar_info(self):
        """Muestra toda la información del postulante"""
        info = self.postulante.mostrar_informacion() #llama al método de la clase dentro del backend
        mensaje = "\n".join([f"{c}: {v}" for c, v in info.items()]) #Muestra el diccionario por línea de Clave: Valor
        messagebox.showinfo("Información del Postulante", mensaje) #Muestra la información en un mensaje flotante 

    def cambiar_contraseña(self):
        pass
        
    def cerrar_sesion(self):
        """Cierra la sesión y vuelve a la ventana principal"""
        self.ventana.destroy()
        self.ventana_principal.deiconify()