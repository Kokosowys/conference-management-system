#!/usr/bin/env python
import os
import unittest
import json
import base64
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from api import app, db, Person, Article, Attachment

def getAuthHeader(name, password='dummy'):
    authStr = "{}:{}".format(name, password)
    authEnc = base64.b64encode(authStr)
    return {"Authorization": "Basic %s" % authEnc}

class TestCase(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.sqlite'
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def createLoginGetToken(self):
        personPostData = {'name' : 'John',
        'password' : 'pass'}
        personAuthHeader = getAuthHeader(personPostData['name'],
            personPostData['password'])

        resp = self.app.post('/api/people',
            data=json.dumps(personPostData),
            content_type='application/json')

        resp = self.app.get('/api/token/generate',
                headers=personAuthHeader)

        gotData = json.loads(resp.data)
        return gotData


    def test_addPersonDataCorrect(self):
        personPostData = {'name' : 'John',
        'surname' : 'Mayer',
        'sex' : 'M',
        'age' : 50,
        'academicDegree' : 'PhD',
        'password' : 'pass'}

        resp = self.app.post('/api/people',
            data=json.dumps(personPostData),
            content_type='application/json')

        self.assertEqual(resp.status_code, 201)

        gotData = json.loads(resp.data)
        self.assertEqual(gotData['name'], personPostData['name'])
        self.assertEqual(type(gotData['personId']), int)

        p = Person.query.get(gotData['personId'])
        self.assertEqual(p.name, personPostData['name'])
        self.assertEqual(p.surname, personPostData['surname'])
        self.assertEqual(p.sex, personPostData['sex'])
        self.assertEqual(p.age, personPostData['age'])
        self.assertEqual(p.academicDegree, personPostData['academicDegree'])

    def test_addPersonNoNameNoPassError(self):
        personPostData = {'name' : 'John',
        'surname' : 'Mayer',
        'sex' : 'M',
        'age' : 50,
        'academicDegree' : 'PhD',
        'password' : 'pass'}
        personPostDataNoName = personPostData.copy()
        personPostDataNoName.pop('name')
        personPostDataNoPass = personPostData.copy()
        personPostDataNoPass.pop('password')

        resp = self.app.post('/api/people',
            data=json.dumps(personPostDataNoName),
            content_type='application/json')

        self.assertEqual(resp.status_code, 400)

        resp = self.app.post('/api/people',
            data=json.dumps(personPostDataNoPass),
            content_type='application/json')

        self.assertEqual(resp.status_code, 400)

    def test_addPersonDuplicateError(self):
        personPostData = {'name' : 'John',
        'surname' : 'Mayer',
        'sex' : 'M',
        'age' : 50,
        'academicDegree' : 'PhD',
        'password' : 'pass'}

        resp = self.app.post('/api/people',
            data=json.dumps(personPostData),
            content_type='application/json')

        self.assertEqual(resp.status_code, 201)

        resp = self.app.post('/api/people',
            data=json.dumps(personPostData),
            content_type='application/json')

        self.assertEqual(resp.status_code, 400)

    def test_addPersonToShortToLongName(self):
        pass

    def test_addPersonToShortToLongPassword(self):
        pass

    def test_addPersonToShortToLongSex(self):
        pass

    def test_addPersonNotValidToSmallToBigAge(self):
        pass

    def test_addPersonToShortToLongAcademicDegree(self):
        pass

    def test_generateAndValidTokenStatusOK(self):
        personPostData = {'name' : 'John',
        'password' : 'pass'}
        personAuthHeader = getAuthHeader(personPostData['name'],
            personPostData['password'])

        resp = self.app.post('/api/people',
            data=json.dumps(personPostData),
            content_type='application/json')
        self.assertEqual(resp.status_code, 201)

        gotData = json.loads(resp.data)
        personId = gotData['personId']

        resp = self.app.get('/api/token/generate',
            headers=personAuthHeader)
        self.assertEqual(resp.status_code, 200)

        gotData = json.loads(resp.data)
        personIdGen = gotData['personId']
        token = gotData['token']

        self.assertEqual(personIdGen, personId)

        resp = self.app.get('/api/token/validate?token={}'.format(token))
        self.assertEqual(resp.status_code, 200)
        gotData = json.loads(resp.data)
        personIdValid = gotData['personId']
        self.assertEqual(personIdValid, personId)

    def test_generateTokenNotAuthErr(self):
        pass

    def test_validTokenWrongToken(self):
        pass

    def test_getPeoplePrintAll(self):
        pass

    def test_getPersonNotExistError(self):
        pass

    def test_getPersonDataCorrect(self):
        pass

    def test_addArticleDataCorrect(self):
        pass

    def test_addArticleNameMissingError(self):
        pass

    def test_addArticleToShortToLongName(self):
        pass

    def test_addArticleToShortToLongTheme(self):
        pass

    def test_addArticleToShortToLongLabel(self):
        pass

    def test_addArticleToShortToLongDescription(self):
        pass

    def test_getArticleDataCorrect(self):
        pass

    def test_getArticleNotExistError(self):
        pass

    def test_getArticleListAllAttachments(self):
        pass

    def test_getAuthorsArticlesFromOnlyOneAuthor(self):
        pass

    def test_getAuthorsArticlesNoArticlesError(self):
        pass

    def test_addAttachmentDataCorrect(self):
        pass

    def test_addAttachmentArticleNotExists(self):
        pass

    def test_addAttchmentAuthorOnly(self):
        pass

    def test_addAttchmentNotAllowedExtError(self):
        pass

    def test_getAttachmentDataCorrect(self):
        pass

    def test_getAttachmentNotExists(self):
        pass


if __name__ == '__main__':
    unittest.main()