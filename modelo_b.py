## Para o modelo:
import math
import gurobipy as gp  # Biblioteca de modelagem matemática para problemas de otimização

## Funções auxiliares:
# Função que detecta subtours (subciclos) em uma solução parcial do modelo
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
                    if j == node: q.append(k); break  # Adiciona o vizinho k se j == node
        tours.append(component)
    return tours  # Retorna todos os componentes conectados (subtours)

# Callback para eliminação de subtours durante a busca de soluções
def subtour_elim_callback(model, where):
    if where == gp.GRB.Callback.MIPSOL:
        vals = model.cbGetSolution(model._vars)  # Obtém valores da solução atual
        edges = [(i, j) for i, j in model._vars.keys() if vals[i, j] > 0.5]  # Arcos incluídos
        tours = get_subtours(edges, model._count)  # Verifica presença de subtours
        if len(tours) > 1:
            for tour in tours:
                if len(tour) < model._count:  # Subtour inválido
                    model.cbLazy(
                        gp.quicksum(model._vars[i, j] for i in tour for j in tour if i != j) <= len(tour) - 1
                    )

# Função para calcular a distância euclidiana entre dois pontos
def get_distance(p1, p2):
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

## O modelo principal:
def solve(location_data):
    # Número total de locais (incluindo o depósito)
    location_count = len(location_data) 

    # Cria um dicionário com todas as distâncias entre pares de pontos
    dist = {
        (i, j): get_distance(location_data[i][:2], location_data[j][:2])
        for i in range(location_count)
        for j in range(location_count)
    }
    
    # Criação do modelo Gurobi
    model = gp.Model("Modelo_B")
    model.setParam('OutputFlag', 1)       # Exibe log no terminal
    model.setParam('TimeLimit', 600)      # Limite de tempo de 10 minutos
    model.setParam('LazyConstraints', 1)  # Permite o uso de lazy constraints (para subtours)
    model.setParam('LogFile', './resultados/gurobi.log')  # Arquivo de log

    # Variáveis de Decisão:

    # x[i,j] = 1 se o caminho de i para j é usado na solução
    rotas_escolhidas = model.addVars(location_count, location_count, vtype=gp.GRB.BINARY, name='x')

    # y[i] = tempo de chegada no local i
    tempo_chegada = model.addVars(location_count, vtype=gp.GRB.CONTINUOUS, name='y', lb=0)

    # Variável que representa o atraso máximo entre todos os locais
    max_atraso = model.addVar(vtype=gp.GRB.CONTINUOUS, name='max_atraso', lb=0)

    # Função Objetivo: Minimizar o atraso máximo
    model.setObjective(max_atraso, sense=gp.GRB.MINIMIZE)

    # Restrições:
    # Cada local deve ter exatamente uma saída (exceto ele mesmo)
    model.addConstrs((rotas_escolhidas.sum(i, '*') == 1 for i in range(location_count)))

    # Cada local deve ter exatamente uma entrada
    model.addConstrs((rotas_escolhidas.sum('*', j) == 1 for j in range(location_count)))

    # Proibir laços (não pode ir de um local para ele mesmo)
    model.addConstrs((rotas_escolhidas[i, i] == 0 for i in range(location_count)), name="no_self_loops")
    
    # Constante M grande para restrições de sequenciamento temporal (Big-M)
    M = sum(
        dist.get((i, j), 0) + location_data[i][2]
        for i in range(location_count)
        for j in range(location_count)
        if i != j
    ) + sum(d[3] for d in location_data)  # Inclui os deadlines também

    # Restrições de sequência: se x[i,j] = 1, y[j] >= y[i] + tempo de serviço + distância
    for i in range(location_count):
        for j in range(1, location_count):  # Começa em 1 para ignorar o depósito como destino
            if i != j:
                model.addConstr(
                    tempo_chegada[j] >= tempo_chegada[i] + location_data[i][2] + dist[i, j]
                    - M * (1 - rotas_escolhidas[i, j])
                )

    # Restrição que define o atraso máximo: max_atraso >= atraso individual
    for i in range(1, location_count):  # Ignora o depósito
        model.addConstr(max_atraso >= tempo_chegada[i] - location_data[i][3])

    # Atribui variáveis ao modelo para uso interno no callback
    model._vars = rotas_escolhidas
    model._count = location_count

    # Executa o solver com callback para eliminação de subtours
    model.optimize(subtour_elim_callback)

    # Se o modelo não encontrou solução viável
    if model.status != gp.GRB.OPTIMAL:
        return None
    
    # Calcula atrasos por local com base no tempo de chegada
    delay_times = [
        max(0, tempo_chegada[i].X - location_data[i][3]) if i > 0 else 0
        for i in range(location_count)
    ]

    # Retorna métricas e solução ótima
    return (
        model.ObjVal,  # Valor da função objetivo (atraso máximo)
        model.ObjBound,  # Limite inferior da função objetivo
        model.Runtime,  # Tempo de execução do solver
        model.MIPGap,  # Gap relativo da solução
        model.NodeCount,  # Número de nós explorados na árvore de busca
        [(i, j) for i, j in rotas_escolhidas.keys() if rotas_escolhidas[i, j].X > 0.5],  # Arcos utilizados
        [tempo_chegada[i].X for i in range(location_count)],  # Tempo de chegada em cada local
        delay_times,  # Lista com atrasos por local
        max_atraso.X  # Valor do atraso máximo
    )