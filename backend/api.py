#!/usr/bin/env python
import os
import json
from collections import namedtuple
from functools import partial

from flask import Flask, current_app, abort, request, jsonify, g, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_httpauth import HTTPBasicAuth
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from flask_principal import (AnonymousIdentity, Identity,
    identity_changed, identity_loaded, Permission, Principal,
    RoleNeed, ActionNeed, UserNeed)

# initialization
app = Flask(__name__)
app.config['SECRET_KEY'] = '!haselko'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

# extensions
db = SQLAlchemy(app)
auth = HTTPBasicAuth()
principals = Principal(app, skip_static=True)

# Model classes (DAO)
class Person(db.Model):
    __tablename__ = 'person'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), index=True)
    surname = db.Column(db.String(32))
    sex = db.Column(db.String(16))
    age = db.Column(db.Integer)
    academicDegree = db.Column(db.String(8))
    password_hash = db.Column(db.String(64))
    roles = db.Column(db.String(64))


    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=600):
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    def get_roles(self):
        if not self.roles:
            self.roles = json.dumps([])
        return json.loads(self.roles)

    def add_role(self, newRoleName):
        rolesTab = self.get_roles()
        if newRoleName not in rolesTab:
            rolesTab.append(newRoleName)
            self.roles = json.dumps(rolesTab)

    def del_role(self, roleName):
        rolesTab = self.get_roles()
        if roleName in rolesTab:
            rolesTab.remove(roleName)
            self.roles = json.dumps(rolesTab)

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None    # valid token, but expired
        except BadSignature:
            return None    # invalid token
        person = Person.query.get(data['id'])
        return person


class Article(db.Model):
    __tablename__ = 'article'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), index=True)
    theme = db.Column(db.String(32))
    label = db.Column(db.String(32))
    description = db.Column(db.String(500))
    text = db.Column(db.String(1024))
    personId = db.Column(
        db.Integer,
        db.ForeignKey('person.id', ondelete='CASCADE'),
        nullable=False,
    )
    person = relationship('Person', backref='articles')
    # attchments are assigned by articleId in attchment obj

class Attachment(db.Model):
    __tablename__ = 'attachment'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), index=True)
    articleId = db.Column(
        db.Integer,
        db.ForeignKey('article.id', ondelete='CASCADE'),
        nullable=False,
    )
    article = relationship('Article', backref='attachments')


# Roles security setup - needs
articleNeed = namedtuple('article', ['method', 'value'])
editArticleNeed = partial(articleNeed, 'edit')
apps_needs = [articleNeed, editArticleNeed]

# Roles security setup - Permissions
class EditArticlePermission(Permission):
    def __init__(self, article_id):
        need = EditArticleNeed(unicode(article_id))
        super(EditArticlePermission, self).__init__(need)

# Roles security setup - methods
@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
    print 'on_identity_loaded: identity: {}'.format(identity)
    person = g.person

    if hasattr(person, 'id'):
        identity.provides.add(UserNeed(person.id))

    if hasattr(person, 'roles'):
        for role in person.get_roles():
            identity.provides.add(RoleNeed(role))

    # if hasattr(person, 'posts'):
    #     for post in person.posts:
    #         identity.provides.add(EditArticleNeed(unicode(post.id)))

    identity.person = person

# Authentication
@auth.verify_password
def verify_password(name_or_token, password):
    # first try to authenticate by token
    person = Person.verify_auth_token(name_or_token)
    if not person:
        # try to authenticate with name/password
        person = Person.query.filter_by(name=name_or_token).first()
        if not person or not person.verify_password(password):
            return False
    g.person = person
    identity_changed.send(current_app._get_current_object(),
        identity=Identity(person.id))
    return True


# File transfer handling
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


# REST API
@app.route('/api/token')
@auth.login_required
def getAuthToken():
    token = g.person.generate_auth_token(600)
    return jsonify({'token': token.decode('ascii'), 'duration': 600})


@app.route('/api/people', methods=['POST'])
def newPerson():
    name = request.json.get('name')
    password = request.json.get('password')
    surname = request.json.get('surname')
    sex = request.json.get('sex')
    age = request.json.get('age')
    academicDegree = request.json.get('academicDegree')
    if name is None or password is None:
        abort(400)    # missing arguments
    if Person.query.filter_by(name=name).first() is not None:
        abort(400)    # existing person
    person = Person(name=name, surname=surname, sex=sex, age=age,
        academicDegree=academicDegree)
    person.hash_password(password)
    db.session.add(person)
    db.session.commit()
    return (jsonify({'name': person.name, 'personId': person.id}),
        201,
        {'Location': url_for('getPerson', id=person.id, _external=True)})


@app.route('/api/people/<int:id>')
@auth.login_required
def getPerson(id):
    person = Person.query.get(id)
    if not person:
        abort(400)
    return jsonify({'name': person.name,
        'surname': person.surname,
        'sex': person.sex,
        'age': person.age,
        'academicDegree': person.academicDegree})

@app.route('/api/articles', methods=['POST'])
@auth.login_required
def newArticle():
    name = request.json.get('name')
    theme = request.json.get('theme')
    label = request.json.get('label')
    description = request.json.get('description')
    text = request.json.get('text')
    if name is None:
        abort(400)

    loggedPerson = g.person
    article = Article(name=name, theme=theme, label=label,
        description=description, text=text, person=loggedPerson)
    db.session.add(article)
    db.session.commit()
    return (jsonify({'articleId':article.id,
        'name':article.name}),
        201,
        {'Location': url_for('getArticle', id=article.id, _external=True)})

@app.route('/api/articles/<int:id>', methods=['GET'])
@auth.login_required
def getArticle(id):
    article = Article.query.get(id)
    if not article:
        abort(400)
    return jsonify({'name' : article.name,
        'theme' : article.theme,
        'label' : article.label,
        'description' : article.description,
        'text' : article.text,
        'attachments' : article.attachments})


@app.route('/api/articles/author/<int:id>', methods=['GET'])
def getAuthorsArticles(id):
    pass

@app.route('/api/articles/attachments', methods=['POST'])
def newAttachment():
    file = request.files['file']
    articleId = request.files['articleId']

    if not file or not allowed_file(file.filename):
        # TODO - check if article present
        abort(400)

    filename = file.filename
    filenameSafe = secure_filename(filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filenameSafe))

    #TODO - add entry into db: id and safe_name

    return (jsonify({'name': attachment.name, 'personId': attachment.id}),
        201,
        {'Location': url_for('getAttachment', id=attachment.id, _external=True)})


@app.route('/api/articles/attachments/<int:attachmentId>', methods=['GET'])
def getAttachment(attachmentId):
    filename = "" #TODO - fetch  filename from db
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


@app.route('/api/resource')
@auth.login_required
def get_resource():
    return jsonify({'data': 'Hello, %s!' % g.person.name})


# Server invoke
if __name__ == '__main__':
    if not os.path.exists('db.sqlite'):
        db.create_all()
    app.run(debug=True, host='0.0.0.0')
