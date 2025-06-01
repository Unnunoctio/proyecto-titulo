import json
import random
from collections import defaultdict

def read_input(file_path):
    with open(file_path, 'r') as file:
        lines = [line.strip() for line in file if line.strip()]
    
    num_packages = int(lines[0])
    packages = []
    for i in range(1, num_packages + 1):
        width, height = map(int, lines[i].split())
        packages.append({'id': i-1, 'width': width, 'height': height})
    
    num_containers = int(lines[num_packages + 1])
    containers = []
    for i in range(num_packages + 2, num_packages + 2 + num_containers):
        width, height = map(int, lines[i].split())
        containers.append({'id': i - (num_packages + 2), 'width': width, 'height': height})
    
    return packages, containers

def greedy_packing(packages, containers):
    # Sort packages by area in descending order
    sorted_packages = sorted(packages, key=lambda p: p['width'] * p['height'], reverse=True)
    container_list = []
    unpacked = []
    
    for container in containers:
        container_list.append({
            'id': container['id'],
            'width': container['width'],
            'height': container['height'],
            'packages': []
        })
    
    # Create a list to represent used containers and their remaining space
    used_containers = []
    
    for package in sorted_packages:
        placed = False
        for container in container_list:
            # Check if package fits in the container
            if package['width'] <= container['width'] and package['height'] <= container['height']:
                # Try to place the package in the container without overlapping
                # For simplicity, we'll use a simple approach: place at (0,0) if possible
                # In a real scenario, you'd need a more sophisticated placement strategy
                # Here, we assume the container is empty (simplified)
                if not container['packages']:
                    container['packages'].append({
                        'id': package['id'],
                        'width': package['width'],
                        'height': package['height'],
                        'x': 0,
                        'y': 0
                    })
                    placed = True
                    break
                else:
                    # Check if the package can fit in the remaining space
                    # This is a placeholder; actual implementation would need a more complex check
                    pass
        if not placed:
            unpacked.append(package)
    
    # Filter out empty containers
    used_containers = [c for c in container_list if c['packages']]
    
    return used_containers, unpacked

def genetic_algorithm(packages, containers, initial_solution):
    # Placeholder for genetic algorithm implementation
    # This would involve creating a population of solutions, evaluating them,
    # and applying selection, crossover, and mutation to evolve better solutions
    # For now, return the initial solution
    return initial_solution

def solve_packing():
    file_path = "instances/instance.txt"
    packages, containers = read_input(file_path)
    
    # Step 1: Greedy algorithm for initial solution
    greedy_containers, unpacked = greedy_packing(packages, containers)
    
    # Step 2: Apply genetic algorithm (placeholder)
    final_containers = genetic_algorithm(packages, containers, greedy_containers)
    
    # Prepare output
    output = {
        "containers": final_containers,
        "unpacked_packages": unpacked,
        "stats": {
            "total_containers": len(final_containers),
            "total_packed": sum(len(c['packages']) for c in final_containers),
            "total_unpacked": len(unpacked)
        }
    }
    
    print(json.dumps(output, indent=4))

if __name__ == "__main__":
    solve_packing()
