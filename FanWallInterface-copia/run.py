from app import create_app, socketio
from flask import request
import os

app = create_app()

# ==========================================
# ENDPOINT PARA DETENER EL SERVIDOR
# ==========================================

@app.route('/shutdown', methods=['POST'])
def shutdown():
    shutdown_func = request.environ.get('werkzeug.server.shutdown')
    if shutdown_func is None:
        return {'error': 'Shutdown only available in development'}, 400
    shutdown_func()
    return {'message': 'Server shutting down...'}, 200

# ==========================================
# EJECUCIÓN PRINCIPAL
# ==========================================

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), allow_unsafe_werkzeug=True)