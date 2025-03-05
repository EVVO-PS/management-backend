from flask import Blueprint, request, jsonify
from models.models import db, Alumno, Domicilio, TelefonoEmergencia
from datetime import datetime, timedelta
from functools import wraps
from sqlalchemy import or_

routes = Blueprint('routes', __name__)

# 🔹 Función de autenticación por token
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or token.split()[1] != 'master123':
            return jsonify({'message': 'Token is missing or invalid!'}), 401
        return f(*args, **kwargs)
    return decorated

# 🔹 Función auxiliar para convertir objeto Alumno a JSON
def alumno_to_dict(alumno):
    return {
        'id': alumno.id,
        'nombre': alumno.nombre,
        'documento': alumno.documento,
        'email': alumno.email,
        'telefono': alumno.telefono,
        'fecha_inscripcion': alumno.fecha_inscripcion.strftime('%Y-%m-%d'),
        'membresia_vencimiento': alumno.membresia_vencimiento.strftime('%Y-%m-%d'),
        'domicilio': {'calle': alumno.domicilio.calle} if alumno.domicilio else None,
        'telefono_emergencia': {
            'nombre_contacto': alumno.telefono_emergencia.nombre_contacto if alumno.telefono_emergencia else None,
            'telefono': alumno.telefono_emergencia.telefono if alumno.telefono_emergencia else None,
            'relacion': alumno.telefono_emergencia.relacion if alumno.telefono_emergencia else None
        }
    }

# 🔹 Login
# @routes.route('/login', methods=['POST'])
# def login():
#     data = request.get_json()
#     if data.get('username') == 'admin' and data.get('password') == 'master123':
#         return jsonify({'token': 'master123', 'message': 'Login successful'}), 200
#     return jsonify({'message': 'Invalid credentials'}), 401

# 🔹 Crear Alumno
@routes.route('/alumnos', methods=['POST'])
def agregar_alumno():
    data = request.get_json()

    try:
        nuevo_alumno = Alumno(
            nombre=data['nombre'],
            documento=data['documento'],
            email=data['email'],
            telefono=data.get('telefono', ''),
            fecha_inscripcion=datetime.strptime(data['fecha_inscripcion'], '%Y-%m-%d').date(),
            membresia_vencimiento=datetime.strptime(data['membresia_vencimiento'], '%Y-%m-%d').date()
        )
        db.session.add(nuevo_alumno)
        db.session.flush()  # Obtiene el ID antes del commit

        # Agregar domicilio si existe
        if domicilio_data := data.get('domicilio'):
            db.session.add(Domicilio(calle=domicilio_data['calle'], alumno_id=nuevo_alumno.id))

        # Agregar teléfono de emergencia si existe
        if telefono_data := data.get('telefono_emergencia'):
            db.session.add(TelefonoEmergencia(
                nombre_contacto=telefono_data['nombre_contacto'],
                telefono=telefono_data['telefono'],
                relacion=telefono_data['relacion'],
                alumno_id=nuevo_alumno.id
            ))

        db.session.commit()
        return jsonify({'mensaje': 'Alumno registrado con éxito'}), 201
    except KeyError as e:
        return jsonify({'error': f'Falta el campo requerido: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al registrar alumno: {str(e)}'}), 500

# 🔹 Obtener lista de alumnos
@routes.route('/alumnos', methods=['GET'])
def obtener_alumnos():
    alumnos = Alumno.query.all()
    return jsonify([alumno_to_dict(alumno) for alumno in alumnos])

# 🔹 Buscar alumnos por nombre o documento
@routes.route('/alumnos/buscar', methods=['GET'])
def buscar_alumnos():
    termino = request.args.get('termino', '')
    alumnos = Alumno.query.filter(
        or_(Alumno.nombre.ilike(f'%{termino}%'), Alumno.documento.ilike(f'%{termino}%'))
    ).all()
    return jsonify([alumno_to_dict(alumno) for alumno in alumnos])

# 🔹 Actualizar alumno
@routes.route('/alumnos/<int:id>', methods=['PUT'])
@token_required
def actualizar_alumno(id):
    alumno = Alumno.query.get(id)
    if not alumno:
        return jsonify({'error': 'Alumno no encontrado'}), 404

    data = request.get_json()
    alumno.nombre = data.get('nombre', alumno.nombre)
    alumno.email = data.get('email', alumno.email)
    alumno.telefono = data.get('telefono', alumno.telefono)

    if 'fecha_inscripcion' in data:
        alumno.fecha_inscripcion = datetime.strptime(data['fecha_inscripcion'], '%Y-%m-%d').date()
    if 'membresia_vencimiento' in data:
        alumno.membresia_vencimiento = datetime.strptime(data['membresia_vencimiento'], '%Y-%m-%d').date()

    db.session.commit()
    return jsonify({'mensaje': 'Alumno actualizado correctamente'})

# 🔹 Eliminar alumno
@routes.route('/alumnos/<int:id>', methods=['DELETE'])
@token_required
def eliminar_alumno(id):
    alumno = Alumno.query.get(id)
    if not alumno:
        return jsonify({'error': 'Alumno no encontrado'}), 404

    db.session.delete(alumno)
    db.session.commit()
    return jsonify({'mensaje': 'Alumno eliminado correctamente'})

# 🔹 Obtener alumnos con membresía vencida o por vencer
@routes.route('/alumnos/alertas', methods=['GET'])
def alertas_membresia():
    hoy = datetime.today().date()
    fecha_limite = hoy + timedelta(days=7)
    alumnos_alerta = Alumno.query.filter(Alumno.membresia_vencimiento <= fecha_limite).all()

    return jsonify([{
        'id': alumno.id,
        'nombre': alumno.nombre,
        'email': alumno.email,
        'telefono': alumno.telefono,
        'membresia_vencimiento': alumno.membresia_vencimiento.strftime('%Y-%m-%d'),
        'estado': 'VENCIDO' if alumno.membresia_vencimiento < hoy else 'POR VENCER'
    } for alumno in alumnos_alerta])

    
