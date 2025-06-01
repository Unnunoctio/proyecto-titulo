import json

def read_input(file_path):
    with open(file_path, 'r') as file:
        lines = [line.strip() for line in file if line.strip()]
    
    # Read packages
    num_packages = int(lines[0])
    packages = []
    for i in range(1, num_packages + 1):
        width, height = map(int, lines[i].split())
        packages.append({
            "id": i - 1,  # 0-based index
            "width": width,
            "height": height
        })
    
    # Read containers
    offset = num_packages + 1
    num_containers = int(lines[offset])
    containers = []
    for i in range(offset + 1, offset + 1 + num_containers):
        width, height = map(int, lines[i].split())
        containers.append({
            "id": i - (offset + 1),  # 0-based index
            "width": width,
            "height": height,
            "packages": [],
            "used_space": []  # List of (x, y, width, height) rectangles
        })
    
    return packages, containers

def ffdh(packages, containers):
    # Sort packages in decreasing order of height
    sorted_packages = sorted(packages, key=lambda p: (-p['height'], -p['width']))
    
    unpacked = []
    
    for package in sorted_packages:
        placed = False
        
        for container in containers:
            # Check if package fits in container's remaining space
            if package['width'] > container['width'] or package['height'] > container['height']:
                continue
            
            # Try to place at the top-left corner first
            x, y = 0, 0
            valid_position = True
            
            # Check if this position overlaps with any existing packages
            for used in container['used_space']:
                ux, uy, uw, uh = used
                if (x < ux + uw and x + package['width'] > ux and
                    y < uy + uh and y + package['height'] > uy):
                    valid_position = False
                    break
            
            if valid_position:
                # Place the package here
                container['packages'].append({
                    "id": package["id"],
                    "width": package["width"],
                    "height": package["height"],
                    "x": x,
                    "y": y
                })
                container['used_space'].append((x, y, package['width'], package['height']))
                placed = True
                break
            
            # If top-left corner is occupied, try other positions (simple approach)
            # This is a simplified version - a more sophisticated approach would use a shelf algorithm
            # Here we just try to place it at the first available position below existing packages
            if not placed:
                # Sort used spaces by y coordinate
                used_sorted = sorted(container['used_space'], key=lambda u: u[1])
                
                # Try to place below each existing package
                for i, used in enumerate(used_sorted):
                    ux, uy, uw, uh = used
                    new_y = uy + uh
                    if new_y + package['height'] > container['height']:
                        continue
                    
                    # Check if we can place it here
                    valid = True
                    for other_used in container['used_space']:
                        ox, oy, ow, oh = other_used
                        if (0 < ox + ow and 0 + package['width'] > ox and
                            new_y < oy + oh and new_y + package['height'] > oy):
                            valid = False
                            break
                    
                    if valid:
                        container['packages'].append({
                            "id": package["id"],
                            "width": package["width"],
                            "height": package["height"],
                            "x": 0,
                            "y": new_y
                        })
                        container['used_space'].append((0, new_y, package['width'], package['height']))
                        placed = True
                        break
                
                if placed:
                    break
        
        if not placed:
            unpacked.append(package)
    
    return containers, unpacked

def format_output(containers, unpacked_packages):
    # Filter out empty containers
    used_containers = [c for c in containers if c['packages']]
    
    # Prepare the output
    output = {
        "containers": [],
        "unpacked_packages": [],
        "stats": {
            "total_containers": len(used_containers),
            "total_packed": sum(len(c['packages']) for c in used_containers),
            "total_unpacked": len(unpacked_packages)
        }
    }
    
    for container in used_containers:
        output["containers"].append({
            "id": container["id"],
            "width": container["width"],
            "height": container["height"],
            "packages": container["packages"]
        })
    
    for package in unpacked_packages:
        output["unpacked_packages"].append({
            "id": package["id"],
            "width": package["width"],
            "height": package["height"]
        })
    
    return output

def main():
    try:
        # Read input
        packages, containers = read_input("instances/instance.txt")
        
        # Apply FFDH algorithm
        used_containers, unpacked = ffdh(packages, containers)
        
        # Format output
        output = format_output(used_containers, unpacked)
        
        # Print output as JSON
        print(json.dumps(output, indent=2))
    
    except FileNotFoundError:
        print("Error: Input file not found at 'instances/instance.txt'")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
