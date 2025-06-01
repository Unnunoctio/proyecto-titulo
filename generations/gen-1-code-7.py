import os

def read_input(file_path):
    with open(file_path, 'r') as file:
        lines = [line.strip() for line in file.readlines() if line.strip()]
    
    # Read packages
    num_packages = int(lines[0])
    packages = []
    for i in range(1, num_packages + 1):
        parts = lines[i].split()
        width, height = map(int, parts)
        packages.append({'id': i, 'width': width, 'height': height})
    
    # Read containers
    offset = num_packages + 1
    num_containers = int(lines[offset])
    containers = []
    for i in range(offset + 1, offset + 1 + num_containers):
        parts = lines[i].split()
        width, height = map(int, parts)
        containers.append({'id': len(containers) + 1, 'width': width, 'height': height, 'packages': []})
    
    return packages, containers

def skyline_pack(packages, containers):
    # Sort packages in decreasing order of height
    sorted_packages = sorted(packages, key=lambda p: (-p['height'], p['width']))
    
    unpacked = []
    used_containers = []
    
    for package in sorted_packages:
        placed = False
        # Try to place in existing containers
        for container in used_containers:
            skyline = container.get('skyline', [(0, 0, container['width'])])
            new_skyline, placement = find_placement(skyline, package, container['height'])
            if placement:
                x, y = placement
                container['packages'].append({
                    'id': package['id'],
                    'width': package['width'],
                    'height': package['height'],
                    'x': x,
                    'y': y
                })
                container['skyline'] = new_skyline
                placed = True
                break
        
        if not placed:
            # Try to place in a new container
            for container_template in containers:
                container_id = len(used_containers) + 1
                # Check if this container template is already used or can be used
                # We can use multiple containers of the same template
                # So create a new container instance
                new_container = {
                    'id': container_id,
                    'width': container_template['width'],
                    'height': container_template['height'],
                    'packages': [],
                    'skyline': [(0, 0, container_template['width'])]
                }
                skyline = new_container['skyline']
                new_skyline, placement = find_placement(skyline, package, new_container['height'])
                if placement:
                    x, y = placement
                    new_container['packages'].append({
                        'id': package['id'],
                        'width': package['width'],
                        'height': package['height'],
                        'x': x,
                        'y': y
                    })
                    new_container['skyline'] = new_skyline
                    used_containers.append(new_container)
                    placed = True
                    break
            if not placed:
                unpacked.append(package)
    
    return used_containers, unpacked

def find_placement(skyline, package, container_height):
    width = package['width']
    height = package['height']
    
    best_y = float('inf')
    best_x = -1
    best_index = -1
    
    # Iterate through the skyline segments to find the best placement
    for i in range(len(skyline)):
        seg_x, seg_y, seg_width = skyline[i]
        # Check if the segment is wide enough
        if seg_width >= width:
            # Check if the height fits within the container
            if seg_y + height <= container_height:
                if seg_y < best_y:
                    best_y = seg_y
                    best_x = seg_x
                    best_index = i
            else:
                continue
        else:
            continue
    
    if best_index == -1:
        return skyline, None
    
    # Calculate the new skyline after placing the package
    new_skyline = []
    placed_segment = (best_x, best_y + height, width)
    
    # Process segments before the placed segment
    for i in range(best_index):
        seg_x, seg_y, seg_width = skyline[i]
        new_skyline.append((seg_x, seg_y, seg_width))
    
    # Handle the segment where the package is placed
    seg_x, seg_y, seg_width = skyline[best_index]
    remaining_width = seg_width - width
    # Left remaining segment (if any)
    if best_x > seg_x:
        new_skyline.append((seg_x, seg_y, best_x - seg_x))
    # The placed package segment
    new_skyline.append(placed_segment)
    # Right remaining segment (if any)
    if remaining_width > 0:
        new_skyline.append((best_x + width, seg_y, remaining_width))
    
    # Process segments after the placed segment
    for i in range(best_index + 1, len(skyline)):
        seg_x, seg_y, seg_width = skyline[i]
        new_skyline.append((seg_x, seg_y, seg_width))
    
    # Merge adjacent segments with the same height
    merged_skyline = []
    if not new_skyline:
        return new_skyline, (best_x, best_y)
    
    current_seg = new_skyline[0]
    for seg in new_skyline[1:]:
        if seg[1] == current_seg[1] and (current_seg[0] + current_seg[2]) == seg[0]:
            # Merge segments
            current_seg = (current_seg[0], current_seg[1], current_seg[2] + seg[2])
        else:
            merged_skyline.append(current_seg)
            current_seg = seg
    merged_skyline.append(current_seg)
    
    return merged_skyline, (best_x, best_y)

def main():
    input_file = os.path.join('instances', 'instance.txt')
    packages, containers = read_input(input_file)
    used_containers, unpacked = skyline_pack(packages, containers)
    
    # Prepare the output
    output = {
        "containers": [
            {
                "id": container['id'],
                "width": container['width'],
                "height": container['height'],
                "packages": [
                    {
                        "id": pkg['id'],
                        "width": pkg['width'],
                        "height": pkg['height'],
                        "x": pkg['x'],
                        "y": pkg['y']
                    }
                    for pkg in container['packages']
                ]
            }
            for container in used_containers
        ],
        "unpacked_packages": [
            {
                "id": pkg['id'],
                "width": pkg['width'],
                "height": pkg['height']
            }
            for pkg in unpacked
        ],
        "stats": {
            "total_containers": len(used_containers),
            "total_packed": sum(len(container['packages']) for container in used_containers),
            "total_unpacked": len(unpacked)
        }
    }
    
    print(output)

if __name__ == "__main__":
    main()
