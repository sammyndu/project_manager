from src import app, db, sqlalchemy
from flask import request, jsonify
from flask_restplus import Resource, fields
from src.model import Project, Action
from src.user import namespace
from .auth import token_required

post_fields = namespace.model("Actions", {'description': fields.String, 'note':fields.String})
@namespace.route("/api/projects/<int:projectId>/actions")
class ProjectAction(Resource):
    @namespace.doc(description='Retrieve all actions for a particular project')
    @token_required
    def get(self, current_user, projectId):
        '''Retrieve all actions for a particular project'''
        actions = db.session.query(Action).filter(Action.project_id == projectId).all()
        if actions:
            action_list = []

            for i in actions:
                action_list.append({'id':i.id, 'project_id':i.project_id, 'description':i.description, 'note':i.note})
            return jsonify(action_list)

        else:
            return {"msg": "no actions with this project id in the database"}

    @namespace.doc(description='Add a new action under an existing project')
    @namespace.expect(post_fields)
    @token_required
    def post(self, current_user, projectId):
        '''Add a new action under an existing project'''
        req = request.get_json()
        description = req.get('description')
        note = req.get('note')
        if not note or not description:
            return {"msg": "Invalid Request"}, 400

        try:
            project = db.session.query(Project).filter(Project.id==projectId).first()
            if project:
                action = Action(project_id=projectId, description=description, note=note) 
                db.session.add(action)
                db.session.commit()
            else:
                return {"msg": "Project with this id does not exist"}, 404
        except:
            return {"msg":'Server Error'}, 500
        
        return {"msg": "Action Created"}, 201

@namespace.route("/api/projects/<int:projectId>/actions/<int:actionId>")
class SingleProjectAction(Resource):
    @namespace.doc(description='Retrieve a single action by ID and project ID')
    @token_required
    def get(self, current_user, projectId, actionId):
        '''Retrieve a single action by action ID and project ID'''
        action = db.session.query(Action).filter(Action.id == actionId, Action.project_id == projectId).first()

        if action:
            result = {'id':action.id, 'project_id':action.project_id, 'description':action.description, 'note':action.note}
            return jsonify(result)

        else:
            return {"msg":"Action with this id and project id does not exist"}, 404

    @namespace.doc(description='Update an action')
    @namespace.expect(post_fields)
    @token_required
    def put(self, current_user, projectId, actionId):
        '''Update an action'''
        try:
            action = db.session.query(Action).filter(Action.id == actionId, Action.project_id == projectId).first()
            if action:
                req = request.get_json()
                description = req.get('description')
                note = req.get('note')
                if not note or not description:
                    return {"msg": "Invalid Request"}, 400
            else:
                return {"msg":"Action with this id and project id does not exist"}, 404
        
        
            action.note = note
            action.description = description
            db.session.commit()
        except:
            return {"msg":"server error"}

        return {"msg":"Action updated"}, 200

    @namespace.doc(description='Delete an action')
    @token_required
    def delete(self, current_user, projectId, actionId):
        '''Delete an action'''
        try:
            action = db.session.query(Action).filter(Action.id == actionId, Action.project_id == projectId).first()

            if action:
                db.session.delete(action)
                db.session.commit()
            else:
                return {'msg':'Action with this id and project id does not exist'}, 404

        except: 
            return {'msg':'server error'}, 500

        return {'msg':'Action is deleted'}

@namespace.route("/api/actions")
class Actions(Resource):
    @namespace.doc(description='Retrieve all actions')
    @token_required
    def get(self, current_user):
        '''Retrieve all actions'''
        actions = db.session.query(Action).all()
        if actions:
            action_list = []

            for i in actions:
                action_list.append({'id':i.id, 'project_id':i.project_id, 'description':i.description, 'note':i.note})

            return jsonify(action_list)

        else:
            return {"msg": "no actions in the database"}

@namespace.route("/api/actions/<int:actionId>")
class SingleAction(Resource):
    @namespace.doc(description='Retrieve a single action by ID')
    @token_required
    def get(self, current_user, actionId):
        '''Retrieve a single action by ID'''
        action = db.session.query(Action).filter(Action.id == actionId).first()

        if action:
            result = {'id':action.id, 'project_id':action.project_id, 'description':action.description, 'note':action.note}
            return jsonify(result)
        else:
            return {"msg":"Action with this id does not exist"}, 404