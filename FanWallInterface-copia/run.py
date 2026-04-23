from app import create_app, socketio
import os

app = create_app()

if __name__ == '__main__':
    #socketio.run(app, debug=True, host='0.0.0.0', port=5000)
    socketio.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), allow_unsafe_werkzeug=True)
