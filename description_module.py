from openai import OpenAI
from dotenv import load_dotenv
import os
import re

# Load environment variables from .env file
load_dotenv()

# Retrieve the folder path from environment variables
step_one_folder = os.getenv('STEP_ONE_FOLDER')
step_three_folder = os.getenv('STEP_THREE_FOLDER')

client = OpenAI()

# Function to create a directory if it doesn't exist
def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        
# Replace spaces with underscores and convert to lowercase
def format_keyword(keyword):
    formatted_keyword = keyword.replace(" ", "_").lower()
    return formatted_keyword
        
# Writing Etsy description
def etsy_title(keyword, prompt):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a highly-skilled Etsy marketer who is focused on keyword-centric Etsy titles."},
            {"role": "user", "content": f"Write an Etsy title using for a keyword '{keyword}' somewhere in the beginning. We also used the prompt {prompt} to create the art. You are selling a pack of downloadable digital prints. The title should be at least 100 characters, but no longer than 140 characters. Utilize the keywords in title separated by | sign."}
        ]
    )

    title = completion.choices[0].message.content.strip('"')
    return title

# Writing product description   
def etsy_description(keyword, prompt):
    completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a highly-skilled Etsy marketer who is focused on keyword-centric Etsy descriptions."},
        {"role": "user", "content": f"Write a description for a keyword '{keyword}' for a pack of downloadable digital prints created by AI. We also used the prompt {prompt} to create the art. It should be a minimum of 300 words. Do not overuse the keyword, but use it enough times. The print will have 300dpi suitable for prints with up to 20 inches; the images are square. Use human-like writing style and avoid detection by ChatGPT detectors."}
    ]
    )
    return completion.choices[0].message.content

# Writing tags  
def etsy_tags(keyword, prompt):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a highly-skilled Etsy marketer who is focused on kEtsy keywords."},
            {"role": "user", "content": f"Write 13 Etsy keywords separated by commas; we are focusing on the keyword '{keyword}'. We also used the prompt {prompt} to create the art. You are selling a pack of downloadable digital prints. Do not overuse the keyword in the tags. Each tag should be no longer than 20 characters!"}
        ]
    )

    # Remove quotation marks and trailing dots
    tags = completion.choices[0].message.content.strip('"').rstrip('.')

    # Split the string into lines
    tag_lines = tags.split('\n')

    # Remove enumeration from each line
    cleaned_tags = [re.sub(r'^\d+\.\s*', '', line) for line in tag_lines]

    # Join the cleaned tags into a single line separated by commas
    final_tags = ', '.join(cleaned_tags)

    return final_tags

# Combining everything
def description_creation(keyword, prompt):
    title = etsy_title(keyword, prompt)
    description = etsy_description(keyword, prompt)
    tags = etsy_tags(keyword, prompt)
    return title, description, tags

def description(base_path, date, zip_name):
    # Ensure the descriptions folder exists
    descriptions_folder = os.path.join(step_three_folder, date, "descriptions")
    if not os.path.exists(descriptions_folder):
        os.makedirs(descriptions_folder)
    
    # Construct the full path to prompt.txt
    prompt_file_path = os.path.join(base_path, "prompt.txt")
    print(prompt_file_path)
    
    # Ensure prompt.txt exists
    if not os.path.exists(prompt_file_path):
        print("prompt.txt not found.")
        return
    
    # Read the keyword and prompt from the prompt.txt file
    with open(prompt_file_path, 'r') as prompt_file:
        lines = prompt_file.readlines()
        if len(lines) >= 2:
            keyword = lines[0].strip()
            prompt = lines[1].strip()

            # Generate descriptions
            title, description, tags = description_creation(keyword, prompt)

            # Create the directory for the formatted keyword if it doesn't exist
            destination = os.path.join(descriptions_folder, zip_name)
            if not os.path.exists(destination):
                os.makedirs(destination)

            # Save results in text files
            title_file_path = os.path.join(destination, "title.txt")
            description_file_path = os.path.join(destination, "description.txt")
            tags_file_path = os.path.join(destination, "tags.txt")

            with open(title_file_path, 'w') as title_file:
                title_file.write(title)

            with open(description_file_path, 'w') as description_file:
                description_file.write(description)

            with open(tags_file_path, 'w') as tags_file:
                tags_file.write(tags)

    print("Descriptions generated and saved successfully.")
    
def main():
    base_path = input("Enter the base path: ")
    date_folder = input("Enter date: ")
    zip_name = input("Enter the name of ZIP file: ")
    description(base_path, date_folder, zip_name)

if __name__ == "__main__":
    main()