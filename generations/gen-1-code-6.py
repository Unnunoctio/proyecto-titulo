import json

def read_input(file_path):
    with open(file_path, 'r') as file:
        lines = [line.strip() for line in file.readlines() if line.strip()]
    
    # Read packages
    num_packages = int(lines[0])
    packages = []
    for i in range(1, num_packages + 1):
        parts = lines[i].split()
        width, height = map(int, parts)
        packages.append({"id": i-1, "width": width, "height": height})
    
    # Read containers
    num_containers = int(lines[num_packages + 1])
    containers = []
    for i in range(num_packages + 2, num_packages + 2 + num_containers):
        parts = lines[i].split()
        width, height = map(int, parts)
        containers.append({"id": i - (num_packages + 2), "width": width, "height": height, "packages": []})
    
    return packages, containers

def pack_packages(packages, containers):
    # Sort packages in decreasing order of area
    sorted_packages = sorted(packages, key=lambda p: p['width'] * p['height'], reverse=True)
    
    unpacked_packages = []
    
    for package in sorted_packages:
        placed = False
        for container in containers:
            # Check if package fits in the container
            if package['width'] <= container['width'] and package['height'] <= container['height']:
                # Try to place the package at the first available position (bottom-left)
                # For simplicity, we assume placement starts at (0,0) and check for overlaps with existing packages
                # This is a simplified approach; more sophisticated methods might be needed for optimal placement
                new_x = 0
                new_y = 0
                
                # Check if the package can be placed at (new_x, new_y) without overlapping existing packages
                can_place = True
                for placed_pkg in container['packages']:
                    # Check for overlap
                    if not (new_x + package['width'] <= placed_pkg['x'] or 
                            new_x >= placed_pkg['x'] + placed_pkg['width'] or
                            new_y + package['height'] <= placed_pkg['y'] or
                            new_y >= placed_pkg['y'] + placed_pkg['height']):
                        can_place = False
                        break
                
                if can_place:
                    # Place the package
                    placed_package = {
                        "id": package["id"],
                        "width": package["width"],
                        "height": package["height"],
                        "x": new_x,
                        "y": new_y
                    }
                    container['packages'].append(placed_package)
                    placed = True
                    break
        
        if not placed:
            unpacked_packages.append({"id": package["id"], "width": package["width"], "height": package["height"]})
    
    return containers, unpacked_packages

def generate_output(containers, unpacked_packages):
    output_containers = []
    container_id_map = {}
    new_id = 0
    for container in containers:
        if container['packages']:
            output_containers.append({
                "id": new_id,
                "width": container["width"],
                "height": container["height"],
                "packages": container["packages"]
            })
            new_id += 1
    
    total_packed = sum(len(container['packages']) for container in output_containers)
    total_unpacked = len(unpacked_packages)
    stats = {
        "total_containers": len(output_containers),
        "total_packed": total_packed,
        "total_unpacked": total_unpacked
    }
    
    output = {
        "containers": output_containers,
        "unpacked_packages": unpacked_packages,
        "stats": stats
    }
    
    return output

def main():
    input_file = "instances/instance.txt"
    packages, containers = read_input(input_file)
    packed_containers, unpacked_packages = pack_packages(packages, containers)
    output = generate_output(packed_containers, unpacked_packages)
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
