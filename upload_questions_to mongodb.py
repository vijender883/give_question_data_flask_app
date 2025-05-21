import os
import json
import glob
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

# MongoDB connection details
MONGODB_URI = "mongodb+srv://admin:RCyKhyxEw0LmSSXN@cluster0.rq9f5.mongodb.net/main?retryWrites=true&w=majority&appName=Cluster0"
DATABASE_NAME = "test"
COLLECTION_NAME = "questionData"

def connect_to_mongodb():
    """Connect to MongoDB Atlas and return the collection object"""
    try:
        # Create a MongoDB client
        client = MongoClient(MONGODB_URI)
        
        # Access the database
        db = client[DATABASE_NAME]
        
        # Access or create the collection
        collection = db[COLLECTION_NAME]
        
        # Create a unique index on the question_name field
        collection.create_index("question_name", unique=True)
        
        print(f"Connected to MongoDB Atlas: {DATABASE_NAME}.{COLLECTION_NAME}")
        return collection
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return None

def process_json_files(collection):
    """Process all JSON files in the 'Question_data_json_files' directory"""
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the JSON files folder
    json_folder = os.path.join(script_dir, "Question_data_json_files")
    
    # Check if the folder exists
    if not os.path.isdir(json_folder):
        print(f"Error: The 'Question_data_json_files' folder does not exist in {script_dir}")
        return
    
    # Find all JSON files in the folder
    json_files = glob.glob(os.path.join(json_folder, "*.json"))
    
    if not json_files:
        print("No JSON files found in the 'Question_data_json_files' folder.")
        return
    
    print(f"Found {len(json_files)} JSON file(s) to process.")
    
    # Process each JSON file
    for file_path in json_files:
        file_name = os.path.basename(file_path)
        try:
            # Load JSON data from file
            with open(file_path, 'r', encoding='utf-8') as file:
                question_data = json.load(file)
            
            # Check if the question has a question_name
            if "question_name" not in question_data:
                print(f"Warning: {file_name} is missing a question_name field. Skipping.")
                continue
            
            # Add timestamps if not present
            if "created_at" not in question_data:
                from datetime import datetime
                current_time = datetime.utcnow().isoformat() + "Z"
                question_data["created_at"] = current_time
                question_data["updated_at"] = current_time
            
            # Insert or update the document using upsert
            result = collection.update_one(
                {"question_name": question_data["question_name"]},
                {"$set": question_data},
                upsert=True
            )
            
            if result.upserted_id:
                print(f"Inserted: {question_data['question_name']} from {file_name}")
            elif result.modified_count:
                print(f"Updated: {question_data['question_name']} from {file_name}")
            else:
                print(f"No changes needed for: {question_data['question_name']} from {file_name}")
                
        except json.JSONDecodeError:
            print(f"Error: {file_name} is not a valid JSON file. Skipping.")
        except DuplicateKeyError:
            print(f"Error: {question_data['question_name']} already exists in the database. Skipping.")
        except Exception as e:
            print(f"Error processing {file_name}: {e}")

def main():
    # Connect to MongoDB
    collection = connect_to_mongodb()
    if collection is None:
        return
    
    # Process JSON files
    process_json_files(collection)
    
    print("Processing complete!")

if __name__ == "__main__":
    main()