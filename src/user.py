from src import app, db, sqlalchemy
from flask import request
from flask_restplus import Api, Resource, fields
from werkzeug.security import check_password_hash, generate_password_hash
from src.model import User

authorizations={
    'Basic Auth': {
        'type':'basic',
        'in': 'header',
        'name': 'Authorization'
    }
}

api =  Api(app, authorizations=authorizations, version='1.0', title='Projects & Actions Api', description="Storing user's projects and actions")

namespace = api.namespace('', description='Main API Routes')

post_fields = namespace.model("Register", {'email': fields.String, 'password':fields.String})

@namespace.route("/api/users/register")
class Users(Resource):
    @namespace.doc(description='Add a user')
    @namespace.expect(post_fields)
    def post(self):
        req = request.get_json()
        email = req.get('email')
        password = req.get('password')
        if email == None or password == None:
            return {"msg":"Bad Request json"}, 400

        hashed_password = generate_password_hash(password)
        
        try:
            query1 = User(username=email, password=hashed_password)
            db.session.add(query1)
            db.session.commit()
        except sqlalchemy.exc.IntegrityError:
            return {"msg":"email already exists"}
        except Exception as e:
            return {"msg":str(e)+""}, 500
        return {"msg":"User Created"}, 201