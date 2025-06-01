import os
import re

from llm_models.class_deepseek_llm import Deepseek_LLM

PROBLEM = """
Una empresa desea optimizar la disposición de diversos paquetes rectangulares dentro de contenedores rectangulares, con el objetivo de minimizar la cantidad de contenedores utilizados.
Cada paquete posee un ancho y una altura determinados, y debe ser ubicado completamente dentro de un único contenedor, sin superponerse con otros paquetes.
El objetivo es determinar la asignación y la posición de cada paquete dentro de los contenedores, cumpliendo con las siguientes condiciones:
- Cada paquete debe estar completamente contenido dentro de un contenedor.
- No debe existir superposición entre paquetes.
- Los paquetes no pueden ser rotados.
- Se debe minimizar la cantidad total de contenedores utilizados.

La información de entrada se proporcionará mediante un archivo de texto (.txt) llamado "instance.txt" en la carpeta "instances", con el siguiente formato:
<cantidad_de_paquetes>
<ancho_1> <alto_1>
<ancho_2> <alto_2>
...
<ancho_n> <alto_n>

<cantidad_de_contenedores>
<ancho_1> <alto_1>
<ancho_2> <alto_2>
...
<ancho_m> <alto_m>
"""

output_schema = Deepseek_LLM().generate_output_schema(PROBLEM)
print(output_schema)
print("\n-----------------------------------")
first_problems_prompts = Deepseek_LLM().generate_first_problems_prompts(PROBLEM, output_schema)

generation = 1
counter = 1
for prompt in first_problems_prompts:
    prompt = f"""
        ------------PROBLEM-------------
        {PROBLEM}
        ------------PROMPT-------------
        {prompt}
    """
    generated_code = Deepseek_LLM().generate_code(prompt)

    match = re.search(r"```python\n(.*?)```", generated_code, re.DOTALL)
    code = match.group(1) if match else generated_code

    file_name = f"generations/gen-{generation}-code-{counter}.py"

    if not os.path.exists("generations"):
        os.makedirs("generations")

    with open(file_name, "w") as f:
        f.write(code)

    counter += 1
