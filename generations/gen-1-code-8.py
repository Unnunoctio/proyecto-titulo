import json

def read_instance(file_path):
    with open(file_path, 'r') as file:
        lines = [line.strip() for line in file.readlines() if line.strip()]
    
    # Read packages
    num_packages = int(lines[0])
    packages = []
    for i in range(1, num_packages + 1):
        parts = list(map(int, lines[i].split()))
        packages.append({
            "id": i - 1,
            "width": parts[0],
            "height": parts[1]
        })
    
    # Read containers
    num_containers = int(lines[num_packages + 1])
    containers = []
    for i in range(num_packages + 2, num_packages + 2 + num_containers):
        parts = list(map(int, lines[i].split()))
        containers.append({
            "id": i - (num_packages + 2),
            "width": parts[0],
            "height": parts[1]
        })
    
    return packages, containers

def sort_packages(packages):
    return sorted(packages, key=lambda p: (-p['width'], -p['height']))

def pack_bins(packages, containers):
    if not containers:
        return [], packages, 0, 0
    
    # Sort containers by area descending to use largest first
    sorted_containers = sorted(containers, key=lambda c: (-c['width'] * c['height'], -c['width'], -c['height']))
    
    packed_containers = []
    remaining_packages = packages.copy()
    unpacked_packages = []
    
    for container in sorted_containers:
        current_container = {
            "id": container['id'],
            "width": container['width'],
            "height": container['height'],
            "packages": []
        }
        
        # Initialize the container's space as a grid (simplified for this approach)
        # We'll use a list of placed rectangles (x, y, width, height)
        placed_rectangles = []
        
        packages_to_remove = []
        
        for package in remaining_packages:
            width = package['width']
            height = package['height']
            
            # Check if package fits in the container
            if width > container['width'] or height > container['height']:
                continue
            
            # Try to place the package in the container using a simple approach (e.g., bottom-left)
            # Find a position (x, y) where the package can fit without overlapping
            found_position = False
            # Try all possible positions in a grid-like manner (simplified)
            # Start with (0,0) and check if it fits
            # If not, try (0, y + 1), etc.
            # This is a simplified approach; a more sophisticated method would use a more efficient packing algorithm
            max_tries = 100  # Prevent infinite loops in this simplified approach
            tries = 0
            for y in range(0, container['height'] - height + 1):
                for x in range(0, container['width'] - width + 1):
                    if tries >= max_tries:
                        break
                    tries += 1
                    # Check if the current rectangle (x, y, width, height) overlaps with any placed rectangle
                    overlap = False
                    for rect in placed_rectangles:
                        if (x < rect['x'] + rect['width'] and
                            x + width > rect['x'] and
                            y < rect['y'] + rect['height'] and
                            y + height > rect['y']):
                            overlap = True
                            break
                    if not overlap:
                        # Place the package here
                        placed_rectangles.append({
                            'x': x,
                            'y': y,
                            'width': width,
                            'height': height
                        })
                        current_container['packages'].append({
                            "id": package['id'],
                            "width": width,
                            "height": height,
                            "x": x,
                            "y": y
                        })
                        packages_to_remove.append(package)
                        found_position = True
                        break
                if found_position:
                    break
            if found_position:
                continue
        
        if current_container['packages']:
            packed_containers.append(current_container)
            # Remove the packed packages from remaining_packages
            for p in packages_to_remove:
                if p in remaining_packages:
                    remaining_packages.remove(p)
    
    unpacked_packages = remaining_packages
    
    total_packed = sum(len(c['packages']) for c in packed_containers)
    total_unpacked = len(unpacked_packages)
    total_containers = len(packed_containers)
    
    return packed_containers, unpacked_packages, total_containers, total_packed, total_unpacked

def main():
    input_file = "instances/instance.txt"
    packages, containers = read_instance(input_file)
    sorted_packages = sort_packages(packages)
    packed_containers, unpacked_packages, total_containers, total_packed, total_unpacked = pack_bins(sorted_packages, containers)
    
    output = {
        "containers": packed_containers,
        "unpacked_packages": unpacked_packages,
        "stats": {
            "total_containers": total_containers,
            "total_packed": total_packed,
            "total_unpacked": total_unpacked
        }
    }
    
    print(json.dumps(output, indent=4))

if __name__ == "__main__":
    main()
