"""
Clase para establecer el periodo como activo
"""
from PeriodoAsignacion import GestorPeriodos, PeriodoAsignacion

def establecer_periodo_activo():
    gestor = GestorPeriodos()
    
    # Listar periodos disponibles
    periodos = PeriodoAsignacion.listar_periodos()
    print("Periodos disponibles:")
    for p in periodos:
        print(f"  - {p['codigo']}: {p['nombre']} (Estado: {p['estado']})")
    
    # Abrir el periodo
    if periodos:
        codigo = periodos[0]['codigo']
        exito, mensaje, periodo = gestor.abrir_periodo(codigo)
        
        if exito:
            print(f"\n✓ Periodo {codigo} establecido como activo")
            print(f"  Archivo postulantes: {periodo.archivo_postulantes}")
            print(f"  Archivo asignaciones: {periodo.archivo_asignaciones}")
        else:
            print(f"\n✗ Error: {mensaje}")
    else:
        print("\n✗ No hay periodos disponibles")

if __name__ == "__main__":
    establecer_periodo_activo()
