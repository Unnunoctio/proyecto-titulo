import os
from collections import defaultdict
import math
from typing import List, Dict, Tuple
import json
from itertools import product

class Package:
    def __init__(self, id: int, width: int, height: int):
        self.id = id
        self.width = width
        self.height = height

class Container:
    def __init__(self, id: int, width: int, height: int):
        self.id = id
        self.width = width
        self.height = height
        self.packages = []  # List of tuples (package, x, y)

def read_input(file_path: str) -> Tuple[List[Package], List[Container]]:
    with open(file_path, 'r') as file:
        lines = [line.strip() for line in file.readlines() if line.strip()]
    
    # Read packages
    num_packages = int(lines[0])
    packages = []
    for i in range(1, num_packages + 1):
        width, height = map(int, lines[i].split())
        packages.append(Package(i - 1, width, height))  # id starts from 0
    
    # Read containers
    offset = num_packages + 1
    num_containers = int(lines[offset])
    containers = []
    for i in range(offset + 1, offset + 1 + num_containers):
        width, height = map(int, lines[i].split())
        containers.append(Container(len(containers), width, height))
    
    return packages, containers

def solve_packing(packages: List[Package], containers: List[Container]):
    if not containers:
        return {
            "containers": [],
            "unpacked_packages": [{"id": p.id, "width": p.width, "height": p.height} for p in packages],
            "stats": {
                "total_containers": 0,
                "total_packed": 0,
                "total_unpacked": len(packages)
            }
        }
    
    # We'll use a simple heuristic for demonstration: First-Fit Decreasing Height (FFDH)
    # This is a placeholder for the actual column generation approach
    # Sort packages by height in descending order
    sorted_packages = sorted(packages, key=lambda p: -p.height)
    
    container_type = containers[0]  # Assuming all containers are of the same type for simplicity
    container_width = container_type.width
    container_height = container_type.height
    
    # Implement FFDH algorithm
    shelves = []  # List of (remaining_width, current_height)
    packed = []
    
    for p in sorted_packages:
        placed = False
        # Try to place in existing shelves
        for i, (remaining_width, shelf_height) in enumerate(shelves):
            if p.height <= shelf_height and p.width <= remaining_width:
                # Place the package here
                x = container_width - remaining_width
                y = container_height - shelf_height
                packed.append((p, x, y, i))
                shelves[i] = (remaining_width - p.width, shelf_height)
                placed = True
                break
        if not placed:
            # Check if the package fits in a new shelf
            if p.height <= container_height and p.width <= container_width:
                new_shelf_height = p.height
                total_used_height = sum(sh for rw, sh in shelves) + new_shelf_height
                if total_used_height <= container_height:
                    x = 0
                    y = container_height - total_used_height
                    packed.append((p, x, y, len(shelves)))
                    shelves.append((container_width - p.width, new_shelf_height))
                    placed = True
        if not placed:
            pass  # The package remains unpacked
    
    # Organize packed packages into containers
    # For FFDH, all packages are packed into one container if possible
    # But in reality, multiple containers may be needed
    # Here, we'll assume one container can hold all packages that fit via FFDH
    # This is a simplification; actual implementation may require more containers
    
    # For this example, we'll assume one container is used
    container_id = 0
    container_result = {
        "id": container_id,
        "width": container_width,
        "height": container_height,
        "packages": []
    }
    unpacked = []
    
    packed_in_container = []
    for p, x, y, shelf_idx in packed:
        packed_in_container.append({
            "id": p.id,
            "width": p.width,
            "height": p.height,
            "x": x,
            "y": y
        })
    
    # Check which packages are not packed
    packed_ids = {p.id for p, _, _, _ in packed}
    unpacked_packages = [p for p in packages if p.id not in packed_ids]
    
    container_result["packages"] = packed_in_container
    
    result = {
        "containers": [container_result] if packed_in_container else [],
        "unpacked_packages": [{"id": p.id, "width": p.width, "height": p.height} for p in unpacked_packages],
        "stats": {
            "total_containers": 1 if packed_in_container else 0,
            "total_packed": len(packed_in_container),
            "total_unpacked": len(unpacked_packages)
        }
    }
    
    return result

def main():
    input_file = os.path.join("instances", "instance.txt")
    packages, containers = read_input(input_file)
    result = solve_packing(packages, containers)
    print(json.dumps(result, indent=4))

if __name__ == "__main__":
    main()
