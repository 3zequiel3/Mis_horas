from app import create_app
from app.config import API_HOST, API_PORT, FLASK_DEBUG
from dotenv import load_dotenv

load_dotenv()

app = create_app()

if __name__ == '__main__':
    host = API_HOST
    port = int(API_PORT)
    debug = FLASK_DEBUG == 'True'
    
    app.run(host=host, port=port, debug=debug)
