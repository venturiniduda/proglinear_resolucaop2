import glob
import os

def read_instances():
    instances = []
    
    for filepath in glob.glob("./instancias/*.txt"):
        with open(filepath, "r") as f:
            lines = [line.strip() for line in f if line.strip()]

        instance_name = filepath
        n = int(lines[0])
        location_data = []

        # Primeiro ponto: depósito
        x0, y0 = map(int, lines[1].split())
        location_data.append([x0, y0, 0, 0])  # depósito

        for line in lines[2:]:
            parts = list(map(int, line.split()))
            location_data.append(parts)
        
        instance_name = f.name.split("/")[-1].split(".")[0].split("\\")[-1]
        instances.append((instance_name, location_data))

        return instances