import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load environment variables or set the base folders manually
generated_folder = os.getenv('GENERATED_FOLDER')
enlarged_folder = os.getenv('ENLARGED_FOLDER')

def create_folder_structure(date_folder):
    # Construct the path to the date folder within the generated_folder
    date_folder_path = os.path.join(generated_folder, date_folder)

    # Check if the date folder exists in the generated folder
    if not os.path.isdir(date_folder_path):
        print(f"Error: The specified date folder {date_folder} does not exist in the generated folder.")
        return

    # Iterate through each keyword folder in the date folder
    for keyword_folder_name in os.listdir(date_folder_path):
        keyword_folder_path = os.path.join(date_folder_path, keyword_folder_name)

        # Check if it's a directory (ignoring files that might be in the date folder)
        if os.path.isdir(keyword_folder_path):
            # Iterate through each orientation folder in the keyword folder
            for orientation_folder_name in os.listdir(keyword_folder_path):
                orientation_folder_path = os.path.join(keyword_folder_path, orientation_folder_name)

                # Again, check if it's a directory
                if os.path.isdir(orientation_folder_path):
                    # Construct the corresponding path in the enlarged_folder
                    new_orientation_folder_path = os.path.join(enlarged_folder, date_folder, keyword_folder_name, orientation_folder_name)

                    # Create the directory structure in enlarged_folder, including any necessary parent directories
                    os.makedirs(new_orientation_folder_path, exist_ok=True)
                    print(f"Created folder structure: {new_orientation_folder_path}")

def main():
    # Ask the user for the date folder name
    date_folder = input("Enter the name of the date folder (e.g., 2024-03-18): ")
    create_folder_structure(date_folder)

if __name__ == "__main__":
    main()