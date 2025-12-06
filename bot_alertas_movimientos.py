# bot_alertas_movimientos.py - BOT SIMPLIFICADO SOLO PARA ALERTAS DE MOVIMIENTOS
import os
import time
import schedule
import requests
from datetime import datetime
import logging
import sys

# ✅ CONFIGURACIÓN DE IMPORTACIONES
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# CONFIGURACIÓN
TELEGRAM_TOKEN = "8539767979:AAF4luTQT7jR74jnhO2Lb4dRRXApWjhEl7o"

class BotAlertasMovimientos:
    def __init__(self):
        self.activo = True
        self.ciclo = 0
        self.token = TELEGRAM_TOKEN
        self.chat_id = os.environ.get('TELEGRAM_CHAT_ID')
        
        # MÓDULOS NECESARIOS
        self.central_precios = CentralPrecios()
        self.gestor_sesiones = GestorSesionesMercado()
        self.detector_movimientos = DetectorMovimientos()
        
        # Estado del bot
        self.alertas_enviadas = 0
        self.estadisticas = {
            'alertas_generadas': 0,
            'alertas_enviadas': 0,
            'errores_precio': 0,
            'pares_monitoreados': 0
        }
        
        logger.info("🚀 INICIANDO BOT DE ALERTAS DE MOVIMIENTOS")
        
        self.enviar_mensaje_inicio()
    
    def enviar_telegram(self, mensaje):
        """Enviar mensaje a Telegram"""
        try:
            if not self.chat_id:
                logger.warning("❌ No hay CHAT_ID configurado para Telegram")
                return False
                
            url = f"https://api.telegram.org/bot{self.token}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': mensaje,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200
                
        except Exception as e:
            logger.error(f"❌ Error enviando mensaje: {e}")
            return False
    
    def enviar_mensaje_inicio(self):
        """Mensaje de inicio"""
        mensaje = (
            f"🚀 BOT DE ALERTAS DE MOVIMIENTOS\n"
            f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            
            f"🎯 FUNCIÓN ÚNICA:\n"
            f"• Detectar cambios porcentuales significativos\n"
            f"• Enviar alertas solo cuando haya movimiento\n"
            f"• No envía señales S/R ni noticias\n\n"
            
            f"📊 PARÁMETROS DETECCIÓN:\n"
            f"• Forex: ±0.3%\n"
            f"• Commodities: ±0.5%\n"
            f"• Índices: ±0.8%\n"
            f"• ❌ Crypto: DESACTIVADO\n\n"
            
            f"⏰ FRECUENCIA: Cada 3 minutos\n"
            f"🔧 ESTADO: 100% OPERATIVO\n"
        )
        
        if self.enviar_telegram(mensaje):
            logger.info("✅ MENSAJE DE INICIO ENVIADO")
    
    def ciclo_deteccion_movimientos(self):
        """Ciclo principal solo para detectar movimientos"""
        self.ciclo += 1
        logger.info(f"🔄 CICLO #{self.ciclo} - BÚSQUEDA DE MOVIMIENTOS")
        
        try:
            # 1. OBTENER ACTIVOS DE LA SESIÓN ACTUAL
            activos_recomendados = self.gestor_sesiones.obtener_activos_recomendados()
            sesion_actual, _ = self.gestor_sesiones.obtener_sesion_actual()
            
            # Filtrar solo activos no-crypto
            activos_filtrados = [activo for activo in activos_recomendados 
                               if not self._es_crypto(activo)]
            
            logger.info(f"📈 Monitoreando {len(activos_filtrados)} activos (Sesión: {sesion_actual})")
            
            # 2. ACTUALIZAR PRECIOS EN LOTE
            precios_actuales = self.central_precios.obtener_precios_lote(activos_filtrados)
            
            # 3. DETECTAR MOVIMIENTOS EN CADA ACTIVO
            alertas_generadas = 0
            for par in activos_filtrados:
                if not self.activo:
                    break
                    
                # Obtener precio actual
                precio_actual = precios_actuales.get(par)
                if not precio_actual:
                    logger.warning(f"⚠️ No se pudo obtener precio para {par}")
                    self.estadisticas['errores_precio'] += 1
                    continue
                
                # Detectar movimientos significativos
                alertas_movimiento = self.detector_movimientos.actualizar_precio(par, precio_actual)
                
                if alertas_movimiento:
                    for alerta in alertas_movimiento:
                        alertas_generadas += 1
                        self.estadisticas['alertas_generadas'] += 1
                        
                        # VERIFICAR CONSISTENCIA antes de enviar
                        if self.central_precios.verificar_consistencia_precios(par, alerta['precio_actual']):
                            self.enviar_alerta_movimiento(alerta)
                            self.estadisticas['alertas_enviadas'] += 1
                        else:
                            logger.warning(f"⚠️ Movimiento descartado por inconsistencia: {par}")
                
                time.sleep(0.5)  # Pausa corta entre activos
            
            # Actualizar estadísticas de pares monitoreados
            self.estadisticas['pares_monitoreados'] = len(activos_filtrados)
            
            logger.info(f"✅ Ciclo #{self.ciclo} - Alertas: {alertas_generadas}")
            
            # REPORTE PERIÓDICO
            if self.ciclo % 10 == 0:  # Cada 10 ciclos (30 minutos)
                self.enviar_reporte_estadisticas()
                
        except Exception as e:
            logger.error(f"💥 Error en ciclo de detección: {e}")
    
    def _es_crypto(self, par):
        """Verificar si un par es criptomoneda"""
        # Lista de símbolos comunes de criptomonedas
        cryptos = ['BTC', 'ETH', 'XRP', 'ADA', 'SOL', 'DOT', 'DOGE', 'SHIB', 
                   'AVAX', 'MATIC', 'LINK', 'ATOM', 'UNI', 'ALGO', 'VET',
                   'LTC', 'BCH', 'XLM', 'ETC', 'TRX', 'FIL', 'EOS', 'XTZ']
        
        # Verificar si el par contiene algún símbolo de crypto
        par_upper = par.upper()
        return any(crypto in par_upper for crypto in cryptos)
    
    def enviar_alerta_movimiento(self, alerta):
        """Enviar alerta de movimiento verificada"""
        # VERIFICAR PRECIO ACTUAL
        precio_actual_verificado = self.central_precios.obtener_precio_actual(alerta['par'])
        
        # Determinar color según dirección
        color_emoji = "🟢" if alerta['direccion'] == "ALCISTA" else "🔴"
        
        mensaje = f"""
{color_emoji} <b>🚨 ALERTA DE MOVIMIENTO</b> {color_emoji}

🏆 <b>PAR:</b> {alerta['par']}
📈 <b>MOVIMIENTO:</b> <b>{alerta['movimiento_porcentual']:+.2f}%</b>
🎯 <b>DIRECCIÓN:</b> {alerta['direccion']}
💰 <b>PRECIO INICIAL:</b> {alerta['precio_inicial']:.5f}
💰 <b>PRECIO ACTUAL:</b> {precio_actual_verificado:.5f} ✅
⏰ <b>PERIODO:</b> {alerta['periodo']}
⚡ <b>MAGNITUD:</b> {alerta['magnitud']}

📊 <b>DETALLES:</b>
• Tipo: {alerta['tipo_activo'].upper()}
• Umbral superado: {alerta['umbral_superado']:.2f}%
• Absoluto: {alerta['movimiento_absoluto']:+.5f}

💡 <b>ACCIÓN RECOMENDADA:</b>
{self._generar_recomendacion_movimiento(alerta)}

⏰ <b>DETECTADO:</b> {alerta['timestamp']}
        """
        
        if self.enviar_telegram(mensaje.strip()):
            logger.info(f"✅ Alerta enviada: {alerta['par']} {alerta['movimiento_porcentual']:+.2f}%")
            self.alertas_enviadas += 1
    
    def _generar_recomendacion_movimiento(self, alerta):
        """Generar recomendación basada en el movimiento"""
        movimiento_abs = abs(alerta['movimiento_porcentual'])
        tipo = alerta['tipo_activo']
        
        if movimiento_abs < 0.5:
            return "Movimiento pequeño - Monitorizar"
        elif movimiento_abs < 1.0:
            if alerta['periodo'] in ['1HORA', '4HORAS']:
                return "Movimiento significativo - Considerar operación"
            else:
                return "Movimiento diario - Evaluar contexto"
        else:
            if tipo == 'forex' and movimiento_abs > 1.0:
                return "🔥 MOVIMIENTO FUERTE - Posible operación"
            elif tipo == 'commodities' and movimiento_abs > 1.5:
                return "🔥 MOVIMIENTO FUERTE - Posible operación"
            else:
                return "⚠️ Movimiento muy fuerte - Evaluar con cuidado"
    
    def enviar_reporte_estadisticas(self):
        """Enviar reporte de estadísticas"""
        estadisticas_precios = self.central_precios.obtener_estadisticas()
        sesion_actual, _ = self.gestor_sesiones.obtener_sesion_actual()
        
        mensaje = f"""
📊 <b>REPORTE ESTADÍSTICAS - BOT MOVIMIENTOS</b>

🔄 <b>Ciclo #{self.ciclo}</b>
⏰ <b>Sesión:</b> {sesion_actual}
📈 <b>Estado:</b> MONITOREO ACTIVO ✅

📊 <b>ESTADÍSTICAS:</b>
• Pares monitoreados: {self.estadisticas['pares_monitoreados']}
• Alertas generadas: {self.estadisticas['alertas_generadas']}
• Alertas enviadas: {self.estadisticas['alertas_enviadas']}
• Precios válidos: {estadisticas_precios['precios_validos_actualmente']}

⚠️ <b>ERRORES:</b>
• Precios no obtenidos: {self.estadisticas['errores_precio']}

✅ <b>SISTEMA OPERATIVO:</b>
• Último ciclo: {datetime.now().strftime('%H:%M:%S')}
• Próximo ciclo: 3 minutos
• Crypto: ❌ DESACTIVADO
        """
        
        self.enviar_telegram(mensaje.strip())
    
    def iniciar(self):
        """Iniciar bot simplificado"""
        logger.info("🎯 INICIANDO BOT SOLO ALERTAS MOVIMIENTOS (SIN CRYPTO)")
        
        # Programar detección cada 3 minutos
        schedule.every(3).minutes.do(self.ciclo_deteccion_movimientos)
        
        # Programar limpieza de cache cada hora
        schedule.every(1).hours.do(self.central_precios.limpiar_cache_antiguo)
        
        # Primer ciclo inmediato
        self.ciclo_deteccion_movimientos()
        
        logger.info("✅ Bot de alertas en ejecución (sin crypto)")
        
        # Bucle principal
        while self.activo:
            try:
                schedule.run_pending()
                time.sleep(30)
            except Exception as e:
                logger.error(f"❌ Error en bucle principal: {e}")
                time.sleep(60)
    
    def detener(self):
        """Detener bot"""
        self.activo = False
        logger.info("🛑 Bot de alertas detenido")
        
        mensaje_despedida = (
            f"🛑 BOT DE ALERTAS DETENIDO\n"
            f"⏰ {datetime.now().strftime('%H:%M:%S')}\n"
            f"🔁 Ciclos: {self.ciclo}\n"
            f"📈 Alertas enviadas: {self.alertas_enviadas}\n"
            f"❌ Crypto: DESACTIVADO\n"
            f"👋 Hasta pronto!"
        )
        
        self.enviar_telegram(mensaje_despedida)

# MÓDULOS NECESARIOS (solo los esenciales)
from central_precios import CentralPrecios
from gestor_sesiones import GestorSesionesMercado
from detector_movimientos import DetectorMovimientos

if __name__ == "__main__":
    print("=" * 60)
    print("🤖 BOT SIMPLIFICADO - SOLO ALERTAS DE MOVIMIENTOS")
    print("📍 Telegram: CONECTADO")
    print("🎯 Función: Detectar cambios % significativos")
    print("❌ Crypto: DESACTIVADO")
    print("⏰ Frecuencia: Cada 3 minutos")
    print("💰 Fuente única de precios")
    print("=" * 60)
    
    bot = BotAlertasMovimientos()
    
    try:
        bot.iniciar()
    except KeyboardInterrupt:
        logger.info("🛑 Bot detenido por usuario")
        bot.detener()
    except Exception as e:
        logger.error(f"💥 Error crítico: {e}")
        bot.detener()
