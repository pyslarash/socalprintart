from dotenv import load_dotenv
import os
import zipfile
from PIL import Image
import uuid
import shutil
from description_module import description
from pdf_module import insert_link_after_paragraph

# Load environment variables from .env file
load_dotenv()

step_one_folder = os.getenv('STEP_ONE_FOLDER')
step_two_folder = os.getenv('STEP_TWO_FOLDER')
step_three_folder = os.getenv('STEP_THREE_FOLDER')

# Function to resize an image to 6000px on the shorter edge and 300dpi
def resize_image(image_path):
    img = Image.open(image_path)
    width, height = img.size
    if width < height:
        new_width = 6000
        new_height = int(6000 * height / width)
    else:
        new_height = 6000
        new_width = int(6000 * width / height)
    img = img.resize((new_width, new_height))
    img = img.convert('RGB')  # Ensure the image is in RGB mode
    img = img.resize((new_width, new_height), Image.BICUBIC)
    img.save(image_path, quality=100, dpi=(300, 300))
    
def final_generation(date_folder):
    # New destination directory
    destination_dir = os.path.join(step_three_folder, date_folder, "zip")
    mockup_dir = os.path.join(step_three_folder, date_folder, "mockups")
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)
    if not os.path.exists(mockup_dir):
        os.makedirs(mockup_dir)
    
    # Iterate through the enlarged folder
    date_folder_path = os.path.join(step_two_folder, date_folder)
    date_folder_path_step_one = os.path.join(step_one_folder, date_folder)
    for keyword_folder_name in os.listdir(date_folder_path):
        keyword_folder_path = os.path.join(date_folder_path, keyword_folder_name)
        keyword_folder_path_step_one = os.path.join(date_folder_path_step_one, keyword_folder_name)
        for prompt_number_folder_name in os.listdir(keyword_folder_path):
            prompt_number_folder_path = os.path.join(keyword_folder_path, prompt_number_folder_name)
            step_one_path = os.path.join(keyword_folder_path_step_one, prompt_number_folder_name)
            print(step_one_path)
            # Skip if the path is not a directory
            if not os.path.isdir(prompt_number_folder_path):
                continue
            for orientation_folder_name in os.listdir(prompt_number_folder_path):
                orientation_folder_path = os.path.join(prompt_number_folder_path, orientation_folder_name)
                # Skip if the path is not a directory
                if not os.path.isdir(orientation_folder_path):
                    continue
                
                # Generate a random filename for the zip file inside the loop for each orientation folder
                generated_name = str(uuid.uuid4()).replace('-', '')[:64]
                zip_filename = generated_name + '.zip'
                zip_file_path = os.path.join(destination_dir, zip_filename)
                description(step_one_path, date_folder, generated_name)
                insert_link_after_paragraph(date_folder, generated_name)
                with zipfile.ZipFile(zip_file_path, 'w') as zipf:
                    for img_file in os.listdir(orientation_folder_path):
                        if img_file.endswith(('.jpg', '.jpeg', '.png')):
                            img_path = os.path.join(orientation_folder_path, img_file)
                            # Assuming `resize_image` is a function defined elsewhere
                            # resize_image(img_path)
                            zipf.write(img_path, os.path.basename(img_path))
                
                # Move mockup images to the mockups directory with the name of the generated zip file
                mockup_destination_dir = os.path.join(mockup_dir, generated_name)
                if not os.path.exists(mockup_destination_dir):
                    os.makedirs(mockup_destination_dir)
                mockup_folder_path = os.path.join(orientation_folder_path, "mockups")
                for mockup_img_file in os.listdir(mockup_folder_path):
                    if mockup_img_file.endswith(('.jpg', '.jpeg', '.png')):
                        shutil.move(os.path.join(mockup_folder_path, mockup_img_file), os.path.join(mockup_destination_dir, mockup_img_file))
    
    print(f"Files zipped successfully in {destination_dir} and mockup images moved to {mockup_dir}.")
    
def main():
    date_folder = input("Enter the date folder name (e.g., 2024-03-18): ")
    final_generation(date_folder)

if __name__ == "__main__":
    main()