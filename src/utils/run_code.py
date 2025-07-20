import os
import subprocess
from typing import Optional, Tuple
from config import RUN_CODE_TIMEOUT


def run_code(folder_path: str, file_name: str) -> Tuple[str, bool, Optional[Exception]]:
    try:
        venv_path = os.path.join(folder_path, "venv")
        if not os.path.exists(venv_path):
            print(f"Dont exists venv at {venv_path}")
            return "", True, Exception(f"Dont exists venv at {venv_path}")
        
        if os.name == 'nt':
            python_exe = os.path.join(venv_path, 'Scripts', 'python.exe')
        else:
            python_exe = os.path.join(venv_path, 'bin', 'python')
        
        if not os.path.exists(python_exe):
            print(f"Error: python executable not found at {python_exe}")
            return "", True, Exception(f"Error: python executable not found at {python_exe}")

        script_path = os.path.join(folder_path, file_name)
        if not os.path.exists(script_path):
            print(f"Error: script not found at {script_path}")
            return "", True, Exception(f"Error: script not found at {script_path}")

        print(f"Running code with python {python_exe} and script {script_path}")
        result = subprocess.run(
            [python_exe, script_path],
            capture_output=True,
            text=True,
            timeout=RUN_CODE_TIMEOUT
        )
        
        if result.returncode != 0:
            return "", True, Exception(f"Error running code: {result.stderr}")
        
        print("Code ran successfully")
        return result.stdout.strip(), False, None
    except subprocess.TimeoutExpired:
        print("Timeout expired while running code")
        return "", True, Exception("Timeout expired while running code")
    except Exception as e:
        print(f"Error running code: {e}")
        return "", True, e
