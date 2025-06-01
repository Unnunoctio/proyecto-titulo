import os

def read_instance_file(file_path):
    with open(file_path, 'r') as file:
        lines = [line.strip() for line in file.readlines() if line.strip()]
    
    # Read packages
    num_packages = int(lines[0])
    packages = []
    for i in range(1, num_packages + 1):
        parts = lines[i].split()
        width, height = map(int, parts)
        packages.append({'id': i-1, 'width': width, 'height': height})
    
    # Read containers
    num_containers = int(lines[num_packages + 1])
    containers = []
    for i in range(num_packages + 2, num_packages + 2 + num_containers):
        parts = lines[i].split()
        width, height = map(int, parts)
        containers.append({'id': i - (num_packages + 2), 'width': width, 'height': height, 'remaining_width': width, 'shelves': []})
    
    return packages, containers

def bfdh_packing(packages, containers):
    # Sort packages in decreasing order of height
    sorted_packages = sorted(packages, key=lambda p: -p['height'])
    
    # Initialize containers
    container_instances = []
    for container in containers:
        container_instances.append({
            'id': container['id'],
            'width': container['width'],
            'height': container['height'],
            'shelves': [{'y': 0, 'remaining_width': container['width'], 'height': container['height']}]
        })
    
    unpacked_packages = []
    packed_packages_info = []
    
    for package in sorted_packages:
        placed = False
        best_container = None
        best_shelf = None
        min_remaining_width = float('inf')
        
        for container in container_instances:
            for shelf in container['shelves']:
                if (shelf['remaining_width'] >= package['width'] and 
                    shelf['height'] >= package['height'] and 
                    shelf['remaining_width'] < min_remaining_width):
                    min_remaining_width = shelf['remaining_width']
                    best_container = container
                    best_shelf = shelf
        
        if best_container is not None:
            # Place the package on the best shelf
            x_pos = best_container['width'] - best_shelf['remaining_width']
            y_pos = best_shelf['y']
            
            # Record the package placement
            if 'packages' not in best_container:
                best_container['packages'] = []
            best_container['packages'].append({
                'id': package['id'],
                'width': package['width'],
                'height': package['height'],
                'x': x_pos,
                'y': y_pos
            })
            
            # Update the shelf's remaining width
            best_shelf['remaining_width'] -= package['width']
            
            # Create a new shelf above this package if there's remaining height
            remaining_height = best_shelf['height'] - package['height']
            if remaining_height > 0:
                new_shelf = {
                    'y': y_pos + package['height'],
                    'remaining_width': best_container['width'],
                    'height': remaining_height
                }
                # Insert the new shelf right after the current shelf to check it next
                index = best_container['shelves'].index(best_shelf)
                best_container['shelves'].insert(index + 1, new_shelf)
            
            placed = True
            break
        
        if not placed:
            unpacked_packages.append({
                'id': package['id'],
                'width': package['width'],
                'height': package['height']
            })
    
    # Prepare the output
    output_containers = []
    for container in container_instances:
        if 'packages' in container and container['packages']:
            output_containers.append({
                'id': container['id'],
                'width': container['width'],
                'height': container['height'],
                'packages': container['packages']
            })
    
    stats = {
        'total_containers': len([c for c in container_instances if 'packages' in c and c['packages']]),
        'total_packed': sum(len(c['packages']) for c in container_instances if 'packages' in c),
        'total_unpacked': len(unpacked_packages)
    }
    
    return {
        'containers': output_containers,
        'unpacked_packages': unpacked_packages,
        'stats': stats
    }

def main():
    file_path = os.path.join('instances', 'instance.txt')
    packages, containers = read_instance_file(file_path)
    result = bfdh_packing(packages, containers)
    print(result)

if __name__ == "__main__":
    main()
