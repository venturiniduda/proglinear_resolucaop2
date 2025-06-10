## Para o modelo:
import math
import gurobipy as gp  # Importa a API do solver Gurobi para modelagem de problemas de otimização

## Funções auxiliares:
# Função para encontrar subtours (subciclos) em uma solução parcial
def get_subtours(edges, n_count):
    visited, tours = [False] * n_count, []  # Lista de visitados e lista de ciclos encontrados
    for i in range(n_count):
        if visited[i]: continue
        component, q = [], [i]  # Inicializa componente conectado e fila
        while q:
            node = q.pop(0)
            if not visited[node]:
                visited[node] = True
                component.append(node)
                for j, k in edges:
                    if j == node: q.append(k); break  # Adiciona vizinhos
        tours.append(component)
    return tours  # Retorna os ciclos encontrados

# Callback usado para eliminar subtours durante a otimização
def subtour_elim_callback(model, where):
    if where == gp.GRB.Callback.MIPSOL:
        vals = model.cbGetSolution(model._vars)  # Recupera a solução atual das variáveis
        edges = [(i, j) for i, j in model._vars.keys() if vals[i, j] > 0.5]  # Arcos usados na solução atual
        tours = get_subtours(edges, model._count)  # Encontra subtours
        if len(tours) > 1:  # Se houver mais de um ciclo, adiciona restrições para quebrar os menores
            for tour in tours:
                if len(tour) < model._count:
                    model.cbLazy(gp.quicksum(model._vars[i, j] for i in tour for j in tour if i != j) <= len(tour) - 1)

# Função para calcular a distância euclidiana entre dois pontos
def get_distance(p1, p2):
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

## O modelo:
def solve(location_data):
    # Número de locais (inclusive o ponto inicial)
    location_count = len(location_data) 
    
    # Dicionário de distâncias entre todos os pares de locais
    dist = {(i, j): get_distance(location_data[i][:2], location_data[j][:2]) 
            for i in range(location_count) for j in range(location_count)}
    
    # Criação do modelo Gurobi
    model = gp.Model()
    model.setParam('OutputFlag', 1)  # Exibe saída no terminal
    model.setParam('TimeLimit', 900)  # Tempo limite de execução (em segundos)
    model.setParam('LazyConstraints', 1)  # Habilita restrições lazy (para subtours)
    model.setParam('LogFile', './resultados/gurobi.log')  # Salva o log em um arquivo

    # Variáveis de decisão:
    
    # x[i,j] = 1 se o caminho de i para j é usado na rota
    rotas_escolhidas = model.addVars(location_count, location_count, vtype=gp.GRB.BINARY, name='x')

    # y[i] representa o tempo de chegada ao local i
    tempo_chegada = model.addVars(location_count, vtype=gp.GRB.CONTINUOUS, name='y', lb=0)

    # w[i] representa o tempo de atraso no atendimento do local i
    tempo_atraso = model.addVars(location_count, vtype=gp.GRB.CONTINUOUS, name='w', lb=0)

    # Função Objetivo:
    # Minimizar a soma total dos atrasos (exceto no depósito, i = 0)
    model.setObjective(
        gp.quicksum(tempo_atraso[i] for i in range(1, location_count)),
        sense = gp.GRB.MINIMIZE
    )

    # Restrições:

    # Cada local deve ter exatamente uma saída
    model.addConstrs((rotas_escolhidas.sum(i, '*') == 1 for i in range(location_count)))

    # Cada local deve ter exatamente uma entrada
    model.addConstrs((rotas_escolhidas.sum('*', j) == 1 for j in range(location_count)))

    # Proíbe laços (não pode ir do local i para o próprio i)
    model.addConstrs((rotas_escolhidas[i, i] == 0 for i in range(location_count)), name="no_self_loops")
    
    # Constante grande usada nas restrições de sequência temporal (Big-M)
    M = sum(dist.get((i, j), 0) + location_data[i][2] 
            for i in range(location_count) for j in range(location_count) if i != j) \
        + sum(d[3] for d in location_data)  # Inclui todos os deadlines
    
    # Restrições de sequenciamento temporal (tempo de chegada consistente com a rota e duração do serviço)
    for i in range(location_count):
        for j in range(1, location_count):
            if i != j:
                model.addConstr(
                    tempo_chegada[j] >= tempo_chegada[i] + location_data[i][2] + dist[i, j] 
                    - M * (1 - rotas_escolhidas[i, j])
                )

    # O atraso só acontece se o tempo de chegada for superior ao deadline
    for i in range(1, location_count):
        model.addConstr(tempo_atraso[i] >= tempo_chegada[i] - location_data[i][3])

    # Guarda variáveis para uso no callback de subtour
    model._vars = rotas_escolhidas
    model._count = location_count

    # Executa a otimização com o callback de subtours
    model.optimize(subtour_elim_callback)

    # Se não encontrou uma solução viável
    if model.status != gp.GRB.OPTIMAL:
        return None

    # Retorna os principais resultados
    return (
        model.ObjVal,  # Valor da função objetivo (soma dos atrasos)
        model.ObjBound,  # Limite inferior da função objetivo
        model.Runtime,  # Tempo de execução
        model.MIPGap,  # Gap relativo da solução
        model.NodeCount,  # Número de nós explorados
        [(i, j) for i, j in rotas_escolhidas.keys() if rotas_escolhidas[i, j].X > 0.5],  # Arcos escolhidos
        [tempo_chegada[i].X for i in range(location_count)],  # Tempos de chegada
        [tempo_atraso[i].X for i in range(location_count)]  # Tempos de atraso
    )
