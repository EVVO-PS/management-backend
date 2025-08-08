from flask import Flask
from app.models.models import db, Alumno
from app.routes.routes import routes
from flask_cors import CORS
import os

app = Flask(__name__)

database_url = os.environ.get('STORAGE_URL')

if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app)

db.init_app(app)

app.register_blueprint(routes, url_prefix='/api')

if __name__ == '__main__':
    app.run(debug=True)