import random
import json
from typing import List, Dict, Tuple

# Read input file
def read_input(filename: str) -> Tuple[List[Dict], List[Dict]]:
    with open(filename, 'r') as file:
        lines = [line.strip() for line in file if line.strip()]
    
    # Read packages
    num_packages = int(lines[0])
    packages = []
    for i in range(1, num_packages + 1):
        width, height = map(int, lines[i].split())
        packages.append({"id": i, "width": width, "height": height})
    
    # Read containers
    num_containers = int(lines[num_packages + 1])
    containers = []
    for i in range(num_packages + 2, num_packages + 2 + num_containers):
        width, height = map(int, lines[i].split())
        containers.append({"id": len(containers) + 1, "width": width, "height": height, "packages": []})
    
    return packages, containers

# Genetic Algorithm Components
class GeneticAlgorithm:
    def __init__(self, packages: List[Dict], containers: List[Dict], population_size: int = 50, generations: int = 100, mutation_rate: float = 0.1):
        self.packages = packages
        self.containers = containers
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
    
    def initialize_population(self) -> List[List[int]]:
        population = []
        for _ in range(self.population_size):
            individual = list(range(1, len(self.packages) + 1))
            random.shuffle(individual)
            population.append(individual)
        return population
    
    def fitness(self, individual: List[int]) -> Tuple[int, List[Dict]]:
        containers_copy = [{"id": c["id"], "width": c["width"], "height": c["height"], "packages": []} for c in self.containers]
        unpacked = []
        
        for package_id in individual:
            package = next(p for p in self.packages if p["id"] == package_id)
            placed = False
            for container in containers_copy:
                if self.place_package(container, package):
                    placed = True
                    break
            if not placed:
                unpacked.append(package)
        
        # Minimize the number of containers used and unpacked packages
        used_containers = sum(1 for c in containers_copy if c["packages"])
        return (used_containers, len(unpacked)), containers_copy, unpacked
    
    def place_package(self, container: Dict, package: Dict) -> bool:
        # Try to place the package in the container using a simple bottom-left heuristic
        width, height = package["width"], package["height"]
        container_width, container_height = container["width"], container["height"]
        packages_in_container = container["packages"]
        
        # If container is empty, place at (0, 0)
        if not packages_in_container:
            if width <= container_width and height <= container_height:
                package_copy = package.copy()
                package_copy["x"] = 0
                package_copy["y"] = 0
                container["packages"].append(package_copy)
                return True
            return False
        
        # Try to place the package adjacent to existing packages (simple heuristic)
        # This is a simplified approach; a more sophisticated one would be better
        max_y = 0
        total_width = 0
        for p in packages_in_container:
            total_width += p["width"]
            if p["y"] + p["height"] > max_y:
                max_y = p["y"] + p["height"]
        
        # Try to place to the right of the last package
        if total_width + width <= container_width and height <= container_height:
            package_copy = package.copy()
            package_copy["x"] = total_width
            package_copy["y"] = 0
            container["packages"].append(package_copy)
            return True
        
        # Try to place on top of the tallest package
        if width <= container_width and max_y + height <= container_height:
            package_copy = package.copy()
            package_copy["x"] = 0
            package_copy["y"] = max_y
            container["packages"].append(package_copy)
            return True
        
        return False
    
    def crossover(self, parent1: List[int], parent2: List[int]) -> List[int]:
        # Order crossover (OX)
        size = len(parent1)
        start, end = sorted(random.sample(range(size), 2))
        child = [-1] * size
        
        # Copy segment from parent1
        child[start:end] = parent1[start:end]
        
        # Fill remaining from parent2 in order
        remaining = [item for item in parent2 if item not in child]
        ptr = 0
        for i in range(size):
            if child[i] == -1:
                child[i] = remaining[ptr]
                ptr += 1
        return child
    
    def mutate(self, individual: List[int]) -> List[int]:
        if random.random() < self.mutation_rate:
            i, j = random.sample(range(len(individual)), 2)
            individual[i], individual[j] = individual[j], individual[i]
        return individual
    
    def select_parents(self, population: List[List[int]], fitness_scores: List[Tuple[int, int]]) -> List[List[int]]:
        # Tournament selection
        parents = []
        for _ in range(2):
            tournament = random.sample(list(zip(population, fitness_scores)), min(5, len(population)))
            tournament.sort(key=lambda x: (x[1][0], x[1][1]))
            parents.append(tournament[0][0])
        return parents
    
    def evolve(self) -> Dict:
        population = self.initialize_population()
        best_fitness = (float('inf'), float('inf'))
        best_solution = None
        best_containers = None
        best_unpacked = None
        
        for generation in range(self.generations):
            fitness_scores = []
            containers_list = []
            unpacked_list = []
            
            for individual in population:
                fitness_score, containers, unpacked = self.fitness(individual)
                fitness_scores.append(fitness_score)
                containers_list.append(containers)
                unpacked_list.append(unpacked)
                
                if fitness_score < best_fitness:
                    best_fitness = fitness_score
                    best_solution = individual
                    best_containers = containers
                    best_unpacked = unpacked
            
            new_population = []
            for _ in range(self.population_size // 2):
                parents = self.select_parents(population, fitness_scores)
                child1 = self.crossover(parents[0], parents[1])
                child2 = self.crossover(parents[1], parents[0])
                child1 = self.mutate(child1)
                child2 = self.mutate(child2)
                new_population.extend([child1, child2])
            
            population = new_population
        
        # Prepare the output
        used_containers = [c for c in best_containers if c["packages"]]
        output = {
            "containers": used_containers,
            "unpacked_packages": best_unpacked,
            "stats": {
                "total_containers": len(used_containers),
                "total_packed": len(self.packages) - len(best_unpacked),
                "total_unpacked": len(best_unpacked)
            }
        }
        return output

# Main execution
if __name__ == "__main__":
    packages, containers = read_input("instances/instance.txt")
    ga = GeneticAlgorithm(packages, containers)
    result = ga.evolve()
    print(json.dumps(result, indent=2))
