import ast
import re
import json
import time
import uuid
import os
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import asdict

from core.llm.api_base import APIBaseLLM
from core.llm.openai import OpenAILLM
from core.models import Problem, GenerationConfig, GenerationRun, ArtifactGenerated, CodeGenerated
from utils.code_executor import CodeExecutor

class APIBaseExpert():
    def __init__(self, config: Dict[str, Any]):
        self.name = config.get("name")
        self.standard_model = config.get("standard-model")
        self.coding_model = config.get("coding-model")
        self.reasoning_model = config.get("reasoning-model")
        self.llm: APIBaseLLM

        if config.get("library") == "openai":
            self.llm = OpenAILLM(config.get("api-key"))
        else:
            raise Exception(f"Unknown library: {config.get('library')}")

    def run_expert(self, problem: Problem, generation_config: GenerationConfig) -> GenerationRun:
        # Define the generation run
        self.generation_run = GenerationRun(
            generation_id=str(uuid.uuid4()),
            problem=problem,
            generation_config=generation_config,
            generations=dict(),
            best_generation=None
        )

        # Define the artifacts to be problem-specific
        self.artifacts_generated = ArtifactGenerated(
            output_schema=None,
            constraints_function=None,
            target_function=None
        )

        # Generate artifacts
        self._generate_output_schema()
        self._generate_constraints_function()
        self._generate_target_function()

        # Save the artifacts
        CodeExecutor.save_code(file_name="output_schema.py", code=self.artifacts_generated.output_schema)
        CodeExecutor.save_code(file_name="constraints_function.py", code=self.artifacts_generated.constraints_function)
        CodeExecutor.save_code(file_name="target_function.py", code=self.artifacts_generated.target_function)

        # #? TEST
        # self.artifacts_generated.output_schema = CodeExecutor.get_code("output_schema.py")
        # self.artifacts_generated.constraints_function = CodeExecutor.get_code("constraints_function.py")
        # self.artifacts_generated.target_function = CodeExecutor.get_code("target_function.py")

        # # Generate first generation
        self.current_epoch = 1
        self._generate_first_generation()
        codes_to_run = list(self.generation_run.generations.values())
        best_codes = dict()

        # #? TEST
        # codes_to_run = []
        # with open(os.path.join("src", "data", "results.txt"), "r", encoding="utf-8") as f:
        #     content = f.read().strip()
        #     data_list = eval(content)

        #     for data in data_list:
        #         cg = CodeGenerated(
        #             code_id = data["code_id"],
        #             father_code_id = data["father_code_id"],
        #             epoch = data["epoch"],
        #             solution_type = data["solution_type"],
        #             solution_cross = data["solution_cross"],
        #             version = data["version"],
        #             code_path = data["code_path"],
        #             result = data["result"],
        #             execution_time = data["execution_time"],
        #             error = data["error"]
        #         )
        #         self.generation_run.generations[cg.code_id] = cg

        # codes_passed = [code for code in self.generation_run.generations.values() if code.error is None]
        # print(len(codes_passed))

        # # Print the first generation
        while True:
            # Run codes and for each result code, a error id generated to check and recreate a code to solve the error.
            codes_passed, codes_with_errors = self._run_codes_generated(codes_to_run)

            print( f"Passed: {len(codes_passed)}, Failed: {len(codes_with_errors)}")

            # Fix codes with errors
            if codes_with_errors:
                codes_to_fix = codes_with_errors
                for attempt in range(self.generation_run.generation_config.max_errors_resolved):
                    codes_fixed = self._fix_codes_generation(codes_with_errors=codes_to_fix)
                    fix_codes_passed, fix_codes_with_errors = self._run_codes_generated(codes_to_run=codes_fixed)

                    codes_passed.extend(fix_codes_passed)
                    print( f"Passed: {len(fix_codes_passed)}, Failed: {len(fix_codes_with_errors)}")

                    if not fix_codes_with_errors:
                        break
                    codes_to_fix = fix_codes_with_errors

            print( f"All Passed: {len(codes_passed)}, Failed: {len(codes_to_run) - len(codes_passed)}")

            # Tests solutions in constraints function
            print("-------------------------------------------")
            codes_passed_constraints = []

            for code in codes_passed:
                try:
                    result, error = CodeExecutor.execute_function_memory(function_code=self.artifacts_generated.constraints_function, function_name="validate_constraints", data=code.result)
                    print(result, error)

                    if result is False:
                        code.error = error
                        continue
                    codes_passed_constraints.append(code)
                except Exception as e:
                    print(f"Error executing constraints function: {e}")
        
            print(len(codes_passed_constraints))
        
            # Define the best codes for solution
            if self.current_epoch == 1:
                for code in codes_passed_constraints:
                    best_codes[code.code_id] = code
            elif self.generation_run.generation_config.selection_strategy == "best-by-solution":
                # Get the best codes from the code with the father
                for code in codes_passed_constraints:
                    father_code = best_codes[code.father_code_id]

                    data = [
                        { "code_id": code.code_id, "result": code.result, "execution_time": code.execution_time },
                        { "code_id": father_code.code_id, "result": father_code.result, "execution_time": father_code.execution_time },
                    ]

                    best_id = CodeExecutor.execute_function_memory(function_code=self.artifacts_generated.target_function, function_name="target_function", data=data)

                    if best_id == code.code_id:
                        print("Best Code is a Child")
                        best_codes.pop(code.father_code_id)
                        best_codes[code.code_id] = code
                    elif best_id == father_code.code_id:
                        print("Best Code is a Father")
                    else:
                        print("Best Code is a None")
            else:
                best_codes = dict()
                for code in codes_passed_constraints:
                    best_codes[code.code_id] = code

            print(len(best_codes.keys()))

            self.current_epoch += 1
            if self.current_epoch > self.generation_run.generation_config.max_epochs:
                break
        
            # Generate next generation
            codes_to_run = []
            if self.generation_run.generation_config.evolution_strategy == "cross" and self.current_epoch == 2:
                # Genera el cruzamiento entre los mejores
                pass
            else:
                # Genera un mejoramiento individual
                for code in best_codes.values():
                    evolved_code = self._evo_individual_generation(code, self.current_epoch)
                    if evolved_code is not None:
                        codes_to_run.append(evolved_code)

        #     #! # Save the result
        #     #! CodeExecutor.save_code(file_name="output_schema.py", code=self.artifacts_generated.output_schema)
        #     #! CodeExecutor.save_code(file_name="constraints_function.py", code=self.artifacts_generated.constraints_function)

        #     #! code_list = []
        #     #! for code_id, code_obj in self.generation_run.generations.items():
        #     #!     code_dict = asdict(code_obj)
        #     #!     code_list.append(code_dict)


        #     #! # Convertir a string antes de escribir
        #     #! with open(os.path.join("src", "data", "results.txt"), "w", encoding="utf-8") as f:
        #     #!     f.write(str(code_list))
        #     #!

    def _generate_output_schema(self) -> None:
        # system_prompt = f"""
        #     You are an expert in data structure design. Your task is to create standardized output schemas.

        #     SPECIFIC INSTRUCTIONS:
        #     2. Define ONLY the data structure (Python dictionary)
        #     3. Use valid and compatible Python syntax
        #     4. All variable names must be in English
        #     5. Include inline comments explaining the purpose of each field
        #     6. Use appropriate data types (str, int, float, list, dict, bool)
        #     7. DO NOT include example values
        #     8. DO NOT add additional explanatory text
        #     9. Response must be pure Python code

        #     EXPECTED FORMAT:
        #     ```python
        #     {{
        #         "field1": str,  # Field description
        #         "field2": int,  # Field description
        #         # ... more fields as needed
        #     }}
        #     ```
        # """
        system_prompt = """
            Define a unified output structure (e.g., object or dictionary) that standardizes the result format for the given problem.
            - Use Python-compatible syntax.
            - Define only the structure.
            - Use English for all variable names.
            - Include inline comments explaining the purpose of each variable.
            - Do NOT provide examples.
            - Do NOT include any extra text or comments.
        """

        user_prompt = f""""
            PROBLEM TO SOLVE:
            DESCRIPTION:
            {self.generation_run.problem.context}

            OBJECTIVE:
            {self.generation_run.problem.objective}

            ---
            Generate the appropriate output schema following the system instructions.
        """

        # Generate the output schema
        output_schema = self.llm.generate(model=self.standard_model, system_prompt=system_prompt, user_prompt=user_prompt, temperature=0.1, top_p=0.9)

        # Store the output schema
        match = re.search(r"```python\n(.*?)```", output_schema, re.DOTALL)
        code = match.group(1) if match else output_schema

        self.artifacts_generated.output_schema = code

    def _generate_constraints_function(self) -> None:
        # Get constraints list from problem
        system_prompt = f"""
            You are an expert constraint analyst. Your task is to identify and prioritize all constraints from problem descriptions.

            ANALYSIS APPROACH:
            1. Read the problem description carefully
            2. Identify ALL explicit and implicit constraints
            3. Categorize constraints by type (technical, business, resource, time, quality, etc.)
            4. Prioritize based on impact and criticality

            OUTPUT REQUIREMENTS:
            - Generate a numbered list of constraints
            - Order by priority (highest impact first)
            - Use consistent format: "Priority: Constraint description"
            - Each constraint on a separate line
            - Use clear, actionable language
            - Include both explicit and reasonably inferred constraints
            - Write in English only

            CONSTRAINT TYPES TO CONSIDER:
            - Performance requirements (speed, throughput, latency)
            - Resource limitations (memory, storage, budget, time)
            - Technical specifications (platforms, formats, standards)
            - Business rules and policies
            - Quality standards (accuracy, reliability, security)
            - User experience requirements
            - Integration constraints
            - Regulatory or compliance requirements

            FORMAT EXAMPLE:
            1. High Priority: [Most critical constraint]
            2. High Priority: [Second most critical constraint]
            3. Medium Priority: [Important but less critical constraint]
            4. Low Priority: [Nice-to-have constraint]

            DO NOT include explanatory text outside the constraint list.
        """

        user_prompt = f""""
            PROBLEM TO ANALYZE:
            DESCRIPTION:
            {self.generation_run.problem.context}

            CONSTRAINTS:
            {self.generation_run.problem.constraints}

            ---
            Based on the problem description above, extract and prioritize ALL constraints following the system instructions.
        """

        # Generate the constraints list
        constraints_list = self.llm.generate(model=self.reasoning_model, system_prompt=system_prompt, user_prompt=user_prompt, temperature=0.3, top_p=0.95)

        # Generate the constraints function
        system_prompt = f""""
            You are an expert Python developer specializing in constraint validation systems. Your task is to generate robust validation functions.

            CORE REQUIREMENTS:
            1. Generate a complete, executable Python function named 'validate_constraints'
            2. Function signature: def validate_constraints(result: Dict) -> Tuple[bool, str]
            3. Return (True, "Success") if all constraints are satisfied
            4. Return (False, "Detailed error message") if any constraint fails
            5. Include ALL necessary imports at the function level
            6. Handle all edge cases and potential errors gracefully

            CONSTRAINT VALIDATION APPROACH:
            - Analyze ALL explicit constraints in the problem description
            - Identify implicit constraints that are logically necessary
            - Validate data types, ranges, formats, and business rules
            - Ensure result values are logically derived from input data
            - Check for data consistency and completeness

            CODE QUALITY REQUIREMENTS:
            - Use type hints where appropriate
            - Include descriptive variable names
            - Add inline comments for complex validation logic
            - Handle file I/O errors gracefully
            - Use UTF-8 encoding for all text operations
            - Follow Python best practices and PEP 8 style

            VALIDATION CATEGORIES TO IMPLEMENT:
            - Data type validation (according to input schema)
            - Value range and boundary checks
            - Format validation (dates, emails, IDs, etc.)
            - Business rule compliance
            - Data completeness and required fields
            - Cross-field validation and dependencies
            - Performance constraints (if applicable)
            - Security constraints (if applicable)

            ERROR HANDLING:
            - Provide specific, actionable error messages
            - Include which constraint failed and why
            - Handle missing or malformed data gracefully
            - Return clear success/failure status

            OUTPUT FORMAT:
            - Only output the complete function code
            - Do NOT include example usage or explanatory text
            - Do NOT execute the function
            - Ensure the function is immediately usable

            FUNCTION TEMPLATE STRUCTURE:
            ```python
            # Import statements here

            def validate_constraints(result: Dict) -> Tuple[bool, str]:
                # Constraint validation logic

                # Return validation result
            ```
        """

        user_prompt = f""""
            PROBLEM DESCRIPTION:
            {self.generation_run.problem.context}

            LIST OF CONSTRAINTS:
            {constraints_list}

            RESULT DATA STRUCTURE:
            {self.artifacts_generated.output_schema}

            ---
            Generate the validate_restrictions function that verifies ALL constraints from the problem description. Following the provided format specification.
        """

        # Generate the constraints function
        constraints_function = self.llm.generate(model=self.coding_model, system_prompt=system_prompt, user_prompt=user_prompt, temperature=0.1, top_p=0.9)

        # Store the constraints function
        match = re.search(r"```python\n(.*?)```", constraints_function, re.DOTALL)
        code = match.group(1) if match else constraints_function

        self.artifacts_generated.constraints_function = code

    def _generate_target_function(self) -> None:
        system_prompt = f"""
            You are tasked with creating a Python evaluation function that determines the best solution among multiple solution candidates.
            Write a complete and executable Python 3 function named `target_function` with the following specifications:

            FUNCTION TEMPLATE STRUCTURE:
            ```python
            # Import statements here

            def target_function(code_list: List[dict]) -> str:
                # Code to evaluate the solutions
                # Return the best solution code
            ```

            RETURN VALUE:
            - Must return the code_id (str) of the best performing solution

            EVALUATION CRITERIA (implement a comprehensive scoring system):
            1. **Result Quality (60% weight)**: Evaluate how well the result satisfies the problem requirements
            - Correctness of output format according to input_schema
            - Accuracy of solution relative to problem objectives
            - Completeness of the solution
            - Edge case handling

            2. **Performance Efficiency (25% weight)**: Consider execution performance
            - Execution time (faster is better, but within reasonable bounds)
            - Time complexity implications
            - Resource utilization efficiency

            3. **Solution Robustness (10% weight)**: Assess solution reliability
            - Error handling (penalize solutions with errors heavily)
            - Code stability and version maturity
            - Solution approach appropriateness

            4. **Evolutionary Quality (5% weight)**: Consider evolutionary aspects
            - Generation progression (later epochs may indicate refinement)
            - Version stability (higher versions may indicate bug fixes)
            - Solution type effectiveness for the problem domain

            IMPLEMENTATION REQUIREMENTS:
            - Use try-catch blocks for robust error handling
            - Ensure the function is deterministic (same input always produces same output)

            CODE STYLE:
            - Use clear variable names and add explanatory comments
            - Include docstring with evaluation criteria explanation
            - Handle type checking and input validation
            - Use helper functions if needed for complex scoring logic
            - Follow PEP 8 style guidelines

            OUTPUT ONLY THE COMPLETE FUNCTION CODE WITHOUT EXTRA TEXT OR MARKDOWN.
        """

        user_prompt = f""""
            PROBLEM TO ANALYZE:
            DESCRIPTION:
            {self.generation_run.problem.context}

            OBJECTIVE:
            {self.generation_run.problem.objective}

            INPUT SCHEMA:
            {{
                "code_id": str,
                "result": {self.artifacts_generated.output_schema},
                "execution_time": float,
            }}

            ---
            Generate the target_function that evaluates the solutions and returns the best solution code_id.
        """

        # Generate the target function
        target_function = self.llm.generate(model=self.coding_model, system_prompt=system_prompt, user_prompt=user_prompt, temperature=0.1, top_p=0.9)

        # Store the constraints function
        match = re.search(r"```python\n(.*?)```", target_function, re.DOTALL)
        code = match.group(1) if match else target_function

        self.artifacts_generated.target_function = code

    def _generate_first_generation(self) -> None:
        system_prompt = f"""
            You are an expert problem-solving assistant. Your task is to identify the best solution approach for the problem.

            ANALYSIS APPROACH:
            1. Read the problem description carefully
            2. Identify the most suitable solution approach
            3. Prioritize based on impact and criticality
            4. Consider the problem constraints and any relevant domain knowledge
            5. Discuss the pros and cons of each approach
            6. Select the best approach based on your analysis

            OUTPUT REQUIREMENTS:
            - Each approach must use a different solution type (e.g., greedy algorithm, dynamic programming, backtracking, simulated annealing, genetic algorithm, brute force, divide and conquer, etc.)
            - Each approach must be independent and complete
            - Order by priority (highest impact first)
            - Return a valid Python list of dictionaries

            EXPECTED FORMAT:
            ```python
            [
                {{
                    "solution_type": "Name of the algorithm/heuristic/metaheuristic/etc.",
                    "step_by_step": [
                        "Step 1: Clear description of first step",
                        "Step 2: Clear description of second step",
                        "Step N: Clear description of final step"
                    ]
                }},
                // ... more dictionaries for each approach
            ]
            ```

            IMPORTANT NOTES:
            - Each step_by_step list should contain 3-8 clear, actionable steps
            - Steps should be specific to the problem and solution approach
            - Return ONLY the Python list, no additional text or formatting
            - Ensure valid JSON/Python syntax
        """

        user_prompt = f""""
            PROBLEM TO ANALYZE:
            DESCRIPTION:
            {self.generation_run.problem.context}

            OBJECTIVE:
            {self.generation_run.problem.objective}

            CONSTRAINTS:
            {self.generation_run.problem.constraints}

            NUMBER OF SOLUTION: {self.generation_run.generation_config.first_generation_size}
            ---
            Generate {self.generation_run.generation_config.first_generation_size} different solution approaches to solve this problem. Each approach should specify a different solution type and provide detailed step-by-step instructions.
        """

        # Generate first generation solutions
        first_problem_solutions_text = self.llm.generate(model=self.reasoning_model, system_prompt=system_prompt, user_prompt=user_prompt, temperature=0.8, top_p=0.95)
        
        # Format to only string code, without python bloque definition
        match = re.search(r"```python\n(.*?)```", first_problem_solutions_text, re.DOTALL)
        code_string = match.group(1) if match else first_problem_solutions_text
        
        # Parse to python list of dictionaries
        first_problem_solutions = json.loads(code_string)

        for solution in first_problem_solutions:
            # Generate the solution code for each solution
            user_prompt = f"""
                PROBLEM TO SOLVE:
                DESCRIPTION:
                {self.generation_run.problem.context}

                OBJECTIVE:
                {self.generation_run.problem.objective}

                CONSTRAINTS:
                {self.generation_run.problem.constraints}

                INSTANCE DATA PATH:
                instances/{self.generation_run.problem.instance_filename}

                INSTANCE DATA FORMAT:
                {self.generation_run.problem.instance_format}

                RESULT DATA STRUCTURE:
                {self.artifacts_generated.output_schema}

                HOW TO SOLVE THIS PROBLEM:
                SOLUTION TYPE: {solution["solution_type"]}
                STEP-BY-STEP INSTRUCTIONS:
                {"\n".join(solution["step_by_step"])}

                ---
                Generate the code to solve this problem using the solution type and step-by-step instructions provided. The code must follow the provided output_schema format precisely and return ONLY the result - no additional prints, comments, or debug output.
            """

            # Generate the solution code
            try:
                solution_code = self._generate_solution_code(user_prompt)
            except Exception as e:
                print(f"Error generating solution code: {e}")
                continue

            # Store the solution code
            path = f"{solution["solution_type"].lower().replace(' ', '_').replace('*','_star')}_e1_none_v1.0.py"

            CodeExecutor.save_code(file_name=path, code=solution_code)
            solution_code_generated = CodeGenerated(
                code_id=str(uuid.uuid4()),
                father_code_id=None,
                epoch=1,
                solution_type=solution["solution_type"],
                solution_cross=None,
                version=1.0,
                code_path=path,
                result=None,
                execution_time=None,
                error=None
            )
            
            self.generation_run.generations[solution_code_generated.code_id] = solution_code_generated
    
    def _generate_solution_code(self, user_prompt: str) -> str:
        system_prompt = f"""
            You are an expert Python developer specializing in algorithmic problem solving.

            CRITICAL REQUIREMENTS:
            - Write complete, executable Python code that solves the problem exactly as specified
            - The code must follow the provided output_schema format precisely
            - When executed, the code must return ONLY the result - no additional prints, comments, or debug output
            - Write efficient, clean, and well-structured code
            - Handle edge cases appropriately
            - Do not generate test data - use only what's provided in the problem
            
            CODE FORMAT:
            - Return ONLY the Python code, no explanations or markdown formatting
            - End with the final return statement or result output

            SOLVER USAGE RESTRICTIONS:
            - If using any optimization solvers (OR-Tools, PuLP, CBC, Gurobi, etc.), you MUST suppress ALL console output
            - Use solver parameters to disable logging: verbose=False, msg=False, logPath="", etc.
            - Redirect solver output to avoid console interference
            - Examples for common solvers:
            * OR-Tools: solver.EnableOutput() should NOT be called, use solver.Solve() silently
            * PuLP: prob.solve(pulp.PULP_CBC_CMD(msg=False))
            * CBC: Use quiet=True or similar parameters
            * Any solver: Wrap solver calls with output redirection if necessary

            CONSOLE OUTPUT CONTROL:
            - NEVER allow ANY library to print to console during execution
            - The ONLY output should be the final result from your solve_problem() function
            - If a solver must print, redirect its output to /dev/null or suppress it completely

            OPTIMIZATION:
            - Prioritize correctness first, then efficiency
            - Use appropriate data structures and algorithms
            - Minimize time and space complexity where possible

            TEMPLATE STRUCTURE:
            ```python
            # Import statements here

            # Code to solve the problem
            def solve_problem() -> Dict:
                # Code to process input data
                # Code to solve the problem
                # Code to return the result

            print(solve_problem())
            ```
        """

        # Generate the solution code
        solution_code = self.llm.generate(model=self.coding_model, system_prompt=system_prompt, user_prompt=user_prompt, temperature=0.1, top_p=0.9)

        match = re.search(r"```python\n(.*?)```", solution_code, re.DOTALL)
        code = match.group(1) if match else solution_code

        return code

    def _run_codes_generated(self, codes_to_run: List[CodeGenerated]) -> Tuple[List[CodeGenerated], List[CodeGenerated]]:
        # Install all dependencies
        CodeExecutor.install_all_dependencies(file_names = [code.code_path for code in codes_to_run])

        # Define stores
        codes_passed = []
        codes_with_errors = []

        # Execute each code and save the result
        for code in codes_to_run:
            # Run the code
            start_time = time.time()
            result, error = CodeExecutor.execute_code(file_name=code.code_path)
            execution_time = time.time() - start_time

            if error:
                code.error = error
                code.execution_time = execution_time
                codes_with_errors.append(code)
                continue
            
            # Parse the result
            try:
                result_dict = ast.literal_eval(result)
            except Exception as e:
                code.error = f"Error parsing result: {e}"
                code.result = result
                code.execution_time = execution_time
                codes_with_errors.append(code)
                continue
            
            # Save the result
            code.result = result_dict
            code.execution_time = execution_time
            codes_passed.append(code)
        
        return codes_passed, codes_with_errors

    def _fix_codes_generation(self, codes_with_errors: List[CodeGenerated]) -> List[CodeGenerated]:
        fix_codes = []

        # Fix the codes with errors
        for cwe in codes_with_errors:
            # get code
            code = CodeExecutor.get_code(file_name=cwe.code_path)

            # Generate user prompt to fix the code
            user_prompt = f"""
                CODE TO FIX:
                {code}

                CODE ERROR:
                {cwe.error}

                CODE RESULT:
                {cwe.result}

                ---
                INSTANCE DATA PATH:
                instances/{self.generation_run.problem.instance_filename}

                INSTANCE DATA FORMAT:
                {self.generation_run.problem.instance_format}

                OUTPUT SCHEMA:
                {self.artifacts_generated.output_schema}
            
                ---
                Fix the code to make it work correctly. The code must follow the provided output_schema format precisely and return ONLY the result - no additional prints, comments, or debug output.
            """

            # Generate the solution code
            try:
                solution_code = self._generate_solution_code(user_prompt)
            except Exception as e:
                print(f"Error generating fix code: {e}")
                continue

            # Store the solution code
            new_version = cwe.version + 0.1
            path = f"{cwe.solution_type.lower().replace(' ', '_').replace('*','_star')}_e{cwe.epoch}_{'none' if cwe.solution_cross is None else cwe.solution_cross.lower().replace(' ', '_').replace('*','_star')}_v{new_version:0.1f}.py"

            CodeExecutor.save_code(file_name=path, code=solution_code)
            solution_code_generated = CodeGenerated(
                code_id=str(uuid.uuid4()),
                father_code_id=cwe.father_code_id,
                epoch=cwe.epoch,
                solution_type=cwe.solution_type,
                solution_cross=cwe.solution_cross,
                version=new_version,
                code_path=path,
                result=None,
                execution_time=None,
                error=None
            )
            
            self.generation_run.generations[solution_code_generated.code_id] = solution_code_generated
            fix_codes.append(solution_code_generated)
        
        return fix_codes

    def _evo_individual_generation(self, code_to_evolve: CodeGenerated, epoch: int) -> Optional[CodeGenerated]:
        system_prompt = f"""
            You are an expert code optimization consultant specializing in algorithmic problem solving and performance improvement.
            Your task is to analyze Python code that is not meeting its objective function requirements and provide a comprehensive improvement plan.

            ANALYSIS FRAMEWORK:
            1. **Correctness Analysis**: Identify logical errors, edge case failures, output format issues
            2. **Performance Analysis**: Analyze time/space complexity, bottlenecks, inefficient operations  
            3. **Implementation Analysis**: Code quality, readability, maintainability issues
            4. **Algorithmic Analysis**: Alternative approaches, optimization opportunities

            OUTPUT FORMAT:
            - Provide a comprehensive improvement plan in the form of a list of suggested changes
            - Each change should be described in detail, including the reason for the change, the impact on the code, and the proposed solution
            - The improvement plan should be structured in a logical and coherent manner, with clear steps and explanations
            - Use clear and concise language, avoiding jargon or technical terms that may be unfamiliar to the target audience
            - Ensure that the improvement plan is actionable and can be implemented effectively
            - Include any relevant context or background information that may be helpful for understanding the code and the problem
            - Provide a clear and concise explanation of the improvement plan, including any potential trade-offs or limitations

            CRITICAL REQUIREMENTS:
            - Prioritize correctness over performance optimizations
            - Provide actionable, specific recommendations
            - Include implementation safety measures
            - Consider edge cases and boundary conditions
            - Suggest validation steps for each change
            - Order improvements by impact and dependency
            - Focus on measurable, objective improvements
        """

        code  = CodeExecutor.get_code(file_name=code_to_evolve.code_path)

        user_prompt = f"""
            PROBLEM TO SOLVE:
            DESCRIPTION:
            {self.generation_run.problem.context}

            OBJECTIVE:
            {self.generation_run.problem.objective}

            CONSTRAINTS:
            {self.generation_run.problem.constraints}

            RESULT DATA STRUCTURE:
            {self.artifacts_generated.output_schema}

            CODE TO EVOLVE:
            {code}

            ---
            Provide specific, actionable improvements with implementation guidance and safety considerations.
        """

        # Generate the improvement plan
        improvement_plan = self.llm.generate(model=self.reasoning_model, system_prompt=system_prompt, user_prompt=user_prompt, temperature=0.3, top_p=0.95)

        user_prompt = f"""
            CODE TO EVOLVE:
            {code}

            IMPROVEMENT PLAN:
            {improvement_plan}

            ---
            Provide the code with the improvement plan applied.
        """

        # Generate the evolved code
        try:
            solution_code = self._generate_solution_code(user_prompt)
        except Exception as e:
            print(f"Error generating evolved code: {e}")
            return None

        # Store the solution code
        cte = code_to_evolve
        path = f"{cte.solution_type.lower().replace(' ', '_').replace('*','_star')}_e{epoch}_{'none' if cte.solution_cross is None else cte.solution_cross.lower().replace(' ', '_').replace('*','_star')}_v1.0.py"

        CodeExecutor.save_code(file_name=path, code=solution_code)
        solution_code_generated = CodeGenerated(
            code_id=str(uuid.uuid4()),
            father_code_id=cte.code_id,
            epoch=epoch,
            solution_type=cte.solution_type,
            solution_cross=cte.solution_cross,
            version=1.0,
            code_path=path,
            result=None,
            execution_time=None,
            error=None
        )
        
        self.generation_run.generations[solution_code_generated.code_id] = solution_code_generated
        return solution_code_generated

        