# compatibilidad.py - Solución para problemas de importación
import sys
import os

def configurar_importaciones():
    """Configurar importaciones para evitar problemas circulares"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
        print(f"✅ Directorio agregado al path: {current_dir}")
    
    # Lista de módulos disponibles
    modulos_disponibles = [
        'yahoo_api', 'analisis_tecnico', 'indicadores_reales',
        'estrategia_dca', 'monitor_mercado', 'config'
    ]
    
    print("📦 Módulos configurados correctamente")
    return True

# Ejecutar configuración al importar
configurar_importaciones()
