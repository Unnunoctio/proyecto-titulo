import json


folder_name = "jsp-0d40132b-cee3-4e37-9492-667d25c72f61"

best_solutions = json.load(open("generations/" + folder_name + "/best_solutions.json"))
best_solutions = sorted(best_solutions, key=lambda x: (x["code_output"]["makespan"], x["code_time"]))

for s in best_solutions:
    print(f"{s["solution_type"]} & {s["epoch"]} & {int(s["code_output"]["makespan"])} & {s["code_time"]:.3f}s \\\\")

best_solution = json.load(open("generations/" + folder_name + "/best_solution.json"))

print("#############################")
print(f"{best_solution["solution_type"]} - {best_solution["code_output"]["makespan"]}")