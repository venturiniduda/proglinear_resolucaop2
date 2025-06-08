import os
import datetime
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.patches import Patch as patches

def format_solution_table(label, solution, is_model_b=False):
    """Formata a tabela de resultados para um único modelo."""
    if solution is None:
        return f"RESULTADO {label}: NENHUMA SOLUÇÃO ENCONTRADA A TEMPO"

    (objective_upper_bound, _, runtime, _, _, routes_raw, arrival_times, delay_times, *rest) = solution
    
    # --- LÓGICA CORRIGIDA PARA MONTAR A ROTA ---
    points_in_order = []
    if routes_raw:
        try:
            route_dict = dict(routes_raw)
            curr = 0
            # O loop deve rodar exatamente o número de vezes do total de locais
            # para garantir que todos os pontos sejam adicionados à lista.
            for _ in range(len(route_dict)):
                points_in_order.append(curr)
                curr = route_dict.get(curr)
                # Se a rota for inválida (o que não deve acontecer), para.
                if curr is None:
                    break
        except Exception as e:
            print(f"Erro ao montar a rota para a tabela: {e}")
            points_in_order = [] # Reseta em caso de erro

    def fmt(value): return "0.00" if abs(value) < 1e-6 else f"{value:.2f}"
    max_delay_str = f"\nMaior Atraso: {fmt(rest[0])}" if is_model_b and rest else ""
    
    result = f"Resultado {label} (Atraso {'Maior' if is_model_b else 'Total'}): {fmt(objective_upper_bound)}{max_delay_str} (Tempo: {runtime:.2f}s)\n"
    result += "+---------------+-----------------+---------------+\n"
    result += "| Ponto da Rota | Hora de Chegada | Tempo de Atraso |\n"
    result += "+---------------+-----------------+---------------+\n"
    for point_idx in points_in_order:
        if point_idx < len(arrival_times):
            arrival, delay = arrival_times[point_idx], delay_times[point_idx]
            result += f"| {str(point_idx):^13} | {fmt(arrival):^15} | {fmt(delay):^15} |\n"
    result += "+---------------+-----------------+---------------+\n"
    # Adiciona uma nota sobre o retorno ao CD, que está no gráfico.
    result += "Nota: A rota completa, incluindo o arco de retorno ao Centro de Distribuição (Ponto 0), está representada no gráfico."
    return result

def log_solution(instance_name, solution_a, solution_b):
    """Gera o arquivo de log com os resultados dos dois modelos."""
    if not os.path.exists("./resultados"):
        os.makedirs("./resultados")

    log_file_content = f"Dia e Hora do Processamento: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    log_file_content += f"Instancia: {instance_name}\n\n"
    log_file_content += format_solution_table("A", solution_a) + "\n\n"
    log_file_content += format_solution_table("B", solution_b, is_model_b=True)
    
    with open(os.path.join("resultados", f"solucao_{instance_name}.txt"), "w", encoding='utf-8') as file:
        file.write(log_file_content)

def plot_resolucao(instance_name, nodes, route):
    """Gera e salva o gráfico da rota encontrada."""
    if not route: return
    image_dir = os.path.join('resultados', 'imagens')
    if not os.path.exists(image_dir): os.makedirs(image_dir)
    
    G = nx.DiGraph(route)
    pos = {i: (nodes[i][0], nodes[i][1]) for i in range(len(nodes))}
    
    plt.figure(figsize=(10, 8))
    plt.title(f"Rota Otimizada - {instance_name}", fontsize=16)
    
    # Garante que as cores dos nós correspondam aos nós presentes no gráfico
    node_colors = ['gold' if node == 0 else 'skyblue' for node in G.nodes()]
    nx.draw(G, pos, labels={n: f"{n}" for n in G.nodes()}, with_labels=True, node_size=500,
            node_color=node_colors, font_size=10, font_weight='bold',
            edge_color='gray', width=1.5, arrows=True, arrowstyle='->', arrowsize=20,
            connectionstyle='arc3,rad=0.1')
            
    legend_elements = [patches(facecolor='gold', label='Depósito'), patches(facecolor='skyblue', label='Clientes')]
    plt.legend(handles=legend_elements, loc='best')
    
    filepath = os.path.join(image_dir, f"solucao_{instance_name}.png")
    plt.savefig(filepath, bbox_inches='tight')
    plt.close()