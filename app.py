from flask import Flask, request, jsonify
import logging

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.DEBUG)

@app.before_request
def log_request_info():
    app.logger.debug('Headers: %s', request.headers)
    app.logger.debug('Body: %s', request.get_data())

@app.route('/webhook', methods=['POST', 'GET'])
def webhook():
    if request.method == 'POST':
        # Process the GitHub data
        data = request.json
        # Add your logic to handle the GitHub event data here
        app.logger.info(f"Received event: {request.headers.get('X-GitHub-Event')}")
        app.logger.info(f"Payload: {data}")
        return jsonify({"message": "Webhook received successfully"}), 200
    elif request.method == 'GET':
        return jsonify({
            "message": "This is the webhook endpoint. Please use POST method to send data.",
            "supported_methods": ["POST"],
            "current_method": request.method
        }), 200
    else:
        return jsonify({
            "error": "Method not allowed",
            "supported_methods": ["POST", "GET"],
            "current_method": request.method
        }), 405

@app.route('/')
def home():
    return jsonify({
        "message": "Welcome to the webhook server",
        "endpoints": {
            "/webhook": "POST to send webhook data, GET for information"
        }
    }), 200

@app.errorhandler(Exception)
def handle_exception(e):
    # Log the exception
    app.logger.error(f"An error occurred: {str(e)}")
    # Return a JSON response
    return jsonify({
        "error": "An internal error occurred",
        "details": str(e)
    }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)