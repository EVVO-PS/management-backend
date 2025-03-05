from flask import Flask
from models.models import db, Alumno
from routes.routes import routes
from flask_cors import CORS
import os

app = Flask(__name__)

# Configuración de SQLite
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'gym.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
CORS(app)  # Esto permite todas las solicitudes CORS

# Inicializar la base de datos
db.init_app(app)

# Registrar las rutas en la aplicación con el prefijo /api
app.register_blueprint(routes, url_prefix='/api')

# Crear la base de datos si no existe
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)