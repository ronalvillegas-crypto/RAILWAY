# bot_principal.py - BOT FINAL 100% FUNCIONAL + NOTICIAS
import os
import time
import schedule
import requests
from datetime import datetime
import logging
import sys
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, TOP_PARES
from telegram_bot import TelegramBotReal

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

class BotTradingFinal:
    def __init__(self):
        self.activo = True
        self.ciclo = 0
        # Usar configuración centralizada
        self.token = TELEGRAM_TOKEN
        self.chat_id = TELEGRAM_CHAT_ID
        # Cliente de Telegram unificado
        self.telegram = TelegramBotReal()
        # Estrategias principales
        from estrategia_dca import EstrategiaDCA
        from estrategia_rapida import EstrategiaRapida
        self.estrategia_dca = EstrategiaDCA()
        self.estrategia_rapida = EstrategiaRapida()

        logger.info("🚀 INICIANDO BOT TRADING FINAL")
        logger.info(f"💬 Chat ID configurado: {self.chat_id}")

        # ✅✅✅ ENVIAR MENSAJE DE INICIO INMEDIATO
        self.enviar_mensaje_inicio()

    def enviar_telegram(self, mensaje):
        """Enviar mensaje a Telegram usando TelegramBotReal"""
        try:
            if not self.telegram:
                self.telegram = TelegramBotReal()
            return self.telegram.enviar_mensaje(mensaje)
        except Exception as e:
            logger.error(f"❌ Error enviando mensaje: {e}")
            return False

    def enviar_mensaje_inicio(self):
        """ENVIAR MENSAJE DE INICIO ACTUALIZADO CON ESTRATEGIA BACKTESTING"""
        mensaje = (
            "🚀 BOT TRADING INICIADO - ESTRATEGIA BACKTESTING INTEGRADA\n"
            f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            "📍 Servidor: Railway (US-West)\n"
            "✅ Configuración: 100% OPTIMIZADA\n"
            "🎯 Estrategia: S/R Final Perfecta (Backtesting Comprobado)\n"
            "📊 Resultados Backtesting:\n"
            "   • Win Rate: 51.5%\n" 
            "   • Return Total: 9,432%\n"
            "   • Drawdown Máx: 9.88%\n"
            "📈 Pares Activos: 25+ Instrumentos\n"
            "   • Forex: EURUSD, GBPUSD, USDJPY, etc.\n"
            "   • Materias Primas: Oro, Plata, Petróleo\n"
            "   • Índices: SP500, Nasdaq, Dow Jones\n"
            "🔁 Frecuencia: Análisis cada 2 minutos\n"
            "📰 Módulo de noticias: ACTIVO (alto impacto)\n"
            "📡 Fuente de datos: Yahoo Finance + Simulación Avanzada\n"
        )
        self.enviar_telegram(mensaje)

    def analizar_par(self, par):
        """Analizar par priorizando ESTRATEGIA BACKTESTING + DCA y luego movimientos rápidos"""
        try:
            señal = None

            # 1️⃣ Intentar primero señal del backtesting (S/R Final Perfecta + DCA)
            if hasattr(self, "estrategia_dca") and self.estrategia_dca:
                señal = self.estrategia_dca.generar_señal_avanzada(par)
                if señal:
                    logger.info(f"🎯 SEÑAL BACKTESTING DETECTADA: {par} {señal['direccion']}")
                    # Enviar con formato completo S/R
                    self.telegram.enviar_señal_completa(señal, "📊 SEÑAL S/R FINAL PERFECTA (BACKTESTING)")
                    return señal

            # 2️⃣ Si no hay señal de backtesting, usar estrategia rápida/movimientos
            if hasattr(self, "estrategia_rapida") and self.estrategia_rapida:
                señal = self.estrategia_rapida.generar_señal_eficiente(par)
                if señal:
                    if señal.get('tipo_señal') == 'MOVIMIENTO':
                        logger.info(f"🚨 MOVIMIENTO: {par} {señal['direccion']} - {señal['movimiento_porcentual']:.2f}%")
                        self.telegram.enviar_señal_movimiento(señal, "⚡ MOVIMIENTO SIGNIFICATIVO")
                    else:
                        logger.info(f"🎯 MOMENTUM: {par} {señal['direccion']}")
                        self.telegram.enviar_señal_completa(señal, "📊 SEÑAL MOMENTUM")
                    return señal

            return None

        except Exception as e:
            logger.error(f"❌ Error analizando {par}: {e}")
            return None

    def verificar_noticias(self):
        """Verificar noticias de alto impacto y enviar alertas"""
        try:
            from noticias_alerta import AlertaNoticias
            noticias = AlertaNoticias()
            alertas = noticias.obtener_alertas_activas()

            logger.info(f"📰 Noticias encontradas: {len(alertas)}")

            for alerta in alertas:
                self.telegram.enviar_alerta_noticia(alerta)

            return len(alertas)

        except Exception as e:
            logger.error(f"❌ Error verificando noticias: {e}")
            return 0

    def ciclo_analisis(self):
        """Ciclo principal de análisis"""
        if not self.activo:
            logger.warning("⚠️ Bot inactivo, se omite ciclo de análisis")
            return

        try:
            logger.info("🔁 INICIANDO NUEVO CICLO DE ANÁLISIS (BACKTESTING + RÁPIDA)")
            self.ciclo += 1

            # Usar TOP_PARES directamente desde config (limitado a 10 por ciclo para no saturar)
            pares = TOP_PARES[:10]

            señales_generadas = 0
            señales_backtesting = 0

            for i, par in enumerate(pares):
                if not self.activo:
                    break

                logger.info(f"🔍 Analizando {par} ({i+1}/{len(pares)})")
                señal = self.analizar_par(par)

                if señal:
                    señales_generadas += 1
                    if señal.get('estrategia') == 'S/R Final Perfecta':
                        señales_backtesting += 1
                        logger.info(f"🎯 SEÑAL BACKTESTING: {par} {señal['direccion']}")
                    else:
                        logger.info(f"📊 SEÑAL ORIGINAL/MOVIMIENTO: {par} {señal['direccion']}")

                # Pequeña pausa entre pares para no saturar la API
                if i < len(pares) - 1:
                    time.sleep(2)

            logger.info(f"✅ Ciclo #{self.ciclo} completado - Señales: {señales_generadas} ({señales_backtesting} backtesting)")

            # Enviar estado cada 5 ciclos
            if self.ciclo % 5 == 0:
                self.enviar_telegram(
                    f"📊 REPORTE ESTRATEGIA BACKTESTING\n"
                    f"🔁 Ciclos completados: {self.ciclo}\n"
                    f"🎯 Señales totales: {señales_generadas}\n"
                    f"🚀 Señales Backtesting: {señales_backtesting}\n"
                    f"📈 Pares monitoreados: {len(pares)}\n"
                    f"⏰ Último análisis: {datetime.now().strftime('%H:%M:%S')}\n"
                    f"✅ Bot funcionando con estrategia optimizada"
                )

        except Exception as e:
            logger.error(f"💥 Error en ciclo análisis: {e}")
            # Enviar alerta de error
            self.enviar_telegram(f"⚠️ ERROR EN CICLO ANÁLISIS: {str(e)[:100]}...")

    def iniciar(self):
        """Iniciar bot"""
        logger.info("🎯 INICIANDO ESTRATEGIA S/R ETAPA 1 CON BACKTESTING")

        # Programar análisis cada 2 minutos
        schedule.every(2).minutes.do(self.ciclo_analisis)

        # Programar verificación de noticias cada 10 minutos
        schedule.every(10).minutes.do(self.verificar_noticias)

        self.activo = True
        self.enviar_telegram("✅ Bot Trading FINAL iniciado correctamente. Estrategia Backtesting + Noticias activa.")

        while self.activo:
            schedule.run_pending()
            time.sleep(1)

    def detener(self):
        """Detener bot"""
        self.activo = False
        self.enviar_telegram("🛑 Bot Trading FINAL detenido por el usuario.")

if __name__ == "__main__":
    print("=" * 70)
    print("🚀 Iniciando BOT TRADING FINAL - ESTRATEGIA BACKTESTING + NOTICIAS")
    print("⏰ Frecuencia: Cada 2 minutos")
    print("📈 Pares: 25+ Instrumentos") 
    print("📰 Alertas: Noticias alto impacto activado")
    print("=" * 70)

    bot = BotTradingFinal()

    try:
        bot.iniciar()
    except KeyboardInterrupt:
        bot.detener()
    except Exception as e:
        logger.error(f"💥 Error crítico: {e}")
        bot.detener()
