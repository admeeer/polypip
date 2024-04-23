from utils import fetch_data
from data_processor import process_data
from misc.helper import assist
import pyquil

def main():
    data = fetch_data()
    processed_data = process_data(data)
    assist(processed_data)

if __name__ == "__main__":
    main()
