from jose import jwt 
import jose
from datetime import datetime, timedelta, timezone
from flask import request, jsonify
from functools import wraps
import os

SECRET_KEY = os.environ.get('SECRET_KEY') or "super secret secrets"

def encode_token(mechanic_id):
    payload = {
        'exp': datetime.now(timezone.utc) + timedelta(days=0, hours=1),
        'iat': datetime.now(timezone.utc),
        "sub": str(mechanic_id)
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token


def token_required(f):
    @wraps(f)
    def decoration(*arg, **kwargs):
        token = None

        #look ofr token in the request
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split()[1]

        if not token:
            return jsonify({"error": "missing token"}), 401
        
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            request.mechanic_id = int(data['sub'])
        except jose.exceptions.ExpiredSignatureError:
            return jsonify({"error": "Token is expired"}),401
        except jose.exceptions.JWTError:
            return jsonify({'error': "Invalid token."}), 401
        
        return f(*arg, **kwargs)
    
    return decoration
        