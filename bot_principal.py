# bot_principal.py - BOT PRINCIPAL PARA RAILWAY
import os
import time
import threading
import schedule
from datetime import datetime
import logging
import sys

# Configurar logging robusto
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot_railway.log')
    ]
)
logger = logging.getLogger(__name__)

class BotTradingRailway:
    def __init__(self):
        self.activo = True
        self.ciclo = 0
        self.monitor = None
        self.ultima_señal = None
        
    def inicializar_modulos(self):
        """Inicializar todos los módulos del bot"""
        try:
            logger.info("🔄 Inicializando módulos...")
            
            # Importar módulos
            from monitor_mercado import MonitorMercado
            from estrategia_dca import EstrategiaDCA
            from yahoo_api import YahooFinanceAPI
            
            # Inicializar componentes
            self.monitor = MonitorMercado()
            self.estrategia = EstrategiaDCA()
            self.yahoo = YahooFinanceAPI()
            
            logger.info("✅ Módulos inicializados correctamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error inicializando módulos: {e}")
            return False
    
    def ciclo_analisis(self):
        """Ciclo principal de análisis"""
        try:
            if not self.activo:
                return
                
            self.ciclo += 1
            logger.info(f"🔄 CICLO #{self.ciclo} - {datetime.now().strftime('%H:%M:%S')}")
            
            # Verificar si los módulos están inicializados
            if not self.monitor:
                if not self.inicializar_modulos():
                    logger.error("❌ No se pudieron inicializar módulos")
                    return
            
            # Pares a analizar (mantener misma estrategia)
            pares = ["EURUSD", "USDCAD", "EURCHF", "EURAUD", "XAUUSD", "XAGUSD", "OILUSD", "XPTUSD"]
            
            señales_generadas = 0
            for par in pares:
                if not self.activo:
                    break
                    
                try:
                    # Usar la MISMA estrategia que en Render
                    señal = self.monitor.analizar_par(par)
                    
                    if señal:
                        logger.info(f"🎯 SEÑAL CONFIRMADA: {par} {señal['direccion']}")
                        self.monitor.ejecutar_señal(señal)
                        señales_generadas += 1
                        self.ultima_señal = {
                            'par': par,
                            'direccion': señal['direccion'],
                            'timestamp': datetime.now().isoformat()
                        }
                        
                except Exception as e:
                    logger.error(f"❌ Error analizando {par}: {e}")
                    continue
                    
                time.sleep(2)  # Pequeña pausa entre pares
            
            if señales_generadas == 0:
                logger.info("📊 No se detectaron oportunidades en este ciclo")
                
            logger.info(f"✅ Ciclo #{self.ciclo} completado - Señales: {señales_generadas}")
            
        except Exception as e:
            logger.error(f"💥 Error en ciclo de análisis: {e}")
    
    def iniciar_bot(self):
        """Iniciar el bot programado"""
        logger.info("🚀 INICIANDO BOT TRADING EN RAILWAY")
        logger.info("📈 Estrategia: S/R Etapa 1 - Misma que Render")
        logger.info("⏰ Frecuencia: Cada 2 minutos")
        
        # Inicializar módulos primero
        if not self.inicializar_modulos():
            logger.error("❌ No se pudo inicializar el bot")
            return False
        
        # Programar ejecución cada 2 minutos (igual que Render)
        schedule.every(2).minutes.do(self.ciclo_analisis)
        
        # Ejecutar inmediatamente el primer análisis
        logger.info("🔍 Ejecutando primer análisis inmediato...")
        self.ciclo_analisis()
        
        logger.info("✅ Bot iniciado correctamente - Entrando en bucle principal")
        
        # Bucle principal
        while self.activo:
            try:
                schedule.run_pending()
                time.sleep(30)  # Verificar cada 30 segundos
                
                # Log de estado cada 10 minutos
                if datetime.now().minute % 10 == 0:
                    logger.info(f"❤️ Bot activo - Ciclos: {self.ciclo}")
                    
            except Exception as e:
                logger.error(f"❌ Error en bucle principal: {e}")
                time.sleep(60)
    
    def detener_bot(self):
        """Detener el bot gracefully"""
        logger.info("🛑 Deteniendo bot...")
        self.activo = False
        
        if self.monitor and hasattr(self.monitor, 'detener_monitoreo'):
            self.monitor.detener_monitoreo()

# Función para mantener el proceso vivo
def mantener_proceso():
    """Función que mantiene el proceso ejecutándose"""
    bot = BotTradingRailway()
    
    try:
        bot.iniciar_bot()
    except KeyboardInterrupt:
        logger.info("⏹️ Bot detenido por usuario")
        bot.detener_bot()
    except Exception as e:
        logger.error(f"💥 Error crítico: {e}")
        bot.detener_bot()
        # Reiniciar después de 60 segundos
        time.sleep(60)
        mantener_proceso()

if __name__ == "__main__":
    print("=" * 70)
    print("🚀 BOT TRADING - RAILWAY VERSION")
    print(f"⏰ Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    mantener_proceso()