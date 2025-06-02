import glob
import os

def read_instances():
    instances = []
    
    for filepath in glob.glob("./instancias/*.txt"):
        with open(filepath, "r") as f:
            lines = [line.strip() for line in f if line.strip()]  # Ignora linhas vazias
            
            if not lines:
                print(f"Arquivo vazio: {filepath}")
                continue
                
            try:
                num_points = int(lines[0])
            except ValueError:
                print(f"Formato inválido na primeira linha de {filepath}")
                continue
                
            if len(lines) < num_points + 1:
                print(f"Arquivo incompleto: {filepath} (esperava {num_points+1} linhas, encontrou {len(lines)})")
                continue
                
            # Processa origem
            try:
                origem = list(map(int, lines[1].split()))
                origem = (origem[0], origem[1], 0, 0)  # Garante (x,y,0,0)
            except (IndexError, ValueError):
                print(f"Coordenadas de origem inválidas em {filepath}")
                continue
                
            locations_data = [origem]
            
            # Processa pontos de entrega
            for line in lines[2:2+num_points]:
                try:
                    dados = list(map(int, line.split()))
                    # Preenche com 0 se faltarem valores
                    dados.extend([0]*(4-len(dados)))
                    locations_data.append(tuple(dados[:4]))  # Pega só os 4 primeiros
                except ValueError:
                    print(f"Linha com formato inválido: {line} em {filepath}")
                    locations_data.append((0, 0, 0, 0))  # Ponto inválido preenchido com 0s
            
            instance_name = os.path.splitext(os.path.basename(filepath))[0]
            instances.append((instance_name, locations_data))
    
    return instances