import os
import re
import subprocess


def detect_dependencies_regex(code):
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


def filter_dependencies_builtin(dependencies):
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
    }

    dependencies_to_install = [dep for dep in dependencies if dep not in builtin_modules]

    if dependencies_to_install:
        print(f"Dependencies to install: {dependencies_to_install}")
    else:
        print("No dependencies to install")

    return dependencies_to_install


def mapping_dependencies(dependency):
    mapping = {"cv2": "opencv-python", "PIL": "Pillow", "sklearn": "scikit-learn", "yaml": "PyYAML", "bs4": "beautifulsoup4", "requests_oauthlib": "requests-oauthlib", "jwt": "PyJWT", "dateutil": "python-dateutil", "serial": "pyserial", "win32api": "pywin32", "psutil": "psutil", "lxml": "lxml"}
    return mapping.get(dependency, dependency)


def check_package_installed(package_name, venv_path):
    """
    Verifica si un paquete está instalado en el entorno virtual.
    """
    if os.name == "nt":
        pip_exe = os.path.join(venv_path, "Scripts", "pip.exe")
    else:
        pip_exe = os.path.join(venv_path, "bin", "pip")

    if not os.path.exists(pip_exe):
        return False

    try:
        # Usar pip show para verificar si el paquete está instalado
        result = subprocess.run(
            [pip_exe, "show", package_name], 
            capture_output=True, 
            text=True, 
            timeout=30
        )
        return result.returncode == 0
    except Exception:
        return False


def filter_already_installed(dependencies, venv_path):
    """
    Filtra las dependencias que ya están instaladas en el entorno virtual.
    """
    not_installed = []
    already_installed = []
    
    for dep in dependencies:
        dep_package = mapping_dependencies(dep)
        if check_package_installed(dep_package, venv_path):
            already_installed.append(dep)
        else:
            not_installed.append(dep)
    
    if already_installed:
        print(f"Already installed (skipping): {already_installed}")
    
    if not_installed:
        print(f"Need to install: {not_installed}")
    else:
        print("All dependencies are already installed")
    
    return not_installed


def install_dependencies(dependencies, venv_path):
    if not dependencies:
        return True

    if os.name == "nt":
        pip_exe = os.path.join(venv_path, "Scripts", "pip.exe")
    else:
        pip_exe = os.path.join(venv_path, "bin", "pip")

    if not os.path.exists(pip_exe):
        print(f"Error: pip executable not found at {pip_exe}")
        return False

    correct_installed = []
    incorrect_installed = []

    for dep in dependencies:
        dep_package = mapping_dependencies(dep)
        try:
            print(f"Installing {dep_package}...")
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

    return len(incorrect_installed) == 0


def process_code_and_install_dependencies(code, file_path):
    dependencies = detect_dependencies_regex(code)
    dependencies_to_install = filter_dependencies_builtin(dependencies)
    if not dependencies_to_install:
        return

    venv_path = os.path.join(file_path, "venv")
    if not os.path.exists(venv_path):
        print(f"Dont exists venv at {venv_path}")
        return

    # Nueva funcionalidad: filtrar dependencias ya instaladas
    dependencies_not_installed = filter_already_installed(dependencies_to_install, venv_path)
    
    # Solo instalar las que no están instaladas
    if dependencies_not_installed:
        install_dependencies(dependencies_not_installed, venv_path)
    else:
        print("No new dependencies to install")