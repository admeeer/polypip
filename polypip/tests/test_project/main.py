import sys
from db import init_db
from utilities.helper import greet
from utilities.data.processor import process_data

def main():
    print("Using standard library:", sys.version)
    init_db()  # Initialize the database
    greet("Python developer")
    processed_data = process_data([1, 2, 3, 4, 5])
    print("Processed data:", processed_data)

if __name__ == "__main__":
    main()
