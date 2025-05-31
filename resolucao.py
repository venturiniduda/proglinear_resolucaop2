import os
import datetime
import networkx as nx
import matplotlib.pyplot as plt

# Adicionar plot de tabelas, comparando resultados do modelo A e B

## FORMATAÇÃO DOS RESULTADOS EM TABELAS ##
def log_solution(instance_name, solution):
    if solution is None:
        if not os.path.exists("./resultados"):
            os.makedirs("./resultados")
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

    # Cabeçalho geral
    log_file_content = f"""
Dia e Hora do Processamento: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Instancia: {instance_name}
Limite superior da funcao objetivo: {objective_upper_bound:.2f}
Limite inferior da funcao objetivo: {objective_lower_bound:.2f}
Tempo total de processamento: {runtime}
Gap Relativo: {relative_gap:.2f}
Contagem de Nos: {node_count}
Rotas: {' '.join(map(str, routes))}
Horarios de Chegada: {' '.join(map(lambda x: f"{x:.2f}", arrival_times))}
Tempos de Atraso (compacto): {' '.join(map(lambda x: f"{x:.2f}", delay_times))}

Tabela Detalhada:

+---------------------+----------------+------------------+
|   RESULTADO REFERENTE AO EXERCICIO 1 - ALTERNATIVA A    |
+----------------+--------------------+-------------------+
| PONTO DA ROTA  | HORA DE CHEGADA    | TEMPO DE ATRASO   |
+----------------+--------------------+-------------------+
"""
    
    # Adiciona cada linha com os dados formatados
    for point, arrival, delay in zip(routes, arrival_times, delay_times):
        log_file_content += f"| {str(point):^14} | {arrival:^18.2f} | {delay:^17.2f} |\n"

    log_file_content += "+----------------+--------------------+-------------------+\n"

    # Garante que o diretório existe
    if not os.path.exists("./resultados"):
        os.makedirs("./resultados")

    # Salva o log no arquivo
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
    
        
    
    