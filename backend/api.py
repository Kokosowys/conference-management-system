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

# contraints
ATTACHMENTS_DIR = '/home/rsztandera/conference-management-system/attachments'

# initialization
app = Flask(__name__)
app.config['SECRET_KEY'] = '!haselko'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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
def verify_password(username_or_token, password):
    # first try to authenticate by token
    person = Person.verify_auth_token(username_or_token)
    if not person:
        # try to authenticate with name/password
        person = Person.query.filter_by(name=username_or_token).first()
        if not person or not person.verify_password(password):
            return False
    g.person = person
    identity_changed.send(current_app._get_current_object(),
        identity=Identity(person.id))
    return True


# REST API
@app.route('/api/users', methods=['POST'])
def new_user():
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
    return (jsonify({'name': person.name}), 201,
            {'Location': url_for('get_user', id=person.id, _external=True)})


@app.route('/api/users/<int:id>')
def get_user(id):
    person = Person.query.get(id)
    if not person:
        abort(400)
    return jsonify({'name': person.name})


@app.route('/api/token')
@auth.login_required
def get_auth_token():
    token = g.person.generate_auth_token(600)
    return jsonify({'token': token.decode('ascii'), 'duration': 600})


@app.route('/api/resource')
@auth.login_required
def get_resource():
    return jsonify({'data': 'Hello, %s!' % g.person.name})

# Server invoke
if __name__ == '__main__':
    if not os.path.exists('db.sqlite'):
        db.create_all()
    app.run(debug=True, host='0.0.0.0')
