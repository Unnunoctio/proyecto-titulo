import ast
import functools
import time
from typing import List

from config import COUNT_FIRST_PROBLEMS, COUNT_SELECTION_CODES, MAX_EPOCHS
from llm_models.class_llm import LLM
from utils.create_venv import create_venv
from utils.delete_files import delete_files, delete_folder
from utils.dependencies import process_code_and_install_dependencies
from utils.move_file import move_file
from utils.run_code import run_code
from utils.save_code import save_code


class GenericExpert:
    def __init__(self, LLModel: LLM):
        self.LLModel = LLModel
        self.output_schema = None

    def run_expert(self, problem):
        self.generate_solution_artifacts(problem)
        file_names = self.generate_first_generation(problem)

        epoch = 1
        best_score = None
        best_scores = []
        while True:
            output_scores, result_errors, timeout_errors, restriction_errors = self.run_generation(file_names)
            print(f"RESULTS ERRORS: {len(result_errors)}")
            print(f"TIMEOUT ERRORS: {len(timeout_errors)}")
            print(f"RESTRICTION ERRORS: {len(restriction_errors)}")

            print("SCORES")
            for score in output_scores:
                print("--------------------------------")
                print(f"File: {score['file_code']}\nScore: {score['score']}\nTime: {score['time']} seconds")

            epoch += 1
            if epoch > MAX_EPOCHS:
                best_score = self.select_best_score(output_scores + best_scores)
                break

            # Seleccionar mejores scores
            best_scores = self.select_best_scores(output_scores + best_scores)
            # ELIMINA LOS CODIGOS QUE NO SEAN LOS MEJORES
            # EVOLUCIONA X VECES CADA UNO DE LOS MEJORES
            # GENERA EL NUEVO FILE NAMES

        # PRINT BEST SCORE
        if best_score is None:
            print("No solution found")
        else:
            print("-------------------------")
            print("Best Solution")
            print(f"Score: {best_score['score']}")
            print(f"Time: {best_score['time']} seconds")
            print("-------------------------")

        self.clear_files(best_score["file_code"], [x for x in file_names if x != best_score['file_code']])


    def generate_solution_artifacts(self, problem):
        try:
            # Generate output schema
            output_schema = self.LLModel.generate_output_schema(problem)
            save_code("generations", "output_schema.py", output_schema)
            self.output_schema = output_schema
            print("Output schema generated successfully")
        except Exception as e:
            print(f"Error generating output schema: {e}")
            raise e

        try:
            # Generate validate restrictions for result
            prompt_restrictions = self.LLModel.generate_prompt_restrictions(problem)
            code_restrictions = self.LLModel.generate_code_restrictions(problem, prompt_restrictions, output_schema)
            save_code("src/generated", "restrictions.py", code_restrictions)
            print("Restrictions generated successfully")
        except Exception as e:
            print(f"Error generating prompt restrictions: {e}")
            raise e

        try:
            # Generate target function
            target_function = self.LLModel.generate_code_target_function(problem, output_schema)
            save_code("src/generated", "target_function.py", target_function)
            print("Target function generated successfully")
        except Exception as e:
            print(f"Error generating target function: {e}")
            raise e

    def generate_first_generation(self, problem) -> List[str]:
        try:
            # create a venv for generation codes
            create_venv("generations")
        except Exception as e:
            print(f"Error creating venv: {e}")
            raise e

        try:
            # Generate first prompts for code generation
            first_problems_prompts = self.LLModel.generate_first_problems_prompts(problem, self.output_schema, COUNT_FIRST_PROBLEMS)
        except Exception as e:
            print(f"Error generating first problems prompts: {e}")
            raise e

        try:
            # Generate code for each prompt
            file_names = []
            counter = 0
            for prompt in first_problems_prompts:
                counter += 1
                # File name
                file_name = f"gen-1-code-{counter}.py"

                # Generate code
                generated_code = self.LLModel.generate_code(problem, prompt, self.output_schema)
                save_code("generations", file_name, generated_code)

                # Process code and install dependencies
                process_code_and_install_dependencies(generated_code, "generations")

                file_names.append(file_name)

            return file_names
        except Exception as e:
            print(f"Error generating code: {e}")
            raise e

    def run_generation(self, file_names) -> List:
        from generated.restrictions import validate_restrictions
        from generated.target_function import target_function

        output_scores = []
        timeout_errors = []
        result_errors = []
        restriction_errors = []

        for file_name in file_names:
            # Run code
            start_time = time.time()
            result, is_error, error = run_code("generations", file_name)
            end_time = time.time()

            if is_error:
                if "Timeout expired while running code" in str(error):
                    timeout_errors.append({"file_code": file_name, "error": error})
                else:
                    result_errors.append({"file_code": file_name, "error": error})
                continue

            # Format result to dict
            try:
                result_dict = ast.literal_eval(result)
            except Exception as e:
                result_errors.append({"file_code": file_name, "error": e})
                continue

            # Validate result
            is_result_valid, error = validate_restrictions(result_dict)
            if not is_result_valid:
                restriction_errors.append({"file_code": file_name, "error": error})
                continue

            # Compute target function score
            score = target_function(result_dict)
            output_scores.append({"file_code": file_name, "score": score, "time": end_time - start_time})

        return output_scores, result_errors, timeout_errors, restriction_errors

    def select_best_scores(self, scores) -> List:
        def compare(a, b):
            score_diff = abs(a["score"] - b["score"])
            if score_diff < 1:
                return a["time"] - b["time"]
            return b["score"] - a["score"]

        sorted_scores = sorted(scores, key=functools.cmp_to_key(compare))

        selected_codes = []
        for i in range(COUNT_SELECTION_CODES):
            selected_codes.append(sorted_scores[i])

        return selected_codes

    def select_best_score(self, scores):
        def compare(a, b):
            score_diff = abs(a["score"] - b["score"])
            if score_diff < 1:
                return a["time"] - b["time"]
            return b["score"] - a["score"]

        sorted_scores = sorted(scores, key=functools.cmp_to_key(compare))

        if len(sorted_scores) == 0:
            return None
        return sorted_scores[0]

    def clear_files(self, best_file_name, file_names):
        # MUEVE output_schema.py y el mejor codigo a la carpeta output
        move_file("generations/output_schema.py", "output/output_schema.py")
        move_file(f"generations/{best_file_name}", "output/best_code.py")

        # ELIMINA LOS CODIGOS
        delete_files("generations", file_names)
        delete_folder("generations", "venv")

        # LIMPIA restrictions.py y target_function.py
        restriccion_code = """
from typing import Tuple

def validate_restrictions(result: dict) -> Tuple[bool, str]:
    pass
"""
        target_function_code = """
def target_function(result):
    pass
"""
        save_code("src/generated", "restrictions.py", restriccion_code)
        save_code("src/generated", "target_function.py", target_function_code)

