import yaml
import uuid
import re
import json
import asyncio
import time
import ast
from typing import List
from dataclasses import asdict
from concurrent.futures import ThreadPoolExecutor

from core.models import Provider, Problem, GenerationConfig, GenerationArtifact, GenerationCode, DataclassJSONEncoder
from core.providers._base import ProviderBase
from utils.prompt_manager import PromptManager as PM
from utils.code_executor import CodeExecutor as CE


class Agent:
    def __init__(self, problem: Problem, generation_config: GenerationConfig):
        # TODO: Load a Agent Config from a YAML file
        with open("src/problem_config.yaml", "r") as f:
            config = yaml.safe_load(f)

            self.PLANNING_MODEL = self._get_provider(config["agents"]["planning-model"])
            self.CODING_MODEL = self._get_provider(config["agents"]["coding-model"])

        # TODO: Load the problem
        self.PROBLEM = problem

        # TODO: Load the generation config
        self.GENERATION_CONFIG = generation_config

        # TODO: Initialize the generations
        self._ID = str(uuid.uuid4())
        self.GENERATIONS = dict()
        # self.BEST_GENERATION = None

        # TODO: Initialize the artifacts
        self.ARTIFACTS = GenerationArtifact(
            output_schema=None,
            constraints_function=None,
            target_function=None
        )

        # TODO: Initialize the executor pool thread
        self.EXECUTOR_POOL = ThreadPoolExecutor(max_workers=5)

    def _get_provider(self, provider_config: dict) -> ProviderBase:
        if provider_config["provider"] == Provider.OPENAI.value:
            from core.providers.openai import OpenAIProvider

            return OpenAIProvider(provider_config["config"])
        elif provider_config["provider"] == Provider.DEEPSEEK.value:
            from core.providers.deepseek import DeepSeekProvider

            return DeepSeekProvider(provider_config["config"])
        # CLAUDE
        # GEMINI
        else:
            raise Exception(f"Unknown provider: {provider_config['provider']}")
        
    async def run(self):
        print(f"Starting Agent, ID: {self._ID}")
        CE.create_folder(self._ID)
        CE.create_folder(f"{self._ID}/artifacts")
        CE.create_folder(f"{self._ID}/generations")

        print("Generating artifacts...")
        self._generate_output_schema()
        self._generate_constraints_function()
        self._generate_target_function()
        
        print("Generating solutions...")
        CE.create_venv()

        best_solutions = []
        for epoch in range(1, self.GENERATION_CONFIG.max_epochs + 1):
            current_solutions = []

            # TODO: GENERATE CODE GENERATION
            if (epoch == 1):
                # TODO: Generate first generation
                best_approaches = await self._select_best_approaches()
                # Generate user prompts for each approach
                user_prompts = [PM.get_user_prompt("coder_generate", "generate_code", context=self.PROBLEM.context, objective=self.PROBLEM.objective, constraints=self.PROBLEM.constraints, instance_path=self.PROBLEM.inst_filename, instance_format=self.PROBLEM.inst_format, solution_type=a["solution_type"], solution_plan=a["plan"], output_schema=self.ARTIFACTS.output_schema) for a in best_approaches]

                loop = asyncio.get_event_loop()
                tasks = [loop.run_in_executor(self.EXECUTOR_POOL, self._generate_solution_code, user_prompts[i], epoch, best_approaches[i]['solution_type'], None, 1, None) for i in range(len(best_approaches))]
                
                current_solutions = await asyncio.gather(*tasks, return_exceptions=False)
            elif (epoch == 2 and self.GENERATION_CONFIG.evo_strategy == "cross"):
                # TODO: Generate second cross generation
                pass
            else:
                # TODO: Generate next evolution generation
                # Get Evo planning
                evo_plans = [self._generate_evolution_plan(s) for s in best_solutions]
                # Get User prompt for each evo plan
                user_prompts = [PM.get_user_prompt("coder_evo", "generate_code", code = CE.get_code(file_name=best_solutions[i].code_path), improvement_plan = evo_plans[i]) for i in range(len(best_solutions))]
                # Generate code for each user prompt
                loop = asyncio.get_event_loop()
                tasks = [loop.run_in_executor(self.EXECUTOR_POOL, self._generate_solution_code, user_prompts[i], epoch, best_solutions[i].solution_type, best_solutions[i].solution_cross, 1, best_solutions[i]._id) for i in range(len(best_solutions))]

                current_solutions = await asyncio.gather(*tasks, return_exceptions=False)

            # TODO: EVALUATE CODE GENERATION
            if (epoch == 1):
                # all
                best_solutions = [s for s in current_solutions if s is not None]
                if (len(best_solutions) == 0):
                    print("-------- NO SOLUTIONS FOUND --------")
                    break
            elif (epoch == 2 and self.GENERATION_CONFIG.evo_strategy == "cross"):
                # pre and all
                pass
            else:
                # select best solutions (father and son)
                for i in range(len(best_solutions)):
                    if (current_solutions[i] is None):
                        continue

                    data = [
                        { "result": best_solutions[i].code_output, "execution_time": best_solutions[i].code_time},
                        { "result": current_solutions[i].code_output, "execution_time": current_solutions[i].code_time}
                    ]

                    best_index = CE.execute_function_memory(function_code=self.ARTIFACTS.target_function, function_name="target_function", data=data)
                    if best_index == 1:
                        # print("Best Solution is a Child")
                        best_solutions[i] = current_solutions[i]
                    # elif best_index == 0:
                    #     print("Best Solution is a Father")
                    # else:
                    #     print("Best Solution is a None")
                    # print("-------------------------------------------")
        
        # TODO: SELECT BEST SOLUTION
        print("Select best solution...")
        data = []
        for s in best_solutions:
            data.append({ "result": s.code_output, "execution_time": s.code_time})
        best_solution_index = CE.execute_function_memory(function_code=self.ARTIFACTS.target_function, function_name="target_function", data=data)
        
        print("---------------- SOLUTIONS ----------------")
        for s in best_solutions:
            print("-----------------------------------------------")
            print(f"Solution Type: {s.solution_type}")
            print(f"\tTotal Cost: {s.code_output['total_cost']}")
            print(f"\tExecution Time: {s.code_time}")
            print(f"\tEpoch: {s.epoch}")
            print(f"\tVersion: {s.version}")
            print("-----------------------------------------------")
        
        print("\n-----------------------------------------------")
        print("---------------- BEST SOLUTION ----------------")
        print(f"Solution Type: {best_solutions[best_solution_index].solution_type}")
        print(f"\tTotal Cost: {best_solutions[best_solution_index].code_output['total_cost']}")
        print(f"\tExecution Time: {best_solutions[best_solution_index].code_time}")
        print(f"\tEpoch: {best_solutions[best_solution_index].epoch}")
        print(f"\tVersion: {best_solutions[best_solution_index].version}")
        print("-----------------------------------------------")

        # TODO: Save all data to a JSON file
        CE.save_code(file_name=f"{self._ID}/problem.json", code=json.dumps(asdict(self.PROBLEM), indent=4))
        CE.save_code(file_name=f"{self._ID}/generation_config.json", code=json.dumps(asdict(self.GENERATION_CONFIG), indent=4))
        CE.save_code(file_name=f"{self._ID}/generations.json", code=json.dumps({k: asdict(v) for k, v in self.GENERATIONS.items()}, indent=4, cls=DataclassJSONEncoder))
        CE.save_code(file_name=f"{self._ID}/best_solutions.json", code=json.dumps([asdict(s) for s in best_solutions], indent=4, cls=DataclassJSONEncoder))
        CE.save_code(file_name=f"{self._ID}/best_solution.json", code=json.dumps(asdict(best_solutions[best_solution_index]), indent=4, cls=DataclassJSONEncoder))

    def _generate_output_schema(self) -> None:
        # TODO: Generate the output schema
        c_system_prompt = PM.get_system_prompt("coder", "output_schema")
        c_user_prompt = PM.get_user_prompt("coder", "output_schema", context=self.PROBLEM.context, objective=self.PROBLEM.objective, constraints=self.PROBLEM.constraints)
        output_schema = self.CODING_MODEL.generate_response(c_system_prompt, c_user_prompt, temperature=0.1, top_p=0.95)

        # Store the output schema
        match = re.search(r"```python\n(.*?)```", output_schema, re.DOTALL)
        code = match.group(1) if match else output_schema

        self.ARTIFACTS.output_schema = code

        # Save the output schema in the generations folder
        path = f"{self._ID}/artifacts/output_schema.py"
        CE.save_code(file_name=path, code=code)

    def _generate_constraints_function(self) -> None:
        # TODO: Generate the constraints function
        r_system_prompt = PM.get_system_prompt("reasoner", "constraints_function")
        r_user_prompt = PM.get_user_prompt("reasoner", "constraints_function", context=self.PROBLEM.context, constraints=self.PROBLEM.constraints, instance_path=self.PROBLEM.inst_filename, instance_format=self.PROBLEM.inst_format)
        constraints_list = self.PLANNING_MODEL.generate_response(r_system_prompt, r_user_prompt, temperature=0.4, top_p=0.9)

        c_system_prompt = PM.get_system_prompt("coder", "constraints_function")
        c_user_prompt = PM.get_user_prompt("coder", "constraints_function", context=self.PROBLEM.context, list_of_constraints=constraints_list, result_data_structure=self.ARTIFACTS.output_schema, instance_path=self.PROBLEM.inst_filename, instance_format=self.PROBLEM.inst_format)
        constraints_function = self.CODING_MODEL.generate_response(c_system_prompt, c_user_prompt, temperature=0, top_p=1)

        # Store the constraints function
        match = re.search(r"```python\n(.*?)```", constraints_function, re.DOTALL)
        code = match.group(1) if match else constraints_function

        self.ARTIFACTS.constraints_function = code

        # Save the constraints function
        path = f"{self._ID}/artifacts/constraints_function.py"
        CE.save_code(file_name=path, code=code)

    def _generate_target_function(self) -> None:
        # TODO: Generate the target function
        input_data_structure = f"""
        {{
            "result": {self.ARTIFACTS.output_schema},
            "execution_time": float,
        }}
        """

        r_system_prompt = PM.get_system_prompt("reasoner", "target_function")
        r_user_prompt = PM.get_user_prompt("reasoner", "target_function", context=self.PROBLEM.context, objective=self.PROBLEM.objective, input_data_structure=input_data_structure)
        evaluation_directives = self.PLANNING_MODEL.generate_response(r_system_prompt, r_user_prompt, temperature=0.5, top_p=0.85)

        c_system_prompt = PM.get_system_prompt("coder", "target_function")
        c_user_prompt = PM.get_user_prompt("coder", "target_function", context=self.PROBLEM.context, objective=self.PROBLEM.objective, evaluation_directives=evaluation_directives, input_data_structure=input_data_structure)
        target_function = self.CODING_MODEL.generate_response(c_system_prompt, c_user_prompt, temperature=0, top_p=1)

        # Store the target function
        match = re.search(r"```python\n(.*?)```", target_function, re.DOTALL)
        code = match.group(1) if match else target_function

        self.ARTIFACTS.target_function = code

        # Save the target function
        path = f"{self._ID}/artifacts/target_function.py"
        CE.save_code(file_name=path, code=code)
    
    async def _select_best_approaches(self) -> List[dict]:
        # TODO: Generate the best approaches
        r_system_prompt = PM.get_system_prompt("reasoner", "select_approaches")
        r_user_prompt = PM.get_user_prompt("reasoner", "select_approaches", context=self.PROBLEM.context, objective=self.PROBLEM.objective, constraints=self.PROBLEM.constraints, num_methods=self.GENERATION_CONFIG.first_gen_size)
        best_approaches = self.PLANNING_MODEL.generate_response(r_system_prompt, r_user_prompt, temperature=0.55, top_p=0.9)

        # Get a list of the text
        match = re.search(r"```python\n(.*?)```", best_approaches, re.DOTALL)
        code = match.group(1) if match else best_approaches

        best_approaches_list = json.loads(code)
        
        # Generate the plan for the approach
        loop = asyncio.get_event_loop()
        tasks = [loop.run_in_executor(None, self._plan_approach, a["solution_type"]) for a in best_approaches_list]
        plannes = await asyncio.gather(*tasks, return_exceptions=False)
        
        return [{"solution_type": a[0]["solution_type"], "plan": a[1]} for a in zip(best_approaches_list, plannes)]

    def _plan_approach(self, approach_name: str) -> str:
        # TODO: Generate the plan for the approach
        r_system_prompt = PM.get_system_prompt("reasoner", "plan_approach")
        r_user_prompt = PM.get_user_prompt("reasoner", "plan_approach", context=self.PROBLEM.context, objective=self.PROBLEM.objective, constraints=self.PROBLEM.constraints, instance_path=self.PROBLEM.inst_filename, instance_format=self.PROBLEM.inst_format, approach_name=approach_name)
        plan = self.PLANNING_MODEL.generate_response(r_system_prompt, r_user_prompt, temperature=0.35, top_p=0.85)
        
        return plan
    
    def _generate_solution_code(self, user_prompt: str, epoch: int, solution_type: str, solution_cross: str | None, version: int, father_id: str) -> GenerationCode | None:
        print(f"Generating solution code for {solution_type} - epoch {epoch} - version {version}")
        
        # Check if the version is greater than the maximum number of errors
        if (version > self.GENERATION_CONFIG.max_errors + 1):
            return None
        
        # TODO: Generate the solution code
        c_system_prompt = PM.get_system_prompt("coder", "generate_code")

        try:
            code_string = self.CODING_MODEL.generate_response(c_system_prompt, user_prompt, temperature=0, top_p=1)

            match = re.search(r"```python\n(.*?)```", code_string, re.DOTALL)
            solution_code = match.group(1) if match else code_string
        except Exception as e:
            print(f"Error generating solution code: {e}")
            return None
        
        # Store the solution code
        path = f"{solution_type.lower().replace(' ', '_').replace('*', '_star')}_e{epoch}_{'none' if solution_cross is None else solution_cross.lower().replace(' ', '_').replace('*', '_star')}_v{version}.py"
        path = f"{self._ID}/generations/{path}"

        scg = GenerationCode( # Solution Code Generated
            _id=str(uuid.uuid4()),
            father_id=father_id,
            epoch=epoch,
            version=version,
            solution_type=solution_type,
            solution_cross=solution_cross,
            code_path=path,
            code_output=None,
            code_time=None,
            code_error=None
        )

        self.GENERATIONS[scg._id] = scg
        CE.save_code(file_name=path, code=solution_code)
        
        # TODO: Try to run the code
        # Install all dependencies
        CE.install_all_dependencies(file_name=path)

        # Run the code
        start_time = time.time()
        result, error = CE.execute_code(file_name=path)
        execution_time = time.time() - start_time

        # Save the code execution result
        scg.code_time = execution_time
        
        if error:
            scg.code_error = error
        
        # Parse the result
        try:
            if (error is None):
                result_dict = ast.literal_eval(result)
        except Exception as e:
            scg.code_error = f"Error parsing result: {e}"
            scg.code_output = result

        if (scg.code_error is not None): # Error de ejecucion
            print("---")
            print(f"EJECUCION: {scg.solution_type} has an error: {scg.code_error}")
            print(f"RESULT: {scg.code_output}")
            print("---\n")

            # TODO: Fix code
            r_system_prompt = PM.get_system_prompt("reasoner", "fix_code")
            r_user_prompt = PM.get_user_prompt("reasoner", "fix_code", code=solution_code, error=scg.code_error, result=scg.code_output, instance_path=self.PROBLEM.inst_filename, instance_format=self.PROBLEM.inst_format, output_schema=self.ARTIFACTS.output_schema)
            fix_plan = self.PLANNING_MODEL.generate_response(r_system_prompt, r_user_prompt, temperature=0.5, top_p=0.9)
            
            fix_user_prompt = PM.get_user_prompt("coder_fix", "generate_code", code=solution_code, error=scg.code_error, fix_plan=fix_plan, instance_path=self.PROBLEM.inst_filename, instance_format=self.PROBLEM.inst_format, output_schema=self.ARTIFACTS.output_schema)
            return self._generate_solution_code(fix_user_prompt, epoch, solution_type, solution_cross, version + 1, father_id)

        # Save the result
        scg.code_output = result_dict
        
        # TODO: Validate the code output to pass a constraints function
        try:
            result, error = CE.execute_function_memory(function_code=self.ARTIFACTS.constraints_function, function_name="validate_constraints", data=scg.code_output)
            
            if result is False:
                scg.code_error = error
                print("---")
                print(f"RESTRICCION: {scg.solution_type} has an error: {scg.code_error}")
                print("---\n")

                # TODO: Fix code
                r_system_prompt = PM.get_system_prompt("reasoner", "fix_code")
                r_user_prompt = PM.get_user_prompt("reasoner", "fix_code", code=solution_code, error=scg.code_error, result=scg.code_output, instance_path=self.PROBLEM.inst_filename, instance_format=self.PROBLEM.inst_format, output_schema=self.ARTIFACTS.output_schema)
                fix_plan = self.PLANNING_MODEL.generate_response(r_system_prompt, r_user_prompt, temperature=0.5, top_p=0.9)
                
                fix_user_prompt = PM.get_user_prompt("coder_fix", "generate_code", code=solution_code, error=scg.code_error, fix_plan=fix_plan, instance_path=self.PROBLEM.inst_filename, instance_format=self.PROBLEM.inst_format, output_schema=self.ARTIFACTS.output_schema)
                return self._generate_solution_code(fix_user_prompt, epoch, solution_type, solution_cross, version + 1, father_id)
        except Exception as e:
            print(f"Error executing constraints function: {e}")

        # TODO: Return the solution code
        return scg
        
    def _generate_evolution_plan(self, solution: GenerationCode) -> str:
        # TODO: Generate the evolution plan
        code = CE.get_code(file_name=solution.code_path)

        r_system_prompt = PM.get_system_prompt("reasoner", "plan_evolution")
        r_user_prompt = PM.get_user_prompt("reasoner", "plan_evolution", context=self.PROBLEM.context, objective=self.PROBLEM.objective, constraints=self.PROBLEM.constraints, instance_path=self.PROBLEM.inst_filename, instance_format=self.PROBLEM.inst_format, solution_type=solution.solution_type, code=code)
        plan = self.PLANNING_MODEL.generate_response(r_system_prompt, r_user_prompt, temperature=0.3, top_p=0.95)

        return plan