import pandas as pd # libreria para leer y sobreescribir la base de datos(excel)
from abc import abstractmethod,ABC #libreria para crear clases abstractas e interfaces
from typing import Optional, Dict, Any # Mejorar la legibilidad del codigo
import os # Libreria para interactuar con el sistema operativo y leer archivos
from dataclasses import dataclass #Crear clases mas sencillamente

#ASIGNAU (ASIGNACIÓN UNIVERSITARIA)

#Inyeccion de dependencia
class Base_Dato(ABC):
    
    @abstractmethod
    def cargar_base(self): 
        """Carga la base de datos desde el excel """
        pass

    @abstractmethod
    def obtener_usuario(self, identificacion: str, contraseña: str):
        """Obtiene los datos completos del usuario si las credenciales son válidas"""
        pass

class BD_ADMIN(Base_Dato):
    
    def cargar_base(self):
        excel = "Admin.xlsx" #Nombre de nuestro archivo excel
        if os.path.exists(excel): #Comprueba la ruta con os, buscando la existencia de nuestro archivo
            """
            Sheet_name= es la hoja del excel que estamos leyendo, 
            comenzando de 0, en este caso se usa la 6
            Skiprows = se salta filas del excel
            """
            base = pd.read_excel(excel,sheet_name=0,skiprows=1)  #lee el excel usando pandas
            return base

        else:
            return None

    def obtener_usuario(self, identificacion: str, contraseña: str):
        """Obtiene los datos del administrador"""
        datos = self.cargar_base()
        if datos is None:
            return None
        
        """ Comprobamos si existe el usuario"""
        usuario = datos[
            (datos["IDENTIFICACIÓN"].astype(str) == identificacion) &
            (datos["CONTRASEÑA"] == contraseña)
        ]
        
        if not usuario.empty:
            # Convertir la fila a diccionario
            return usuario.iloc[0].to_dict()
        
        return None
    
class BD_USUARIO(Base_Dato):
    def cargar_base(self):
        excel = "Postulantes.xlsx" #Nombre de nuestro archivo excel
        if os.path.exists(excel): 
            base = pd.read_excel(excel,sheet_name=5,skiprows=1)  #lee el excel usando panda
            return base
        else:
            return None
        
    def obtener_usuario(self, identificacion: str, contraseña: str):
        datos = self.cargar_base()
        if datos is None:
            return None
        
        usuario = datos[
            (datos["IDENTIFICACIÓN"].astype(str) == identificacion) &
            (datos["CONTRASEÑA"] == contraseña)
        ]
        
        if not usuario.empty:
            return usuario.iloc[0].to_dict()
        
        return None

#Inyección de Datos
class IniciarSesion:
    
    @classmethod
    def Iniciar(cls, intento_identificacion: str, intento_contra: str, bd: Base_Dato):
        """
        Valida las credenciales y retorna los datos del usuario
        Retorna: (boolean, dict: datos_usuario)
        """
        datos_usuario = bd.obtener_usuario(intento_identificacion, intento_contra)
        
        if datos_usuario is not None:
            return True, datos_usuario
        
        return False, None
    

"Clase Padre"
class Usuario(ABC):
    
    """ Muestra los datos del usuario """
    @abstractmethod
    def mostrar_informacion(self):
        pass
    
"Clase Hija"
@dataclass
class Administrador(Usuario):
    #Atributo de clase
    Periodo = "2025 - 2"
    
    #Atributos de instancia
    identificacion: str = ""
    nombre: str = ""
    _cedula: str = ""
    id: int = 0

    #Metodos
    @classmethod
    def crear_desde_bd(cls, datos: Dict[str, Any]):
        """
        Crea una instancia de Administrador desde el excel
        """
        return cls(
            identificacion=str(datos.get("IDENTIFICACIÓN", "")),
            nombre=str(datos.get("NOMBRE", "")),
            _cedula=str(datos.get("CEDULA", "")),
            id=int(datos.get("ID", 0))
        )
    
    #Métodos 
    def mostrar_informacion(self):
        return {
            'tipo': 'Administrador',
            'identificacion': self.identificacion,
            'nombre': self.nombre,
            'cedula': self._cedula,
            'id': self.id,
            'periodo': self.Periodo
        }
        
    def subir_malla(self):
        return print("Se ha subido nueva malla curricular")

    def editar_malla(self):
        return print("Se ha editado la malla curricular")

    def esta_activo(self):
        return self.estado
        
"Clase Hija"
@dataclass
class Postulante(Usuario):

    # Atributos de instancia
    identificacion: str = ""
    contraseña: str = ""
    fecha_postulacion: str = ""
    puntaje_postulacion: float = 0.0
    segmento_aspirante: int = 0
    instancia_postulacion: int = 0
    prioridad_carrera: int = 0
    nombre_carrera: str = ""
    ofa_id: str = ""
    cus_id: str = ""
    
    @classmethod
    def crear_desde_bd(cls, datos: Dict[str, Any]) :
        """
        Crea una instancia de Postulante desde los datos del excel
        """
        return cls(
            identificacion=str(datos.get("IDENTIFICACIÓN", "")),
            contraseña=str(datos.get("CONTRASEÑA", "")),
            fecha_postulacion=str(datos.get("FECHA_POSTULACION", "")),
            puntaje_postulacion=float(datos.get("PUNTAJE_POSTULACION", 0.0)),
            segmento_aspirante=int(datos.get("SEGMENTO_ASPIRANTE", 0)),
            instancia_postulacion=int(datos.get("INSTANCIA_POSTULACION", 0)),
            prioridad_carrera=int(datos.get("PRIORIDAD_ELECCION_CARRERA", 0)),
            nombre_carrera=str(datos.get("NOMBRE_CARRERA", "")),
            ofa_id=str(datos.get("OFA_ID", "")),
            cus_id=str(datos.get("CUS_ID", ""))
        )

    #Metodos
    def mostrar_informacion(self):
        return {
            'tipo': 'Postulante',
            'identificacion': self.identificacion,
            'fecha_postulacion': self.fecha_postulacion,
            'puntaje': self.puntaje_postulacion,
            'segmento': self.segmento_aspirante,
            'carrera': self.nombre_carrera,
            'prioridad': self.prioridad_carrera
        }

    def ver_puntaje(self):
        return self.puntaje_postulacion
    
    def obtener_postulaciones(self):
        """Retorna información de las postulaciones del usuario"""
        return {
            'carrera': self.nombre_carrera,
            'prioridad': self.prioridad_carrera,
            'puntaje': self.puntaje_postulacion,
            'segmento': self.segmento_aspirante
        }

    def cambiar_contraseña(self):
        pass


class SobrecargaUsuario:
    """Sobrecarga para crear instancias de usuarios según el tipo de Base De Datos"""
    
    @staticmethod
    def crear_usuario(bd: Base_Dato, datos: Dict[str, Any]):
        """
        Crea la instancia correcta de usuario según el tipo de base de datos
        """
        if isinstance(bd, BD_ADMIN): 
            return Administrador.crear_desde_bd(datos)
        elif isinstance(bd, BD_USUARIO):
            return Postulante.crear_desde_bd(datos)
        else:
            return None
        
#CAMBIAR ESTAS CLASES         
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
        pass
