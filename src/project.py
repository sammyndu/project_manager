from src import app, db, sqlalchemy
from flask import request, jsonify
from flask_restplus import Resource
from src.model import Project
from src.user import namespace
from .auth import token_required

@namespace.route("/api/projects")
class Projects(Resource):
    @namespace.doc(description='list all projects')
    @token_required
    def get(self, current_user):
        project = db.session.query(Project).all()
        if project:
            project_list = []
            for i in project:
                project_list.append({'id':i.id, 'name':i.name, 'description':i.description, 'completed':i.completed})

            return jsonify(project_list)

        else:
            return {"msg": "no projects in the database"}

    @namespace.doc(description='Add a new project')
    @token_required
    def post(self, current_user):
        req = request.get_json()
        name = req.get('name')
        description = req.get('description')
        if not name or not description:
            return {"msg": "Invalid Request"}, 400

        try:
            project = Project(name=name, description=description) 
            db.session.add(project)
            db.session.commit()
        except sqlalchemy.exc.IntegrityError:
            return {"msg":"Project name already exists"}
        except:
            return {"msg":'Server Error'}, 500
        
        return {"msg": "Project Created"}, 201

@namespace.route("/api/projects/<int:projectId>")
class SingleProject(Resource):
    @namespace.doc(description='Get a single project by Id')
    @token_required
    def get(self, current_user, projectId):
        project = db.session.query(Project).filter(Project.id==projectId).first()
        if project:
            result = {'id':project.id, 'name':project.name, 'description':project.description, 'completed':project.completed}
            return jsonify(result)
        else:
            return {"msg":"Project does not exist"}, 404

    @namespace.doc(description='Update a project')
    @token_required
    def put(self, current_user, projectId):
        project = db.session.query(Project).filter(Project.id==projectId).first()
        if project:
            req = request.get_json()
            name = req.get('name')
            description = req.get('description')
            if not name or not description:
                return {"msg": "Invalid Request"}, 400
        else:
            return {"msg":"Project does not exist"}, 404
        
        try:
            project.name = name
            project.description = description
            db.session.commit()
        except sqlalchemy.exc.IntegrityError:
            return {"msg":"Project name already exists"}
        except:
            return {"msg":"server error"}

        return {"msg":"Project updated"}, 200

    @namespace.doc(description='Update thee completed property of a project')
    @token_required
    def patch(self, current_user, projectId):
        project = db.session.query(Project).filter(Project.id==projectId).first()
        if project:
            req = request.get_json()
            completed = req.get('completed')
            if completed == "":
                return {"msg": "Invalid Request"}, 400
        else:
            return {"msg":"Project does not exist"}, 404
        
        try:
            project.completed = completed
            db.session.commit()
        except:
            return {"msg":"server error"}

        return {"msg":"Project updated"}, 200

    @namespace.doc(description='Delete a project')
    @token_required
    def delete(self, current_user, projectId):
        project = db.session.query(Project).filter(Project.id==projectId).first()
        if project:
            try:
                db.session.delete(project)
                db.session.commit()
            except: 
                return {'msg':'server error'}, 500
        else:
            return {'msg':'Project does not exist'}, 404

        return {'msg':'Projet is deleted'}