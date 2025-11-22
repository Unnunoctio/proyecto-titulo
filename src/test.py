import json


folder_name = "bp1-5593c2e2-e9c4-40e1-8815-f41001a6f003"

best_solutions = json.load(open("generations/" + folder_name + "/best_solutions.json"))
best_solutions = sorted(best_solutions, key=lambda x: (x["code_output"]["total_boxes_used"], x["code_time"]))

for s in best_solutions:
    print(f"{s["solution_type"]} & {s["epoch"]} & {int(s["code_output"]["total_boxes_used"])} & {s["code_time"]:.3f}s \\\\")

best_solution = json.load(open("generations/" + folder_name + "/best_solution.json"))

print("#############################")
print(f"{best_solution["solution_type"]} - {best_solution["code_output"]["total_boxes_used"]}")