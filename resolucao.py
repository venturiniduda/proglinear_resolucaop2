import os
import datetime
import networkx as nx
import matplotlib.pyplot as plt

# Adicionar plot de tabelas, comparando resultados do modelo A e B

## FORMATAÇÃO DOS RESULTADOS EM TABELAS ##
def log_solution(instance_name, solution):
    if solution is None:
        with open(f"./resultados/solucao_{instance_name}.txt", "w") as file:
            file.write("Problema sem solução!")
        return
    
    (
        objective_upper_bound,
        objective_lower_bound,
        runtime,
        relative_gap,
        node_count,
        routes,
        arrival_times,
        delay_times
    ) = solution
        
    log_file_content = f"""
Dia e Hora do Processamento: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Instância: {instance_name}
Limite superior da funcao objetivo: {f"{objective_upper_bound:.2f}"}
Limite inferior da funcao objetivo: {f"{objective_lower_bound:.2f}"}
Tempo total de processamento: {runtime}
Gap Relativo: {f"{relative_gap:.2f}"}
Contagem de Nos: {node_count}
Rotas: {' '.join(map(str, routes))}
Horarios de Chegada: {' '.join(map(lambda x: f"{x:.2f}", arrival_times))}
Tempos de Atraso: {' '.join(map(lambda x: f"{x:.2f}", delay_times))}
"""
    
    if not os.path.exists("./resultados"):
      os.makedirs("./resultados")
    
    with open(f"./resultados/solucao_{instance_name}.txt", "w") as file:
        file.write(log_file_content)


## FORMATAÇÃO DOS RESULTADOS EM GRÁFICO ##
def plot_solution(nodes, selected_route):
    G = nx.DiGraph()
    pos = {i: (nodes[i][0], nodes[i][1]) for i in range(len(nodes))}
    
    G.add_nodes_from(pos.keys())
    G.add_edges_from(selected_route)
    
    nx.draw(G, pos, with_labels=True, node_size=500, node_color='lightblue', font_size=10, font_weight='bold', arrows=True)
    
    plt.axhline(0, color='black', lw=1)

    plt.show()
    
        
    
    