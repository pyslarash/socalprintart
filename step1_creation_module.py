from prompt_module import generate_prompt_from_keyword # Importing a function to generate prompts
from bulk_process_module import bulk_image_creation # Importing a bulk image creation function
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Retrieve the folder path from environment variables
keyword_folder = os.getenv('KEYWORD_FOLDER')

def main():
    # Ask the user for the keyword file name
    keyword_file_name = input("Enter the name of the keyword file: ")
    
    # Construct the full path to the keyword file
    keyword_file_path = os.path.join(keyword_folder, keyword_file_name)
    
    # Check if the keyword file exists
    if not os.path.exists(keyword_file_path):
        print(f"File '{keyword_file_name}' not found in keyword folder.")
        return
    
    # Generate prompts and get the date folder
    num_prompts_per_keyword = int(input("Enter the number of prompts to generate per keyword: "))
    
    # Ask the user for the number of images to generate per set
    num_images = int(input("Enter the number of images to generate per set: "))
    
    # Ask the user to choose the types of images to generate
    while True:
        print("Choose the types of images to generate:")
        print("1. Vertical")
        print("2. Horizontal")
        print("3. Square")
        print("4. Vertical & Horizontal")
        print("5. Vertical & Square")
        print("6. Horizontal & Square")
        print("7. All")
        choice = int(input("Enter your choice (1-7): "))
        
        # Map the user's choice to the corresponding image types
        if choice == 1:
            image_types = ["vertical"]
        elif choice == 2:
            image_types = ["horizontal"]
        elif choice == 3:
            image_types = ["square"]
        elif choice == 4:
            image_types = ["vertical", "horizontal"]
        elif choice == 5:
            image_types = ["vertical", "square"]
        elif choice == 6:
            image_types = ["horizontal", "square"]
        elif choice == 7:
            image_types = ["vertical", "horizontal", "square"]
        else:
            print("Invalid choice. Please enter a number between 1 and 7.")
            continue  # Ask the user to input a valid choice
        
        break  # Break the loop if a valid choice is made
    
    # Calculate total cost
    total_keywords = sum(1 for line in open(keyword_file_path))
    total_images = total_keywords * num_prompts_per_keyword * num_images * len(image_types)
    total_cost = total_images * 0.002
    print(f"Total cost for generating {total_images} images: ${total_cost:.2f}")
    
    # Ask if the user wishes to continue
    continue_response = input("Do you wish to continue? (y/n): ").lower()
    if continue_response != "y":
        print("Operation canceled.")
        return
    
    date_folder = generate_prompt_from_keyword(keyword_file_name, num_prompts_per_keyword)
    
    if date_folder is None:
        print("Prompt generation failed. Exiting.")
        return
    
    # Call the bulk image creation function
    bulk_image_creation(date_folder, num_images, image_types)

if __name__ == "__main__":
    main()
