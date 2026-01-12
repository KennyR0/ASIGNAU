import tkinter as tk # Interfaz grafica
from tkinter import messagebox #Interfaz de mensaje flotante
from PIL import Image, ImageTk # Para manejar imágenes
from Backend_Completo import (SistemaAutenticacion, Administrador, Postulante) #Importado del Backend - Usando el Facade
from VentanaAdministrador_Completa import VentanaAdministrador 
from VentanaPostulante_Completa import VentanaPostulante

# Colores del tema
azul_oscuro = "#00071D"
azul_oscuro2 = "#00072D"
azul_claro = "#00074D"

class Ventana_principal():
    def __init__(self, principal):
        
        self.principal = principal
        self.principal.title("AsignaU") # Titulo de la ventana
        
        # Pantalla completa
        self.principal.attributes('-fullscreen', True)
        
        # Obtener dimensiones de pantalla
        self.screen_width = self.principal.winfo_screenwidth()
        self.screen_height = self.principal.winfo_screenheight()
        
        # Calcular ancho del panel izquierdo (40% de la pantalla)
        self.left_width = int(self.screen_width * 0.4)

        # Panel izquierdo (contenido)
        self.left_frame = tk.Frame(self.principal, bg=azul_oscuro, width=self.left_width)
        self.left_frame.pack(side="left", fill="both")
        self.left_frame.pack_propagate(False)

        # Panel derecho (imagen)
        self.right_frame = tk.Frame(self.principal, bg=azul_oscuro2)
        self.right_frame.pack(side="right", fill="both", expand=True)

        # Cargar imagen de fondo en el panel derecho
        try:
            big_img = Image.open("primer_logo.png")
            # Redimensionar imagen proporcionalmente al tamaño de la pantalla
            img_size = min(self.screen_width - self.left_width, self.screen_height)
            big_img = big_img.resize((img_size, img_size))
            self.big_photo = ImageTk.PhotoImage(big_img)
            big_lbl = tk.Label(self.right_frame, image=self.big_photo, bg=azul_oscuro2)
            big_lbl.place(relx=0.5, rely=0.5, anchor="center")
        except Exception:
            pass

        # Crear contenido del panel izquierdo
        self._crear_inicio()

    def _crear_inicio(self):
        """Crea el contenido inicial del panel izquierdo"""
        # Limpiar panel izquierdo
        for widget in self.left_frame.winfo_children():
            widget.destroy()

        # Contenedor centrado para el contenido
        contenedor = tk.Frame(self.left_frame, bg=azul_oscuro)
        contenedor.place(relx=0.5, rely=0.5, anchor="center")

        # Título de bienvenida
        lbl_title = tk.Label(
            contenedor, 
            text="Bienvenido a\nAsignaU",
            font=("Trebuchet MS", 36, "bold"), 
            fg="white", 
            bg=azul_oscuro, 
            justify="center"
        )
        lbl_title.pack(pady=(0, 30))

        # Descripción
        lbl_sub = tk.Label(
            contenedor,
            text=("Te damos la bienvenida a nuestro sistema de aceptación de cupo.\n"
                  "AsignaU es la herramienta que utilizarás para manejar\n"
                  "la solicitud y aceptación de cupos a la universidad\n"
                  "ecuatoriana de tu elección."),
            font=("Trebuchet MS", 14), 
            fg="white", 
            bg=azul_oscuro, 
            justify="center"
        )
        lbl_sub.pack(pady=(0, 50))

        # Botón Postulante
        btn_postulante = tk.Button(
            contenedor, 
            text="Iniciar sesión como postulante", 
            bg=azul_claro, 
            fg="white",
            font=("Trebuchet MS", 14), 
            width=32, 
            height=2,
            command=self.login_postulante, 
            cursor="hand2"
        )
        btn_postulante.pack(pady=10)

        # Botón Administrador
        btn_admin = tk.Button(
            contenedor, 
            text="Iniciar sesión como administrador", 
            bg=azul_claro, 
            fg="white",
            font=("Trebuchet MS", 14), 
            width=32, 
            height=2,
            command=self.login_admin, 
            cursor="hand2"
        )
        btn_admin.pack(pady=10)

        # Botón Salir
        btn_salir = tk.Button(
            contenedor, 
            text="Salir", 
            bg=azul_claro, 
            fg="white",
            font=("Trebuchet MS", 14), 
            width=32, 
            height=2,
            command=self.salir, 
            cursor="hand2"
        )
        btn_salir.pack(pady=10)
    
    def centrar_ventana(self):
        
        self.principal.update_idletasks() 
        ancho = self.principal.winfo_width() #obtener ancho actual de un widget en pixeles
        alto = self.principal.winfo_height()
        # Calcula la coordenada X e Y para centrar la ventana en la pantalla
        x = (self.principal.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.principal.winfo_screenheight() // 2) - (alto // 2)
        # Aplica la nueva geometría: tamaño y posición centrada
        self.principal.geometry(f'{ancho}x{alto}+{x}+{y}')
    
    def login_postulante(self):
        self.principal.withdraw() #cierra la ventana principal
        ventana_login = tk.Toplevel(self.principal)
        app = Login(ventana_login, "postulante", self.principal)

    def login_admin(self):
        self.principal.withdraw()
        ventana_login = tk.Toplevel(self.principal) #Toplevel: Crea la ventana login sobre las demás
        app = Login(ventana_login, "administrador", self.principal)
    
    def salir(self):
        self.principal.destroy()

class Login:
    def __init__(self, ventana_loging, tipo_usuario: str, ventana_principal):

        self.tipo_usuario = tipo_usuario  # "postulante" o "administrador"
        self.ventana_login = ventana_loging
        self.ventana_principal = ventana_principal
        
        ventana_loging.title("Login")
        ventana_loging.geometry("450x350")
        ventana_loging.configure(bg=azul_oscuro)
        ventana_loging.resizable(False, False)
        
        # Centrar ventana
        self.centrar_ventana()

        # Título
        titulo = tk.Label(ventana_loging, text="Iniciar Sesión", 
                         font=("Trebuchet MS", 20, "bold"),
                         bg=azul_oscuro, fg="white")
        titulo.pack(pady=30)

        # Frame para campos
        frame_campos = tk.Frame(ventana_loging, bg=azul_oscuro)
        frame_campos.pack(pady=20)

        # identificacion = cedula,correo,pasaporte
        self.etiqueta_cedula = tk.Label(frame_campos, text="Identificación:", 
                                        font=("Trebuchet MS", 12),
                                        bg=azul_oscuro, fg="white")
        self.etiqueta_cedula.grid(row=0, column=0, padx=10, pady=10, sticky="e")

        self.entry_cedula = tk.Entry(frame_campos, font=("Trebuchet MS", 12), width=25)
        self.entry_cedula.grid(row=0, column=1, padx=10, pady=10)

        # Contraseña
        self.etiqueta_contraseña = tk.Label(frame_campos, text="Contraseña:", 
                                            font=("Trebuchet MS", 12),
                                            bg=azul_oscuro, fg="white")
        self.etiqueta_contraseña.grid(row=1, column=0, padx=10, pady=10, sticky="e")

        self.__entry_contraseña = tk.Entry(frame_campos, show="*", 
                                           font=("Trebuchet MS", 12), width=25)
        self.__entry_contraseña.grid(row=1, column=1, padx=10, pady=10)

        # Frame para botones
        frame_botones = tk.Frame(ventana_loging, bg=azul_oscuro)
        frame_botones.pack(pady=30)

        # Botón login
        self.login_button = tk.Button(
            frame_botones, 
            text="Iniciar Sesión", 
            command=self.validar_login,
            font=("Trebuchet MS", 12),
            bg=azul_claro,
            fg="white",
            width=15,
            height=1,
            cursor="hand2"
        )
        self.login_button.grid(row=0, column=0, padx=10)

        # Botón cancelar
        self.cancelar_button = tk.Button(
            frame_botones, 
            text="Cancelar", 
            command=self.cancelar,
            font=("Trebuchet MS", 12),
            bg=azul_claro,
            fg="white",
            width=15,
            height=1,
            cursor="hand2"
        )
        self.cancelar_button.grid(row=0, column=1, padx=10)

    def validar_login(self):
        """Valida las credenciales del usuario usando el Facade"""
        cedula = self.entry_cedula.get().strip() 
        contraseña = self.__entry_contraseña.get() 
        
        # Validar que los campos no estén vacíos
        if not cedula or not contraseña:
            messagebox.showerror("Error", "Por favor complete todos los campos")
            return
        
        # Usar el Facade según el tipo de usuario
        if self.tipo_usuario == "postulante":
            exito, usuario, mensaje = SistemaAutenticacion.login_postulante(cedula, contraseña)
        else:
            exito, usuario, mensaje = SistemaAutenticacion.login_administrador(cedula, contraseña)
        
        if exito and usuario:
            messagebox.showinfo("Éxito", mensaje)
            self.ventana_login.destroy()
            
            # Usar el método del Facade para determinar el tipo
            tipo = SistemaAutenticacion.obtener_tipo_usuario(usuario)
            if tipo == "administrador":
                self.abrir_ventana_admin(usuario)
            elif tipo == "postulante":
                self.abrir_ventana_postulante(usuario)
        else:
            messagebox.showerror("Error", mensaje)

    def centrar_ventana(self):
    
        self.ventana_login.update_idletasks()
        ancho = self.ventana_login.winfo_width()
        alto = self.ventana_login.winfo_height()
        x = (self.ventana_login.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.ventana_login.winfo_screenheight() // 2) - (alto // 2)
        self.ventana_login.geometry(f'{ancho}x{alto}+{x}+{y}')

    def abrir_ventana_admin(self, admin: Administrador):
        """Abre la ventana del administrador con sus datos"""
        ventana_admin = tk.Toplevel()
        VentanaAdministrador(ventana_admin, admin, self.ventana_principal)

    def abrir_ventana_postulante(self, postulante: Postulante):
        """Abre la ventana del postulante con sus datos"""
        ventana_postulante = tk.Toplevel()
        VentanaPostulante(ventana_postulante, postulante, self.ventana_principal)

    def cancelar(self):
        """Cancela el login y vuelve a la ventana principal"""
        self.ventana_login.destroy() #Destruye la ventana login
        self.ventana_principal.deiconify() #Restaura la ventana previamente eliminada con withdrwaw



