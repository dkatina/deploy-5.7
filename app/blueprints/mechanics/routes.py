from flask import  jsonify, request
from marshmallow import ValidationError
from sqlalchemy import select
from . import mechanics_bp
from .schemas import mechanic_schema, mechanics_schema, login_schema
from app.models import Mechanic, db
from app.extensions import limiter, cache
from app.utils.auth import encode_token, token_required

@mechanics_bp.route('/login', methods=['POST'])
def login():
    try:
        creds = login_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query = select(Mechanic).where(Mechanic.email == creds['email'])
    mechanic = db.session.execute(query).scalars().first()

    if mechanic and mechanic.password == creds['password']:
        token = encode_token(mechanic.id)
        return jsonify({'token': token})

#CREATE
@mechanics_bp.route('/', methods=['POST'])
def create_mechanic():
    try:
        mechanic_data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query = select(Mechanic).where(Mechanic.email == mechanic_data['email'])
    mechanic = db.session.execute(query).scalars().first()

    if mechanic: #returns true and access if-block
        return jsonify({"error": "Email already associated with another account."}), 400
    
    new_mechanic = Mechanic(**mechanic_data)

    db.session.add(new_mechanic)
    db.session.commit()

    return mechanic_schema.jsonify(new_mechanic), 201

#READ
@mechanics_bp.route("/", methods=['GET'])
@cache.cached(timeout=60)
def get_mechanics():

    query = select(Mechanic)
    mechanics = db.session.execute(query).scalars().all()

    return mechanics_schema.jsonify(mechanics), 200
    
#Get single mechanic
@mechanics_bp.route("/<int:mechanic_id>", methods=['GET'])
@limiter.limit("20/day")
def get_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)

    if mechanic:
        return mechanic_schema.jsonify(mechanic), 200
    
    return jsonify({"error": "Invalid mechanic_id"}), 400


#UPDATE
@mechanics_bp.route("/", methods=['PUT'])
@limiter.limit("5/day")
@token_required
def update_mechanic():
    mechanic = db.session.get(Mechanic, request.mechanic_id)

    if not mechanic:
        return jsonify({"error": "Invalid mechanic_id"}), 400
    
   
    try:
        mechanic_data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400 
    
    query = select(Mechanic).where(Mechanic.email == mechanic_data['email'])
    db_mechanic = db.session.execute(query).scalars().first()

    if db_mechanic and db_mechanic != mechanic:
        return jsonify({'error': 'Email already associated with another account.'}), 400
    
    
    for field, value in mechanic_data.items():
        setattr(mechanic, field, value)

    db.session.commit()
    return mechanic_schema.jsonify(mechanic), 200

@mechanics_bp.route("/", methods=['DELETE'])
@limiter.limit("8/day")
@token_required
def delete_mechanic():
    mechanic = db.session.get(Mechanic, request.mechanic_id)

    if not mechanic:
        return jsonify({"error": "Invalid mechanic_id"}), 400

    db.session.delete(mechanic)
    db.session.commit()
    return jsonify({"message": f"mechanic {request.mechanic_id} was deleted."})


@mechanics_bp.route("/popularity", methods=['GET'])
def popularity():

    query = select(Mechanic)
    mechanics = db.session.execute(query).scalars().all()

    mechanics.sort(key= lambda mechanic : len(mechanic.tickets), reverse=True)

    return mechanics_schema.jsonify(mechanics)