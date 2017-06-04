#!/usr/bin/env python
import os
import json
from collections import namedtuple
from functools import partial

from flask import Flask, current_app, abort, request, jsonify, g, url_for
from flask_sqlalchemy import SQLAlchemy
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

# extensions
db = SQLAlchemy(app)
auth = HTTPBasicAuth()
principals = Principal(app, skip_static=True)

# Needs
articleNeed = namedtuple('article', ['method', 'value'])
editArticleNeed = partial(articleNeed, 'edit')
apps_needs = [articleNeed, editArticleNeed]

# Permissions
class EditArticlePermission(Permission):
    def __init__(self, article_id):
        need = EditArticleNeed(unicode(article_id))
        super(EditArticlePermission, self).__init__(need)

#Model classes (DAO)
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
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
        user = User.query.get(data['id'])
        return user


@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    identity_changed.send(current_app._get_current_object(),
        identity=Identity(user.id))
    return True

@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
    print 'on_identity_loaded: identity: {}'.format(identity)
    user = g.user

    if hasattr(user, 'id'):
        identity.provides.add(UserNeed(user.id))

    if hasattr(user, 'roles'):
        for role in user.get_roles():
            identity.provides.add(RoleNeed(role))

    # if hasattr(user, 'posts'):
    #     for post in user.posts:
    #         identity.provides.add(EditArticleNeed(unicode(post.id)))

    identity.user = user

@app.route('/api/users', methods=['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        abort(400)    # missing arguments
    if User.query.filter_by(username=username).first() is not None:
        abort(400)    # existing user
    user = User(username=username)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return (jsonify({'username': user.username}), 201,
            {'Location': url_for('get_user', id=user.id, _external=True)})


@app.route('/api/users/<int:id>')
def get_user(id):
    user = User.query.get(id)
    if not user:
        abort(400)
    return jsonify({'username': user.username})


@app.route('/api/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token(600)
    return jsonify({'token': token.decode('ascii'), 'duration': 600})


@app.route('/api/resource')
@auth.login_required
def get_resource():
    return jsonify({'data': 'Hello, %s!' % g.user.username})

if __name__ == '__main__':
    if not os.path.exists('db.sqlite'):
        db.create_all()
    app.run(debug=True, host='0.0.0.0')
