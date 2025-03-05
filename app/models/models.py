from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

# Inicializar SQLAlchemy
db = SQLAlchemy()

# Modelo para los alumnos/clientes
class Alumno(db.Model):
    __tablename__ = 'alumno'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    documento = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    telefono = db.Column(db.String(20), nullable=True)
    fecha_inscripcion = db.Column(db.Date, nullable=False)
    membresia_vencimiento = db.Column(db.Date, nullable=False)
    
    # Relación con Domicilio
    domicilio = relationship('Domicilio', backref='alumno', cascade='all, delete-orphan', uselist=False)
    telefono_emergencia = relationship('TelefonoEmergencia', backref='alumno', cascade='all, delete-orphan', uselist=False)

class Domicilio(db.Model):
    __tablename__ = 'domicilio'
    id = db.Column(db.Integer, primary_key=True)
    calle = db.Column(db.String(100), nullable=False)
    alumno_id = db.Column(db.Integer, db.ForeignKey('alumno.id'), nullable=False)

class TelefonoEmergencia(db.Model):
    __tablename__ = 'telefono_emergencia'
    id = db.Column(db.Integer, primary_key=True)
    nombre_contacto = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    relacion = db.Column(db.String(50), nullable=False)
    alumno_id = db.Column(db.Integer, db.ForeignKey('alumno.id'), nullable=False)