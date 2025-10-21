import tkinter as tk
from tkinter import messagebox

class Login:
    def __init__(self, ventana_loging):
        self.ventana_loging = ventana_loging
        ventana_loging.title("Login")

        self.etiqueta_cedula = tk.Label(ventana_loging, text="Cédula:")
        self.etiqueta_cedula.pack()

        self.entry_cedula = tk.Entry(ventana_loging)
        self.entry_cedula.pack()

        self.etiqueta_contraseña = tk.Label(ventana_loging, text="Contraseña:")
        self.etiqueta_contraseña.pack()

        self.entry_contraseña = tk.Entry(ventana_loging, show="*")
        self.entry_contraseña.pack()

        self.login_button = tk.Button(ventana_loging, text="Iniciar Sesión", command=None)
        self.login_button.pack()


class Ventana_principal():
    def __init__(self, principal):
        self.principal = principal
        self.principal.title("ASIGNAU")
        self.principal.geometry("600x400")
        self.principal.resizable(False, False)
        self.principal.attributes('-fullscreen', True)
        
        self.centrar_ventana()
        
        barra_superior = tk.Frame(principal, bg="#2c3e50", height=60)
        barra_superior.pack(fill=tk.X, side=tk.TOP)
        
        titulo = tk.Label(barra_superior, text="Accede a nuestro programa ASIGNAU", 
                         font=("Arial", 18, "bold"), bg="#2c3e50", fg="white")
        titulo.pack(pady=15)

        frame_principal = tk.Frame(principal, bg="white")
        frame_principal.pack(fill=tk.BOTH, expand=True, padx=20, pady=40)

        frame_botones = tk.Frame(frame_principal, bg="white")
        frame_botones.pack(expand=True)
        
        btn_postulante = tk.Button(
            frame_botones,
            text="Iniciar sesión\ncomo postulante",
            font=("Arial", 12),
            bg="#69f870",
            fg="white",
            width=20,
            height=4,
            cursor="hand2",
            relief=tk.RAISED,
            bd=3,
            command=self.login_postulante
        )
        btn_postulante.pack(side=tk.LEFT, padx=20)

        btn_admin = tk.Button(
            frame_botones,
            text="Iniciar sesión\ncomo administrador",
            font=("Arial", 12),
            bg="#e74c3c",
            fg="white",
            width=20,
            height=4,
            cursor="hand2",
            relief=tk.RAISED,
            bd=3,
            command=None
        )
        btn_admin.pack(side=tk.LEFT, padx=20)
    
    def centrar_ventana(self):
        self.principal.update_idletasks()
        ancho = self.principal.winfo_width()
        alto = self.principal.winfo_height()
        x = (self.principal.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.principal.winfo_screenheight() // 2) - (alto // 2)
        self.principal.geometry(f'{ancho}x{alto}+{x}+{y}')
    
    def login_postulante(self):
        self.principal.withdraw()
        ventana_login = tk.Toplevel(self.principal)
        app = Login(ventana_login)