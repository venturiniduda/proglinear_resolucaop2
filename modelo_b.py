## Para o modelo:
import math
import gurobipy as gp

## Funções auxiliares:
def get_subtours(edges, n_count):
    visited, tours = [False] * n_count, []
    for i in range(n_count):
        if visited[i]: continue
        component, q = [], [i]
        while q:
            node = q.pop(0)
            if not visited[node]:
                visited[node] = True
                component.append(node)
                for j, k in edges:
                    if j == node: q.append(k); break
        tours.append(component)
    return tours

def subtour_elim_callback(model, where):
    if where == gp.GRB.Callback.MIPSOL:
        vals = model.cbGetSolution(model._vars)
        edges = [(i, j) for i, j in model._vars.keys() if vals[i, j] > 0.5]
        tours = get_subtours(edges, model._count)
        if len(tours) > 1:
            for tour in tours:
                if len(tour) < model._count:
                    model.cbLazy(gp.quicksum(model._vars[i, j] for i in tour for j in tour if i != j) <= len(tour) - 1)

def get_distance(p1, p2):
    # Função para calcular a distância euclidiana entre os dois pontos 
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

## O modelo:
def solve(location_data):
    # Contagem das rotas: 
    # (representa o nosso "n" do modelo algébrico)
    location_count = len(location_data) 

    # Armazenando as distâncias:
    dist = {(i, j): get_distance(location_data[i][:2], location_data[j][:2]) for i in range(location_count) for j in range(location_count)}
    
    model = gp.Model("Modelo_B")
    model.setParam('OutputFlag', 1)
    model.setParam('TimeLimit', 60)
    model.setParam('LazyConstraints', 1)
    model.setParam('LogFile', './resultados/gurobi.log')

    # Variáveis de Decisão:
    ## representação de rotas escolhidas (x)
    rotas_escolhidas = model.addVars(location_count, location_count, vtype=gp.GRB.BINARY, name='x')

    ## representação do tempo de chegada em cada local (y)
    tempo_chegada = model.addVars(location_count, vtype=gp.GRB.CONTINUOUS, name='y', lb=0)

    ## representação do tempo de atraso máximo
    max_atraso = model.addVar(vtype=gp.GRB.CONTINUOUS, name='max_atraso', lb=0)

    # Função Objetivo:
    # maximizar o tempo de atraso mínimo total
    model.setObjective(max_atraso, sense=gp.GRB.MINIMIZE)

    # Restrições:
    model.addConstrs((rotas_escolhidas.sum(i, '*') == 1 for i in range(location_count)))
    model.addConstrs((rotas_escolhidas.sum('*', j) == 1 for j in range(location_count)))
    model.addConstrs((rotas_escolhidas[i, i] == 0 for i in range(location_count)), name="no_self_loops")
    
    M = sum(dist.get((i, j), 0) + location_data[i][2] for i in range(location_count) for j in range(location_count) if i != j) + sum(d[3] for d in location_data)
    for i in range(location_count):
        for j in range(1, location_count):
            if i != j: 
                model.addConstr(tempo_chegada[j] >= tempo_chegada[i] + location_data[i][2] + dist[i, j] - M * (1 - rotas_escolhidas[i, j]))
    
    for i in range(1, location_count): 
        model.addConstr(max_atraso >= tempo_chegada[i] - location_data[i][3])

    model._vars, model._count = rotas_escolhidas, location_count
    model.optimize(subtour_elim_callback)

    if model.status != gp.GRB.OPTIMAL:
        return None
    
    delay_times = [max(0, tempo_chegada[i].X - location_data[i][3]) if i > 0 else 0 for i in range(location_count)]

    return (
        # Limite superior da função objetivo
        model.ObjVal,
        
        # Limite inferior da função objetivo
        model.ObjBound,

        # Tempo de execução
        model.Runtime,

        # Gap Relativo
        model.MIPGap,

        # Número de nós
        model.NodeCount,

        # Rotas escolhidas
         [(i, j) for i, j in rotas_escolhidas.keys() if rotas_escolhidas[i, j].X > 0.5],

        # Tempos de chegada em cada local
        [tempo_chegada[i].X for i in range(location_count)],

        # Tempo de atraso em cada local
        delay_times,

        # Tempo de atraso máximo
        max_atraso.X
    )