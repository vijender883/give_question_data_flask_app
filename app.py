from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import json
from bson import ObjectId

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# MongoDB Atlas connection
def get_database():
    # Your connection string
    connection_string = "mongodb+srv://admin:RCyKhyxEw0LmSSXN@cluster0.rq9f5.mongodb.net/main?retryWrites=true&w=majority&appName=Cluster0"
    
    # Create a connection using MongoClient
    client = MongoClient(connection_string)
    
    # Return the database
    return client['test']  # Your database name

# Custom JSON encoder to handle MongoDB ObjectId
class MongoJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super(MongoJSONEncoder, self).default(obj)

app.json_encoder = MongoJSONEncoder

@app.route('/get_data', methods=['POST'])
def get_data():
    try:
        # Get request data
        request_data = request.get_json()
        
        if not request_data or 'question_name' not in request_data:
            return jsonify({"error": "Missing 'question' parameter"}), 400
        
        question = request_data['question_name']
        
        # Get the database and collection
        db = get_database()
        collection = db['questionData']  # Your collection name
        
        # Query MongoDB for the document with the specified question_name
        result = collection.find_one({"question_name": question})
        
        if result:
            # Process the result to handle MongoDB types and add image placeholders
            processed_result = process_document(result)
            return jsonify(processed_result), 200
        else:
            return jsonify({"error": "Question not found"}), 404
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/add_new_question', methods=['POST'])
def add_new_question():
    try:
        # Get request data
        request_data = request.get_json()
        
        if not request_data or 'question_name' not in request_data:
            return jsonify({"status": "failure", "message": "Missing 'question_name' parameter"}), 400
        
        # Get the database and collection
        db = get_database()
        collection = db['questionData']
        
        # Check if question already exists
        existing_question = collection.find_one({"question_name": request_data['question_name']})
        if existing_question:
            return jsonify({"status": "failure", "message": "Question with this name already exists"}), 409
        
        # Insert the new question
        result = collection.insert_one(request_data)
        
        if result.inserted_id:
            return jsonify({"status": "success", "id": str(result.inserted_id)}), 201
        else:
            return jsonify({"status": "failure", "message": "Failed to insert question"}), 500
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"status": "failure", "message": str(e)}), 500

@app.route('/edit_question', methods=['POST'])
def edit_question():
    try:
        # Get request data
        request_data = request.get_json()
        
        if not request_data or 'question_name' not in request_data:
            return jsonify({"status": "failure", "message": "Missing 'question_name' parameter"}), 400
        
        # Get the database and collection
        db = get_database()
        collection = db['questionData']
        
        # Check if question exists
        existing_question = collection.find_one({"question_name": request_data['question_name']})
        if not existing_question:
            return jsonify({"status": "failure", "message": "Question not found"}), 404
        
        # Update the question
        result = collection.update_one(
            {"question_name": request_data['question_name']},
            {"$set": request_data}
        )
        
        if result.modified_count > 0:
            return jsonify({"status": "success"}), 200
        else:
            return jsonify({"status": "failure", "message": "No changes were made"}), 200
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"status": "failure", "message": str(e)}), 500

@app.route('/delete_question', methods=['POST'])
def delete_question():
    try:
        # Get request data
        request_data = request.get_json()
        
        if not request_data or 'question_name' not in request_data:
            return jsonify({"status": "failure", "message": "Missing 'question_name' parameter"}), 400
        
        question_name = request_data['question_name']
        
        # Get the database and collection
        db = get_database()
        collection = db['questionData']
        
        # Check if question exists before deletion
        existing_question = collection.find_one({"question_name": question_name})
        if not existing_question:
            return jsonify({"status": "failure", "message": "Question not found"}), 404
        
        # Delete the question
        result = collection.delete_one({"question_name": question_name})
        
        if result.deleted_count > 0:
            return jsonify({"status": "success"}), 200
        else:
            return jsonify({"status": "failure", "message": "Failed to delete question"}), 500
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"status": "failure", "message": str(e)}), 500

def process_document(document):
    """Process MongoDB document to handle ObjectId and add image placeholders"""
    # Create a copy of the document to modify
    result = {}
    
    # Handle ObjectId
    result["_id"] = str(document["_id"])
    
    # Copy all other fields except examples which need special handling
    for key, value in document.items():
        if key != "_id" and key != "examples":
            result[key] = value
    
    # Handle examples with special processing for visualization data
    if "examples" in document:
        result["examples"] = []
        
        for i, example in enumerate(document["examples"]):
            # Create a copy of the example
            processed_example = {}
            
            # Copy all fields except visualization which might need special handling
            for key, value in example.items():
                if key != "visualization":
                    processed_example[key] = value
            
            # Handle visualization if it exists
            if "visualization" in example:
                # Check if it's an object with image_data or already a string
                if isinstance(example["visualization"], dict) and "image_data" in example["visualization"]:
                    # Replace with placeholder format
                    processed_example["visualization"] = f"<<<<{document['question_name']}_{i}.png>>>>"
                else:
                    # Keep as is if it's already in the right format or something else
                    processed_example["visualization"] = example["visualization"]
            
            result["examples"].append(processed_example)
    
    return result


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=False)  # Choose an available port