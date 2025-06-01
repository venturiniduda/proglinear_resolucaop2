import math
import gurobipy as gp
import matplotlib.pyplot as plt
import networkx as nx

M = 10 ** 7

def get_distance(p1, p2):
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

def load_instance(file_path):
    with open(file_path, "r") as f:
        lines = [line.strip() for line in f if line.strip()]
    
    n = int(lines[0])
    location_data = []

    # Primeiro ponto: depósito
    x0, y0 = map(int, lines[1].split())
    location_data.append([x0, y0, 0, 0])  # depósito

    for line in lines[2:]:
        parts = list(map(int, line.split()))
        location_data.append(parts)

    return location_data

def solve(location_data):
    location_count = len(location_data)
    
    model = gp.Model()
    model.setParam('TimeLimit', 3600)
    model.setParam('OutputFlag', 0)
    model.setParam('LogFile', './resultados/gurobi.log')

    chosen_route = model.addVars(location_count, location_count, vtype=gp.GRB.BINARY, name='chosen_route')
    arrival_time = model.addVars(location_count, vtype=gp.GRB.CONTINUOUS, lb=0, name='arrival_time')
    delay_time = model.addVars(location_count, vtype=gp.GRB.CONTINUOUS, lb=0, name='delay_time')

    # Objetivo: minimizar atraso total (exceto depósito)
    model.setObjective(
        gp.quicksum(delay_time[i] for i in range(1, location_count)),
        sense=gp.GRB.MINIMIZE
    )

    # Cada local com 1 entrada e 1 saída
    model.addConstrs(
        gp.quicksum(chosen_route[i, j] for j in range(location_count) if i != j) == 1
        for i in range(location_count)
    )
    model.addConstrs(
        gp.quicksum(chosen_route[i, j] for i in range(location_count) if i != j) == 1
        for j in range(location_count)
    )

    # Forçar retorno ao depósito
    model.addConstr(
        gp.quicksum(chosen_route[i, 0] for i in range(1, location_count)) == 1
    )

    # Restrições de tempo
    for i in range(location_count):
        for j in range(location_count):
            if i != j:
                travel_time = get_distance(location_data[i][:2], location_data[j][:2])
                service_time = location_data[i][2]
                model.addConstr(
                    arrival_time[j] >= arrival_time[i] + service_time + travel_time - M * (1 - chosen_route[i, j])
                )

    # Atraso em relação ao deadline
    for i in range(1, location_count):
        deadline = location_data[i][3]
        delay_aux = model.addVar(vtype=gp.GRB.CONTINUOUS, lb=0, name=f'delay_aux_{i}')
        model.addConstr(delay_aux == arrival_time[i] - deadline)
        model.addConstr(delay_time[i] >= delay_aux)

    # Eliminação de sub-rotas (MTZ)
    u = model.addVars(location_count, vtype=gp.GRB.CONTINUOUS, lb=0, ub=location_count - 1, name="u")
    for i in range(1, location_count):
        for j in range(1, location_count):
            if i != j:
                model.addConstr(u[i] - u[j] + (location_count - 1) * chosen_route[i, j] <= location_count - 2)

    model.optimize()

    if model.status != gp.GRB.OPTIMAL:
        return None

    return (
        model.ObjVal,
        model.ObjBound,
        model.Runtime,
        model.MIPGap,
        model.NodeCount,
        [(i, j) for i in range(location_count) for j in range(location_count) if chosen_route[i, j].X > 0.5],
        [arrival_time[i].X for i in range(location_count)],
        [delay_time[i].X for i in range(location_count)]
    )

def print_result(result):
    obj, bound, time, gap, nodes, route, arrival, delay = result
    print(f"\n📌 Resultado do modelo:")
    print(f" - Valor da função objetivo (atraso total): {obj:.2f}")
    print(f" - Limite inferior: {bound:.2f}")
    print(f" - Tempo de execução: {time:.2f} segundos")
    print(f" - GAP: {gap:.4f}")
    print(f" - Nós processados: {nodes}")
    print(" - Rota encontrada:")
    for arc in route:
        print(f"   {arc[0]} → {arc[1]}")
    print(" - Tempos de chegada:")
    for i, t in enumerate(arrival):
        print(f"   Local {i}: {t:.2f}")
    print(" - Atrasos:")
    for i, d in enumerate(delay):
        print(f"   Local {i}: {d:.2f}")

def plot_route(title, nodes, route):
    G = nx.DiGraph()
    pos = {i: (nodes[i][0], nodes[i][1]) for i in range(len(nodes))}
    G.add_nodes_from(pos)
    G.add_edges_from(route)
    plt.figure(figsize=(8, 6))
    nx.draw(G, pos, with_labels=True, node_size=600, node_color='lightblue',
            font_size=10, font_weight='bold', arrows=True, arrowstyle='->', connectionstyle='arc3,rad=0.1')
    plt.title(title)
    plt.grid(True)
    plt.show()

# ===== EXECUÇÃO FINAL =====
if __name__ == "__main__":
    path = "./instancias/inst_10.txt"  # certifique-se que esse caminho está correto
    location_data = load_instance(path)
    result = solve(location_data)
    
    if result:
        print_result(result)
        plot_route("Rota Ótima - Atraso Total Mínimo", location_data, result[5])
    else:
        print("⚠️ Nenhuma solução ótima foi encontrada.")
