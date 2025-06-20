import os

def create_venv(folder_path: str):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    # Create virtual environment
    venv_path = os.path.join(folder_path, "venv")
    os.system(f"python -m venv {venv_path}")