import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://postgres:123456@{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)
        self.new_question = {
            'question': 'Is this a test question?',
            'answer': 'Yes',
            'category': 2,
            'difficulty': 4
        }

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
    TODO (DONE)
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])
        self.assertTrue(data['questions'])

    def test_nonexistent_page_404(self):
        res = self.client().get('/questions?page=1234')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 404)
        self.assertTrue(data['message'])

    def test_get_all_six_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertEqual(len(data['categories']), 6)

    def test_add_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['added_question_id'])

    def test_add_question_without_required_fields_400(self):
        res = self.client().post('/questions', json={
            'question': '',
            'answer': '',
            'difficulty': 1,
            'category': 1

        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 400)
        self.assertTrue(data['message'])

    def test_delete_question(self):
        # adds a new question to the database
        # (so there's always something to delete) and then deletes it
        res0 = self.client().post('/questions', json=self.new_question)
        data0 = json.loads(res0.data)

        self.assertEqual(res0.status_code, 200)
        self.assertEqual(data0['success'], True)
        self.assertTrue(data0['added_question_id'])
        question_id = data0['added_question_id']

        res = self.client().delete('/questions/{}'.format(question_id))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted_question_id'], question_id)

    def test_delete_nonexistent_question_404(self):
        res = self.client().delete('/questions/5000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 404)
        self.assertTrue(data['message'])

    def test_search_with_results(self):
        res = self.client().post('questions', json={'searchTerm': 'test'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertEqual(data['search_term'], 'test')
        self.assertTrue(data['results_number'])

    def test_search_without_results(self):
        res = self.client().post('questions', json={
            'searchTerm': 'sthnonexistenttest'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['search_term'], 'sthnonexistenttest')
        self.assertEqual(data['results_number'], 0)

    def test_viewing_by_category(self):
        res = self.client().get('categories/2/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        for question in data['questions']:
            self.assertEqual(question['category'], 2)
        self.assertEqual(data['current_category'], {'id': 2, 'type': 'Art'})

    def test_viewing_by_nonexistent_category_404(self):
        res = self.client().get('categories/85/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 404)
        self.assertTrue(data['message'])

    def test_playing_with_all_categories(self):
        json_data = {'previous_questions': [],
                     'quiz_category': {'id': 0, 'type': 'click'}}
        res = self.client().post('/quizzes',
                                 json=json_data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        self.assertEqual(data['quiz_category'], {'id': 0, 'type': 'click'})
        self.assertEqual(data['previous_questions'], [])

    def test_playing_art(self):
        json_data = {'previous_questions': [],
                     'quiz_category': {'id': 2, 'type': 'Art'}}
        res = self.client().post('/quizzes',
                                 json=json_data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        self.assertEqual(data['quiz_category'], {'id': 2, 'type': 'Art'})
        self.assertEqual(data['previous_questions'], [])
        self.assertEqual(data['question']['category'], 2)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()