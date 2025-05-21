import json
import sys
from pymongo import MongoClient
from bson import json_util

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
        
        # Access the collection
        collection = db[COLLECTION_NAME]
        
        print(f"Connected to MongoDB Atlas: {DATABASE_NAME}.{COLLECTION_NAME}")
        return collection
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return None

def extract_question(collection, question_name):
    """Find and extract a question by its question_name"""
    try:
        # Find the document with the given question_name
        document = collection.find_one({"question_name": question_name})
        
        if not document:
            print(f"Question '{question_name}' not found in the database.")
            return
        
        # Convert the document to a formatted JSON string
        formatted_json = json.dumps(json.loads(json_util.dumps(document)), indent=2)
        
        # Print the formatted JSON
        print("\nQuestion Data:")
        print(formatted_json)
        
        # Optionally save to a file
        filename = f"{question_name}_data.json"
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(formatted_json)
        print(f"\nData also saved to {filename}")
        
    except Exception as e:
        print(f"Error extracting question: {e}")

def main():
    # Get the question_name from command line arguments or prompt the user
    if len(sys.argv) > 1:
        question_name = sys.argv[1]
    else:
        question_name = input("Enter the question name to extract: ")
    
    # Connect to MongoDB
    collection = connect_to_mongodb()
    if collection is None:
        return
    
    # Extract and print the question
    extract_question(collection, question_name)

if __name__ == "__main__":
    main()