# analisis_correlaciones.py - ANÁLISIS DE CORRELACIONES ENTRE ACTIVOS
import numpy as np
from datetime import datetime, timedelta

class AnalizadorCorrelaciones:
    """
    Analiza correlaciones entre activos para evitar sobre-exposición
    """
    
    def __init__(self):
        self.correlaciones_conocidas = {
            # Forex
            "EURUSD_USDCHF": -0.85,  # Fuertemente negativa
            "EURUSD_GBPUSD": 0.75,   # Fuertemente positiva
            "USDJPY_XAUUSD": -0.60,  # Yen seguro vs Oro seguro
            
            # Materias Primas
            "XAUUSD_XAGUSD": 0.80,   # Metales preciosos correlacionados
            "OILUSD_USDCAD": -0.70,  # Petróleo vs Dólar Canadiense
            "XAUUSD_SPX500": -0.40,  # Oro vs Acciones (hedging)
            
            # Índices
            "SPX500_NAS100": 0.90,   # Alta correlación
            "SPX500_DJI30": 0.85,    # Alta correlación
        }
        
        self.grupos_correlacionados = {
            "DOLAR_FUERTE": ["EURUSD", "GBPUSD", "AUDUSD", "XAUUSD"],
            "RIESGO_ON": ["SPX500", "NAS100", "AUDUSD", "NZDUDS"],
            "RIESGO_OFF": ["USDJPY", "XAUUSD", "USDCHF"],
            "MATERIAS_PRIMAS": ["XAUUSD", "XAGUSD", "OILUSD", "COPPER"]
        }
    
    def obtener_correlacion(self, activo1, activo2):
        """Obtener correlación conocida entre dos activos"""
        clave1 = f"{activo1}_{activo2}"
        clave2 = f"{activo2}_{activo1}"
        
        return self.correlaciones_conocidas.get(clave1) or self.correlaciones_conocidas.get(clave2, 0.0)
    
    def analizar_exposicion_actual(self, operaciones_activas):
        """Analizar exposición actual del portfolio"""
        exposicion = {
            "total_operaciones": len(operaciones_activas),
            "por_grupo": {},
            "correlacion_promedio": 0.0,
            "recomendacion": "NEUTRAL"
        }
        
        # Contar operaciones por grupo
        for grupo, activos in self.grupos_correlacionados.items():
            count = sum(1 for op in operaciones_activas if op['par'] in activos)
            exposicion["por_grupo"][grupo] = count
        
        # Calcular correlación promedio
        if len(operaciones_activas) > 1:
            correlaciones = []
            for i in range(len(operaciones_activas)):
                for j in range(i + 1, len(operaciones_activas)):
                    corr = self.obtener_correlacion(
                        operaciones_activas[i]['par'], 
                        operaciones_activas[j]['par']
                    )
                    correlaciones.append(abs(corr))
            
            if correlaciones:
                exposicion["correlacion_promedio"] = sum(correlaciones) / len(correlaciones)
        
        # Generar recomendación
        if exposicion["total_operaciones"] >= 3 and exposicion["correlacion_promedio"] > 0.6:
            exposicion["recomendacion"] = "ALTA_CORRELACION - REDUCIR EXPOSICIÓN"
        elif exposicion["total_operaciones"] >= 5:
            exposicion["recomendacion"] = "MUCHAS_OPERACIONES - PAUSAR NUEVAS"
        else:
            exposicion["recomendacion"] = "DIVERSIFICADO - OK"
        
        return exposicion
    
    def recomendar_activo_diversificar(self, operaciones_activas):
        """Recomendar activo para diversificar exposición actual"""
        activos_activos = [op['par'] for op in operaciones_activas]
        
        # Todos los activos disponibles
        todos_activos = list(set(
            [activo for grupo in self.grupos_correlacionados.values() for activo in grupo]
        ))
        
        # Encontrar activo menos correlacionado
        mejor_activo = None
        menor_correlacion_promedio = float('inf')
        
        for activo in todos_activos:
            if activo in activos_activos:
                continue
                
            # Calcular correlación promedio con activos actuales
            correlaciones = []
            for activo_activo in activos_activos:
                corr = abs(self.obtener_correlacion(activo, activo_activo))
                correlaciones.append(corr)
            
            if correlaciones:
                corr_promedio = sum(correlaciones) / len(correlaciones)
                if corr_promedio < menor_correlacion_promedio:
                    menor_correlacion_promedio = corr_promedio
                    mejor_activo = activo
        
        return mejor_activo, menor_correlacion_promedio
    
    def deberia_evitar_señal(self, nueva_señal, operaciones_activas):
        """Decidir si evitar señal por alta correlación"""
        if len(operaciones_activas) == 0:
            return False, "Primera operación - OK"
        
        nuevo_activo = nueva_señal['par']
        
        # Verificar correlación con cada operación activa
        for operacion in operaciones_activas:
            activo_activo = operacion['par']
            correlacion = self.obtener_correlacion(nuevo_activo, activo_activo)
            
            # Si correlación > 0.7 y misma dirección, evitar
            if (abs(correlacion) > 0.7 and 
                nueva_señal['direccion'] == operacion['direccion']):
                return True, f"Alta correlación ({correlacion:.2f}) con {activo_activo}"
        
        return False, "Correlación aceptable"
