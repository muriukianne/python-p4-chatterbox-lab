from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'GET':
        # Query all messages from the database
        messages = Message.query.all()
        # Return a JSON response with the serialized messages
        return jsonify([message.to_dict() for message in messages])

    elif request.method == 'POST':
        # Get the incoming JSON data
        data = request.get_json()
        
        # Create a new message from the request data
        new_message = Message(
            body=data['body'],
            username=data['username']
        )
        
        # Add the new message to the session and commit to save it
        db.session.add(new_message)
        db.session.commit()

        # Return the newly created message in the response
        return jsonify(new_message.to_dict()), 201  # 201 is the status code for resource creation

@app.route('/messages/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def messages_by_id(id):
    # Replace get() with db.session.get()
    message = db.session.get(Message, id)  # Use db.session.get() instead of Message.query.get(id)
    if message is None:
        return jsonify({"error": "Message not found"}), 404  # Return 404 if message not found

    if request.method == 'PATCH':
        # Get the incoming JSON data for the update
        data = request.get_json()

        # Update the message's body
        message.body = data.get('body', message.body)  # Only update if 'body' is provided

        # Commit the changes to the database
        db.session.commit()

        # Return the updated message in the response
        return jsonify(message.to_dict())

    elif request.method == 'DELETE':
        # Delete the message from the database
        db.session.delete(message)
        db.session.commit()

        # Return a success message or an empty response
        return '', 204  # 204 No Content status code for successful deletion

    return jsonify(message.to_dict())  # Return a JSON response for a single message (GET request)

if __name__ == '__main__':
    app.run(port=5555)
