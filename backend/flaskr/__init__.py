import os
from flask import Flask, request, abort, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10
def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE
  current_questions = [question.format() for question in selection[start:end]]
  return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs (DONE)
  '''
  cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow (DONE)
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Origin','http://localhost:3000')
    response.headers.add('Access-Control-Allow-Methods','GET,POST,OPTIONS,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response
  '''
  @TODO: 
  Create an endpoint to handle GET requests  (DONE)
  for all available categories.
  '''
  @app.route('/categories')
  # route handler to get categories
  def get_categories():
    categories_dict = {}
    categories = Category.query.all()
    formatted_categories = [category.format() for category in categories]
    for category in formatted_categories:
      categories_dict[category['id']] = category['type']
    return jsonify({'success': True, 'categories': categories_dict}), 200

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

  @app.route('/questions')
  def display_questions():
    categories = Category.query.all()
    formatted_categories = [category.format() for category in categories]
    categories_dict = {} 
    for category in formatted_categories:
      categories_dict[category['id']] = category['type']
    selection = Question.query.all()
    total_questions = len(selection)
   
    if request.args.get('page', 1, type=int) > (
      (total_questions - 1) // QUESTIONS_PER_PAGE) + 1:
        abort(404)
    current_questions = paginate_questions(request, selection)
    current_category = None
    return jsonify({'success': True,
      'categories': categories_dict,
      'questions': current_questions,
      'total_questions': total_questions,
      'current_category': current_category}), 200



  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''

  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    question_to_delete = Question.query.filter(Question.id == question_id).one_or_none()
    if question_to_delete is None:
      abort(404)
    question_to_delete.delete()
    return jsonify({'success': True, 'deleted_question_id': question_id}), 200

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  
  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

  @app.route('/questions', methods=['POST'])
  def add_or_search_question():
    search = request.json.get('searchTerm')
    if search:
      selection = Question.query.filter(
          Question.question.ilike(f'%{search}%'))
      results_number = selection.count()
      current_questions = [question.format() for question in selection]
      return jsonify({'questions': current_questions,'search_term': search,'results_number': results_number}), 200
      
    else:
      question = request.json['question']
      answer = request.json['answer']
      category = request.json['category']
      difficulty = request.json['difficulty']
      # abort with bad request error if any field is missing
      if not difficulty or not category or not answer or not question:
        abort(400)
      new_question = Question(question, answer, category, difficulty)
      new_question.insert()
      return jsonify({'success': True, 'added_question_id': new_question.id}), 200


  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions')
  def display_questions_based_on_category(category_id):
    if category_id > 6 or category_id < 1:
      abort(404)
    selection = Question.query.filter(Question.category == category_id)
    questions_number = selection.count()
    current_questions = paginate_questions(request, selection)
    current_category = Category.query.filter_by(id=category_id).first().format()
    return jsonify({'success': True, 'questions': current_questions, 'current_category': current_category,'questions_number': questions_number}), 200


  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''

  @app.route('/quizzes', methods=['POST'])
  def play_the_quiz():
    category = request.json.get('quiz_category')
    previous_questions = request.json.get('previous_questions')
    if category['id'] == 0:  # id 0 means all categories
      questions_whole = [question.format() for question in Question.query.all()]
      if len(questions_whole) == len(previous_questions):
        return jsonify({'quiz_category': category,'question': None,'previous_questions': previous_questions}), 200
      if len(previous_questions) > 0:  # if there were previous questions
        s = set(previous_questions)
        questions = [question['id'] for question in questions_whole]
        questions_to_choose_from = [x for x in questions if x not in s]
        chosen_question_id = random.choice(questions_to_choose_from)
        current_question = Question.query.filter(
            Question.id == chosen_question_id).one_or_none(
        ).format()  # gets formatted question of that id
        return jsonify({'quiz_category': category, 'question': current_question, 'previous_questions': previous_questions}), 200
      else:
          # if there were no previous questions, we can make it random
          current_question = random.choice(questions_whole)
          return jsonify({'quiz_category': category, 'question': current_question, 'previous_questions': previous_questions}), 200

    else:
      questions_in_category_whole = [question.format() for question in Question.query.filter(Question.category == category['id'])]
      if len(questions_in_category_whole) == len(
        previous_questions):
        return jsonify({'quiz_category': category, 'question': None, 'previous_questions': previous_questions}), 200
      if len(previous_questions) > 0:  # if there were previous questions
          s = set(previous_questions)
          questions_in_this_category = [question['id'] for question in questions_in_category_whole]
          questions_to_choose_from = [
              x for x in questions_in_this_category if x not in s]
          chosen_question_id = random.choice(questions_to_choose_from)
          current_question = Question.query.filter(Question.id == chosen_question_id).one_or_none().format()  # gets formatted question of that id
          return jsonify({'quiz_category': category, 'question': current_question, 'previous_questions': previous_questions}), 200

      else:
          # if there were no previous questions, we can make it random
          current_question = random.choice(questions_in_category_whole)
          return jsonify({'quiz_category': category, 'question': current_question, 'previous_questions': previous_questions}), 200



  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(400)
  def bad_request(error):
      return jsonify({'success': False, 'error': 400, 'message': 'bad request'}), 400

  @app.errorhandler(404)
  def not_found(error):
      return jsonify({'success': False, 'error': 404, 'message': 'resources not found'}), 404

  @app.errorhandler(422)
  def unprocessable(error):
      return jsonify({'success': False, 'error': 422, 'message': 'unprocessable'}), 422

  @app.errorhandler(500)
  def internal_server_error(error):
      return jsonify({'success': False, 'error': 500, 'message': 'internal server error'}), 500
  return app


      
  