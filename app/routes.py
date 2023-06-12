from datetime import datetime

from flask import render_template, url_for, request, session, jsonify

from app import app, db
from app.models import Topic, Question, PerformanceTracker
from app.helpers import datetime_format, percent


@app.route('/')
@app.route('/index')
def index():
    """Render the index page and display all topics."""
    topics = Topic.get_all_topics()
    return render_template('index.html', topics=topics)


@app.route('/quiz')
def quiz():
    """Render the quiz page."""
    return render_template('quiz.html')


@app.route('/history')
def history_list():
    """Retrieve all topics with performance and render history-list."""
    topics = Topic.get_all_topics_with_performance()
    return render_template('history_list.html', topics=topics)


@app.route('/history/<topic_id>')
def history_detail(topic_id):
    """Retrieve the performance for a given topic and render history-detail."""
    topic = Topic.query.get(topic_id)
    history = topic.get_performance()
    return render_template('history_detail.html', history=history, topic=topic)


@app.route('/get_barchart_data/<topic_id>')
def get_barchart_data(topic_id):
    """Retrieve the performance for a given topic and return as JSON."""
    topic = Topic.query.get(topic_id)
    history = topic.get_performance()
    dates = [datetime_format(item.date) for item in history]
    accuracies = [item.accuracy for item in history]
    return jsonify({'dates': dates, 'accuracies': accuracies})


@app.route('/get_question', methods=['POST'])
def get_question():
    """Get the next question for the quiz.

    Retrieves the sorted questions from the session if they already exist.
    If not, it initializes the quiz by creating and storing the sorted
    questions in the session. If the topic ID has changed, it clears the
    session and updates the questions accordingly. Finally, it retrieves
    and returns the current question.

    Returns:
        A JSON response containing the serialized question.
    """
    try:
        # Retrieve sorted questions and topic ID from session
        sorted_questions = session['sorted_questions']
        topic_id = session['topic_id']
    except KeyError:
        # Initialize quiz
        topic_id = request.json['topic_id']
        topic = Topic.query.get(topic_id)
        sorted_questions = [q.id for q in topic.get_questions()]
        session['sorted_questions'] = sorted_questions
        session['topic_id'] = topic_id
        session['number_of_questions'] = len(sorted_questions)
    else:
        new_topic_id = request.json['topic_id']
        if new_topic_id != topic_id:
            # New topic, clear current session and update questions
            session.clear()
            topic = Topic.query.get(new_topic_id)
            sorted_questions = [q.id for q in topic.get_questions()]
            session['sorted_questions'] = sorted_questions
            session['topic_id'] = new_topic_id
            session['number_of_questions'] = len(sorted_questions)
    question_id = sorted_questions[request.json['current_idx']]
    return jsonify(Question.query.get(question_id).serialize())


@app.route('/get_number_of_questions', methods=['POST'])
def get_number_of_questions():
    """Get the number of questions for the quiz and return as JSON."""
    topic_id = request.json['topicId']
    topic = Topic.query.get(topic_id)
    number_of_questions = topic.get_number_of_questions()
    return jsonify({'number_of_questions': number_of_questions})


@app.route('/check_answer', methods=['POST'])
def check_answer():
    """Check the submitted answer for a question.

    Retrieves the current question based on the provided index and session data.
    Compares the selected choice with the correct choice of the question to
    determine if the answer is correct. Updates the question's score based on
    the correctness of the answer. Returns a JSON response with the result,
    including the correctness, selected choice, correct choice and explanation.

    Returns:
        A JSON response containing the result of the answer check.
    """
    current_idx = request.json['current_idx']
    question_id = session['sorted_questions'][current_idx]
    question = Question.query.get(question_id)
    selected_choice = request.json['selected_choice']
    is_correct = 1 if question.correct_choice == selected_choice else 0
    question.update(is_correct)
    return jsonify({
        'is_correct': is_correct,
        'selected_choice': selected_choice,
        'correct_choice': question.correct_choice,
        'explanation': question.question_explanation
    })


@app.route('/save_results', methods=['POST'])
def save_results():
    """Save the results to database, clear session and confirm success."""
    topic_id = request.json['topic_id']
    accuracy = request.json['accuracy']
    # Update the topic's last seen date
    topic = Topic.query.get(topic_id)
    topic.last_seen = datetime.now()
    # Add results as PerformanceTracker object
    performance_tracker = PerformanceTracker(topic_id=topic_id,
                                             accuracy=accuracy,
                                             topic_name=topic.name)
    db.session.add(performance_tracker)
    db.session.commit()
    # Clear session
    session.clear()
    return jsonify({'success': True})
