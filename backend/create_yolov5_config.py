import yaml
import os

def create_yolov5_yaml(project_root):
    """
    Creates the YOLOv5 data.yaml file from the uploaded dataset files.
    """
    # Define file paths relative to the project_root
    train_file = os.path.join(project_root, 'train.txt')
    val_file = os.path.join(project_root, 'test.txt')
    names_file = os.path.join(project_root, 'classes.names')
    
    # 1. Read class names from your 'classes.names' file
    try:
        with open(names_file, 'r') as f:
            names = [line.strip() for line in f.readlines() if line.strip()]
        nc = len(names)
    except FileNotFoundError:
        print(f"Error: Could not find '{names_file}'. Please check the file name and path.")
        return
    
    # 2. Create the YOLOv5 data.yaml dictionary
    # YOLOv5 can directly use your train.txt and test.txt files which contain absolute image paths
    data = {
        'train': train_file, 
        'val': val_file,
        'nc': nc,           # Number of classes (4 in your case)
        'names': names      # ['prohibitory', 'danger', 'mandatory', 'other']
    }

    # 3. Save the dictionary to the YAML file
    yaml_file_path = os.path.join(project_root, 'traffic_sign_data.yaml')
    with open(yaml_file_path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False)
        
    print(f"Successfully created YOLOv5 config file: '{yaml_file_path}'")
    print("-" * 40)
    print(yaml.dump(data, default_flow_style=False))
    print("-" * 40)
    
# --- IMPORTANT: Set the Absolute Project Path ---
# The path in your train.txt/test.txt files is '/home/my_name/ts/...'.
# You MUST get the absolute path where those image and label files are stored.
# You can use your 'getting-full-path.py' script to find the correct path if needed.
# For example, if your traffic_sign data folder is /home/user/my_data/traffic_signs, 
# and inside that folder you have the images and label files (.txt), set PROJECT_DIR to:
PROJECT_DIR = '/home/my_name/ts/' # ADJUST THIS PATH! 

# NOTE: Since your train.txt contains absolute paths, we can use the root directory 
# of the data as the path to ensure the file lists are correctly read. 

create_yolov5_yaml(PROJECT_DIR)