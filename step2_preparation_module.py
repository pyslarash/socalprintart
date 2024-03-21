from dotenv import load_dotenv
import os
from mockup_module import mockups
from final_generation_module import final_generation
from rename_module import rename

step_one_folder = os.getenv('STEP_ONE_FOLDER')
step_two_folder = os.getenv('STEP_TWO_FOLDER')

def main():
    date_folder = input("Enter the date you'd like to process: ")
    rename(date_folder)
    mockups(date_folder)
    final_generation(date_folder)    
    
if __name__ == "__main__":
    main()