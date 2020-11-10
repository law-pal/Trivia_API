import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category, DB_HOST, DB_NAME, DB_PASSWORD, DB_USER


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path =  "postgresql+psycopg2://{}:{}@{}/{}".format(DB_USER, DB_PASSWORD, DB_HOST, DB_NAME)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    #test for questions pagination and 404 error = OK
    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['categories']))

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not Found')

    #test for get categories and 404 invalid category = OK
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])

    def test_404_sent_requesting_invalid_category(self):
        res = self.client().get('/category/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not Found')

    #test for deleting question and error 422 = OK
    def test_delete_question(self):
        question = Question(question='test question', answer='test answer', difficulty=1, category=1)
        question.insert()
        question_id = question.id

        res = self.client().delete(f'/questions/{question_id}')
        data = json.loads(res.data)
        question = Question.query.filter(Question.id == question.id).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['response'], True)
        self.assertEqual(data['deleted'], str(question_id))
        self.assertEqual(question, None)

    def test_unprocessable_entity(self):
        res = self.client().delete('/questions/eeee')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable')

    # test for create a new question and error 422
    def test_create_new_question(self):
        test_question = {
            'question': 'test question',
            'answer': 'test answer',
            'difficulty': 1,
            'category': 1 
        }
        #test for question before
        questions_before = Question.query.all()
        res = self.client().post('/questions', json=test_question)
        data = json.loads(res.data)
        #test for questions after
        questions_after = Question.query.all()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        #test for length of questions before and after
        self.assertTrue(len(questions_after) - len(questions_before) == 1)

    #test error 422
    def test_unprocessable_create_question(self):
        test_question = {
            'question': 'test question',
            'answer': 'test answer',
            'difficulty': 1
        }

        res = self.client().post('questions', json=test_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable')

    #test for searching questions and error 404 = OK
    def test_search_term(self):
        test_search = {'searchTerm': 'p'}
        res = self.client().post('/questions/search', json=test_search)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIsNotNone(data['questions'])
        self.assertIsNotNone(data['total_questions'])

    def test_404_search_term(self):
        test_search = {'searchTerm': ''}
        res = self.client().post('questions/search', json=test_search)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not Found')

    #test to get questions by category and error 404 = OK 
    def test_get_questions_by_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['response'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])

    def test_404_get_questions_by_category(self):
        res = self.client().post('/categories/@/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not Found')

    #test for quizzes and error 422 =OK
    def test_get_quiz_questions(self):
        test_quiz = {'previous_questions':[],'quiz_category':{'type':'Sports','id': 6}}
        res = self.client().post('/quizzes', json=test_quiz)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

    def test_422_unprocessable_quizzes(self):
        test_quiz = {'previous_questions':[]}
        res = self.client().post('/quizzes', json=test_quiz)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()