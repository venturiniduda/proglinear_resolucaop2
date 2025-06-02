import os
import datetime
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.patches import Patch as patches

# Adicionar plot de tabelas, comparando resultados do modelo A e B

## FORMATAÇÃO DOS RESULTADOS EM TABELAS ##
def log_solution(instance_name, solution_a, solution_b):
    if solution_a is None or solution_b is None:
        if not os.path.exists("./resultados"):
            os.makedirs("./resultados")
        with open(f"./resultados/solucao_{instance_name}.txt", "w") as file:
            file.write("Problema sem solução!")
        return

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
            *rest  # para capturar o 8º valor se existir
        ) = solution

        max_delay_str = f"\nMaior Tempo de Atraso (max delay): {rest[0]:.2f}" if show_max_delay and rest else ""

        result = f"""
Limite superior da funcao objetivo (Atraso Total): {objective_upper_bound:.2f}
Limite inferior da funcao objetivo: {objective_lower_bound:.2f}
Tempo total de processamento: {runtime}
Gap Relativo: {relative_gap:.2f}
Contagem de Nos: {node_count}
Rotas: {' '.join(map(str, routes))}
Horarios de Chegada: {' '.join(map(lambda x: f"{x:.2f}", arrival_times))}
Tempos de Atraso (compacto): {' '.join(map(lambda x: f"{x:.2f}", delay_times))}{max_delay_str}

+---------------------+----------------+------------------+
|   RESULTADO REFERENTE AO EXERCICIO 1 - {label:^12}   |
+----------------+--------------------+-------------------+
| PONTO DA ROTA  | HORA DE CHEGADA    | TEMPO DE ATRASO   |
+----------------+--------------------+-------------------+
"""
        for point, arrival, delay in zip(routes, arrival_times, delay_times):
            result += f"| {str(point):^14} | {arrival:^18.2f} | {delay:^17.2f} |\n"
        result += "+----------------+--------------------+-------------------+\n"

        return result

    log_file_content = f"""
Dia e Hora do Processamento: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Instancia: {instance_name}
"""

    log_file_content += "\nRESULTADO A:\n"
    log_file_content += format_solution("ALTERNATIVA A", solution_a)

    log_file_content += "\nRESULTADO B:\n"
    log_file_content += format_solution("ALTERNATIVA B", solution_b, show_max_delay=True)

    if not os.path.exists("./resultados"):
        os.makedirs("./resultados")

    with open(f"./resultados/solucao_{instance_name}.txt", "w") as file:
        file.write(log_file_content)

## FORMATAÇÃO DOS RESULTADOS EM GRÁFICO ##
def plot_resolucao(title, nodes, route):
    G = nx.DiGraph()
    G.add_nodes_from(range(len(nodes)))
    G.add_edges_from(route)

    # Usar layout automático para evitar sobreposição
    pos = nx.spring_layout(G, seed=42)  # semente fixa para reprodutibilidade

    # Definir a cor dos nós: vermelho para o nó inicial (0), azul claro para os demais
    node_colors = ['yellow' if i == 0 else 'lightblue' for i in G.nodes]

    plt.figure(figsize=(8, 6))
    nx.draw(
        G, pos,
        with_labels=True,
        node_size=600,
        node_color=node_colors,
        font_size=10,
        font_weight='bold',
        arrows=True,
        arrowstyle='->',
        connectionstyle='arc3,rad=0.1'
    )

     # Adiciona legenda
    legend_elements = [
        patches(facecolor='yellow', edgecolor='black', label='Ponto de Início'),
        patches(facecolor='lightblue', edgecolor='black', label='Demais Pontos')
    ]
    plt.legend(handles=legend_elements, loc='lower left')

    plt.title(title)
    plt.grid(True)

     # Salvar a figura
    filename = title.replace(" ", "_") + '.png'
    filepath = os.path.join('./resultados/imagens', filename)
    plt.savefig(filepath, bbox_inches='tight')
    plt.close()  # fecha a figura para liberar memória

    # plt.show()
        
    
    