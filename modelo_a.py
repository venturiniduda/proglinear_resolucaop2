## Para o modelo:
import math
import gurobipy as gp

# Constante suficientemente grande para desativar as subrotas
M = 10 ** 7

## O modelo:
def get_distance(p1, p2):
    # Função para calcular a distância euclidiana entre os dois pontos 
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

def solve(location_data):
    # Contagem das rotas: 
    # (representa o nosso "n" do modelo algébrico)
    location_count = len(location_data) 
    
    model = gp.Model()
    model.setParam('OutputFlag', 1)

    # Define 1 hora de timeout (tempo limite de processamento):
    model.setParam('TimeLimit', 3600)
    # Para salvar os retornos do Gurobi:
    model.setParam('LogFile', './resultados/gurobi.log')

    # Variáveis de Decisão:
    ## representação de rotas escolhidas (x)
    rotas_escolhidas = model.addVars(location_count, location_count, vtype=gp.GRB.BINARY, name='rotas_escolhidas')

    ## representação do tempo de chegada em cada local (y)
    tempo_chegada = model.addVars(location_count, vtype=gp.GRB.CONTINUOUS, name='tempo_chegada', lb=0)

    ## representação do tempo de atraso em cada local (w)
    tempo_atraso = model.addVars(location_count, vtype=gp.GRB.CONTINUOUS, name='tempo_atraso', lb=0)

    # Função Objetivo:
    # minimizar o tempo de atraso total, consequentemente minimizar a multa total
    # model.setObjective(
    #     gp.quicksum(delay_time[i] for i in range(1, location_count - 1)),
    #     sense = gp.GRB.MINIMIZE
    # )

    model.setObjective(
        gp.quicksum(tempo_atraso[i] for i in range(1, location_count)),
        sense = gp.GRB.MINIMIZE
    )

    # Restrições:
    ## Garantir que cada local (exceto depósito) deve ter uma entrada
    model.addConstrs(
        gp.quicksum(rotas_escolhidas[i, j] for i in range(location_count) if i != j) == 1
        for j in range(1, location_count)
    )

    ## Garantir que cada local (incluindo depósito) deve ter uma saída
    model.addConstrs(
        gp.quicksum(rotas_escolhidas[i, j] for j in range(location_count) if i != j) == 1
        for i in range(location_count)
    )

    # Eliminação de sub-rotas com MTZ:
    ## Variável auxiliar para eliminação de sub-rotas:
    u = model.addVars(location_count, vtype=gp.GRB.CONTINUOUS, lb=1, ub=location_count - 1, name="u")

    ## Adiciona a restrição:
    for i in range(1, location_count):
        for j in range(1, location_count):
            if i != j:
                model.addConstr(u[i] - u[j] + (location_count - 1) * rotas_escolhidas[i, j] <= location_count - 2)

    ## Garantir que retornará para o depósito
    model.addConstr(
        gp.quicksum(rotas_escolhidas[i, 0] for i in range(1, location_count)) == 1
    )

    ## Garantir que, se a rota for utilizada, o tempo de chegada
    ## respeita o tempo de chegada da rota anterior + deslocamento + serviço:
    for i in range(location_count):
        for j in range(location_count):
            if i == j:
                continue
            distancia = get_distance(location_data[i][:2], location_data[j][:2])
            tempo_servico = location_data[i][2]

            # Lembrete: a constante M é utilizada para garantir que, se a rota NÃO for escolhida, será ignorada
            model.addConstr(
                tempo_chegada[j] >= tempo_chegada[i] + tempo_servico + distancia - M * (1 - rotas_escolhidas[i, j])
            )
        
    ## Garantir que o tempo de atraso em cada local seja maior ou igual ao tempo de chegada menos o tempo máximo permitido:
    # Atraso em relação ao deadline
    for i in range(1, location_count):
        deadline = location_data[i][3]
        delay_aux = model.addVar(vtype=gp.GRB.CONTINUOUS, lb=0, name=f'delay_aux_{i}')
        model.addConstr(delay_aux == tempo_chegada[i] - deadline)
        model.addConstr(tempo_atraso[i] >= delay_aux)
             
    model.optimize()

    if model.status != gp.GRB.OPTIMAL:
        return None

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
        [(i, j) for i in range(location_count) for j in range(location_count) if rotas_escolhidas[i, j].X > 0.5],

        # Tempos de chegada em cada local
        [tempo_chegada[i].X for i in range(location_count)],

        # Tempo de atraso em cada local
        [tempo_atraso[i].X for i in range(location_count)]
    )