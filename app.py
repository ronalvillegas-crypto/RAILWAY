# app.py - Web interface para Railway
from flask import Flask, jsonify
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
start_time = datetime.now()

@app.route('/')
def home():
    return jsonify({
        "status": "ACTIVE",
        "service": "BingX Trading Bot - Railway",
        "start_time": start_time.isoformat(),
        "message": "Bot ejecutándose en Railway",
        "endpoints": ["/", "/health", "/status"]
    })

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/status')
def status():
    return jsonify({
        "status": "running", 
        "platform": "railway",
        "uptime_seconds": int((datetime.now() - start_time).total_seconds())
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"🌐 Web server en puerto {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
