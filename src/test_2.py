import os
import time
import ast

from core.models import CodeGenerated
from utils.code_executor import CodeExecutor

def get_best_code(path: str, last_epoch: int) -> CodeGenerated:
    generations = {}
    with open(os.path.join("src", "data", path), "r", encoding="utf-8") as f:
        content = f.read().strip()
        data_list = eval(content)

        for data in data_list:
            cg = CodeGenerated(
                code_id=data["code_id"],
                father_code_id=data["father_code_id"],
                epoch=data["epoch"],
                solution_type=data["solution_type"],
                solution_cross=data["solution_cross"],
                version=data["version"],
                code_path=data["code_path"],
                result=data["result"],
                execution_time=data["execution_time"],
                error=data["error"],
            )
            generations[cg.code_id] = cg

    # for code_id, code_obj in generations.items():
    #     if code_obj.result is not None and code_obj.result["total_boxes_used"] < 49:
    #         print(f"{code_obj.solution_type} & {code_obj.epoch} & {code_obj.result["total_boxes_used"]} & {round(code_obj.execution_time, 3)}s")


    best_codes = []

    for code_id, code_obj in generations.items():
        if code_obj.result is not None and code_obj.epoch == last_epoch:
            father = generations[code_obj.father_code_id]

            if father.result["total_boxes_used"] == 0 and code_obj.result["total_boxes_used"] == 0:
                continue

            if father.result["total_boxes_used"] == 0:
                best_codes.append(code_obj)
                continue
            if code_obj.result["total_boxes_used"] == 0:
                best_codes.append(father)
                continue

            if father.result["total_boxes_used"] < code_obj.result["total_boxes_used"]:
                best_codes.append(father)
            elif father.result["total_boxes_used"] == code_obj.result["total_boxes_used"]:
                if father.execution_time < code_obj.execution_time:
                    best_codes.append(father)
                else:
                    best_codes.append(code_obj)
            else:
                best_codes.append(code_obj)

    # # ordenar por nombre
    # best_codes.sort(key=lambda x: x.solution_type)

    # table = ""

    # for code_obj in best_codes:
    #     line = f"{code_obj.solution_type} & {code_obj.epoch} & {code_obj.result["total_boxes_used"]} & {round(code_obj.execution_time, 3)}s \\\\"
    #     table += line + "\n"
    # print(table)

    # print(table)
    # print("------------------------------")
    # print("Solution Type: ", code_obj.solution_type)
    # print("Epoch:", code_obj.epoch)
    # print("Total Cost:", code_obj.result['total_cost'])
    # print("Execution Time:", code_obj.execution_time)

    best_codes.sort(key=lambda x: (x.result["total_boxes_used"], x.execution_time))
    return best_codes[0]


best_1 = get_best_code("results_binpack1_5_5_individual_best.txt", 5)
print("-----------------------------")
best_2 = get_best_code("results_binpack1_5_15_individual_best.txt", 15)
print("-----------------------------")
best_3 = get_best_code("results_binpack1_15_5_individual_best.txt", 5)
print("-----------------------------")
best_4 = get_best_code("results_binpack1_15_15_individual_best.txt", 15)

print(best_1.result["total_boxes_used"])
print(best_2.result["total_boxes_used"])
print(best_3.result["total_boxes_used"])
print(best_4.result["total_boxes_used"])

instances_path = [
    "src\\test\\binpack1_instances\\u120_01_49.txt",
    "src\\test\\binpack1_instances\\u120_02_46.txt",
    "src\\test\\binpack1_instances\\u120_03_49.txt",
    "src\\test\\binpack1_instances\\u120_04_50.txt",
    "src\\test\\binpack1_instances\\u250_01_100.txt",
    "src\\test\\binpack1_instances\\u250_02_102.txt",
    "src\\test\\binpack1_instances\\u250_03_100.txt",
    "src\\test\\binpack1_instances\\u250_04_101.txt",
    "src\\test\\binpack1_instances\\u500_01_201.txt",
    "src\\test\\binpack1_instances\\u500_02_202.txt",
    "src\\test\\binpack1_instances\\u500_03_204.txt",
    "src\\test\\binpack1_instances\\u500_04_206.txt",
    "src\\test\\binpack1_instances\\u1000_01_406.txt",
    "src\\test\\binpack1_instances\\u1000_02_411.txt",
    "src\\test\\binpack1_instances\\u1000_03_411.txt",
    "src\\test\\binpack1_instances\\u1000_04_397.txt",
]

best_codes = [
    best_1,
    best_2,
    best_3,
    best_4,
]

codes_folders = [
    "src\\test\\binpack1_5_5_individual_best",
    "src\\test\\binpack1_5_15_individual_best",
    "src\\test\\binpack1_15_5_individual_best",
    "src\\test\\binpack1_15_15_individual_best",
]

for instance_path in instances_path:
    with open(instance_path, "r", encoding="utf-8") as f:
        data = f.read()

    with open(os.path.join("instances", "instance.txt"), "w", encoding="utf-8") as f:
        f.write(data)

    for i in range(len(best_codes)):
        best_code = best_codes[i]
        code_folder = codes_folders[i]

        CodeExecutor.FOLDER_PATH = code_folder
        start = time.time()
        result, error = CodeExecutor.execute_code(file_name=best_code.code_path)
        end = time.time()
        result_dict = ast.literal_eval(result)
        print(f"""
            instance: {instance_path}
            code type: {best_code.solution_type}
            execution time: {end - start}
            value: {result_dict['total_boxes_used']}
            -------------------------------------
        """)
    print("##################################################")

# # ordenar por nombre
# best_codes.sort(key=lambda x: x.solution_type)

# table = ""

# for code_obj in best_codes:
#     line = f"{code_obj.solution_type} & {code_obj.epoch} & {code_obj.result['total_cost']} & {round(code_obj.execution_time, 3)}s \\\\"
#     table += line + "\n"

# print(table)
    # print("------------------------------")
    # print("Solution Type: ", code_obj.solution_type)
    # print("Epoch:", code_obj.epoch)
    # print("Total Cost:", code_obj.result['total_cost'])
    # print("Execution Time:", code_obj.execution_time)


