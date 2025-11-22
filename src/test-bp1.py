import json
import os
from pathlib import Path
import shutil
import ast
from utils.code_executor import CodeExecutor as CE

# BP1U
folder_names = [
    "bp1-a4df00e2-5b55-46a5-beb9-3d010b896586", # 5-5
    "bp1-c4b48209-bdaa-4e47-96b5-31e11d3186a5", # 5-15
    "bp1-7b17270d-c9a3-47b6-a896-1b144c8a4e92", # 15-5
    "bp1-5593c2e2-e9c4-40e1-8815-f41001a6f003", # 15-15
]

best_solutions = [
    json.load(open("generations/" + fn + "/best_solution.json"))
    for fn in folder_names
]

data = [
    "u120 01 & 150 & 120 & 49 & ",
    "u120 02 & 150 & 120 & 46 & ",
    "u120 03 & 150 & 120 & 49 & ",
    "u120 04 & 150 & 120 & 50 & ",
    "u250 01 & 150 & 250 & 100 & ",
    "u250 02 & 150 & 250 & 102 & ",
    "u250 03 & 150 & 250 & 100 & ",
    "u250 04 & 150 & 250 & 101 & ",
    "u500 01 & 150 & 500 & 201 & ",
    "u500 02 & 150 & 500 & 202 & ",
    "u500 03 & 150 & 500 & 204 & ",
    "u500 04 & 150 & 500 & 206 & ",
    "u1000 01 & 150 & 1000 & 406 & ",
    "u1000 02 & 150 & 1000 & 411 & ",
]

# Paso 1 - change name instance to instance-base-bp1-pre
os.rename("instances/instance-base-bp1.txt", "instances/instance-base-bp1-pre.txt")

# Paso 2 - recorrer las instancias, copiarlas en la carpeta instances, cambiar el nombre, y ejecutar cada codigo
for i, file in enumerate(sorted(Path("data/bp1d").iterdir()), start=1):
    if file.is_file():
        # print(f"file name: {file.name}")
        # continue
        shutil.copy2(file, "instances/instance-base-bp1.txt")

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
            
            value = int(result_dict["total_boxes_used"])
            if i == len(best_solutions) - 1:
                results += f"{value} \\\\"
            else:
                results += f"{value} & "

        os.remove("instances/instance-base-bp1.txt")
        # Paso 4 - guardar los resultados
        print(results)

os.rename("instances/instance-base-bp1-pre.txt", "instances/instance-base-bp1.txt")