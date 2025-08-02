from flask import Flask, send_file, request
from dashboards import weather, photo#, alerts, image
import os
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

app = Flask(__name__)
DASHBOARDS = [weather, photo]#, alerts, image]
STATE_FILE = 'dashboard_state.txt'

@app.route('/')
def serve_dashboard():
    requestor = request.headers.get('X-Forwarded-For', request.remote_addr)
    logging.info(f"Dashboard accessed by: {requestor}")

    # Read or rotate
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            idx = int(f.read().strip())
    else:
        idx = 0

    # Generate image
    dashboard = DASHBOARDS[idx % len(DASHBOARDS)]
    path = dashboard.render()  # returns path to PNG

    # Update state
    with open(STATE_FILE, 'w') as f:
        f.write(str((idx + 1) % len(DASHBOARDS)))

    log.info(f"Serving dashboard {dashboard.__name__} from file: {path}")

    # Serve image
    return send_file(path, mimetype='image/png')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)