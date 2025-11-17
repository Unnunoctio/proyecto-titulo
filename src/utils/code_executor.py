import os
import re
import subprocess
from typing import List, Tuple, Optional, Dict

class CodeExecutor:
    FOLDER_PATH: str = "generations"

    @classmethod
    def create_venv(cls):
        try:
            if not os.path.exists(cls.FOLDER_PATH):
                os.makedirs(cls.FOLDER_PATH)
        
            # Create a virtual environment
            venv_path = os.path.join(cls.FOLDER_PATH, "venv")
            os.system(f"python -m venv {venv_path}")
            print("Virtual environment created")
        except Exception as e:
            raise Exception(f"Error creating virtual environment: {e}")

    @classmethod
    def _detect_dependencies_regex(cls, code: str) -> List[str]:
        dependencies = set()

        patterns = [r"^import\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)", r"^from\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)\s+import"]
        lines = code.split("\n")

        for line in lines:
            line = line.strip()
            for pattern in patterns:
                match = re.search(pattern, line)
                if match:
                    module = match.group(1).split(".")[0]
                    dependencies.add(module)

        return list(dependencies)

    @classmethod
    def _filter_dependencies_builtin(cls, dependencies: List[str]) -> List[str]:
        builtin_modules = {
            "os",
            "sys",
            "json",
            "datetime",
            "re",
            "math",
            "random",
            "time",
            "collections",
            "itertools",
            "functools",
            "operator",
            "string",
            "io",
            "pathlib",
            "glob",
            "shutil",
            "tempfile",
            "urllib",
            "http",
            "socket",
            "threading",
            "multiprocessing",
            "subprocess",
            "argparse",
            "logging",
            "unittest",
            "pickle",
            "csv",
            "sqlite3",
            "hashlib",
            "base64",
            "binascii",
            "struct",
            "array",
            "copy",
            "types",
            "inspect",
            "gc",
            "weakref",
            "abc",
            "contextlib",
            "warnings",
            "traceback",
            "platform",
            "site",
            "importlib",
            "pkgutil",
            "zipfile",
            "tarfile",
            "gzip",
            "bz2",
            "lzma",
            "zlib",
            "email",
            "smtplib",
            "imaplib",
            "poplib",
            "ftplib",
            "telnetlib",
            "xmlrpc",
            "html",
            "xml",
            "cgi",
            "cgitb",
            "wsgiref",
            "heapq",
            "bisect",
            "queue",
            "enum",
            "decimal",
            "fractions",
            "statistics",
            "secrets",
            "typing"
        }

        dependencies_to_install = [dep for dep in dependencies if dep not in builtin_modules]
        return dependencies_to_install

    @classmethod
    def _mapping_dependencies(cls, dependency: str) -> str:
        mapping = {"cv2": "opencv-python", "PIL": "Pillow", "sklearn": "scikit-learn", "yaml": "PyYAML", "bs4": "beautifulsoup4", "requests_oauthlib": "requests-oauthlib", "jwt": "PyJWT", "dateutil": "python-dateutil", "serial": "pyserial", "win32api": "pywin32", "psutil": "psutil", "lxml": "lxml"}
        return mapping.get(dependency, dependency)

    @classmethod
    def _check_package_installed(cls, package: str) -> bool:
        venv_path = os.path.join(cls.FOLDER_PATH, "venv")
        
        if os.name == "nt":
            pip_exe = os.path.join(venv_path, "Scripts", "pip.exe")
        else:
            pip_exe = os.path.join(venv_path, "bin", "pip")

        if not os.path.exists(pip_exe):
            return False

        try:
            # Usar pip show para verificar si el paquete está instalado
            result = subprocess.run(
                [pip_exe, "show", package], 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            return result.returncode == 0
        except Exception:
            return False

    @classmethod
    def _filter_already_installed(cls, dependencies: List[str]) -> List[str]:
        not_installed = []
        already_installed = []
        
        for dep in dependencies:
            dep_package = cls._mapping_dependencies(dep)
            if cls._check_package_installed(dep_package):
                already_installed.append(dep)
            else:
                not_installed.append(dep)
        
        return not_installed

    @classmethod
    def _install_dependencies(cls, dependencies: List[str]):
        venv_path = os.path.join(cls.FOLDER_PATH, "venv")

        if not dependencies:
            print("No dependencies to install")
            return

        if os.name == "nt":
            pip_exe = os.path.join(venv_path, "Scripts", "pip.exe")
        else:
            pip_exe = os.path.join(venv_path, "bin", "pip")

        if not os.path.exists(pip_exe):
            raise Exception("pip executable not found. Please create the virtual environment first.")
        
        # Instalar las dependencias
        correct_installed = []
        incorrect_installed = []

        for dep in dependencies:
            dep_package = cls._mapping_dependencies(dep)
            try:
                subprocess.run([pip_exe, "install", dep_package], capture_output=True, text=True, check=True, timeout=120)
                correct_installed.append(dep)
            except subprocess.TimeoutExpired:
                print(f"Timeout installing {dep_package}")
                incorrect_installed.append(dep)
            except subprocess.CalledProcessError as e:
                print(f"Error installing {dep_package}: {e}")
                incorrect_installed.append(dep)
            except Exception as e:
                print(f"Unexpected error installing {dep_package}: {e}")
                incorrect_installed.append(dep)

        print(f"Correctly installed: {correct_installed}")
        if incorrect_installed:
            print(f"Incorrectly installed: {incorrect_installed}")

    @classmethod
    def install_all_dependencies(cls, file_name: str):
        if not os.path.exists(os.path.join(cls.FOLDER_PATH, "venv")):
            cls.create_venv()

        # all_dependencies_to_install = set()
        # for file_name in file_names:
        with open(os.path.join(cls.FOLDER_PATH, file_name), "r") as f:
            code = f.read()
            dependencies = cls._detect_dependencies_regex(code)
            dependencies_to_install = cls._filter_dependencies_builtin(dependencies)
            if not dependencies_to_install:
                return
            
            not_installed = cls._filter_already_installed(dependencies_to_install)
            if not not_installed:
                return

            # all_dependencies_to_install.update(not_installed)
        
        print(f"Dependencies to install: {not_installed}")
        cls._install_dependencies(not_installed)

    @classmethod
    def save_code(cls, file_name: str, code: str):
        try:
            if not os.path.exists(cls.FOLDER_PATH):
                os.makedirs(cls.FOLDER_PATH)

            with open(os.path.join(cls.FOLDER_PATH, file_name), "w", encoding="utf-8") as f:
                f.write(code)
        except Exception as e:
           raise Exception(f"Error saving code: {e}")
        
    @classmethod
    def get_code(cls, file_name: str) -> str:
        code_path = os.path.join(cls.FOLDER_PATH, file_name)
        if not os.path.exists(code_path):
            return None
        
        with open(code_path, "r", encoding="utf-8") as f:
            code = f.read()
        
        return code
    
    @classmethod
    def execute_code(cls, file_name: str, timeout: int = 30) -> Tuple[Optional[str], Optional[Exception]]:
        venv_path = os.path.join(cls.FOLDER_PATH, "venv")
        
        try:
            if os.name == "nt":
                python_exe = os.path.join(venv_path, "Scripts", "python.exe")
            else:
                python_exe = os.path.join(venv_path, "bin", "python")
            
            if not os.path.exists(python_exe):
                return None, Exception("Python executable not found. Please create the virtual environment first.")
            
            code_path = os.path.join(cls.FOLDER_PATH, file_name)
            if not os.path.exists(code_path):
                return None, Exception(f"Code file not found: {code_path}")

            result = subprocess.run(
                [python_exe, code_path], 
                capture_output=True, 
                text=True, 
                timeout=timeout
            )

            if result.returncode != 0:
                return None, Exception(f"Error executing code: {result.stderr}")
            
            return result.stdout.strip(), None
        except subprocess.TimeoutExpired:
            return None, Exception(f"Timeout executing code: {file_name}")
        except Exception as e:
            return None, Exception(f"Unexpected error executing code: {file_name}: {e}")

    @classmethod
    def execute_function_memory(cls, function_code: str, function_name:str, data: Dict):
        try:
            # # Create a namespace for the function
            # execution_namespace = {}
            # exec(function_code, {}, execution_namespace)

            # # Call the function
            # result = execution_namespace[function_name](data)
            # execution_namespace.clear() # Limpiar la memoria
            exec(function_code, globals())
            result = globals()[function_name](data)
            return result
        except Exception as e:
            print(f"Error executing function: {e}")
            return None
