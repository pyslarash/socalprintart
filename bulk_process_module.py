from single_set_module import stability_images
from dotenv import load_dotenv
import os

def bulk_image_creation(date_folder, num_images, image_types):
    # Generate images for each image type
    for image_type in image_types:
        stability_images(date_folder, num_images, image_type)

def main():
    load_dotenv()
    num_images = int(input("Enter the number of images to generate per set: "))
    date_folder = input("Enter the date folder: ")
    
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
    
    bulk_image_creation(date_folder, num_images, image_types)

if __name__ == "__main__":
    main()