# app.py
from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from datetime import datetime
import os

app = Flask(__name__)
# MongoDB Atlas connection (using password "bookstore")
mongodb_uri = os.environ.get('MONGODB_URI', 'mongodb+srv://bookstore:bookstore@cluster.chzj50s.mongodb.net/github_actions_db?retryWrites=true&w=majority')
client = MongoClient(mongodb_uri)
db = client['github_actions_db']
collection = db['actions']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    
    event_type = request.headers.get('X-GitHub-Event')
    
    if event_type == 'push':
        author = data['pusher']['name']
        to_branch = data['ref'].split('/')[-1]
        timestamp = datetime.utcnow().strftime("%d %B %Y - %I:%M %p UTC")
        
        action = {
            'type': 'PUSH',
            'author': author,
            'to_branch': to_branch,
            'timestamp': timestamp
        }
    
    elif event_type == 'pull_request':
        author = data['pull_request']['user']['login']
        from_branch = data['pull_request']['head']['ref']
        to_branch = data['pull_request']['base']['ref']
        timestamp = datetime.utcnow().strftime("%d %B %Y - %I:%M %p UTC")
        
        action = {
            'type': 'PULL_REQUEST',
            'author': author,
            'from_branch': from_branch,
            'to_branch': to_branch,
            'timestamp': timestamp
        }
    
    elif event_type == 'pull_request' and data['action'] == 'closed' and data['pull_request']['merged']:
        author = data['pull_request']['merged_by']['login']
        from_branch = data['pull_request']['head']['ref']
        to_branch = data['pull_request']['base']['ref']
        timestamp = datetime.utcnow().strftime("%d %B %Y - %I:%M %p UTC")
        
        action = {
            'type': 'MERGE',
            'author': author,
            'from_branch': from_branch,
            'to_branch': to_branch,
            'timestamp': timestamp
        }
    
    else:
        return jsonify({'message': 'Unsupported event type'}), 400

    collection.insert_one(action)
    return jsonify({'message': 'Webhook received and processed successfully'}), 200

@app.route('/get_actions')
def get_actions():
    actions = list(collection.find({}, {'_id': 0}).sort('timestamp', -1).limit(10))
    return jsonify(actions)

if __name__ == '__main__':
    app.run(debug=True)