from openai import OpenAI
from dotenv import load_dotenv
import os
from datetime import datetime
import re

# Load environment variables from .env file
load_dotenv()

# Retrieve the folder path from environment variables
keyword_folder = os.getenv('KEYWORD_FOLDER')
# prompt_folder = os.getenv('PROMPT_FOLDER')
step_one_folder = os.getenv('STEP_ONE_FOLDER')
# Ensure the folder path is available
if not keyword_folder:
    raise ValueError("No KEYWORD_FOLDER found in environment variables or it is not set")

# if not prompt_folder:
#     raise ValueError("No KEYWORD_FOLDER found in environment variables or it is not set")

if not step_one_folder:
    raise ValueError("No STEP_ONE_FOLDER found in environment variables or it is not set")

# Instantiate the OpenAI client
client = OpenAI()

def prompt(keyword):
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a highly-skilled prompt engineer who is generating prompts to create images using Stability AI."},
                {"role": "user", "content": f"Create a prompt around this keyword: {keyword}. You are focused on prompts generating abstract art. The art has to have soft tones and be quite detailed. Create prompts with as much details as possible. Separate different details using commas. For example: 'abstract image of a snail, soft colors, patterns, blurred background, textures', etc. Do not use words like create, generate, develop, etc - only describe the image. Don't use quotation marks in your answer."}
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def generate_prompt_from_keyword(file_name, num_prompts_per_keyword):
    # Construct the file path for the keyword file
    keyword_file_path = os.path.join(keyword_folder, file_name)
    
    # Check if the keyword file exists
    if not os.path.exists(keyword_file_path):
        print(f"File '{file_name}' not found in keyword folder.")
        return
    
    # Get today's date
    today_date = datetime.now().strftime("%Y-%m-%d")
    
    try:
        # Read the keywords from the file
        with open(keyword_file_path, 'r') as file:
            keywords = file.readlines()
        
        # Process each keyword
        for keyword_index, keyword in enumerate(keywords, start=1):
            keyword = keyword.strip()
            formatted_keyword = format_keyword(keyword)
            
            # Construct folder paths
            keyword_folder_path = os.path.join(step_one_folder, today_date, formatted_keyword)
            os.makedirs(keyword_folder_path, exist_ok=True)
            
            # Generate prompts for each keyword
            for prompt_number in range(1, num_prompts_per_keyword + 1):
                prompt_content = prompt(keyword)
                if prompt_content:
                    # Construct prompt file path
                    folder_number = f"{prompt_number:02}"
                    prompt_file_name = f"prompt.txt"
                    prompt_file_path = os.path.join(keyword_folder_path, folder_number, prompt_file_name)
                    
                    # Ensure the directory exists or create it
                    os.makedirs(os.path.dirname(prompt_file_path), exist_ok=True)
                    
                    # Write prompt content to file
                    with open(prompt_file_path, 'w') as prompt_file:
                        prompt_file.write(keyword + '\n')
                        prompt_file.write(prompt_content)
                    
                    print(f"Prompt {prompt_number} generated for keyword '{keyword}'.")
                else:
                    print(f"Failed to generate prompt {prompt_number} for keyword '{keyword}'.")
    except Exception as e:
        print(f"An error occurred: {e}")
        
    return today_date

def format_keyword(keyword):
    formatted_keyword = keyword.replace(" ", "_").lower()
    return formatted_keyword

def main():
    # Get the name of the keyword file from the user
    keyword_file_name = input("Enter the name of the keyword file (e.g., keywords.txt): ")
    
    # Get the number of prompts to generate per keyword
    num_prompts_per_keyword = int(input("Enter the number of prompts to generate per keyword: "))
    
    # Generate prompts from keywords in the specified file
    generate_prompt_from_keyword(keyword_file_name, num_prompts_per_keyword)

if __name__ == "__main__":
    main()