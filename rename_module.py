import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load environment variables or set the base folders manually
step_two_folder = os.getenv('STEP_TWO_FOLDER')

def rename_files_in_orientation_folder(folder_path):
    # Get a list of all image files in the orientation folder
    image_files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    image_files.sort()  # Sort the file names

    # Determine the padding length needed for numbering (always set to 4)
    padding_length = 4

    # Rename the files sequentially
    for i, old_name in enumerate(image_files, start=1):
        new_name = f"{i:0{padding_length}d}" + os.path.splitext(old_name)[1]  # Pad the new name with zeros
        old_path = os.path.join(folder_path, old_name)
        new_path = os.path.join(folder_path, new_name)
        os.rename(old_path, new_path)
        print(f"Renamed: {old_name} -> {new_name}")

def rename(date_folder):
    # Construct the path to the date folder
    date_folder_path = os.path.join(step_two_folder, date_folder)
    if not os.path.isdir(date_folder_path):
        print(f"Error: The specified date folder {date_folder} does not exist.")
        return

    # Traverse subfolders until we reach the orientation folders
    for keyword_folder in os.listdir(date_folder_path):
        keyword_folder_path = os.path.join(date_folder_path, keyword_folder)
        if not os.path.isdir(keyword_folder_path):
            continue
        
        for prompt_number_folder in os.listdir(keyword_folder_path):
            prompt_number_folder_path = os.path.join(keyword_folder_path, prompt_number_folder)
            if not os.path.isdir(prompt_number_folder_path):
                continue

            for orientation_folder in os.listdir(prompt_number_folder_path):
                orientation_folder_path = os.path.join(prompt_number_folder_path, orientation_folder)
                if not os.path.isdir(orientation_folder_path):
                    continue

                # Rename files within the orientation folder
                print(f"Processing folder: {orientation_folder_path}")
                # Call function to rename files in the orientation folder
                rename_files_in_orientation_folder(orientation_folder_path)

def main():
    # Get the date folder from the user
    date_folder = input("Enter the name of the date folder (e.g., 2024-03-18): ")
    rename(date_folder)

if __name__ == "__main__":
    main()
