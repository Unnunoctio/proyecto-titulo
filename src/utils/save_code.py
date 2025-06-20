import os
import re
from typing import Optional, Tuple


def save_code(folder_path: str, file_name: str, content: str) -> Tuple[bool, Optional[Exception]]:
    try:
        match = re.search(r"```python\n(.*?)```", content, re.DOTALL)
        code = match.group(1) if match else content

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        with open(os.path.join(folder_path, file_name), "w") as f:
            f.write(code)

        return True, None
    except Exception as e:
        print(f"Error saving code: {e}")
        return False, e
