import os
import datetime
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.patches import Patch as patches

## FORMATAÇÃO DOS RESULTADOS EM TABELAS ##
def log_solution(instance_name, solution_a, solution_b, selected_model):
    if not os.path.exists("./resultados"):
        os.makedirs("./resultados")

    file_path = f"./resultados/solucao_{instance_name}.txt"

    def format_solution(label, solution, show_max_delay=False):
        (
            objective_upper_bound,
            objective_lower_bound,
            runtime,
            relative_gap,
            node_count,
            routes,
            arrival_times,
            delay_times,
            *rest
        ) = solution

        max_delay_str = f"\nMaior Tempo de Atraso (max delay): {rest[0]:.2f}" if show_max_delay and rest else ""

        data_sorted = list(zip(routes, arrival_times, delay_times))

        result = f"""
Limite superior da funcao objetivo (Atraso Total): {objective_upper_bound:.2f}
Limite inferior da funcao objetivo: {objective_lower_bound:.2f}
Tempo total de processamento: {runtime}
Gap Relativo: {relative_gap:.2f}
Contagem de Nos: {node_count}
Rotas: {' '.join(map(str, routes))}
Horarios de Chegada: {' '.join(map(lambda x: f"{x:.2f}", arrival_times))}
Tempos de Atraso (compacto): {' '.join(map(lambda x: f"{x:.2f}", delay_times))}{max_delay_str}

+---------------------+----------------+------------------+-------------------+
|   RESULTADO REFERENTE AO EXERCICIO 1 - {label:^14}   |
+----------------+--------------------+-------------------+
| PONTO DA ROTA  | HORA DE CHEGADA    | TEMPO DE ATRASO   |
+----------------+--------------------+-------------------+
"""
        for point, arrival, delay in data_sorted:
            result += f"| {str(point):^14} | {arrival:^18.2f} | {delay:^17.2f} |\n"
        result += "+----------------+--------------------+-------------------+\n"
        return result

    # Início do conteúdo
    log_file_content = f"""
\n{'='*80}
Dia e Hora do Processamento: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Instancia: {instance_name}
"""

    # Modelo A
    if selected_model in ('1', '3'):
        log_file_content += "\nRESULTADO A:\n"
        if solution_a is not None:
            log_file_content += format_solution("ALTERNATIVA A", solution_a)
        else:
            log_file_content += "Problema sem solução para o Modelo A.\n"

    # Modelo B
    if selected_model in ('2', '3'):
        log_file_content += "\nRESULTADO B:\n"
        if solution_b is not None:
            log_file_content += format_solution("ALTERNATIVA B", solution_b, show_max_delay=True)
        else:
            log_file_content += "Problema sem solução para o Modelo B.\n"

    # Grava no arquivo
    with open(file_path, "a") as file:
        file.write(log_file_content)

## FORMATAÇÃO DOS RESULTADOS EM GRÁFICO ##
def plot_resolucao(instance_name, nodes, route):
    if not os.path.exists('./resultados/imagens'):
        os.makedirs('./resultados/imagens')

    G = nx.DiGraph()
    pos = {i: (nodes[i][0], nodes[i][1]) for i in range(len(nodes))}
    G.add_edges_from(route)
    plt.figure(figsize=(8, 6))
    plt.axis('equal')
    plt.margins(0.3)

    node_colors = ['yellow' if i == 0 else 'lightblue' for i in G.nodes]

    nx.draw(
        G, pos,
        with_labels=True,
        node_size=300,
        node_color=node_colors,
        font_size=10,
        font_weight='bold',
        arrows=True,
        arrowstyle='->',
        connectionstyle='arc3,rad=0.1'
    )

    legend_elements = [
        patches(facecolor='yellow', edgecolor='black', label='Ponto de Início'),
        patches(facecolor='lightblue', edgecolor='black', label='Demais Pontos')
    ]
    plt.legend(handles=legend_elements, loc='lower left')

    plt.title(instance_name)
    plt.grid(True)

    filename = f"solucao_{instance_name}.png"
    filepath = os.path.join('./resultados/imagens', filename)
    plt.savefig(filepath, bbox_inches='tight')
    plt.close()
