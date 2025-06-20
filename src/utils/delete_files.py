import os
import shutil

def delete_files(folder_path, file_names):
    for file_name in file_names:
        file_path = os.path.join(folder_path, file_name)
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Error deleting file: {e}")

def delete_folder(folder_path, folder_name):
    try:
        delete_folder_path = os.path.join(folder_path, folder_name)
        shutil.rmtree(delete_folder_path)
    except Exception as e:
        print(f"Error deleting folder: {e}")