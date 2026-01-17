import json
import os
from pathlib import Path
import shutil
import ast
from utils.code_executor import CodeExecutor as CE

# SCP
folder_names = [
    "jsp-9dea287a-62bb-486c-9578-ad03c9da7a35", # 5-5
    "jsp-1cd7e2fc-ac07-41db-b5c5-08bde92d5e41", # 5-15
    "jsp-dfceb6da-f48a-4637-8d18-9fb8e31e2be3", # 15-5
    "jsp-0d40132b-cee3-4e37-9492-667d25c72f61", # 15-15
]

best_solutions = [
    json.load(open("generations/" + fn + "/best_solution.json"))
    for fn in folder_names
]

data_abz = [
    "ABZ5 & 10 X 10 & 1234 & ",
    "ABZ7 & 15 X 20 & 668 & ",
    "ABZ8 & 15 X 20 & 687 & ",
    "ABZ9 & 15 X 20 & 707 & ",
]

data = [
    "LA19 & 10 X 10 & 842 & ",
    "LA20 & 10 X 10 & 902 & ",
    "LA21 & 10 X 15 & 1053 & ",
    "LA24 & 10 X 15 & 935 & ",
    "LA25 & 10 X 15 & 977 & ",
]

# Paso 1 - change name instance to instance-base-scp-pre
os.rename("instances/instance-base-jsp.txt", "instances/instance-base-jsp-pre.txt")

# Paso 2 - recorrer las instancias, copiarlas en la carpeta instances, cambiar el nombre, y ejecutar cada codigo
for i, file in enumerate(sorted(Path("data/jsp").iterdir()), start=1):
    if file.is_file():
        shutil.copy2(file, "instances/instance-base-jsp.txt")

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
            
            value = int(result_dict["makespan"])
            if i == len(best_solutions) - 1:
                results += f"{value} \\\\"
            else:
                results += f"{value} & "

        os.remove("instances/instance-base-jsp.txt")
        # Paso 4 - guardar los resultados
        print(results)

os.rename("instances/instance-base-jsp-pre.txt", "instances/instance-base-jsp.txt")