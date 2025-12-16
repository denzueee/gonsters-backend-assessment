"""
Entry point untuk menjalankan aplikasi Flask dengan SocketIO
Digunakan ketika menjalankan dengan: python -m app
"""

if __name__ == "__main__":
    import eventlet

    eventlet.monkey_patch()

    from app import create_app
    from app.websocket.websocket_handler import socketio

    app = create_app()
    socketio.run(app, host="0.0.0.0", port=5000, debug=False)
