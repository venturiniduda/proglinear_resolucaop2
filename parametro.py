import glob
import os

def is_last_point_depot(location_data):
    """
    Verifica se o último ponto da instância é igual ao depósito.
    """
    if not location_data:
        return False
    return location_data[0][:2] == location_data[-1][:2]

def read_instances():
    """
    Lê todos os arquivos .txt da pasta 'instancias', formata os dados e
    retorna uma lista de tuplas, cada uma contendo o nome da instância
    e os dados de localização.
    """
    instances = []
    
    search_path = os.path.join("instancias", "*.txt")
    filepaths = glob.glob(search_path)

    for filepath in filepaths:
        with open(filepath, "r", encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]

        location_data = []
        x0, y0 = map(int, lines[1].split())
        location_data.append([x0, y0, 0, 0])  # Adiciona o depósito

        for line in lines[2:]:
            parts = list(map(int, line.split()))
            location_data.append(parts)

        # # Verifica se último ponto é o depósito; se não, adiciona
        # if not is_last_point_depot(location_data):
        #     location_data.append(location_data[0])  # Adiciona retorno ao depósito

        instance_name = os.path.basename(filepath)
        instance_name = os.path.splitext(instance_name)[0]
        
        instances.append((instance_name, location_data))

    return instances
