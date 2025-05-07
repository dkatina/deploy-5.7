from flask import  jsonify, request
from marshmallow import ValidationError
from sqlalchemy import select

from app.blueprints import part_descriptions
from . import serialized_parts_bp
from .schemas import serialized_part_schema, serialized_parts_schema
from app.models import PartDescription, SerializedPart, db
from app.extensions import limiter, cache

#CREATE
@serialized_parts_bp.route('/', methods=['POST'])
@limiter.limit("15/hour")
def create_serialized_part():
    try:
        serialized_part_data = serialized_part_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_serialized_part = SerializedPart(**serialized_part_data)

    db.session.add(new_serialized_part)
    db.session.commit()

    return jsonify({
        "message": f"Added new {new_serialized_part.description.brand} {new_serialized_part.description.part_name} to database",
        "part": serialized_part_schema.dump(new_serialized_part)
    })

#READ
@serialized_parts_bp.route("/", methods=['GET'])
@limiter.exempt
def get_serialized_parts():
    page = int(request.args.get('page'))
    per_page = int(request.args.get('per_page'))
    query = select(SerializedPart)
    serialized_parts = db.paginate(query, page=page, per_page=per_page)
    return serialized_parts_schema.jsonify(serialized_parts), 200
    
#Get single serialized_part
@serialized_parts_bp.route("/<int:serialized_part_id>", methods=['GET'])
def get_serialized_part(serialized_part_id):
    serialized_part = db.session.get(SerializedPart, serialized_part_id)

    if serialized_part:
        return serialized_part_schema.jsonify(serialized_part), 200
    
    return jsonify({"error": "Invalid serialized_part_id"}), 400


#UPDATE
@serialized_parts_bp.route("/<int:serialized_part_id>", methods=['PUT'])
@limiter.limit("5/hour")
def update_serialized_part(serialized_part_id):
    serialized_part = db.session.get(SerializedPart, serialized_part_id)

    if not serialized_part:
        return jsonify({"error": "Invalid serialized_part_id"}), 400
    
    try:
        serialized_part_data = serialized_part_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400 
    
    
    for field, value in serialized_part_data.items():
        setattr(serialized_part, field, value)

    db.session.commit()
    return serialized_part_schema.jsonify(serialized_part), 200

@serialized_parts_bp.route("/<int:serialized_part_id>", methods=['DELETE'])
@limiter.limit("5/hour")
def delete_serialized_part(serialized_part_id):
    serialized_part = db.session.get(SerializedPart, serialized_part_id)

    if not serialized_part:
        return jsonify({"error": "Invalid serialized_part_id"}), 400

    db.session.delete(serialized_part)
    db.session.commit()
    return jsonify({"message": f"serialized_part {serialized_part_id} was deleted."})

@serialized_parts_bp.route("/stock/<int:description_id>", methods={'GET'})
def get_individual_stock(description_id):
    part_description = db.session.get(PartDescription, description_id)

    parts = part_description.serialized_parts

    count = 0
    for part in parts:
        if not part.ticket_id:
            count += 1

    return jsonify({
        "Item": part_description.part_name,
        "quantity": count
    })
    


    