from functools import wraps
from flask import g, request, redirect, url_for, jsonify
import jwt

uid = None

def authenticate(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('x-auth')
        if token is None:
            return jsonify({
                'code': 4005,
                'message': 'Missing authentication header.'
            }), 401
        else:
            decoded = jwt.decode(token, 'secret', algorithm='HS256')
            g.uid = decoded['uid']
            return f(*args, **kwargs)
    return decorated_function