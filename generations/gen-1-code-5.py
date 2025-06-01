import json
from collections import defaultdict

def read_input(file_path):
    with open(file_path, 'r') as file:
        lines = [line.strip() for line in file.readlines() if line.strip()]
    
    num_packages = int(lines[0])
    packages = []
    for i in range(1, num_packages + 1):
        parts = lines[i].split()
        width, height = map(int, parts)
        packages.append({'id': i-1, 'width': width, 'height': height})
    
    offset = num_packages + 1
    num_containers = int(lines[offset])
    containers = []
    for i in range(offset + 1, offset + 1 + num_containers):
        parts = lines[i].split()
        width, height = map(int, parts)
        containers.append({'id': i - (offset + 1), 'width': width, 'height': height})
    
    return packages, containers

def can_place(package, x, y, container_width, container_height, placed_packages):
    pw, ph = package['width'], package['height']
    if x + pw > container_width or y + ph > container_height:
        return False
    for p in placed_packages:
        px, py, pwidth, pheight = p['x'], p['y'], p['width'], p['height']
        if not (x >= px + pwidth or x + pw <= px or y >= py + pheight or y + ph <= py):
            return False
    return True

def place_package(package, container, placed_packages):
    container_width = container['width']
    container_height = container['height']
    best_spot = None
    # Try bottom-left placement
    for y in range(container_height - package['height'] + 1):
        for x in range(container_width - package['width'] + 1):
            if can_place(package, x, y, container_width, container_height, placed_packages):
                return (x, y)
    return None

def branch_and_bound(packages, containers):
    containers = sorted(containers, key=lambda c: (c['width'], c['height']))
    packages_sorted = sorted(packages, key=lambda p: -(p['width'] * p['height']))
    
    best_solution = {
        'containers': [],
        'unpacked_packages': [],
        'stats': {
            'total_containers': float('inf'),
            'total_packed': 0,
            'total_unpacked': len(packages)
        }
    }
    
    def backtrack(index, current_containers, remaining_packages):
        nonlocal best_solution
        if index == len(packages_sorted):
            total_containers = len(current_containers)
            total_packed = len(packages_sorted) - len(remaining_packages)
            if total_containers < best_solution['stats']['total_containers'] or \
               (total_containers == best_solution['stats']['total_containers'] and total_packed > best_solution['stats']['total_packed']):
                unpacked = [{'id': p['id'], 'width': p['width'], 'height': p['height']} for p in remaining_packages]
                best_solution = {
                    'containers': current_containers.copy(),
                    'unpacked_packages': unpacked,
                    'stats': {
                        'total_containers': total_containers,
                        'total_packed': total_packed,
                        'total_unpacked': len(unpacked)
                    }
                }
            return
        
        package = packages_sorted[index]
        placed = False
        for container_idx, container in enumerate(current_containers):
            placed_packages = container['packages']
            position = place_package(package, container, placed_packages)
            if position is not None:
                x, y = position
                new_package_info = {
                    'id': package['id'],
                    'width': package['width'],
                    'height': package['height'],
                    'x': x,
                    'y': y
                }
                current_containers[container_idx]['packages'].append(new_package_info)
                backtrack(index + 1, current_containers, remaining_packages)
                current_containers[container_idx]['packages'].pop()
                placed = True
        
        if not placed and len(current_containers) < len(containers):
            new_container = containers[len(current_containers)]
            new_container_dict = {
                'id': len(current_containers),
                'width': new_container['width'],
                'height': new_container['height'],
                'packages': []
            }
            position = place_package(package, new_container, [])
            if position is not None:
                x, y = position
                new_package_info = {
                    'id': package['id'],
                    'width': package['width'],
                    'height': package['height'],
                    'x': x,
                    'y': y
                }
                new_container_dict['packages'] = [new_package_info]
                current_containers.append(new_container_dict)
                backtrack(index + 1, current_containers, remaining_packages)
                current_containers.pop()
        
        if not placed:
            backtrack(index + 1, current_containers, remaining_packages + [package])
    
    backtrack(0, [], [])
    return best_solution

def main():
    packages, containers = read_input('instances/instance.txt')
    solution = branch_and_bound(packages, containers)
    print(json.dumps(solution, indent=4))

if __name__ == '__main__':
    main()
