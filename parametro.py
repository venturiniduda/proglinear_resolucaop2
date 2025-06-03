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
                locations_data = []
            except ValueError:
                print(f"Formato inválido na primeira linha de {filepath}")
                continue
                
            # Processa origem
            try:
                origem = list(map(int, lines[1].split()))
                origem = (origem[0], origem[1], 0, 0)  # Depósito
            except (IndexError, ValueError):
                print(f"Coordenadas de origem inválidas em {filepath}")
                continue
                
            locations_data.append([origem])
            
            # Processa pontos de entrega
            for line in lines[2:]:
                try:
                    dados = list(map(int, line.split()))
                    # Preenche com 0 se faltarem valores
                    dados.extend([0]*(4-len(dados)))
                    locations_data.append(tuple(dados[:4]))  # Pega só os 4 primeiros
                except ValueError:
                    print(f"Linha com formato inválido: {line} em {filepath}")
                    locations_data.append((0, 0, 0, 0))  # Ponto inválido preenchido com 0s
    
    return instances