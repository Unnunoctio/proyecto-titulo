import json
import os
from pathlib import Path
import shutil
import ast
from utils.code_executor import CodeExecutor as CE

# SCP
folder_names = [
    "f094c5a1-e3ae-49af-90ed-1cbb041822fa", # 5-5
    "5484f65c-c303-4ae6-b335-0925da113d5b", # 5-15
    "07a7d94d-9edc-44d8-a654-b6b487813641", # 15-5
    "d5235124-e61c-41eb-a305-bebf4745f169", # 15-15
]

best_solutions = [
    json.load(open("generations/" + fn + "/best_solution.json"))
    for fn in folder_names
]

data = [
    "4.1 & 200 & 1000 & 429 & ",
    "4.2 & 200 & 1000 & 512 & ",
    "5.1 & 200 & 2000 & 253 & ",
    "5.2 & 200 & 2000 & 302 & ",
    "A.1 & 300 & 3000 & 253 & ",
    "A.2 & 300 & 3000 & 252 & ",
    "B.2 & 300 & 3000 & 76 & ",
    "B.3 & 300 & 3000 & 80 & ",
    "C.1 & 400 & 4000 & 227 & ",
    "C.2 & 400 & 4000 & 219 & ",
    "D.1 & 400 & 4000 & 60 & ",
    "D.2 & 400 & 4000 & 66 & ",
    "E.1 & 50 & 500 & 5 & ",
    "E.2 & 50 & 500 & 5 & ",
]

# Paso 1 - change name instance to instance-base-scp-pre
os.rename("instances/instance-base-scp.txt", "instances/instance-base-scp-pre.txt")

# Paso 2 - recorrer las instancias, copiarlas en la carpeta instances, cambiar el nombre, y ejecutar cada codigo
for i, file in enumerate(sorted(Path("data/scp").iterdir()), start=1):
    if file.is_file():
        shutil.copy2(file, "instances/instance-base-scp.txt")

        # Paso 3 - ejecutar el codigo de cada best_solutions
        results = data[i-1]
        for i in range(len(best_solutions)):
            result, error = CE.execute_code(file_name=best_solutions[i]["code_path"])
            if error is not None and i == len(best_solutions) - 1:
                results += "- \\\\"
                continue
            elif error is not None and i != len(best_solutions) - 1:
                results += "- & "
                continue
            
            result_dict = ast.literal_eval(result)
            
            value = int(result_dict["total_cost"])
            if i == len(best_solutions) - 1:
                results += f"{value} \\\\"
            else:
                results += f"{value} & "

        os.remove("instances/instance-base-scp.txt")
        # Paso 4 - guardar los resultados
        print(results)

os.rename("instances/instance-base-scp-pre.txt", "instances/instance-base-scp.txt")