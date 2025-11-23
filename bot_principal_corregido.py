# bot_principal.py - BOT FINAL S/R + MOVIMIENTOS + NOTICIAS
import time
import schedule
from datetime import datetime
import logging
import sys

from config import TOP_PARES, RISK_MANAGEMENT
from telegram_bot import TelegramBotReal
from estrategia_dca import EstrategiaDCA
from estrategia_rapida import EstrategiaRapida
from noticias_alerta import AlertaNoticias

# =========================
# CONFIGURACIÓN DE LOGGING
# =========================
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

        # Módulos principales
        self.telegram = TelegramBotReal()
        self.estrategia_sr = EstrategiaDCA()          # Soporte/Resistencia + Backtesting
        self.estrategia_rapida = EstrategiaRapida()  # Momentum + Movimientos fuertes
        self.alertas_noticias = AlertaNoticias()     # Noticias alto impacto

        # Pares a monitorear (top 10 para no saturar)
        self.pares = TOP_PARES[:10]

        logger.info("🚀 INICIANDO BOT TRADING FINAL (S/R + Movimientos + Noticias)")
        logger.info(f"📊 Pares configurados: {', '.join(self.pares)}")

        # Enviar mensaje de inicio
        self.enviar_mensaje_inicio()

    # =========================
    # MENSAJE DE INICIO
    # =========================
    def enviar_mensaje_inicio(self):
        """Enviar mensaje de inicio usando el formato del TelegramBotReal"""
        config = {
            "pares": self.pares,
            "capital_inicial": RISK_MANAGEMENT.get("capital_inicial", 1000),
            "max_drawdown": int(RISK_MANAGEMENT.get("max_drawdown", 0.50) * 100),
            "consecutive_loss_limit": RISK_MANAGEMENT.get("consecutive_loss_limit", 5)
        }

        # Si existe el método especial de inicio, lo usamos
        if hasattr(self.telegram, "enviar_mensaje_inicio_bot"):
            self.telegram.enviar_mensaje_inicio_bot(config)
        else:
            # Mensaje genérico
            mensaje = f"""
🤖 BOT TRADING INICIADO

• Pares: {', '.join(self.pares)}
• Capital Inicial: ${config['capital_inicial']:.2f}
• Stop-loss Global: {config['max_drawdown']}%
• Módulos: S/R + Movimientos fuertes + Noticias alto impacto
⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            self.telegram.enviar_mensaje(mensaje.strip())

    # =========================
    # NOTICIAS
    # =========================
    def verificar_noticias_impacto(self):
        """Verificar noticias de alto impacto cada X minutos"""
        try:
            alertas = self.alertas_noticias.obtener_alertas_activas()

            for alerta in alertas:
                logger.info(f"📰 ALERTA NOTICIA: {alerta['nombre']} - Impacto: {alerta['impacto']}")
                self.telegram.enviar_alerta_noticia(alerta)

            return len(alertas)

        except Exception as e:
            logger.error(f"❌ Error verificando noticias: {e}")
            return 0

    # =========================
    # ANÁLISIS POR PAR
    # =========================
    def analizar_par(self, par):
        """
        Analizar un par y enviar:
        1) Señal por Soporte/Resistencia (backtesting)
        2) Señal por movimiento fuerte en %
        3) Señal momentum rápida (si aplica)
        """
        señal_enviada = None

        # 1️⃣ Estrategia S/R (Soporte y Resistencia + Backtesting)
        try:
            señal_sr = self.estrategia_sr.generar_señal_avanzada(par)
            if señal_sr:
                logger.info(f"🏔️ S/R: {par} {señal_sr['direccion']} - Estrategia {señal_sr.get('estrategia', '')}")
                # Señal completa: se muestra S/R, TP, SL, DCA
                self.telegram.enviar_señal_completa(
                    señal_sr,
                    "🏔️ Señal generada por Soporte/Resistencia + Backtesting"
                )
                señal_enviada = señal_sr
        except Exception as e:
            logger.error(f"❌ Error en estrategia S/R para {par}: {e}")

        # 2️⃣ Estrategia Rápida (Movimiento fuerte o Momentum)
        try:
            señal_rapida = self.estrategia_rapida.generar_señal_eficiente(par)

            if señal_rapida:
                if señal_rapida.get('tipo_señal') == 'MOVIMIENTO':
                    # Movimiento fuerte en % (alerta de vigilancia)
                    logger.info(
                        f"🚨 MOVIMIENTO: {par} {señal_rapida['direccion']} "
                        f"- {señal_rapida['movimiento_porcentual']:.2f}% ({señal_rapida['periodo_movimiento']})"
                    )
                    self.telegram.enviar_señal_movimiento(
                        señal_rapida,
                        "⚡ Cambio porcentual fuerte, vigilancia del par recomendada"
                    )
                else:
                    # Señal momentum "normal"
                    logger.info(f"📊 MOMENTUM: {par} {señal_rapida['direccion']}")
                    self.telegram.enviar_señal_completa(
                        señal_rapida,
                        "📊 Señal de momentum rápido"
                    )

                # Si no hubo señal S/R, devolvemos esta
                if not señal_enviada:
                    señal_enviada = señal_rapida

        except Exception as e:
            logger.error(f"❌ Error en estrategia rápida para {par}: {e}")

        return señal_enviada

    # =========================
    # CICLO PRINCIPAL
    # =========================
    def ciclo_analisis(self):
        """Ciclo principal de análisis con todos los pares"""
        self.ciclo += 1
        logger.info(
            f"🔄 CICLO #{self.ciclo} - {datetime.now().strftime('%H:%M:%S')} "
            f"(S/R + Movimientos + Noticias)"
        )

        try:
            señales_totales = 0
            señales_sr = 0
            señales_mov = 0

            for i, par in enumerate(self.pares):
                if not self.activo:
                    break

                logger.info(f"🔍 Analizando {par} ({i + 1}/{len(self.pares)})")
                señal = self.analizar_par(par)

                if señal:
                    señales_totales += 1
                    if señal.get('estrategia', '').startswith('S/R'):
                        señales_sr += 1
                    if señal.get('tipo_señal') == 'MOVIMIENTO':
                        señales_mov += 1

                # Pausa pequeña para no saturar APIs
                if i < len(self.pares) - 1:
                    time.sleep(2)

            logger.info(
                f"✅ Ciclo #{self.ciclo} completado - "
                f"Señales: {señales_totales} | S/R: {señales_sr} | Movimientos: {señales_mov}"
            )

            # Cada 5 ciclos, enviar mini-reporte a Telegram
            if self.ciclo % 5 == 0:
                resumen = f"""
📊 <b>REPORTE RÁPIDO BOT</b>

🔁 Ciclos completados: {self.ciclo}
🎯 Señales totales último ciclo: {señales_totales}
🏔️ Señales S/R: {señales_sr}
⚡ Señales por movimiento fuerte: {señales_mov}
📈 Pares monitoreados: {len(self.pares)}
⏰ Último análisis: {datetime.now().strftime('%H:%M:%S')}
"""
                self.telegram.enviar_mensaje(resumen.strip())

        except Exception as e:
            logger.error(f"💥 Error en ciclo análisis: {e}")
            self.telegram.enviar_mensaje(
                f"⚠️ ERROR EN CICLO ANÁLISIS:\n{str(e)[:150]}"
            )

    # =========================
    # CONTROL START / STOP
    # =========================
    def iniciar(self):
        """Iniciar bot con schedulers"""
        logger.info("🎯 INICIANDO SCHEDULERS DEL BOT")

        # Análisis de mercado cada 2 minutos
        schedule.every(2).minutes.do(self.ciclo_analisis)

        # Noticias alto impacto cada 10 minutos
        schedule.every(10).minutes.do(self.verificar_noticias_impacto)

        # Primera ejecución inmediata
        self.ciclo_analisis()
        self.verificar_noticias_impacto()

        logger.info("✅ Bot en ejecución - Monitoreo cada 2 minutos + Noticias cada 10 minutos")

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
        logger.info("🛑 Bot detenido")

        mensaje = f"""
🛑 BOT DETENIDO

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🔁 Ciclos totales: {self.ciclo}
📴 Servicio finalizado
"""
        self.telegram.enviar_mensaje(mensaje.strip())


if __name__ == "__main__":
    print("=" * 70)
    print("🤖 BOT TRADING RAILWAY - S/R + MOVIMIENTOS + NOTICIAS")
    print("📍 Telegram: CONECTADO vía TelegramBotReal")
    print("🎯 Estrategias: S/R Backtesting + Momentum + Movimiento %")
    print("📰 Alertas: Noticias alto impacto activadas")
    print("=" * 70)

    bot = BotTradingFinal()

    try:
        bot.iniciar()
    except KeyboardInterrupt:
        bot.detener()
    except Exception as e:
        logger.error(f"💥 Error crítico: {e}")
        bot.detener()
