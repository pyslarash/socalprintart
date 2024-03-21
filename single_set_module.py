import base64
import os
import requests
from dotenv import load_dotenv
from datetime import datetime
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Instantiate the OpenAI client
client = OpenAI()

engine_id = "stable-diffusion-v1-6"
api_host = os.getenv('API_HOST', 'https://api.stability.ai')
api_key = os.getenv("STABILITY_API_KEY")
generated_folder = os.getenv('GENERATED_FOLDER')
step_one_folder = os.getenv('STEP_ONE_FOLDER')

if api_key is None:
    raise Exception("Missing Stability API key.")

def paraphrase_prompt(keyword, prompt):
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a highly-skilled prompt engineer who is generating prompts to create images using Stability AI."},
                {"role": "user", "content": f"Paraphrase this prompt: {prompt}. You MUST focus on this keyword: {keyword}. Change colors, textures, views in your new prompt. Do not change the main character from the keyword in any circumstance!!! Make sure it's different, but is kept in the same style. Only provide the prompt in the output - no quotation marks or numbers. Separate styles by commas."}
            ]
        )
        response_content = completion.choices[0].message.content
        
        # Trim leading whitespace
        trimmed_content = response_content.strip()
        
        return trimmed_content
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def stability(keyword, prompt, img_width, img_height):
    text_prompt = paraphrase_prompt(keyword, prompt)
    
    response = requests.post(
        f"{api_host}/v1/generation/{engine_id}/text-to-image",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {api_key}"
        },
        json={
            "text_prompts": [
                {
                    "text": text_prompt
                }
            ],
            "cfg_scale": 7,
            "height": img_height,
            "width": img_width,
            "samples": 1,
            "steps": 40,
        },
    )

    if response.status_code != 200:
        raise Exception("Non-200 response: " + str(response.text))

    data = response.json()
    
    return data

def stability_images(date_folder, num_images, image_type):
    date_folder_path = os.path.join(step_one_folder, date_folder)
    for root, dirs, files in os.walk(date_folder_path):
        for file_name in files:
            if file_name == "prompt.txt":
                # Read the keyword and prompt from the prompt.txt file
                with open(os.path.join(root, file_name), 'r') as prompt_file:
                    lines = prompt_file.readlines()
                    keyword = lines[0].strip()
                    prompt = lines[1].strip()
                
                # Filter out filenames that do not start with a number
                existing_images = [filename for filename in os.listdir(root) if filename[0].isdigit()]
                
                if existing_images:
                    last_index = max(int(filename.split('.')[0]) for filename in existing_images)
                    start_index = last_index + 1
                else:
                    start_index = 1
                
                # Define image width and height based on the image type
                if image_type == "square":
                    img_width = 1024
                    img_height = 1024
                elif image_type == "horizontal":
                    img_width = 1280
                    img_height = 1024
                elif image_type == "vertical":
                    img_width = 1024
                    img_height = 1280
                else:
                    raise ValueError("Invalid image type. Supported types are: square, horizontal, vertical")
                
                # Create image_type directory within the root directory
                image_type_directory = os.path.join(root, image_type)
                os.makedirs(image_type_directory, exist_ok=True)
                
                # Generate and save the images
                for i in range(start_index, start_index + num_images):
                    # Generate stability data
                    stability_data = stability(keyword, prompt, img_width, img_height)
                    # Extract image data from stability data
                    image_data = stability_data["artifacts"][0]["base64"]
                    # Decode base64 image data and save the image
                    image_path = os.path.join(image_type_directory, f"{i:04d}.jpg")
                    with open(image_path, 'wb') as f:
                        f.write(base64.b64decode(image_data))

def main():
    # Get input from the user
    date_folder = input("Enter the date in the format 'YYYY-MM-DD': ")
    num_images = int(input("Enter the number of images to generate: "))
    print("Select the type of image:")
    print("1. Square")
    print("2. Horizontal")
    print("3. Vertical")
    choice = int(input("Enter your choice (1-3): "))
    
    # Map the user's choice to the corresponding image type
    if choice == 1:
        image_type = "square"
    elif choice == 2:
        image_type = "horizontal"
    elif choice == 3:
        image_type = "vertical"
    else:
        print("Invalid choice. Defaulting to square.")
        image_type = "square"
    
    # Generate and save the images
    stability_images(date_folder, num_images, image_type)

if __name__ == "__main__":
    main()