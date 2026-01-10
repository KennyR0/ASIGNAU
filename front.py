import tkinter as tk # Interfaz grafica
from tkinter import messagebox #Interfaz de mensaje flotante
from Backend_Completo import (SistemaAutenticacion, Administrador, Postulante) #Importado del Backend - Usando el Facade
from VentanaAdministrador_Completa import VentanaAdministrador 
from VentanaPostulante_Completa import VentanaPostulante

class Ventana_principal():
    def __init__(self, principal):
        
        self.principal = principal
        self.principal.title("ASIGNAU") # Titulo de la ventana
        self.principal.geometry("900x600") # Geometria de la ventana
        self.principal.resizable(False, False) #Controlar si se puede cambiar el tamaño
        self.principal.attributes('-fullscreen', True) #No obliga a la ventana a ejecutarse en pantalla completa
        
        self.centrar_ventana() 
        
        #Barra Superior
        barra_superior = tk.Frame(principal, bg="#2c3e50", height=60)
        barra_superior.pack(fill=tk.X, side=tk.TOP)
        
        #Título Central
        titulo = tk.Label(barra_superior, text="Accede a nuestro programa ASIGNAU", 
                         font=("Arial", 18, "bold"), bg="#2c3e50", fg="white")
        titulo.pack(pady=15)

        #Frames del sistemaa
        frame_principal = tk.Frame(principal, bg="white")
        frame_principal.pack(fill=tk.BOTH, expand=True, padx=20, pady=40)

        frame_botones = tk.Frame(frame_principal, bg="white")
        frame_botones.pack(expand=True)

        #Botones
        btn_postulante = tk.Button( 
            frame_botones,
            text="Iniciar sesión\ncomo postulante",
            font=("Arial", 12),
            bg="#00af09", #Cambia el color del boton
            fg="black", #Cambia el color de las letras del boton
            width=20, #Ancho del boton
            height=4, #Altura dedl boton
            cursor="hand2", #Muestra que el boton se puede clickear
            relief=tk.RAISED, #simula efecto 3d
            bd=3, #Ancho del borde
            command=self.login_postulante 
        )
        btn_postulante.pack(side=tk.LEFT, padx=20)

        btn_admin = tk.Button(
            frame_botones,
            text="Iniciar sesión\ncomo administrador",
            font=("Arial", 12),
            bg="#5f16cc", 
            fg="black", 
            width=20,
            height=4, 
            cursor="hand2",
            relief=tk.RAISED,
            bd=3,
            command=self.login_admin
        )
        btn_admin.pack(side=tk.LEFT, padx=20)

        btn_salir = tk.Button(
            frame_botones,
            text="Salir",
            font=("Arial", 12),
            bg="#f4480a",
            fg="black",
            width=20,
            height=4,
            cursor="hand2",
            relief=tk.RAISED, #simula efecto 3d
            bd=3,
            command=self.salir
        )
        btn_salir.pack(side=tk.LEFT, padx=20)
    
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
        """
        Usa el Facade SistemaAutenticacion para el login de postulante
        """
        self.principal.withdraw() #cierra la ventana principal
        ventana_login = tk.Toplevel(self.principal)
        app = Login(ventana_login, "postulante", self.principal)

    def login_admin(self):
        """
        Usa el Facade SistemaAutenticacion para el login de administrador
        """
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
        ventana_loging.geometry("400x300")
        
        # Centrar ventana
        self.centrar_ventana()

         # Título
        titulo = tk.Label(ventana_loging, text="Iniciar Sesión", 
                         font=("Arial", 16, "bold"))
        titulo.pack(pady=20)

        # Frame para campos
        frame_campos = tk.Frame(ventana_loging)
        frame_campos.pack(pady=20)

        # identificacion = cedula,correo,pasaporte
        self.etiqueta_cedula = tk.Label(frame_campos, text="Identificacion:", 
                                        font=("Arial", 11))
        self.etiqueta_cedula.grid(row=0, column=0, padx=10, pady=10, sticky="e")

        self.entry_cedula = tk.Entry(frame_campos, font=("Arial", 11), width=25)
        self.entry_cedula.grid(row=0, column=1, padx=10, pady=10)

        # Contraseña
        self.etiqueta_contraseña = tk.Label(frame_campos, text="Contraseña:", 
                                            font=("Arial", 11))
        self.etiqueta_contraseña.grid(row=1, column=0, padx=10, pady=10, sticky="e")

        self.__entry_contraseña = tk.Entry(frame_campos, show="*", 
                                           font=("Arial", 11), width=25)
        self.__entry_contraseña.grid(row=1, column=1, padx=10, pady=10)

        # Frame para botones
        frame_botones = tk.Frame(ventana_loging)
        frame_botones.pack(pady=20)

        # Botón login
        self.login_button = tk.Button(
            frame_botones, 
            text="Iniciar Sesión", 
            command=self.validar_login,
            font=("Arial", 11),
            bg="#4CAF50",
            fg="white",
            width=15,
            cursor="hand2"
        )
        self.login_button.grid(row=0, column=0, padx=10) # Posiciona los botones en una cuadrícula

        # Botón cancelar
        self.cancelar_button = tk.Button(
            frame_botones, 
            text="Cancelar", 
            command=self.cancelar,
            font=("Arial", 11),
            bg="#f44336",
            fg="white",
            width=15,
            cursor="hand2"
        )
        self.cancelar_button.grid(row=0, column=1, padx=10)

    def validar_login(self):
        """ 
        Usa el Facade SistemaAutenticacion para simplificar el proceso de login.
        El Facade oculta la complejidad de las clases internas del backend.
        """
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

class RegistroActividad:
    """Clase auxiliar para registrar eventos del sistema."""
    LOG_FILE = "registro_actividad.txt"

    @staticmethod
    def registrar_evento(mensaje: str):
        fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        linea = f"[{fecha}] {mensaje}\n"
        with open(RegistroActividad.LOG_FILE, "a", encoding="utf-8") as archivo:
            archivo.write(linea)


def parchear_eventos(Ventana_principal, Login):
    """Agrega registro de eventos a métodos clave sin modificar los originales."""

    # Guardamos el método original .salir() y lo ampliamos
    original_salir = Ventana_principal.salir
    def nuevo_salir(self):
        RegistroActividad.registrar_evento("El usuario cerró la aplicación desde la ventana principal.")
        original_salir(self)
    Ventana_principal.salir = nuevo_salir

    # Guardamos el método original .validar_login() y lo ampliamos
    original_validar = Login.validar_login
    def nuevo_validar(self):
        cedula = self.entry_cedula.get().strip()
        RegistroActividad.registrar_evento(f"Intento de inicio de sesión con ID: {cedula}")
        original_validar(self)
    Login.validar_login = nuevo_validar


# Activamos el parche una sola vez
parchear_eventos(Ventana_principal, Login)

