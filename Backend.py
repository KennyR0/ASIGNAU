import pandas as pd
from abc import abstractmethod,ABC
import os
#ASIGNAU (ASIGNACIÓN UNIVERSITARIA)

#Iyección de
class Base_Dato(ABC):
    
    @abstractmethod
    def cargar_base(self):
        pass

class BD_ADMIN(Base_Dato):
    
    def cargar_base(self):
        excel = "Admin.xlsx" #Nombre de nuestro archivo excel
        if os.path.exists(excel): #Comprueba la ruta con os, buscando la existencia de nuestro archivo
            """
            Sheet_name= es la hoja del excel que estamos leyendo, 
            comenzando de 0, en este caso se usa la 6
            Skiprows = se salta rows/filas del excel
            """
            base = pd.read_excel(excel,sheet_name=0,skiprows=1)  #lee el excel usando panda
            return base
        else:
            return None

class BD_USUARIO(Base_Dato):
    def cargar_base(self):
        excel = "Postulantes.xlsx" #Nombre de nuestro archivo excel
        if os.path.exists(excel): 
            base = pd.read_excel(excel,sheet_name=5,skiprows=1)  #lee el excel usando panda
            return base
        else:
            return None

class IniciarSesion:
    
    def Inciar(self,intento_identifacion:str,intento_contra:str,bd:Base_Dato):
        self.datos = bd.cargar_base() 
        self._usuario = self.datos[
            (self.datos["IDENTIFICACIÓN"].astype(str) == intento_identifacion) &
            (self.datos["CONTRASEÑA"] == intento_contra)
        ]
        if not self._usuario.empty:
            return True
        return False
    
#Primero Invitado -> Login A/P -> LOGICA [ce][contra] -> Instancia A/P
"""
"Clase Padre"
class Usuario(ABC):


    @abstractmethod
    def iniciar_sesion(self):
        pass

    @abstractmethod
    def cargar_base(self):
        pass


"Clase Hija"
class Administrador(Usuario):

    #Atributo de clase
    Periodo  = "2025 - 2"
    #Atributos de instancia
    def __init__(self, usuario):
        self.admin = {
        #CARGARIA EL USUARIO LOGIADO
        }
    
    #Metodos
    def iniciar_sesion(self,intento_correo:str,intento_contra:str):
        print(f"Paso la cedula: {intento_correo} y la contraseña: {intento_contra}")
        admin = self.cargar_base()
        # Verificar contraseña
        if admin[0] == (intento_correo) and admin[1] == intento_contra:
            print("Login exitoso")
            return True
        
        print("Contraseña incorrecta")
        return False
    
    def visualizar_ventana(self):
        #Aqui visualizaria la ventana de login
        pass
    
    def cargar_base(self):
        credenciales = ["prueba1@uleam.edu.ec","ADMIN123"]
        return credenciales
        
    def subir_malla(self):
        return print("Se ha subido nueva malla curricular")

    def editar_malla(self):
        return print("Se ha editado la malla curricular")

    def esta_activo(self):
        return self.estado
        
"Clase Hija"
class Postulante(Usuario):
    
    #Atributos de Instancia 
    def __init__(self):
        self.postulante = {
            
        }

    #Metodos
    def ver_puntaje(self):
        return self.puntaje

    def iniciar_sesion(self,intento_cedu:str,intento_contra:str):
        print(f"Paso la cedula: {intento_cedu} y la contraseña: {intento_contra}")
        base_dato = self.cargar_base()
        usuario = base_dato[base_dato['IDENTIFICACION'] == intento_cedu]
        #tengo miedo che
        # Verificar contraseña
        if str(usuario.iloc[7]['CONTRASEÑA']) == (intento_contra):
            print("Login exitoso")
            return True
        
        print("Contraseña incorrecta")
        return False
    
        
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
"""