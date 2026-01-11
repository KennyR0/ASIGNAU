"""
Sistema ASIGNAU - Asignación Universitaria Automatizada
Versión: 1.0.0

Este es el punto de entrada principal del sistema.
Para ejecutar: python main.py
"""

from front import Ventana_principal, tk


if __name__ == "__main__":
    root = tk.Tk()
    app = Ventana_principal(root)
    root.mainloop()