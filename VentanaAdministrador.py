from Backend import Administrador
from front import tk,messagebox

class VentanaAdministrador:
    """Ventana para el administrador con sus datos cargados"""
    
    def __init__(self, ventana, admin: Administrador, ventana_principal):
        self.ventana = ventana
        self.admin = admin  # INSTANCIA DE ADMINISTRADOR CON DATOS
        self.ventana_principal = ventana_principal
        
        self.ventana.title("Panel de Administrador")
        self.ventana.geometry("800x600")
        
        # Barra superior con información del admin
        barra_superior = tk.Frame(ventana, bg="#2c3e50", height=80)
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

        # Frame principal
        frame_principal = tk.Frame(ventana, bg="white")
        frame_principal.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Botones de funcionalidad
        tk.Button(frame_principal, text="Subir Malla Curricular", 
                 font=("Arial", 12), width=30, height=2,
                 command=None).pack(pady=10)
        
        tk.Button(frame_principal, text="Editar Malla Curricular", 
                 font=("Arial", 12), width=30, height=2,
                 command=None).pack(pady=10)
        
        tk.Button(frame_principal, text="Ver Información Completa", 
                 font=("Arial", 12), width=30, height=2,
                 command=self.mostrar_info).pack(pady=10)
        
        tk.Button(frame_principal, text="Cerrar Sesión", 
                 font=("Arial", 12), width=30, height=2,
                 bg="#f44336", fg="white",
                 command=self.cerrar_sesion).pack(pady=10)

    def mostrar_info(self):
        """Muestra toda la información del administrador"""
        info = self.admin.mostrar_informacion() #llama al método de la clase dentro del backend
        mensaje = "\n".join([f"{c}: {v}" for c, v in info.items()]) #Muestra el diccionario por línea de Clave: Valor
        messagebox.showinfo("Información del Administrador", mensaje) #Muestra la información en un mensaje flotante 

    def cerrar_sesion(self):
        """Cierra la sesión y vuelve a la ventana principal"""
        self.ventana.destroy()
        self.ventana_principal.deiconify()