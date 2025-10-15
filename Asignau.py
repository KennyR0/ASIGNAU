import pandas as pd

#ASIGNAU (ASIGNACIÓN UNIVERSITARIA)

"Clase Padre"
class Invitado:

    def iniciar_sesion(self,intento_cedu:str,intento_contra):
        print(f"Paso la cedula: {intento_cedu} y la contraseña: {intento_contra}")
        base_dato = self.cargar_base()
        usuario = base_dato[base_dato['Identificación']== intento_cedu]

        if usuario.iloc[0]['Contraseña'] == intento_contra:
            return True
        return False
        

    def visualizar_ventana(self):
        #Aqui visualizaria la ventana de login
        pass
    
    def cargar_base(self):
        base = pd.read_excel("EJEMPLO_MATRIZ_ASIGNACIÓN_2025-2.xlsx",sheet_name=1)
        return base

"Clase Hija"
class Administrador(Invitado):

    #Atributo de clase
    Periodo  = "2025 - 2"
    #Atributos de instancia
    def __init__(self,nombre,cedula,correo,contraseña):
        print(f"Administrador: {nombre}, con correo: {correo} y cédula:{cedula} creado")

        self.nombre = nombre
        self.cedula = cedula
        self.correo = correo
        self.contraseña = contraseña
        self.estado = True
    
    #Metodos
    def subir_malla(self):
        return print("Se ha subido nueva malla curricular")

    def editar_malla(self):
        return print("Se ha editado la malla curricular")

    def esta_activo(self):
        return self.estado
        
"Clase Hija"
class Postulante(Invitado):
    
    #Atributos de Instancia 
    def __init__(self,nombre):
        self.postulante = {
            'Nombre' : nombre
        }

    #Metodos
    def ver_puntaje(self):
        return self.puntaje

    def cambiar_contraseña(self,nueva_contraseña):
        self.contraseña = nueva_contraseña
        return (f"Contraseña cambiada ")

class Solicitud_cupo():
    #Atributo de clase
    Periodo = "2025 - 2"

    #Atributo de instancia
    def __init__(self,nombre,carrera,universidad,):
        print(f"Cupo del postulante: {nombre}, de la carrera: {carrera} para {universidad} ha sido leído")

        self.postulante = nombre
        self.carrera = carrera
        self.universidad = universidad
        self.Periodo = 2025
        self.estado = True
    
    #Metodos
    def seleccionar_carrera(self):
        return (f"Se selecciona la carrera: {self.carrera}")
    
    def fecha(self):
        return self.Periodo
    
    def esta_activo(self):
        return self.estado

class Cupo:

    def __init__(self, id_cupo, carrera, ocupado=False):
        self.id_cupo = id_cupo
        self.carrera = carrera
        self.ocupado = ocupado

    #Metodo
    def asignar(self):
        self.ocupado = True

    def liberar(self):
        self.ocupado = False

    def esta_disponible(self):
        return not self.ocupado

class Asignacion:
    #Atributos
    def __init__(self, postulante, carrera, universidad):
        self.postulante = postulante
        self.carrera = carrera
        self.universidad = universidad
    #Metodo
    def asignar_cupo(self):
        return (f"Se le asigna el cupo al postulante {self.postulante}")

    def validar_postulante(self):
        return (f"Se ha validado el postulante")

    def cancelar_asignacion(self):
        return (f"Se ha cancelado el cupo")

class Reporte:

    def __init__(self):
        self.reporte = {
            'IES_ID' : id
        }
    
Intento = Invitado()
print(Intento.iniciar_sesion("1350432058","PEpe1315"))