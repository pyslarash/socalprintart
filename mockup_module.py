import os
import random
import requests
import time
from dotenv import load_dotenv
from PIL import Image
import base64

# Load environment variables from .env file
load_dotenv()

# Load API keys and folder paths
api_key = os.getenv('PRINTFUL_TOKEN')
imgbb_api_key = os.getenv('IMG_BB_TOKEN')
step_two_folder = os.getenv('STEP_TWO_FOLDER')
step_one_folder = os.getenv('STEP_ONE_FOLDER')

# Constants
MAX_RETRIES = 10
RETRY_DELAY = 60

def get_base_filename(file_path):
    """Extracts the filename without extension."""
    base_filename = os.path.basename(file_path)
    filename_without_extension = os.path.splitext(base_filename)[0]
    return filename_without_extension

def upload_image_to_imgbb(image_path):
    """Uploads an image to imgbb and returns the URL."""
    url = "https://api.imgbb.com/1/upload"
    with open(image_path, "rb") as file:
        image_data = base64.b64encode(file.read()).decode('utf-8')
    payload = {
        "key": imgbb_api_key,
        "image": image_data,
        "expiration": 600
    }
    response = requests.post(url, data=payload)
    try:
        response.raise_for_status()
        result = response.json()
        image_url = result["data"]["url"]
        print(f"Image uploaded successfully. URL: {image_url}")
        return image_url
    except (requests.RequestException, KeyError) as e:
        print(f"Image upload failed: {e}")
        return None

def get_image_orientation(image_path):
    """Determines the orientation of an image."""
    with Image.open(image_path) as img:
        width, height = img.size
        if width == height:
            return "square"
        elif width < height:
            return "vertical"
        else:
            return "horizontal"
        
def save_file(url, filename, original_image_path):
    """
    Saves the file to the specified path.
    """
    orientation = get_image_orientation(original_image_path)
    print(orientation)
    path_parts = original_image_path.split(os.sep)
    date_folder, keyword_folder, prompt_number, orientation = path_parts[-5], path_parts[-4], path_parts[-3], path_parts[-2]
    # Modify the output folder path
    output_folder = os.path.join(step_two_folder, date_folder, keyword_folder, prompt_number, orientation, "mockups")
    os.makedirs(output_folder, exist_ok=True)
    filepath = os.path.join(output_folder, filename)
    try:
        with open(filepath, 'wb') as f:
            f.write(requests.get(url).content)
        print(f"Saved file: {filepath}")
    except IOError as e:
        print(f"Error saving file: {e}")

def mockup_generator(image_path, mockup_counter, orientation):
    """Generates a mockup for the image."""
    filename = get_base_filename(image_path)
    uploaded_image_url = upload_image_to_imgbb(image_path)
    if not uploaded_image_url:
        print("Image upload to imgbb failed. Aborting mockup generation.")
        return mockup_counter

    image_orientation = get_image_orientation(image_path)

    # API endpoints and headers
    url_create_task_poster = 'https://api.printful.com/mockup-generator/create-task/171'
    url_task_status = 'https://api.printful.com/mockup-generator/task'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }

    poster_option_groups = [
        "Lifestyle",
        "Lifestyle 10",
        "Lifestyle 2",
        "Lifestyle 3",
        "Lifestyle 4",
        "Lifestyle 5",
        "Lifestyle 6",
        "Lifestyle 7",
        "Lifestyle 8",
        "Lifestyle 9",
        "Lifestyle, Premium"
    ]

    variant_ids = {
        "square": {"poster": 6879},
        "vertical": {"poster": 6880},
        "horizontal": {"poster": 6880}
    }

    payload_template = {
        "variant_ids": [],
        "format": "jpg",
        "files": [
            {
                "placement": "default",
                "image_url": uploaded_image_url
            }
        ]
    }
    
    position_settings = {
        "square": {"area_width": 1800, "area_height": 1800, "width": 1800, "height": 1800, "top": 0, "left": 0},
        "vertical": {"area_width": 1800, "area_height": 2400, "width": 1800, "height": 2400, "top": 0, "left": 0},
        "horizontal": {"area_width": 2400, "area_height": 1800, "width": 2400, "height": 1800, "top": 0, "left": 0}
    }

    payload_poster = payload_template.copy()
    payload_poster["variant_ids"] = [variant_ids[image_orientation]["poster"]]
    payload_poster["files"][0]["position"] = position_settings[image_orientation]
    payload_poster["option_groups"] = poster_option_groups
    
    # Implementing backoff for rate limiting
    retry_delay = RETRY_DELAY
    for attempt in range(MAX_RETRIES):
        response = requests.post(url_create_task_poster, json=payload_poster, headers=headers)
        if response.status_code == 429:  # Rate limit exceeded
            print(f"Rate limit exceeded. Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
        elif response.status_code == 200:
            return handle_mockup_response(response, filename, url_task_status, headers, image_path, mockup_counter, orientation)
        else:
            print(f"Error creating mockup task: {response.status_code} - {response.text}")
            return mockup_counter
    else:
        print("Max retries exceeded. Failed to create mockup task.")
        return mockup_counter

def handle_mockup_response(response, product_type, url_task_status, headers, original_image_path, mockup_counter, orientation):
    """Handles the mockup response."""
    if response.status_code == 200:
        task_key = response.json().get("result", {}).get("task_key")
        print(f"Mockup generation task created for {product_type}. Task Key: {task_key}")

        selected_styles = set()

        for _ in range(10):
            task_response = requests.get(f'{url_task_status}?task_key={task_key}', headers=headers)
            task_status = task_response.json().get("result", {}).get("status")

            if task_status == "completed":
                mockups = task_response.json().get("result", {}).get("mockups", [])
                extra_files = mockups[0].get("extra", [])
                random.shuffle(extra_files)

                for mockup in extra_files:
                    style = mockup.get("style")
                    if style not in selected_styles:
                        url_data = mockup.get("url")
                        filename = f'mockup_{mockup_counter}.jpg'
                        save_file(url_data, filename, original_image_path)
                        selected_styles.add(style)
                        mockup_counter += 1
                        
                        break  # Break after saving one mockup per orientation
                break
            elif task_status == "failed":
                print(f"Mockup generation task for {product_type} failed.")
                break
            else:
                print(f"Mockup generation in progress for {product_type}. Checking again in 10 seconds.")
                time.sleep(10)
    else:
        print(f"Error in creating mockup task for {product_type}: {response.status_code} - {response.text}")
    
    return mockup_counter

def mockups(date_folder):
    date_folder_path = os.path.join(step_one_folder, date_folder)
    processed_images = set()  # Set to keep track of processed images

    if not os.path.isdir(date_folder_path):
        print("Error: The specified date folder does not exist.")
        return

    for keyword_folder_name in os.listdir(date_folder_path):
        keyword_folder_path = os.path.join(date_folder_path, keyword_folder_name)
        for prompt_number in os.listdir(keyword_folder_path):
            prompt_number_path = os.path.join(keyword_folder_path, prompt_number)
            for orientation_folder_name in os.listdir(prompt_number_path):
                orientation_folder_path = os.path.join(prompt_number_path, orientation_folder_name)
                if os.path.isdir(orientation_folder_path):
                    jpg_files = [f for f in os.listdir(orientation_folder_path) if f.lower().endswith('.jpg') and f not in processed_images]
                    
                    # Adjust the selection logic here to ensure no image is used more than once
                    selected_images = random.sample(jpg_files, min(len(jpg_files), 4))  # Select up to 4 images

                    mockup_counter = 1
                    for image_file in selected_images:
                        image_path = os.path.join(orientation_folder_path, image_file)
                        if image_file not in processed_images:  # Check if the image has been processed
                            print(f"Processing image: {image_path}")
                            mockup_generator(image_path, mockup_counter, orientation_folder_name)
                            processed_images.add(image_file)  # Mark the image as processed
                            mockup_counter += 1

def main():
    date_folder = input("Enter the folder name (e.g., 2024-03-16): ")
    mockups(date_folder)
    
if __name__ == "__main__":
    main()
