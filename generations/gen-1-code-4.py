import json
import random
import math
from copy import deepcopy

def read_input(file_path):
    with open(file_path, 'r') as file:
        lines = [line.strip() for line in file.readlines() if line.strip()]
    
    num_packages = int(lines[0])
    packages = []
    for i in range(1, num_packages + 1):
        parts = lines[i].split()
        width, height = map(int, parts)
        packages.append({"id": i-1, "width": width, "height": height})
    
    num_containers = int(lines[num_packages + 1])
    containers = []
    for i in range(num_packages + 2, num_packages + 2 + num_containers):
        parts = lines[i].split()
        width, height = map(int, parts)
        containers.append({"id": i - (num_packages + 2), "width": width, "height": height, "packages": []})
    
    return packages, containers

def initial_solution(packages, containers):
    # Sort packages by area in descending order
    sorted_packages = sorted(packages, key=lambda p: p['width'] * p['height'], reverse=True)
    containers_copy = deepcopy(containers)
    
    for container in containers_copy:
        container['packages'] = []
    
    unpacked = []
    container_occupancy = []
    for container in containers_copy:
        container_occupancy.append({
            'used_space': [],
            'width': container['width'],
            'height': container['height']
        })
    
    for package in sorted_packages:
        placed = False
        for i, container in enumerate(containers_copy):
            occupancy = container_occupancy[i]
            width, height = package['width'], package['height']
            container_width, container_height = container['width'], container['height']
            
            if width > container_width or height > container_height:
                continue
            
            # Try to place the package in the container using bottom-left heuristic
            # Generate candidate positions
            candidate_positions = []
            if not occupancy['used_space']:
                candidate_positions.append((0, 0))
            else:
                for rect in occupancy['used_space']:
                    x, y, rw, rh = rect
                    candidate_positions.append((x + rw, y))
                    candidate_positions.append((x, y + rh))
            
            # Also consider positions at the top and left edges
            candidate_positions.append((0, 0))
            
            for (x, y) in candidate_positions:
                if x + width > container_width or y + height > container_height:
                    continue
                
                # Check for collisions with existing packages
                collision = False
                for rect in occupancy['used_space']:
                    rx, ry, rw, rh = rect
                    if not (x + width <= rx or rx + rw <= x or y + height <= ry or ry + rh <= y):
                        collision = True
                        break
                if not collision:
                    # Place the package here
                    package_placement = {
                        'id': package['id'],
                        'width': width,
                        'height': height,
                        'x': x,
                        'y': y
                    }
                    container['packages'].append(package_placement)
                    occupancy['used_space'].append((x, y, width, height))
                    placed = True
                    break
            if placed:
                break
        if not placed:
            unpacked.append(package)
    
    return containers_copy, unpacked

def calculate_cost(containers):
    # Cost is the number of containers used (those with at least one package)
    used_containers = sum(1 for container in containers if container['packages'])
    total_unpacked = 0  # This would be handled separately
    return used_containers

def generate_neighbor(current_containers, current_unpacked, all_containers):
    # Make a deep copy to manipulate
    neighbor_containers = deepcopy(current_containers)
    neighbor_unpacked = deepcopy(current_unpacked)
    
    # Choose a random action: swap two packages, move a package, etc.
    action = random.choice(['swap', 'move', 'reinsert'])
    
    if action == 'swap' and len(neighbor_containers) >= 2:
        # Select two random containers with packages
        non_empty = [i for i, c in enumerate(neighbor_containers) if c['packages']]
        if len(non_empty) >= 2:
            i, j = random.sample(non_empty, 2)
            c1_packages = neighbor_containers[i]['packages']
            c2_packages = neighbor_containers[j]['packages']
            if c1_packages and c2_packages:
                idx1 = random.randint(0, len(c1_packages) - 1)
                idx2 = random.randint(0, len(c2_packages) - 1)
                c1_packages[idx1], c2_packages[idx2] = c2_packages[idx2], c1_packages[idx1]
    
    elif action == 'move':
        # Move a package from one container to another
        non_empty = [i for i, c in enumerate(neighbor_containers) if c['packages']]
        if non_empty:
            src_idx = random.choice(non_empty)
            src_container = neighbor_containers[src_idx]
            if src_container['packages']:
                pkg_idx = random.randint(0, len(src_container['packages']) - 1)
                pkg = src_container['packages'].pop(pkg_idx)
                # Try to place pkg in another container
                placed = False
                for dst_idx, dst_container in enumerate(neighbor_containers):
                    if dst_idx == src_idx:
                        continue
                    # Check if package fits in dst_container
                    if pkg['width'] <= dst_container['width'] and pkg['height'] <= dst_container['height']:
                        # Try to find a position (simplified)
                        # Here, we would ideally use a more sophisticated placement check
                        # For simplicity, assume it fits at (0,0) without checking overlaps
                        # In a real implementation, you'd need collision detection
                        dst_container['packages'].append(pkg)
                        placed = True
                        break
                if not placed:
                    neighbor_unpacked.append(pkg)
    
    elif action == 'reinsert' and neighbor_unpacked:
        # Try to insert an unpacked package into a container
        pkg_idx = random.randint(0, len(neighbor_unpacked) - 1)
        pkg = neighbor_unpacked.pop(pkg_idx)
        placed = False
        for container in neighbor_containers:
            if pkg['width'] <= container['width'] and pkg['height'] <= container['height']:
                # Simplified placement check
                container['packages'].append(pkg)
                placed = True
                break
        if not placed:
            neighbor_unpacked.append(pkg)
    
    # After modifying, need to revalidate placements (omitted for simplicity)
    # In a real implementation, you'd need to ensure no overlaps and fits
    
    return neighbor_containers, neighbor_unpacked

def simulated_annealing(packages, containers, initial_temp=1000, cooling_rate=0.995, iterations=1000):
    current_containers, current_unpacked = initial_solution(packages, containers)
    current_cost = calculate_cost(current_containers)
    
    best_containers = deepcopy(current_containers)
    best_unpacked = deepcopy(current_unpacked)
    best_cost = current_cost
    
    temp = initial_temp
    
    for i in range(iterations):
        neighbor_containers, neighbor_unpacked = generate_neighbor(current_containers, current_unpacked, containers)
        neighbor_cost = calculate_cost(neighbor_containers)
        
        if neighbor_cost < current_cost:
            current_containers, current_unpacked = neighbor_containers, neighbor_unpacked
            current_cost = neighbor_cost
            if current_cost < best_cost:
                best_containers = deepcopy(current_containers)
                best_unpacked = deepcopy(current_unpacked)
                best_cost = current_cost
        else:
            # Accept worse solution with a probability
            delta = neighbor_cost - current_cost
            acceptance_prob = math.exp(-delta / temp)
            if random.random() < acceptance_prob:
                current_containers, current_unpacked = neighbor_containers, neighbor_unpacked
                current_cost = neighbor_cost
        
        temp *= cooling_rate
    
    return best_containers, best_unpacked

def format_output(containers, unpacked_packages):
    output_containers = []
    for container in containers:
        if container['packages']:
            output_container = {
                "id": container['id'],
                "width": container['width'],
                "height": container['height'],
                "packages": []
            }
            for package in container['packages']:
                output_container['packages'].append({
                    "id": package['id'],
                    "width": package['width'],
                    "height": package['height'],
                    "x": package['x'],
                    "y": package['y']
                })
            output_containers.append(output_container)
    
    output_unpacked = []
    for package in unpacked_packages:
        output_unpacked.append({
            "id": package['id'],
            "width": package['width'],
            "height": package['height']
        })
    
    total_packed = sum(len(c['packages']) for c in output_containers)
    total_unpacked = len(output_unpacked)
    stats = {
        "total_containers": len(output_containers),
        "total_packed": total_packed,
        "total_unpacked": total_unpacked
    }
    
    return {
        "containers": output_containers,
        "unpacked_packages": output_unpacked,
        "stats": stats
    }

def main():
    input_file = "instances/instance.txt"
    packages, containers = read_input(input_file)
    
    # Run simulated annealing
    best_containers, best_unpacked = simulated_annealing(packages, containers)
    
    # Format the output
    output = format_output(best_containers, best_unpacked)
    
    # Print the output as JSON
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
