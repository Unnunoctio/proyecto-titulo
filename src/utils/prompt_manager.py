import importlib.util
from pathlib import Path
from typing import Callable

class PromptManager:
    BASE_DIR = Path("src/core/prompts")
    SYSTEM_DIR = BASE_DIR / "systems"
    USER_DIR = BASE_DIR / "users"
    _module_cache = {}

    # ==========================================================
    #   SYSTEM PROMPTS ESTÁTICOS (ARCHIVOS .TXT)
    # ==========================================================
    @classmethod
    def get_system_prompt(cls, role: str, name: str) -> str:
        path = cls.SYSTEM_DIR / role / f"{name}.txt"

        if not path.exists():
            raise FileNotFoundError(f"System prompt not found: {path}")
        
        return path.read_text(encoding="utf-8").strip()
    
    # ==========================================================
    #   MÓDULOS DE USUARIO (PYTHON BUILDERS)
    # ==========================================================
    @classmethod
    def _load_module(cls, name: str):
        """Carga y cachea dinámicamente un módulo de user prompts."""
        if name in cls._module_cache:
            return cls._module_cache[name]

        module_path = cls.USER_DIR / f"{name}.py"
        if not module_path.exists():
            raise FileNotFoundError(f"User prompt not found: {module_path}")

        spec = importlib.util.spec_from_file_location(f"core.prompts.users.{name}", module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        cls._module_cache[name] = module
        return module

    @classmethod
    def get_user_prompt(cls, role: str, name: str, **kwargs) -> str:
        # if role not in ("reasoner", "coder"):
        #     raise ValueError(f"Invalid role: {role}")
        
        module = cls._load_module(name)
        func_name = f"build_{role}_prompt"

        if not hasattr(module, func_name):
            raise AttributeError(f"Module {module} does not have a function named {func_name}")
        
        func: Callable = getattr(module, func_name)
        return func(**kwargs)