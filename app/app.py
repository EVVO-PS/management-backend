from flask import Flask
from models.models import db, Alumno
from routes.routes import routes
from flask_cors import CORS
import os

app = Flask(__name__)

# 1. Obtener la URL de la base de datos de Vercel
database_url = os.environ.get('STORAGE_URL')

# 2. Reemplazar el protocolo para que SQLAlchemy funcione
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

# 3. Configurar la aplicación para USAR la base de datos de Vercel
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app)

# Inicializar la extensión SQLAlchemy con la app
db.init_app(app)

# Registrar las rutas (Blueprints)
app.register_blueprint(routes, url_prefix='/api')

# La sección 'db.create_all()' se elimina.
# Las tablas se deben crear manualmente una sola vez.

if __name__ == '__main__':
    app.run(debug=True)