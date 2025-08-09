import os
import threading
import time

# Ensure Flask app imports correctly
from app import LabelMakerApp

def start_flask_in_thread(host: str = '127.0.0.1', port: int = 5002):
    app_wrapper = LabelMakerApp()
    thread = threading.Thread(
        target=lambda: app_wrapper.app.run(host=host, port=port, debug=False, use_reloader=False),
        daemon=True,
    )
    thread.start()
    return thread

def main():
    # Start backend
    host = os.environ.get('HOST', '127.0.0.1')
    port = int(os.environ.get('FLASK_PORT', 5002))
    start_flask_in_thread(host, port)

    # Slight delay to ensure server is listening
    time.sleep(0.7)

    # Import pywebview lazily to avoid hard dependency when unused
    import webview

    # Create a native window pointing to the local Flask URL
    window = webview.create_window('AGT Designer', f'http://{host}:{port}/')
    # Use EdgeHTML/WebKit depending on platform; defaults are fine
    webview.start(gui=None, debug=False)

if __name__ == '__main__':
    main()

