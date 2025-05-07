from flask import  jsonify, request
from marshmallow import ValidationError
from sqlalchemy import select
from . import part_descriptions_bp
from .schemas import part_description_schema, part_descriptions_schema
from app.models import PartDescription, db
from app.extensions import limiter, cache

#CREATE
@part_descriptions_bp.route('/', methods=['POST'])
@limiter.limit("15/hour")
def create_part_description():
    try:
        part_description_data = part_description_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_part_description = PartDescription(**part_description_data)

    db.session.add(new_part_description)
    db.session.commit()

    return part_description_schema.jsonify(new_part_description), 201

#READ
@part_descriptions_bp.route("/", methods=['GET'])
@limiter.exempt
def get_part_descriptions():
    page = int(request.args.get('page'))
    per_page = int(request.args.get('per_page'))
    query = select(PartDescription)
    part_descriptions = db.paginate(query, page=page, per_page=per_page)
    return part_descriptions_schema.jsonify(part_descriptions), 200
    
#Get single part_description
@part_descriptions_bp.route("/<int:part_description_id>", methods=['GET'])
def get_part_description(part_description_id):
    part_description = db.session.get(PartDescription, part_description_id)

    if part_description:
        return part_description_schema.jsonify(part_description), 200
    
    return jsonify({"error": "Invalid part_description_id"}), 400


#UPDATE
@part_descriptions_bp.route("/<int:part_description_id>", methods=['PUT'])
@limiter.limit("5/hour")
def update_part_description(part_description_id):
    part_description = db.session.get(PartDescription, part_description_id)

    if not part_description:
        return jsonify({"error": "Invalid part_description_id"}), 400
    
    try:
        part_description_data = part_description_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400 
    
    
    for field, value in part_description_data.items():
        setattr(part_description, field, value)

    db.session.commit()
    return part_description_schema.jsonify(part_description), 200

@part_descriptions_bp.route("/<int:part_description_id>", methods=['DELETE'])
@limiter.limit("5/hour")
def delete_part_description(part_description_id):
    part_description = db.session.get(PartDescription, part_description_id)

    if not part_description:
        return jsonify({"error": "Invalid part_description_id"}), 400

    db.session.delete(part_description)
    db.session.commit()
    return jsonify({"message": f"part_description {part_description_id} was deleted."})

@part_descriptions_bp.route("/search", methods=['GET'])
def search_by_part_name():
    name = request.args.get("name")
    print(name)
    query = select(part_description).where(part_description.part_name.like(f"%{name}%"))
    part_description = db.session.execute(query).scalars().first()
    print(part_description)
    return part_description_schema.jsonify(part_description)


    