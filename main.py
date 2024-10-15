import config
from web_api import app

def ensure_path():
    config.SUBMIT_DIR.mkdir(exist_ok=True)
    config.LOG_DIR.mkdir(exist_ok=True)

if __name__ == '__main__':
    ensure_path()
    app.run(host='0.0.0.0', port=2022)
