from flask import  jsonify, request
from marshmallow import ValidationError
from sqlalchemy import select
from . import customers_bp
from .schemas import customer_schema, customers_schema
from app.models import Customer, db
from app.extensions import limiter, cache

#CREATE
@customers_bp.route('/', methods=['POST'])
@limiter.limit("15/hour")
def create_customer():
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query = select(Customer).where(Customer.email == customer_data['email'])
    customer = db.session.execute(query).scalars().first()

    if customer: #returns true and access if-block
        return jsonify({"error": "Email already associated with another account."}), 400
    
    new_customer = Customer(**customer_data)

    db.session.add(new_customer)
    db.session.commit()

    return customer_schema.jsonify(new_customer), 201

#READ
@customers_bp.route("/", methods=['GET'])
@limiter.exempt
def get_customers():
    page = int(request.args.get('page'))
    per_page = int(request.args.get('per_page'))
    query = select(Customer)
    customers = db.paginate(query, page=page, per_page=per_page)
    return customers_schema.jsonify(customers), 200
    
#Get single customer
@customers_bp.route("/<int:customer_id>", methods=['GET'])
def get_customer(customer_id):
    customer = db.session.get(Customer, customer_id)

    if customer:
        return customer_schema.jsonify(customer), 200
    
    return jsonify({"error": "Invalid customer_id"}), 400


#UPDATE
@customers_bp.route("/<int:customer_id>", methods=['PUT'])
@limiter.limit("5/hour")
def update_customer(customer_id):
    customer = db.session.get(Customer, customer_id)

    if not customer:
        return jsonify({"error": "Invalid customer_id"}), 400
    
   
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400 
    
    query = select(Customer).where(Customer.email == customer_data['email'])
    db_customer = db.session.execute(query).scalars().first()

    if db_customer and db_customer != customer:
        return jsonify({'error': 'Email already associated with another account.'}), 400
    
    
    for field, value in customer_data.items():
        setattr(customer, field, value)

    db.session.commit()
    return customer_schema.jsonify(customer), 200

@customers_bp.route("/<int:customer_id>", methods=['DELETE'])
@limiter.limit("5/hour")
def delete_customer(customer_id):
    customer = db.session.get(Customer, customer_id)

    if not customer:
        return jsonify({"error": "Invalid customer_id"}), 400

    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": f"Customer {customer_id} was deleted."})

@customers_bp.route("/search", methods=['GET'])
def search_by_email():
    email = request.args.get("email")
    print(email)
    query = select(Customer).where(Customer.email.like(f"%{email}%"))
    customer = db.session.execute(query).scalars().all()
    print(customer)
    return customers_schema.jsonify(customer)


    