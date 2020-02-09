import os
from src import app, db, sqlalchemy
from flask import request, jsonify
from flask_restplus import Resource
from src.model import Project
from src.user import namespace
from .auth import token_required
from werkzeug.utils import secure_filename

def allowed_file(filename):
    Allowed_Extensions = set(['txt', 'pdf', 'png', 'jpg', 'jpeg'])
    return '.' in filename and filename.rsplit('.',1)[1].lower() in Allowed_Extensions

def get_project_list(project, request_args=""):
    if project:
        project_list = []
        for i in project:
            project_list.append({'id':i.id, 'name':i.name, 'description':i.description, 'completed':i.completed, "user_stories": i.user_stories})

        return jsonify(project_list)
    else:
        if request_args == 'search':
            return {"msg": "no projects matching "+word+" in the database"}, 404
        else:
            return {"msg": "no projects in the database"}, 404

@app.errorhandler(413)
def request_entity_too_large(error):
    return {"msg":"file size cannot be more than 1mb"}

@namespace.route("/api/projects")
class Projects(Resource):
    @namespace.doc(description='list all projects')
    @token_required
    def get(self, current_user):
        try:
            word =  request.args.get("search")
            limit_ =  request.args.get("limit")
            offset_ =  request.args.get("offset")
            if word:
                project = db.session.query(Project).filter(Project.name.contains(word) | Project.description.contains(word)).all()
                return get_project_list(project, "search")
            elif offset_ and limit_:
                project = db.session.query(Project).limit(limit_).offset(offset_)
                return get_project_list(project)
            else:
                project = db.session.query(Project).all()
                return get_project_list(project)
        except:
            return {"msg":'Server Error'}, 500

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

        return {'msg':'Project is deleted'}

@namespace.route("/api/projects/<projectId>/upload")
class Upload(Resource):
    @namespace.doc(description='Upload user stories file to database')
    @token_required
    def put(self, current_user, projectId):
        try:
            if 'user_stories' not in request.files:
                return {"msg": "no file found"}, 404
            user_stories = request.files.get('user_stories')
            if user_stories.filename == "":
                return {"msg": "no file found"}, 400
            if user_stories and allowed_file(user_stories.filename):
                filename =  secure_filename(user_stories.filename)
                project = db.session.query(Project).filter(Project.id==projectId).first()
                if project:
                    project.user_stories = os.path.join(app.config['UPLOAD_URL'], filename)
                    db.session.commit()
                    user_stories.save(os.path.join(app.config['UPLOAD_URL'], filename))
                    return {"msg": "file succesfully uploaded"}, 200
                else:
                    return {'msg':'Project does not exist'}, 404
            else:
                return {"msg": "allowed file types are txt, pdf, png, jpg, jpeg"}, 400
        except Exception as e:
            if e.code == 413:
                return {"msg":'file cannot be more than 1mb'}, 413
            else:
                return {"msg":'Server Error'}, 500

