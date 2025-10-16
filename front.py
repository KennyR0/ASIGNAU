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
