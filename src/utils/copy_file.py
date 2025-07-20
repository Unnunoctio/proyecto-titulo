import shutil

def copy_file(src, dst):
    try:
        shutil.copy(src, dst)
    except Exception as e:
        print(f"Error copying file: {e}")
        raise e