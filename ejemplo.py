import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
azul_marino = "#002A5E" 
gris_claro = "#ecf0f1"
azul_brillante = "#3498db" 
azul_claro = "#00074D"
celeste = "#b6ffff" 
negro = "#000000"
azul_oscuro = "#00071D"
azul_oscuro2 = "#00072D"
class AsignacionCupo:
    def __init__(self, root):
        self.root = root
        self.root.title("AsignaU")
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = 1000
        window_height = 550
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.minsize(800, 550) 
        self.root.resizable(False, False)
        self.main_card_frame = tk.Frame(self.root, bg=azul_oscuro2)
        self.main_card_frame.place(relx=0.5, rely=0.5, anchor="center", width=850, height=650)
        left_frame = tk.Frame(self.root, bg=azul_oscuro, width=400, height=500)
        left_frame.pack(side="left", fill="both")  

        welcome_label = tk.Label(left_frame, text="Bienvenido a \n AsignaU" , font=("Trebuchet MS", 24, "bold"), fg="white", bg=azul_oscuro)
        welcome_label.place(x=100, y=100)
        welcome_label = tk.Label(left_frame, text="te damos la bienida a nuestro sistema de aceptacion de cupo \n Asignau es la herramienta que utilizarás para manejar  \n la solicitud y aceptación  de cupos a la universidad \n ecuatoriana de tu elección" , font=("Trebuchet MS", 10), fg="white", bg=azul_oscuro)
        welcome_label.place(x=30, y=200)

        def login3():
            for widget in self.root.winfo_children():
                widget.destroy()


            self.root = root
            self.root.title("inicio")
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            window_width = 1000
            window_height = 550
            x = (screen_width // 2) - (window_width // 2)
            y = (screen_height // 2) - (window_height // 2)
            self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
            self.root.minsize(800, 550) 
            self.root.resizable(False, False)
            azul_marino = "#002A5E" 
            gris_claro = "#ecf0f1"
            azul_brillante = "#3498db" 

            # PANEL IZQUIERDO: BIENVENIDA Y LOGO
            left_frame = tk.Frame(root, bg=azul_marino, width=400, height=500)
            left_frame.pack(side="left", fill="both") 
            welcome_label = tk.Label(left_frame, text="Bienvenido de nuevo", font=("Trebuchet MS", 20, "bold"), fg="white", bg=azul_marino)
            welcome_label.place(x=50, y=100) 
            logo_image = Image.open("segundo logo.png")  
            logo_image = logo_image.resize((200, 200))  
            logo_photo = ImageTk.PhotoImage(logo_image) 

            logo_label = tk.Label(left_frame, image=logo_photo, bg=azul_marino)
            logo_label.image = logo_photo 
            logo_label.place(x=100, y=150) 

            socials = ["Facebook", "Twitter", "Instagram", "YouTube"]

        
            for i, name in enumerate(socials):
                icon = tk.Label(left_frame, text=name, font=("Trebuchet MS", 10, "underline"), fg="white", bg=azul_marino, cursor="hand2")
                icon.place(x=50 + i*70, y=400) 


        #parte dercha
            right_frame = tk.Frame(root, bg=gris_claro, width=500, height=600)
            right_frame.pack(side="right", fill="both") 
            form_title = tk.Label(right_frame, text="Iniciar sesión", font=("Trebuchet MS", 18, "bold"), bg=gris_claro)
            form_title.place(x=80, y=80)

            email_label = tk.Label(right_frame, text="Correo electrónico", font=("Trebuchet MS", 12), bg=gris_claro)
            email_label.place(x=50, y=140)

            email_entry = tk.Entry(right_frame, width=30, font=("Trebuchet MS", 12))
            email_entry.place(x=50, y=170)

            password_label = tk.Label(right_frame, text="Contraseña", font=("Trebuchet MS", 12), bg=gris_claro)
            password_label.place(x=50, y=210)

            password_entry = tk.Entry(right_frame, width=30, font=("Trebuchet MS", 12), show="*")
            password_entry.place(x=50, y=240)

            remember_var = tk.BooleanVar()

            remember_check = tk.Checkbutton(right_frame, text="Recordarme", variable=remember_var, bg=gris_claro)
            remember_check.place(x=50, y=270)

            # Marco superior para pestañas
            marco_tabs = tk.Frame(right_frame, bg=gris_claro)
            marco_tabs.place(x=50, y=30)

            def activar_admin():
                boton_admin.config(relief="solid", bd=2)
                boton_estudiante.config(relief="flat", bd=0)
                login()

            def activar_estudiante():
                boton_estudiante.config(relief="solid", bd=2)
                boton_admin.config(relief="flat", bd=0)
                login()

            boton_admin = tk.Button(
                marco_tabs, text="Administrador",
                command=activar_admin, relief="solid", bd=2,
                font=("Trebuchet MS", 10), width=12
            )
            boton_estudiante = tk.Button(
                marco_tabs, text="Estudiantes",
                command=activar_estudiante, relief="flat", bd=0,
                font=("Trebuchet MS", 10), width=12
            )

            boton_admin.grid(row=0, column=0, padx=2)
            boton_estudiante.grid(row=0, column=1, padx=2)


        
            def login():
                email = email_entry.get()       
                password = password_entry.get() 

                if email and password:
                    for widget in self.root.winfo_children():
                        widget.destroy()


                    self.root = root
                    self.root.title("inicio")
                    screen_width = self.root.winfo_screenwidth()
                    screen_height = self.root.winfo_screenheight()
                    window_width = 1000
                    window_height = 550
                    x = (screen_width // 2) - (window_width // 2)
                    y = (screen_height // 2) - (window_height // 2)
                    self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
                    self.root.minsize(800, 550) 
                    self.root.resizable(False, False)
                    azul_marino = "#002A5E" 
                    gris_claro = "#ecf0f1"
                    azul_brillante = "#3498db" 
                else:
                    messagebox.showwarning("Error", "Por favor completa todos los campos.")

            login_btn = tk.Button(right_frame, text="Iniciar sesión ahora", bg=azul_brillante, fg="white", font=("Trebuchet MS", 12), command=login)
            login_btn.place(x=50, y=310)


            forgot_btn = tk.Label(right_frame, text="¿Olvidaste tu contraseña?", font=("Trebuchet MS", 10, "underline"), fg="blue", bg=gris_claro, cursor="hand2")
            forgot_btn.place(x=50, y=350)

            terms = tk.Label(right_frame, text='Al hacer clic en "Iniciar sesión ahora" aceptas\nTérminos de servicio | Política de privacidad', font=("Trebuchet MS", 9), bg=gris_claro, justify="center")
            terms.place(x=50, y=400)

            root.mainloop() 
        info_btn = tk.Button(left_frame, text="              inicio de sesión             ", bg=azul_claro, fg="white", font=("Trebuchet MS", 12), command=login3)
        info_btn.place(x=100, y=300) 
        def info():
            email = email_entry.get()      
            password = password_entry.get() 
        info_btn = tk.Button(left_frame, text="                ver fechas                  ", bg=azul_claro, fg="white", font=("Trebuchet MS", 12), command=info)
        info_btn.place(x=100, y=360)
        #DERECHA
        right_frame = tk.Frame(self.root, bg=azul_oscuro2)
        right_frame.pack(side="right", fill="both", expand=True)


        frame_width = 600
        frame_height = 600

        logo_image = Image.open("Copilot_20251020_132329.png")
        logo_image = logo_image.resize((frame_width, frame_height))
        logo_photo = ImageTk.PhotoImage(logo_image)
        logo_label = tk.Label(right_frame, image=logo_photo, bg=azul_oscuro2, bd=0, highlightthickness=0)
        logo_label.image = logo_photo  
        logo_label.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.root.mainloop() #importante: recordar comentar cada linea de codigo pa no olvidarme que hacen

    def cargar(self):
        email_entry = tk.Entry(right_frame, width=30, font=("Trebuchet MS", 12))
        email_entry.place(x=50, y=170)
        password_entry = tk.Entry(right_frame, width=30, font=("Trebuchet MS", 12), show="*")
        password_entry.place(x=50, y=240)


root = tk.Tk()  
AsignacionCupo(root)        