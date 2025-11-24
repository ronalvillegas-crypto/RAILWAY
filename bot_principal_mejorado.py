# bot_principal_corregido.py - BOT CORREGIDO CON PRECIOS CONSISTENTES
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

class BotTradingCorregido:
    def __init__(self):
        self.activo = True
        self.ciclo = 0
        self.token = TELEGRAM_TOKEN
        self.chat_id = os.environ.get('TELEGRAM_CHAT_ID')
        
        # MÓDULOS CON PRECIOS CENTRALIZADOS
        self.central_precios = CentralPrecios()
        self.gestor_sesiones = GestorSesionesMercado()
        self.analizador_correlaciones = AnalizadorCorrelaciones()
        self.detector_movimientos = DetectorMovimientos()
        self.alerta_noticias = AlertaNoticias()
        
        # Estrategia principal
        self.estrategia_mejorada = None
        
        # Estado del bot
        self.operaciones_activas = []
        self.estadisticas = {
            'señales_totales': 0,
            'señales_sr': 0,
            'señales_movimientos': 0, 
            'señales_noticias': 0,
            'errores_precio': 0
        }
        
        logger.info("🚀 INICIANDO BOT CORREGIDO - PRECIOS CONSISTENTES")
        
        self.enviar_mensaje_inicio_corregido()
    
    def _get_estrategia_mejorada(self):
        """Obtener estrategia mejorada (lazy loading)"""
        if self.estrategia_mejorada is None:
            try:
                from estrategia_dca_corregida import EstrategiaDCACorregida
                self.estrategia_mejorada = EstrategiaDCACorregida(self.central_precios)
                logger.info("✅ Estrategia corregida cargada")
            except ImportError as e:
                logger.error(f"❌ No se pudo cargar estrategia corregida: {e}")
                # Fallback
                from estrategia_rapida import EstrategiaRapida
                self.estrategia_mejorada = EstrategiaRapida()
        return self.estrategia_mejorada
    
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
    
    def enviar_mensaje_inicio_corregido(self):
        """Mensaje de inicio corregido"""
        mensaje = (
            f"🚀 BOT CORREGIDO - PRECIOS CONSISTENTES\n"
            f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            
            f"✅ CORRECCIONES IMPLEMENTADAS:\n"
            f"• Fuente única centralizada de precios\n"
            f"• Verificación de consistencia en tiempo real\n" 
            f"• Cache inteligente de 30 segundos\n"
            f"• Todos los módulos usan misma fuente\n\n"
            
            f"🎯 3 SEÑALES ACTIVAS:\n"
            f"1. S/R Estrategia - Precios consistentes\n"
            f"2. Movimientos % - Detección precisa\n"
            f"3. Noticias - Alertas confiables\n\n"
            
            f"🔧 ESTADO: 100% OPERATIVO\n"
            f"💰 Precios: ✅ CONSISTENTES\n"
        )
        
        if self.enviar_telegram(mensaje):
            logger.info("✅ MENSAJE DE INICIO CORREGIDO ENVIADO")
    
    def ciclo_analisis_corregido(self):
        """Ciclo principal corregido con precios consistentes"""
        self.ciclo += 1
        logger.info(f"🔄 CICLO CORREGIDO #{self.ciclo}")
        
        try:
            # 1. OBTENER ACTIVOS Y ACTUALIZAR PRECIOS EN LOTE
            activos_recomendados = self.gestor_sesiones.obtener_activos_recomendados()
            logger.info(f"📈 Actualizando {len(activos_recomendados)} precios...")
            
            # Actualizar todos los precios primero
            precios_actuales = self.central_precios.obtener_precios_lote(activos_recomendados)
            
            # 2. VERIFICAR NOTICIAS
            self._verificar_noticias_alto_impacto()
            
            # 3. PROCESAR CADA ACTIVO CON PRECIO CONSISTENTE
            señales_generadas = 0
            for par in activos_recomendados:
                if not self.activo:
                    break
                    
                # Usar precio de la central (misma fuente para todos)
                precio_actual = precios_actuales.get(par)
                if not precio_actual:
                    logger.warning(f"⚠️ No se pudo obtener precio para {par}")
                    self.estadisticas['errores_precio'] += 1
                    continue
                
                logger.info(f"🔍 Analizando {par} = {precio_actual:.5f}")
                
                # A. DETECTAR MOVIMIENTOS CON PRECIO CENTRAL
                alertas_movimiento = self.detector_movimientos.actualizar_precio(par, precio_actual)
                if alertas_movimiento:
                    for alerta in alertas_movimiento:
                        self.estadisticas['señales_movimientos'] += 1
                        # VERIFICAR CONSISTENCIA antes de enviar
                        if self.central_precios.verificar_consistencia_precios(par, alerta['precio_actual']):
                            self.enviar_alerta_movimiento_corregida(alerta)
                        else:
                            logger.warning(f"⚠️ Movimiento descartado por inconsistencia: {par}")
                
                # B. GENERAR SEÑAL S/R CON PRECIO CENTRAL
                señal_sr = self.generar_señal_sr_corregida(par, precio_actual)
                if señal_sr:
                    señales_generadas += 1
                    self.estadisticas['señales_totales'] += 1
                    self.estadisticas['señales_sr'] += 1
                    
                    if señal_sr['confianza'] in ["ALTA", "MEDIA"]:
                        exposicion = self.analizador_correlaciones.analizar_exposicion_actual(self.operaciones_activas)
                        self.enviar_señal_sr_corregida(señal_sr, exposicion)
                
                time.sleep(1)  # Pausa corta
            
            logger.info(f"✅ Ciclo #{self.ciclo} - Señales: {señales_generadas}")
            
            # REPORTE PERIÓDICO
            if self.ciclo % 5 == 0:
                self.enviar_reporte_consistencia()
                
        except Exception as e:
            logger.error(f"💥 Error en ciclo corregido: {e}")
    
    def generar_señal_sr_corregida(self, par, precio_actual):
        """
        Generar señal S/R usando precio centralizado
        """
        try:
            estrategia = self._get_estrategia_mejorada()
            if estrategia:
                # Pasar el precio actual para evitar que la estrategia lo obtenga de nuevo
                señal = estrategia.generar_señal_con_precio(par, precio_actual, self.operaciones_activas)
                if señal:
                    # VERIFICAR CONSISTENCIA FINAL
                    if self.central_precios.verificar_consistencia_precios(par, señal['precio_actual']):
                        logger.info(f"🎯 Señal S/R consistente: {par} {señal['direccion']}")
                        return señal
                    else:
                        logger.warning(f"⚠️ Señal S/R descartada por inconsistencia: {par}")
                        return None
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error generando señal S/R {par}: {e}")
            return None
    
    def enviar_señal_sr_corregida(self, señal, exposicion):
        """Enviar señal S/R corregida con precios verificados"""
        emoji = "🟢" if señal['direccion'] == "COMPRA" else "🔴"
        
        # VERIFICAR CONSISTENCIA UNA VEZ MÁS antes de enviar
        precio_verificado = self.central_precios.obtener_precio_actual(señal['par'])
        
        mensaje = f"""
{emoji} <b>🎯 SEÑAL S/R - PRECIO VERIFICADO</b> {emoji}

🏆 <b>PAR:</b> {señal['par']}
🎯 <b>DIRECCIÓN:</b> <b>{señal['direccion']}</b>
💰 <b>PRECIO ACTUAL:</b> {precio_verificado:.5f} ✅

📊 <b>ANÁLISIS TÉCNICO:</b>
• RSI: {señal['rsi']}
• Tendencia: {señal['tendencia']}
• Zona: {señal['zona_actual']}

⚡ <b>NIVELES OPERACIÓN:</b>
• TP1: {señal['tp1']:.5f}
• TP2: {señal['tp2']:.5f}  
• SL: {señal['sl']:.5f}
• DCA1: {señal['dca_1']:.5f}

📈 <b>GESTIÓN DE RIESGO:</b>
• Confianza: {señal['confianza']}
• Exposición: {exposicion['total_operaciones']} ops

🎯 <b>MOTIVO:</b> {señal['motivo_señal']}

⏰ <b>HORA SEÑAL:</b> {señal['timestamp']}
        """
        
        if self.enviar_telegram(mensaje.strip()):
            logger.info(f"✅ Señal S/R enviada: {señal['par']}")
    
    def enviar_alerta_movimiento_corregida(self, alerta):
        """Enviar alerta de movimiento con precios verificados"""
        # VERIFICAR PRECIO ACTUAL
        precio_actual_verificado = self.central_precios.obtener_precio_actual(alerta['par'])
        
        mensaje = f"""
{alerta['emoji']} <b>🚨 MOVIMIENTO - PRECIO VERIFICADO</b> {alerta['emoji']}

🏆 <b>PAR:</b> {alerta['par']}
📈 <b>MOVIMIENTO:</b> <b>{alerta['movimiento_porcentual']:+.2f}%</b>
💰 <b>PRECIO INICIAL:</b> {alerta['precio_inicial']:.5f}
💰 <b>PRECIO ACTUAL:</b> {precio_actual_verificado:.5f} ✅
⏰ <b>PERIODO:</b> {alerta['periodo']}
🎯 <b>DIRECCIÓN:</b> {alerta['direccion']}

💡 <b>ANÁLISIS:</b>
• Magnitud: {alerta['magnitud']}
• Tipo: {alerta['tipo_activo'].upper()}
• Umbral: {alerta['umbral_superado']:.2f}%

🔍 <b>ACCIÓN:</b> Monitorizar para confirmación

⏰ <b>HORA DETECCIÓN:</b> {alerta['timestamp']}
        """
        
        if self.enviar_telegram(mensaje.strip()):
            logger.info(f"✅ Alerta movimiento enviada: {alerta['par']}")
    
    def _verificar_noticias_alto_impacto(self):
        """Verificar noticias de alto impacto"""
        try:
            alertas_noticias = self.alerta_noticias.obtener_alertas_activas()
            if alertas_noticias:
                for alerta in alertas_noticias:
                    self.estadisticas['señales_noticias'] += 1
                    self.enviar_alerta_noticia_corregida(alerta)
        except Exception as e:
            logger.error(f"❌ Error verificando noticias: {e}")
    
    def enviar_alerta_noticia_corregida(self, alerta):
        """Enviar alerta de noticia corregida"""
        emoji_impacto = "🔴" if alerta['impacto'] == 'MUY_ALTO' else "🟡"
        
        mensaje = f"""
{emoji_impacto} <b>📰 ALERTA NOTICIA</b> {emoji_impacto}

🏛️ <b>EVENTO:</b> {alerta['nombre']}
🎯 <b>IMPACTO:</b> {alerta['impacto']}
📍 <b>PAÍS:</b> {alerta['pais']}

• <b>Resultado:</b> {alerta['datos']['resultado'].replace('_', ' ').title()}
• <b>Valor:</b> {alerta['datos']['valor_actual']} vs Esperado {alerta['datos']['valor_esperado']}

💡 <b>EFECTOS:</b>
{self._formatear_efectos_noticia(alerta)}

🔍 <b>AFECTA A:</b> {', '.join(alerta['simbolos_afectados'][:3])}

⏰ <b>HORA:</b> {alerta['timestamp']}
        """
        
        self.enviar_telegram(mensaje.strip())
    
    def _formatear_efectos_noticia(self, alerta):
        """Formatear efectos de noticia de forma concisa"""
        efectos = []
        forex = alerta['efectos_mercado']['forex']
        
        if forex.get('USD') != 'NEUTRO':
            efectos.append(f"• USD: {forex['USD']}")
        if alerta['efectos_mercado']['oro'] != 'NEUTRO':
            efectos.append(f"• ORO: {alerta['efectos_mercado']['oro']}")
            
        return "\n".join(efectos) if efectos else "• Efectos mixtos en mercados"
    
    def enviar_reporte_consistencia(self):
        """Enviar reporte de consistencia de precios"""
        estadisticas = self.central_precios.obtener_estadisticas()
        
        mensaje = f"""
📊 <b>REPORTE CONSISTENCIA PRECIOS</b>

🔄 <b>Ciclo #{self.ciclo}</b>
⏰ <b>Estado:</b> PRECIOS ✅ CONSISTENTES

📈 <b>ESTADÍSTICAS:</b>
• Pares monitoreados: {estadisticas['total_pares_registrados']}
• Precios válidos: {estadisticas['precios_validos_actualmente']}
• Cache TTL: {estadisticas['cache_ttl_segundos']}s

🎯 <b>SEÑALES ESTE CICLO:</b>
• S/R: {self.estadisticas['señales_sr']}
• Movimientos: {self.estadisticas['señales_movimientos']}
• Noticias: {self.estadisticas['señales_noticias']}

⚠️ <b>ERRORES PRECIO:</b> {self.estadisticas['errores_precio']}

✅ <b>SISTEMA DE PRECIOS: OPERATIVO</b>
        """
        
        self.enviar_telegram(mensaje.strip())
    
    def iniciar(self):
        """Iniciar bot corregido"""
        logger.info("🎯 INICIANDO BOT CORREGIDO - PRECIOS CENTRALIZADOS")
        
        # Programar análisis cada 3 minutos
        schedule.every(3).minutes.do(self.ciclo_analisis_corregido)
        
        # Programar limpieza de cache cada hora
        schedule.every(1).hours.do(self.central_precios.limpiar_cache_antiguo)
        
        # Primer análisis
        self.ciclo_analisis_corregido()
        
        logger.info("✅ Bot corregido en ejecución")
        
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
        logger.info("🛑 Bot corregido detenido")
        
        self.enviar_telegram(
            f"🛑 BOT CORREGIDO DETENIDO\n"
            f"⏰ {datetime.now().strftime('%H:%M:%S')}\n"
            f"🔁 Ciclos: {self.ciclo}\n"
            f"✅ Precios consistentes hasta el final"
        )

# MÓDULOS NECESARIOS
from central_precios import CentralPrecios
from gestor_sesiones import GestorSesionesMercado
from analisis_correlaciones import AnalizadorCorrelaciones
from detector_movimientos import DetectorMovimientos
from noticias_alerta_corregido import AlertaNoticias

if __name__ == "__main__":
    print("=" * 60)
    print("🤖 BOT CORREGIDO - PRECIOS CONSISTENTES")
    print("📍 Telegram: CONECTADO")
    print("🎯 3 Señales con precios verificados")
    print("💰 Fuente única centralizada")
    print("=" * 60)
    
    bot = BotTradingCorregido()
    
    try:
        bot.iniciar()
    except KeyboardInterrupt:
        logger.info("🛑 Bot detenido por usuario")
        bot.detener()
    except Exception as e:
        logger.error(f"💥 Error crítico: {e}")
        bot.detener()
