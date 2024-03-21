from openai import OpenAI
from dotenv import load_dotenv
import os
from datetime import datetime
import re

# Load environment variables from .env file
load_dotenv()

# Retrieve the folder path from environment variables
keyword_folder = os.getenv('KEYWORD_FOLDER')
# Ensure the folder path is available
if not keyword_folder:
    raise ValueError("No KEYWORD_FOLDER found in environment variables or it is not set")

# Instantiate the OpenAI client
client = OpenAI()

def keywords(topic, amount):
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a highly-skilled Etsy marketer who is focused on coming up with theme-specific competitive keywords for your products."},
                {"role": "user", "content": f"Come up with specific '{amount}' keywords for a topic: '{topic}'. The topic is just a general topic, and you need to come up with more specific keywords based on that topic. For example, if the topic 'pets' was given, you need to focus on keywords that include what types of pets like cats, dogs, rats, snakes, etc. The keywords should be long-tailed. You are focusing on abstract art. Do not include sale keywords; only use keywords describing the object or theme. Only list the keywords and that's it."}
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Saving keywords to file
def save_keywords_to_file(keywords, folder_path):
    # Ensure the directory exists, create it if it doesn't
    os.makedirs(folder_path, exist_ok=True)
    
    # Format current date and time
    current_time = datetime.now().strftime("%Y-%m-%d")
    filename = f"keywords_{current_time}.txt"
    filepath = os.path.join(folder_path, filename)
    
    # Check if numbers are present before keywords
    if any(re.match(r'^\d+\.\s', line) for line in keywords.split('\n')):
        # Remove numbering if present
        cleaned_keywords = '\n'.join(line.split('. ', 1)[-1] for line in keywords.split('\n'))
    else:
        cleaned_keywords = keywords
    
    # Write keywords to the file
    with open(filepath, 'w') as file:
        file.write(cleaned_keywords)
    print(f"Keywords saved to {filepath}")

# Main script to interact with the user and process requests
if __name__ == "__main__":
    topic = input("Enter the topic for keywords: ")
    amount = input("Enter the amount of keywords: ")
    
    # Generate keywords
    generated_keywords = keywords(topic, amount)
    
    if generated_keywords:
        # Save generated keywords to a file
        save_keywords_to_file(generated_keywords, keyword_folder)
    else:
        print("Failed to generate keywords.")
