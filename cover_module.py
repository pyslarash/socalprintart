from dotenv import load_dotenv
import os
from PIL import Image

# Load environment variables from .env file
load_dotenv()

generated_folder = os.getenv('GENERATED_FOLDER')
final_folder = os.getenv('FINAL_FOLDER')
logo_path = "logo/logo.png"

# Function to resize the logo proportionally to fit 200px on the shortest edge
def resize_logo(logo_path):
    logo = Image.open(logo_path)
    width, height = logo.size
    if width < height:
        new_width = 100
        new_height = int(100 * height / width)
    else:
        new_height = 100
        new_width = int(100 * width / height)
    return logo.resize((new_width, new_height))

# Function to create a collage with images
def create_collage(images, orientation):
    # Determine collage dimensions based on orientation
    if orientation == 'horizontal':
        max_images_per_row = 4
        max_images_per_col = 5
    elif orientation == 'vertical':
        max_images_per_row = 5
        max_images_per_col = 4
    elif orientation == 'square':
        max_images_per_row = 4
        max_images_per_col = 4
    else:
        print("Couldn't find the right orientation")
        return None

    # Calculate the dimensions of the collage
    num_images = len(images)
    num_rows = min(num_images, max_images_per_col)
    num_cols = min(num_images, max_images_per_row)
    img_width, img_height = images[0].size
    collage_width = num_cols * img_width
    collage_height = num_rows * img_height

    # Create a blank canvas for the collage
    collage = Image.new('RGB', (collage_width, collage_height), color='white')

    # Paste each image onto the canvas
    for i, img in enumerate(images):
        row = i // num_cols
        col = i % num_cols
        x_offset = col * img_width
        y_offset = row * img_height
        collage.paste(img, (x_offset, y_offset))

    # Resize the collage to 800x800 pixels
    collage = collage.resize((800, 800))

    return collage

def main():
    # Ask the user to enter the date folder name
    date_folder = input("Enter the date folder name (e.g., 2024-03-18): ")

    # Define the final folder path
    final_date_folder = os.path.join(final_folder, date_folder)

    # Create final folder if it doesn't exist
    os.makedirs(final_date_folder, exist_ok=True)

    # Define the path to the orientation folder
    date_folder_path = os.path.join(generated_folder, date_folder)
    
    # Get a list of all keyword folders
    keyword_folders = [f.name for f in os.scandir(date_folder_path) if f.is_dir()]

    for keyword_folder in keyword_folders:
        # Define the path to the keyword folder
        keyword_folder_path = os.path.join(date_folder_path, keyword_folder)
        
        # Get a list of all orientation folders within the keyword folder
        orientation_folders = [f.path for f in os.scandir(keyword_folder_path) if f.is_dir()]

        for orientation_folder in orientation_folders:
            # Determine orientation from the folder name
            orientation = os.path.basename(orientation_folder)

            images = []
            # Iterate through image files in orientation folder
            for img_file in os.listdir(orientation_folder):
                if img_file.endswith(('.jpg', '.jpeg', '.png')):
                    img_path = os.path.join(orientation_folder, img_file)
                    img = Image.open(img_path)
                    images.append(img)

            # Create collage with the images
            collage = create_collage(images, orientation)

            # Define the path to the keyword subfolder in final folder
            keyword_subfolder = os.path.join(final_date_folder, keyword_folder, "collages")
            os.makedirs(keyword_subfolder, exist_ok=True)

            # Save the collage in the keyword subfolder
            collage_filename = f"{orientation}.jpg"
            collage_path = os.path.join(keyword_subfolder, collage_filename)
            collage.save(collage_path)

    print("Collages created and saved successfully.")

if __name__ == "__main__":
    main()
