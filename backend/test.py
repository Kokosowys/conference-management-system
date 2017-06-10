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
        'password' : 'password'}
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
        'password' : 'password'}

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
        'password' : 'password'}
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


    def test_addPersonToShortToLongName(self):
        nameToShortLen = Person.const()['nameMinLen'] - 1
        nameToLongLen = Person.const()['nameMaxLen'] + 1

        shortNamePost = {'name' : 'a'*nameToShortLen,
        'password' : 'password'}
        longNamePost = {'name' : 'a'*nameToLongLen,
        'password' : 'password'}

        resp = self.app.post('/api/people',
            data=json.dumps(shortNamePost),
            content_type='application/json')

        self.assertEqual(resp.status_code, 400)
        self.assertTrue("Name length" in resp.data)

        resp = self.app.post('/api/people',
            data=json.dumps(longNamePost),
            content_type='application/json')

        self.assertEqual(resp.status_code, 400)
        self.assertTrue("Name length" in resp.data)

    def test_addPersonToShortToLongSurname(self):
        surnameToShortLen = Person.const()['surnameMinLen'] - 1
        surnameToLongLen = Person.const()['surnameMaxLen'] + 1

        shortsurNamePost = {'name' : 'John',
        'surname' : 'a'*surnameToShortLen,
        'password' : 'password'}
        longsurNamePost = {'name' : 'John',
        'surname' : 'a'*surnameToLongLen,
        'password' : 'password'}

        resp = self.app.post('/api/people',
            data=json.dumps(shortsurNamePost),
            content_type='application/json')

        self.assertEqual(resp.status_code, 400)
        self.assertTrue("Surname length" in resp.data)

        resp = self.app.post('/api/people',
            data=json.dumps(longsurNamePost),
            content_type='application/json')

        self.assertEqual(resp.status_code, 400)
        self.assertTrue("Surname length" in resp.data)

    def test_addPersonToShortToLongPassword(self):
        passwordToShortLen = Person.const()['passwordMinLen'] - 1
        passwordToLongLen = Person.const()['passwordMaxLen'] + 1

        shortpasswordPost = {'name' : 'John',
        'password' : 'a'*passwordToShortLen}
        longpasswordPost = {'name' : 'John',
        'password' : 'a'*passwordToLongLen}

        resp = self.app.post('/api/people',
            data=json.dumps(shortpasswordPost),
            content_type='application/json')

        self.assertEqual(resp.status_code, 400)
        self.assertTrue("Password length" in resp.data)

        resp = self.app.post('/api/people',
            data=json.dumps(longpasswordPost),
            content_type='application/json')

        self.assertEqual(resp.status_code, 400)
        self.assertTrue("Password length" in resp.data)

    def test_addPersonToShortToLongSex(self):
        sexMinLen = Person.const()['sexMinLen']
        sexMaxLen = Person.const()['sexMaxLen']
        sexToLongLen = sexMaxLen + 1

        longsexPost = {'name' : 'John',
        'sex' : 'a'*sexToLongLen,
        'password' : 'password'}
        minPost = {'name' : 'John',
        'sex' : 'a'*sexMinLen,
        'password' : 'password'}
        maxPost = {'name' : 'John',
        'sex' : 'a'*sexMaxLen,
        'password' : 'password'}

        resp = self.app.post('/api/people',
            data=json.dumps(longsexPost),
            content_type='application/json')

        self.assertEqual(resp.status_code, 400)
        self.assertTrue("Sex length" in resp.data)

        resp = self.app.post('/api/people',
            data=json.dumps(minPost),
            content_type='application/json')

        self.assertEqual(resp.status_code, 201)

        resp = self.app.post('/api/people',
            data=json.dumps(maxPost),
            content_type='application/json')

        self.assertEqual(resp.status_code, 201)

    def test_addPersonNotValidToSmallToBigAge(self):
        ageMin = Person.const()['ageMin']
        ageMax = Person.const()['ageMax']
        toYoung = ageMin - 1
        toOld = ageMax + 1

        youngPost = {'name' : 'John',
        'age' : toYoung,
        'password' : 'password'}
        oldPost = {'name' : 'John',
        'age' : toOld,
        'password' : 'password'}
        minPost = {'name' : 'John',
        'age' : ageMin,
        'password' : 'password'}
        maxPost = {'name' : 'John',
        'age' : ageMax,
        'password' : 'password'}

        resp = self.app.post('/api/people',
            data=json.dumps(youngPost),
            content_type='application/json')

        self.assertEqual(resp.status_code, 400)
        self.assertTrue("Age must be between" in resp.data)

        resp = self.app.post('/api/people',
            data=json.dumps(oldPost),
            content_type='application/json')

        self.assertEqual(resp.status_code, 400)
        self.assertTrue("Age must be between" in resp.data)

        resp = self.app.post('/api/people',
            data=json.dumps(minPost),
            content_type='application/json')

        self.assertEqual(resp.status_code, 201)

        resp = self.app.post('/api/people',
            data=json.dumps(maxPost),
            content_type='application/json')

        self.assertEqual(resp.status_code, 201)

    def test_addPersonToShortToLongAcademicDegree(self):
        academicDegreeMinLen = Person.const()['academicDegreeMinLen']
        academicDegreeMaxLen = Person.const()['academicDegreeMaxLen']
        academicDegreeToShortLen = academicDegreeMinLen - 1
        academicDegreeToLongLen = academicDegreeMaxLen + 1

        longacademicDegreePost = {'name' : 'John',
        'academicDegree' : 'a'*academicDegreeToLongLen,
        'password' : 'password'}
        minPost = {'name' : 'John',
        'academicDegree' : 'a'*academicDegreeMinLen,
        'password' : 'password'}
        maxPost = {'name' : 'John',
        'academicDegree' : 'a'*academicDegreeMaxLen,
        'password' : 'password'}

        resp = self.app.post('/api/people',
            data=json.dumps(longacademicDegreePost),
            content_type='application/json')

        self.assertEqual(resp.status_code, 400)
        self.assertTrue("AcademicDegree length" in resp.data)

        resp = self.app.post('/api/people',
            data=json.dumps(minPost),
            content_type='application/json')

        self.assertEqual(resp.status_code, 201)

        resp = self.app.post('/api/people',
            data=json.dumps(maxPost),
            content_type='application/json')

        self.assertEqual(resp.status_code, 201)

    def test_generateAndValidTokenStatusOK(self):
        personPostData = {'name' : 'John',
        'password' : 'password'}
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

    @unittest.skip("demonstrating skipping")
    def test_generateTokenNotAuthErr(self):
        pass

    @unittest.skip("demonstrating skipping")
    def test_validTokenWrongToken(self):
        pass

    @unittest.skip("demonstrating skipping")
    def test_getPeoplePrintAll(self):
        pass

    @unittest.skip("demonstrating skipping")
    def test_getPersonNotExistError(self):
        pass

    @unittest.skip("demonstrating skipping")
    def test_getPersonDataCorrect(self):
        pass

    @unittest.skip("demonstrating skipping")
    def test_addArticleDataCorrect(self):
        pass

    @unittest.skip("demonstrating skipping")
    def test_addArticleNameMissingError(self):
        pass

    @unittest.skip("demonstrating skipping")
    def test_addArticleToShortToLongName(self):
        pass

    @unittest.skip("demonstrating skipping")
    def test_addArticleToShortToLongTheme(self):
        pass

    @unittest.skip("demonstrating skipping")
    def test_addArticleToShortToLongLabel(self):
        pass

    @unittest.skip("demonstrating skipping")
    def test_addArticleToShortToLongDescription(self):
        pass

    @unittest.skip("demonstrating skipping")
    def test_getArticleDataCorrect(self):
        pass

    @unittest.skip("demonstrating skipping")
    def test_getArticleNotExistError(self):
        pass

    @unittest.skip("demonstrating skipping")
    def test_getArticleListAllAttachments(self):
        pass

    @unittest.skip("demonstrating skipping")
    def test_getAuthorsArticlesFromOnlyOneAuthor(self):
        pass

    @unittest.skip("demonstrating skipping")
    def test_getAuthorsArticlesNoArticlesError(self):
        pass

    @unittest.skip("demonstrating skipping")
    def test_addAttachmentDataCorrect(self):
        pass

    @unittest.skip("demonstrating skipping")
    def test_addAttachmentArticleNotExists(self):
        pass

    @unittest.skip("demonstrating skipping")
    def test_addAttchmentAuthorOnly(self):
        pass

    @unittest.skip("demonstrating skipping")
    def test_addAttchmentNotAllowedExtError(self):
        pass

    @unittest.skip("demonstrating skipping")
    def test_getAttachmentDataCorrect(self):
        pass

    @unittest.skip("demonstrating skipping")
    def test_getAttachmentNotExists(self):
        pass


if __name__ == '__main__':
    unittest.main()