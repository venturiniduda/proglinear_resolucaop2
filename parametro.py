import glob
import os

def read_instances():
    instances = []
    
    paths = os.path.join("./instancias", "*.txt")

    for file in glob.glob(paths):
        with open(file, "r") as file:
            lines = file.readlines()[1:]
            locations_data = []

            start_location_coords = list(map(int, lines[0].strip().split()))
            locations_data.append((*start_location_coords, 0, 0))

            for line in lines[1:]:
                data = list(map(int, line.strip().split()))
                coords, service_time, max_time = data[:2], data[2], data[3]

                locations_data.append((*coords, service_time, max_time))
            
            instance_name = file.name.split("/")[-1].split(".")[0].split("\\")[-1]
            instances.append((instance_name, locations_data))
    
    return instances