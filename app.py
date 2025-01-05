import logging
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import eventlet

# Setup logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app and SocketIO with eventlet
app = Flask(__name__)
socketio = SocketIO(app, async_mode='eventlet')

# Store questions, answers, and votes
questions = []
votes = {}

@app.route('/')
def host_page():
    return render_template('host.html')

@app.route('/user')
def user_page():
    return render_template('user.html')

@app.route('/results')
def results_page():
    return render_template('results.html')

# Socket event: When host sends a new question
@socketio.on('new_question')
def handle_new_question(data):
    logging.debug(f"Received new question: {data}")
    questions.append(data)
    votes[data['question']] = {answer: 0 for answer in data['answers']}
    emit('question_received', data, broadcast=True)

# Socket event: When user submits a vote
@socketio.on('user_vote')
def handle_user_vote(data):
    logging.debug(f"Received user vote: {data}")
    question = data['question']
    answer = data['answer']

    if question in votes:
        votes[question][answer] += 1

    # Log updated votes
    logging.debug(f"Updated votes for '{question}': {votes[question]}")
    
    # Send updated results to everyone (users and host)
    emit('update_results', {'question': question, 'votes': votes[question]}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)
