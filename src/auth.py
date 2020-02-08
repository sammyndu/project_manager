import jwt
from src import app, db, sqlalchemy
from flask import request, jsonify, Response, make_response
from flask_restplus import Resource
from src.model import User
from src.user import namespace
from werkzeug.security import check_password_hash
import datetime
from functools import wraps

def token_required(f):
    '''A decorated function to check authorize users for particular routes'''
    @wraps(f)
    def decorated(*args, **kwargs):
        #checks if the token was sent in the header
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        else:
            return {"msg":"Unauthorized"}, 403
    
        if token: 
            # if there is a token, it decodes it and passes the user back to the function to access the logged 
            # users info as long as the token is valid
            try:
                data = jwt.decode(token, app.config['SECRET_KEY'])
                current_user = db.session.query(User).filter(User.id == data['id']).first()
            except:
                return {"error":"invalid token"}
            args = list(args)
            args.insert(1, current_user)
            args = tuple(args)
        else:
            return {"msg":"token is missing"}

        return f(*args, **kwargs)

    return decorated


@namespace.route('/api/users/auth')
class Auth(Resource):
    def post(self):
        '''Handles authentication verification'''
        auth = request.authorization
        if auth and auth.username and auth.password:
            query1 = db.session.query(User).filter(User.username==auth.username).first()
            if query1 and check_password_hash(query1.password, auth.password):
                token = jwt.encode({'id': query1.id, \
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60)},\
                        app.config['SECRET_KEY'])
                return jsonify({'token': token.decode('UTF-8')})
            else:
                return {"msg":"Unauthorized"}, 403
                
        return make_response('Please Login', 401, {'WWW.Authenticate':'Basic realm="Login Required"'})