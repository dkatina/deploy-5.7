from flask import redirect
from app import create_app
from app.models import db



app = create_app('ProductionConfig')

@app.route('/', methods=['GET'])
def index():
    return redirect('/api/docs')

with app.app_context():
    # db.drop_all()
    db.create_all()

