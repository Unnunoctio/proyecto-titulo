import ast
import os
import re
import subprocess


def detect_dependencies(code):
    dependencies = set()

    try:
        tree = ast.parse(code)

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module = alias.name.split(".")[0]
                    dependencies.add(module)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    module = node.module.split(".")[0]
                    dependencies.add(module)

        return list(dependencies)
    except Exception as e:
        print(f"Error detecting dependencies: {e}, using regex method")
        return detect_dependencies_regex(code)


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
            subprocess.run([pip_exe, "install", dep_package], capture_output=True, text=True, check=True, timeout=120)
            correct_installed.append(dep)
        except subprocess.TimeoutExpired:
            incorrect_installed.append(dep)
        except subprocess.CalledProcessError:
            incorrect_installed.append(dep)
        except Exception:
            incorrect_installed.append(dep)

    print(f"Correctly installed: {correct_installed}")
    if incorrect_installed:
        print(f"Incorrectly installed: {incorrect_installed}")

    return len(incorrect_installed) == 0


def process_code_and_install_dependencies(code, file_path):
    dependencies = detect_dependencies(code)
    dependencies_to_install = filter_dependencies_builtin(dependencies)
    if not dependencies_to_install:
        return

    venv_path = os.path.join(file_path, "venv")
    if not os.path.exists(venv_path):
        print(f"Dont exists venv at {venv_path}")
        return

    print(f"Installing dependencies to {venv_path}")
    install_dependencies(dependencies_to_install, venv_path)
