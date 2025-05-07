from flask import  jsonify, request
from marshmallow import ValidationError
from sqlalchemy import select
from . import service_tickets_bp
from .schemas import service_ticket_schema, service_tickets_schema
from app.models import Mechanic, PartDescription, SerializedPart, ServiceTicket, db, Customer
from app.blueprints.mechanics.schemas import mechanics_schema
from app.extensions import limiter
from app.blueprints.serialized_parts.schemas import serialized_parts_schema, responses_schema


#Create Ticket
@service_tickets_bp.route('/', methods=['POST'])
def create_ticket():
    try:
        ticket_data = service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages)
    
    customer = db.session.query(Customer, ticket_data['customer_id'])

    if customer:
        new_ticket = ServiceTicket(**ticket_data)
        db.session.add(new_ticket)
        db.session.commit()

        return service_ticket_schema.jsonify(new_ticket), 201
    return jsonify({"error": "Invalid customer_id"})


#Get Ticekts
@service_tickets_bp.route('/', methods=['GET'])
@limiter.exempt
def get_tickets():
    query = select(ServiceTicket)
    tickets = db.session.execute(query).scalars().all()

    if tickets:
        return service_tickets_schema.jsonify(tickets), 200
    return jsonify({'error': "No tickets to view."})


#Get Specific Ticket
@service_tickets_bp.route('/<int:service_ticket_id>', methods=['GET'])
@limiter.exempt
def get_ticket(service_ticket_id):
    ticket = db.session.get(ServiceTicket, service_ticket_id)

    if ticket:
        return service_ticket_schema.jsonify(ticket), 200
    return jsonify({'error': "Invalid service_ticket_id."})



#Add Mechanic to Ticket
@service_tickets_bp.route("/<int:ticket_id>/add-mechanic/<int:mechanic_id>", methods=['PUT'])
def add_mechanic(ticket_id, mechanic_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    mechanic = db.session.get(Mechanic, mechanic_id)

    if ticket and mechanic:
        if mechanic not in ticket.mechanics:
            ticket.mechanics.append(mechanic)
            db.session.commit()
            return jsonify({
                "message": f"successfully added {mechanic.name} to the ticket",
                "ticket": service_ticket_schema.dump(ticket),
                "mechanics": mechanics_schema.dump(ticket.mechanics)
            }), 200
        return jsonify({"error": f"{mechanic.name} already assigned to ticket."}), 400
    return jsonify({'error': "Invalid ticket_id or mechanic_id."}), 400
    


#Remove Mechanic from Ticket
@service_tickets_bp.route("/<int:ticket_id>/remove-mechanic/<int:mechanic_id>", methods=['PUT'])
def remove_mechanic(ticket_id, mechanic_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    mechanic = db.session.get(Mechanic, mechanic_id)

    if ticket and mechanic:
        if mechanic in ticket.mechanics:
            ticket.mechanics.remove(mechanic)
            db.session.commit()
            return jsonify({
                "message": f"successfully removed {mechanic.name} from the ticket",
                "ticket": service_ticket_schema.dump(ticket),
                "mechanics": mechanics_schema.dump(ticket.mechanics)
            }), 200
        return jsonify({"error": f"{mechanic.name} was not assigned to this ticket."}), 400
    return jsonify({'error': "Invalid ticket_id or mechanic_id."}), 400


@service_tickets_bp.route("/<int:ticket_id>/add-part/<int:part_id>", methods=['PUT'])
def add_part(ticket_id, part_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    part = db.session.get(SerializedPart, part_id)

    if ticket and part:
        if not part.ticket_id:
            ticket.serialized_parts.append(part)
            db.session.commit()
            return jsonify({
                "message": f"successfully added {part.description.part_name} to the ticket",
                "ticket": service_ticket_schema.dump(ticket),
                "parts": serialized_parts_schema.dump(ticket.serialized_parts)
            }), 200
        return jsonify({
            'error': "this part has already been used"
        }), 400
    return jsonify({'error': "Invalid ticket_id or part_id."}), 400


@service_tickets_bp.route("/<int:ticket_id>/add-to-cart/<int:description_id>", methods=['PUT'])
def add_to_cart(ticket_id, description_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    description = db.session.get(PartDescription, description_id)

    parts = description.serialized_parts

    for part in parts:
        if not part.ticket_id:
            ticket.serialized_parts.append(part)
            db.session.commit()
            return jsonify({
                "message": f"successfully added {part.description.part_name} to the ticket",
                "ticket": service_ticket_schema.dump(ticket),
                "parts": responses_schema.dump(ticket.serialized_parts)
            }), 200

    # query = select(SerializedPart).where(SerializedPart.desc_id == description_id, SerializedPart.ticket_id == None)
    # part = db.session.execute(query).scalars().first()

    # ticket.serialized_parts.append(part)
    # db.session.commit()
    # return jsonify({
    #     "message": f"successfully added {part.description.part_name} to the ticket",
    #     "ticket": service_ticket_schema.dump(ticket),
    #     "parts": serialized_parts_schema.dump(ticket.serialized_parts)
    # }), 200


    
    

