#!/usr/bin/env python

import os
import shutil
import unittest
import json
import io
import base64
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from coverage import coverage
cov = coverage(branch=True, omit=['/home/rafszt/Envs/confmansys/*', 'test.py'])
cov.start()
from api import app, db, Person, Article, Attachment

TEST_UPLOAD_DIR = 'testuploads/'


def getAuthHeader(name, password='dummy'):
    authStr = "{}:{}".format(name, password)
    authEnc = base64.b64encode(authStr)
    return {"Authorization": "Basic %s" % authEnc}

def listOfUploadedFiles():
    return os.listdir(TEST_UPLOAD_DIR)

class TestCase(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.sqlite'
        app.config['UPLOAD_FOLDER'] = TEST_UPLOAD_DIR
        os.makedirs(TEST_UPLOAD_DIR)
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        shutil.rmtree(TEST_UPLOAD_DIR)

    def registerPersonGetAuth(self, personPostData):
        personAuthHeader = getAuthHeader(personPostData['name'],
            personPostData['password'])

        resp = self.app.post('/api/people',
            data=json.dumps(personPostData),
            content_type='application/json')

        resp = self.app.get('/api/token/generate',
                headers=personAuthHeader)

        gotData = json.loads(resp.data)
        auth = getAuthHeader(gotData['token'])
        return auth

    def createPersonFromNameGetAuth(self, name="John"):
        personPostData = {'name' : name,
        'password' : 'password'}
        return self.registerPersonGetAuth(personPostData)

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

    def test_generateTokenNotAuthErr(self):
        resp = self.app.get('/api/token/generate')
        self.assertEqual(resp.status_code, 401)

    def test_validTokenWrongToken(self):
        token = 'randomValue'
        resp = self.app.get('/api/token/validate?token={}'.format(token))
        self.assertEqual(resp.status_code, 403)

        gotData = json.loads(resp.data)
        self.assertEqual(gotData['tokenValidation'], False)

    def test_getPeoplePrintAll(self):
        expectedPeopleNames = ['Anna',
        'Maria', 'Michal', 'Olek', 'Daria',
        'Piotr', 'Tomasz', 'Rafal', 'Renata',
        'Mateusz', 'Kazimiera']
        expectedPeopleNames.sort()

        resp = self.app.get('/api/people')
        self.assertEqual(resp.status_code, 401)

        auth = self.createPersonFromNameGetAuth(name=expectedPeopleNames[0])
        resp = self.app.get('/api/people',
            headers=auth)

        self.assertEqual(resp.status_code, 200)
        gotData = json.loads(resp.data)

        self.assertEqual(len(gotData), 1)

        for i in range (1, len(expectedPeopleNames)):
            self.createPersonFromNameGetAuth(name=expectedPeopleNames[i])

        resp = self.app.get('/api/people',
            headers=auth)
        gotData = json.loads(resp.data)
        gotNames = [p['name'] for p in gotData]
        gotNames.sort()
        self.assertEqual(gotNames, expectedPeopleNames)


    def test_getPersonExistNotExistError(self):
        validId = 1
        invalidId = 2
        auth = self.createPersonFromNameGetAuth()

        resp = self.app.get('/api/people/{}'.format(validId),
            headers=auth)
        self.assertEqual(resp.status_code, 200)

        resp = self.app.get('/api/people/{}'.format(invalidId),
            headers=auth)
        self.assertEqual(resp.status_code, 400)

        gotData = json.loads(resp.data)
        self.assertTrue(str(invalidId) in gotData['Error'])


    def test_getPersonDataCorrect(self):
        personPostData = {'name' : 'John',
        'surname' : 'Mayer',
        'sex' : 'M',
        'age' : 50,
        'academicDegree' : 'PhD',
        'password' : 'password'}
        personId = 1

        auth = self.registerPersonGetAuth(personPostData)
        resp = self.app.get('/api/people/{}'.format(personId),
            headers=auth)
        self.assertEqual(resp.status_code, 200)

        gotData = json.loads(resp.data)
        self.assertEqual(gotData['name'], personPostData['name'])
        self.assertEqual(gotData['surname'], personPostData['surname'])
        self.assertEqual(gotData['sex'], personPostData['sex'])
        self.assertEqual(gotData['age'], personPostData['age'])
        self.assertEqual(gotData['academicDegree'], personPostData['academicDegree'])

    def test_addArticleDataCorrect(self):
        articlePostData = {'name' : 'Elephants ethernal life',
        'theme' : 'mythology',
        'label' : 'historical',
        'description' : 'Short introduction into elephants ethernal life',
        'text' : 'Following document is constructed as follows: 1/begin 2/end'}
        auth = self.createPersonFromNameGetAuth()

        resp = self.app.post('/api/articles',
            data=json.dumps(articlePostData),
            headers=auth,
            content_type='application/json')

        self.assertEqual(resp.status_code, 201)


    def test_addArticleNameMissingError(self):
        articlePostDataNoName = {'theme' : 'mythology',
        'label' : 'historical',
        'description' : 'Short introduction into elephants ethernal life',
        'text' : 'Following document is constructed as follows: 1/begin 2/end'}
        auth = self.createPersonFromNameGetAuth()

        resp = self.app.post('/api/articles',
            data=json.dumps(articlePostDataNoName),
            headers=auth,
            content_type='application/json')
        self.assertEqual(resp.status_code, 400)

        gotData = json.loads(resp.data)
        self.assertTrue('Missing name' in gotData['Error'])


    def test_addArticleToShortToLongName(self):
        nameMinLen = Article.const()['nameMinLen']
        nameMaxLen = Article.const()['nameMaxLen']
        nameToShortLen = nameMinLen - 1
        nameToLongLen = nameMaxLen + 1

        articleToShortName = {'name' : 'a'*nameToShortLen}
        articleToLongName = {'name' : 'a'*nameToLongLen}
        articleMinName = {'name' : 'a'*nameMinLen}
        articleMaxName = {'name' : 'a'*nameMaxLen}

        auth = self.createPersonFromNameGetAuth()

        resp = self.app.post('/api/articles',
            data=json.dumps(articleToShortName),
            headers=auth,
            content_type='application/json')

        self.assertEqual(resp.status_code, 400)
        self.assertTrue("name length" in resp.data)

        resp = self.app.post('/api/articles',
            data=json.dumps(articleToLongName),
            headers=auth,
            content_type='application/json')

        self.assertEqual(resp.status_code, 400)
        self.assertTrue("name length" in resp.data)

        resp = self.app.post('/api/articles',
            data=json.dumps(articleMinName),
            headers=auth,
            content_type='application/json')

        self.assertEqual(resp.status_code, 201)

        resp = self.app.post('/api/articles',
            data=json.dumps(articleMaxName),
            headers=auth,
            content_type='application/json')

        self.assertEqual(resp.status_code, 201)

    def test_addArticleToShortToLongTheme(self):
        themeMinLen = Article.const()['themeMinLen']
        themeMaxLen = Article.const()['themeMaxLen']
        themeToShortLen = themeMinLen - 1
        themeToLongLen = themeMaxLen + 1

        articleToShorttheme = {'name' : 'Elephants ethernal life',
        'theme' : 'a'*themeToShortLen}
        articleToLongtheme = {'name' : 'Elephants ethernlife',
        'theme' : 'a'*themeToLongLen}
        articleMintheme = {'name' : 'Elephants ethernal life',
        'theme' : 'a'*themeMinLen}
        articleMaxtheme = {'name' : 'Elephants ethernal life',
        'theme' : 'a'*themeMaxLen}

        auth = self.createPersonFromNameGetAuth()

        resp = self.app.post('/api/articles',
            data=json.dumps(articleToShorttheme),
            headers=auth,
            content_type='application/json')

        self.assertEqual(resp.status_code, 400)
        self.assertTrue("theme length" in resp.data)

        resp = self.app.post('/api/articles',
            data=json.dumps(articleToLongtheme),
            headers=auth,
            content_type='application/json')

        self.assertEqual(resp.status_code, 400)
        self.assertTrue("theme length" in resp.data)

        resp = self.app.post('/api/articles',
            data=json.dumps(articleMintheme),
            headers=auth,
            content_type='application/json')

        self.assertEqual(resp.status_code, 201)

        resp = self.app.post('/api/articles',
            data=json.dumps(articleMaxtheme),
            headers=auth,
            content_type='application/json')

        self.assertEqual(resp.status_code, 201)


    def test_addArticleToShortToLongLabel(self):
        labelMinLen = Article.const()['labelMinLen']
        labelMaxLen = Article.const()['labelMaxLen']
        labelToShortLen = labelMinLen - 1
        labelToLongLen = labelMaxLen + 1

        articleToShortlabel = {'name' : 'Elephants ethernal life',
        'label' : 'a'*labelToShortLen}
        articleToLonglabel = {'name' : 'Elephants ethernlife',
        'label' : 'a'*labelToLongLen}
        articleMinlabel = {'name' : 'Elephants ethernal life',
        'label' : 'a'*labelMinLen}
        articleMaxlabel = {'name' : 'Elephants ethernal life',
        'label' : 'a'*labelMaxLen}

        auth = self.createPersonFromNameGetAuth()

        resp = self.app.post('/api/articles',
            data=json.dumps(articleToShortlabel),
            headers=auth,
            content_type='application/json')

        self.assertEqual(resp.status_code, 400)
        self.assertTrue("label length" in resp.data)

        resp = self.app.post('/api/articles',
            data=json.dumps(articleToLonglabel),
            headers=auth,
            content_type='application/json')

        self.assertEqual(resp.status_code, 400)
        self.assertTrue("label length" in resp.data)

        resp = self.app.post('/api/articles',
            data=json.dumps(articleMinlabel),
            headers=auth,
            content_type='application/json')

        self.assertEqual(resp.status_code, 201)

        resp = self.app.post('/api/articles',
            data=json.dumps(articleMaxlabel),
            headers=auth,
            content_type='application/json')

        self.assertEqual(resp.status_code, 201)

        self.assertEqual(resp.status_code, 201)

    def test_addArticleToLongDescription(self):
        descriptionMaxLen = Article.const()['descriptionMaxLen']
        descriptionToLongLen = descriptionMaxLen + 1

        articleToLongdescription = {'name' : 'Elephants ethernlife',
        'description' : 'a'*descriptionToLongLen}
        articleMaxdescription = {'name' : 'Elephants ethernal life',
        'description' : 'a'*descriptionMaxLen}

        auth = self.createPersonFromNameGetAuth()

        resp = self.app.post('/api/articles',
            data=json.dumps(articleToLongdescription),
            headers=auth,
            content_type='application/json')

        self.assertEqual(resp.status_code, 400)
        self.assertTrue("description length" in resp.data)

        resp = self.app.post('/api/articles',
            data=json.dumps(articleMaxdescription),
            headers=auth,
            content_type='application/json')

        self.assertEqual(resp.status_code, 201)

    def test_addArticleToLongText(self):
        textMaxLen = Article.const()['textMaxLen']
        textToLongLen = textMaxLen + 1

        articleToLongtext = {'name' : 'Elephants ethernlife',
        'text' : 'a'*textToLongLen}
        articleMaxtext = {'name' : 'Elephants ethernal life',
        'text' : 'a'*textMaxLen}

        auth = self.createPersonFromNameGetAuth()

        resp = self.app.post('/api/articles',
            data=json.dumps(articleToLongtext),
            headers=auth,
            content_type='application/json')

        self.assertEqual(resp.status_code, 400)
        self.assertTrue("text length" in resp.data)

        resp = self.app.post('/api/articles',
            data=json.dumps(articleMaxtext),
            headers=auth,
            content_type='application/json')

    def test_getArticleDataCorrect(self):
        articlePostData = {'name' : 'Elephants ethernal life',
        'theme' : 'mythology',
        'label' : 'historical',
        'description' : 'Short introduction into elephants ethernal life',
        'text' : 'Following document is constructed as follows: 1/begin 2/end'}
        auth = self.createPersonFromNameGetAuth()

        resp = self.app.post('/api/articles',
            data=json.dumps(articlePostData),
            headers=auth,
            content_type='application/json')
        self.assertEqual(resp.status_code, 201)

        gotData = json.loads(resp.data)
        articleId = gotData['articleId']
        resp = self.app.get('/api/articles/{}'.format(articleId),
            headers=auth)
        self.assertEqual(resp.status_code, 200)

        gotData = json.loads(resp.data)
        self.assertEqual(gotData['name'], articlePostData['name'])
        self.assertEqual(gotData['theme'], articlePostData['theme'])
        self.assertEqual(gotData['label'], articlePostData['label'])
        self.assertEqual(gotData['description'], articlePostData['description'])
        self.assertEqual(gotData['text'], articlePostData['text'])


    def test_getArticleNotExistError(self):
        articleId = 1
        auth = self.createPersonFromNameGetAuth()

        resp = self.app.get('/api/articles/{}'.format(articleId),
            headers=auth)
        self.assertEqual(resp.status_code, 400)

        gotData = json.loads(resp.data)
        self.assertEqual("Article with id {} not exists".format(articleId),
            gotData['Error'])

    def test_getAuthorsArticlesFromOnlyOneAuthor(self):
        articleDataOne = {'name' : 'Article 1',
        'theme' : 'mythology',
        'label' : 'historical',
        'description' : 'Short introduction into elephants ethernal life',
        'text' : 'Following document is constructed as follows: 1/begin 2/end'}
        articleDataTwo = articleDataOne.copy()
        articleDataTwo['name'] = 'Article 2'

        authorOneAuth = self.createPersonFromNameGetAuth(name="Author1")
        authorOneId = 1
        authorTwoAuth = self.createPersonFromNameGetAuth(name="Author2")

        resp = self.app.post('/api/articles',
            data=json.dumps(articleDataOne),
            headers=authorOneAuth,
            content_type='application/json')
        self.assertEqual(resp.status_code, 201)

        resp = self.app.post('/api/articles',
            data=json.dumps(articleDataTwo),
            headers=authorTwoAuth,
            content_type='application/json')
        self.assertEqual(resp.status_code, 201)

        resp = self.app.get('/api/articles/author/{}'.format(authorOneId),
            headers=authorOneAuth)
        self.assertEqual(resp.status_code, 200)

        gotData = json.loads(resp.data)
        self.assertEqual(len(gotData), 1)
        self.assertEqual(gotData.pop()['name'], articleDataOne['name'])

    def test_addAttachmentDataCorrect(self):
        fileData =dict(file=(io.BytesIO(b"this is a test"), 'test.pdf'))
        articlePostData = {'name' : 'Elephants ethernal life'}

        auth = self.createPersonFromNameGetAuth()
        resp = self.app.post('/api/articles',
            data=json.dumps(articlePostData),
            headers=auth,
            content_type='application/json')
        self.assertEqual(resp.status_code, 201)

        gotData = json.loads(resp.data)
        articleId = gotData['articleId']

        resp = self.app.post('/api/articles/{}/attachments'.format(articleId),
            headers=auth,
            data=fileData,
            content_type='multipart/form-data',
            follow_redirects=True)
        self.assertEqual(resp.status_code, 201)
        self.assertIn(fileData['file'][1], listOfUploadedFiles())

    def test_addAttachmentArticleNotExists(self):
        fileData =dict(file=(io.BytesIO(b"this is a test"), 'test.pdf'))
        articleId = 1
        auth = self.createPersonFromNameGetAuth()

        resp = self.app.post('/api/articles/{}/attachments'.format(articleId),
            headers=auth,
            data=fileData,
            content_type='multipart/form-data',
            follow_redirects=True)
        self.assertEqual(resp.status_code, 400)

        gotData = json.loads(resp.data)
        self.assertEqual("Article with id {} not exists".format(articleId),
            gotData['Error'])

    def test_addAttchmentAuthorOnly(self):
        fileData =dict(file=(io.BytesIO(b"this is a test"), 'test.pdf'))
        articlePostData = {'name' : 'Elephants ethernal life'}

        authorOneAuth = self.createPersonFromNameGetAuth(name="Author1")
        authorTwoAuth = self.createPersonFromNameGetAuth(name="Author2")

        resp = self.app.post('/api/articles',
            data=json.dumps(articlePostData),
            headers=authorOneAuth,
            content_type='application/json')
        self.assertEqual(resp.status_code, 201)

        gotData = json.loads(resp.data)
        articleId = gotData['articleId']
        resp = self.app.post('/api/articles/{}/attachments'.format(articleId),
            headers=authorTwoAuth,
            data=fileData,
            content_type='multipart/form-data',
            follow_redirects=True)
        self.assertEqual(resp.status_code, 403)

        gotData = json.loads(resp.data)
        self.assertIn('Only author of that article', gotData['Error'])

    def test_addAttchmentNotAllowedExtError(self):
        fileData =dict(file=(io.BytesIO(b"this is a test"), 'test.wrongExt'))
        articlePostData = {'name' : 'Elephants ethernal life'}

        auth = self.createPersonFromNameGetAuth()
        resp = self.app.post('/api/articles',
            data=json.dumps(articlePostData),
            headers=auth,
            content_type='application/json')
        self.assertEqual(resp.status_code, 201)

        gotData = json.loads(resp.data)
        articleId = gotData['articleId']
        resp = self.app.post('/api/articles/{}/attachments'.format(articleId),
            headers=auth,
            data=fileData,
            content_type='multipart/form-data',
            follow_redirects=True)
        self.assertEqual(resp.status_code, 400)

        gotData = json.loads(resp.data)
        self.assertIn('Wrong extention of file {}'.format(fileData['file'][1]),
            gotData['Error'])

    def test_getAttachmentDataCorrect(self):
        fileData =dict(file=(io.BytesIO(b"this is a test"), 'test.pdf'))
        articlePostData = {'name' : 'Elephants ethernal life'}

        auth = self.createPersonFromNameGetAuth()
        resp = self.app.post('/api/articles',
            data=json.dumps(articlePostData),
            headers=auth,
            content_type='application/json')
        self.assertEqual(resp.status_code, 201)

        gotData = json.loads(resp.data)
        articleId = gotData['articleId']
        resp = self.app.post('/api/articles/{}/attachments'.format(articleId),
            headers=auth,
            data=fileData,
            content_type='multipart/form-data',
            follow_redirects=True)
        self.assertEqual(resp.status_code, 201)

        gotData = json.loads(resp.data)
        attachmentId = gotData['attachmentId']
        resp = self.app.get('/api/articles/attachments/{}'.format(attachmentId),
            headers=auth)
        self.assertEqual(resp.status_code, 200)

    def test_getAttachmentNotExists(self):
        attachmentId = 1
        auth = self.createPersonFromNameGetAuth()
        resp = self.app.get('/api/articles/attachments/{}'.format(attachmentId),
            headers=auth)
        self.assertEqual(resp.status_code, 400)

        gotData = json.loads(resp.data)
        self.assertEqual(gotData['Error'], 'Attachment with id {} \
            not exists'.format(attachmentId))


    def test_getArticleListAllAttachments(self):
        fileName = 'test.pdf'
        fileData =dict(file=(io.BytesIO(b"this is a test"), fileName))
        articlePostData = {'name' : 'Elephants ethernal life'}

        auth = self.createPersonFromNameGetAuth()
        resp = self.app.post('/api/articles',
            data=json.dumps(articlePostData),
            headers=auth,
            content_type='application/json')
        self.assertEqual(resp.status_code, 201)

        gotData = json.loads(resp.data)
        articleId = gotData['articleId']
        resp = self.app.post('/api/articles/{}/attachments'.format(articleId),
            headers=auth,
            data=fileData,
            content_type='multipart/form-data',
            follow_redirects=True)
        self.assertEqual(resp.status_code, 201)

        resp = self.app.get('/api/articles/{}'.format(articleId),
            headers=auth)
        self.assertEqual(resp.status_code, 200)

        gotData = json.loads(resp.data)
        gotAttachmentsList = gotData['attachments']
        self.assertEqual(len(gotAttachmentsList), 1)
        self.assertEqual(gotAttachmentsList.pop()['name'], fileName)


if __name__ == '__main__':
    try:
        print 'tests start'
        unittest.main()
        print 'test end'
    except:
        pass
    cov.stop()
    cov.save()
    print "\n\nCoverage Report:\n"
    cov.report()
    cov.html_report(directory='tmp/coverage')
    cov.erase()