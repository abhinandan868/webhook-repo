from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from datetime import datetime
import os
import json

app = Flask(__name__)

mongodb_uri = 'mongodb://localhost:27017/'
client = MongoClient(mongodb_uri)
db = client['webHookups']
collection = db['changes']

@app.route('/', methods=['GET', 'POST'])
def webhook_and_fetch_data():
    if request.method == 'POST':
        # Handle the incoming webhook request and store data in MongoDB
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

    elif request.method == 'GET':
        # Handle the GET request to fetch data from MongoDB and display on the HTML page
        return render_template('index.html')


@app.route('/fetch-data', methods=['GET'])
def fetch_data():
    # Fetch all documents from the collection
    data = list(collection.find({}, {'_id': 0})) 
    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True)
