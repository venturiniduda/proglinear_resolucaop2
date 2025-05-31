## Para o modelo:
import math
import gurobipy

M = 10 ** 7

## O modelo:
def get_distance(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def solve(location_data):
    location_data.append(location_data[0])
    location_count = len(location_data)
    
    model = gurobipy.Model()
    model.setParam('TimeLimit', 3600) # 1 hora de timeout 
    model.setParam('LogFile', './resultados/gurobi.log')

    # Variáveis de Decisão:
    ## representação de rotas escolhidas
    chosen_route = model.addVars(location_count, location_count, vtype=gurobipy.GRB.BINARY, name='chosen_route')

    ## representação do tempo de chegada em cada local
    arrival_time = model.addVars(location_count, vtype=gurobipy.GRB.CONTINUOUS, name='arrival_time', lb=0)

    ## representação do tempo de atraso em cada local
    delay_time = model.addVars(location_count, vtype=gurobipy.GRB.CONTINUOUS, name='delay_time', lb=0)

    # Função Objetivo:
    ## minimizar o tempo de atraso total, consequentemente minimizar a multa total
    model.setObjective(
        gurobipy.quicksum(delay_time[i] for i in range(1, location_count - 1)),
        sense = gurobipy.GRB.MINIMIZE
    )

    # Restrições:
    ## Garantir que se chegue em um local apenas 1 vez
    model.addConstrs(
        gurobipy.quicksum(chosen_route[i, j] for j in range(1, location_count) if i != j) == 1
        for i in range(0, location_count - 1)
    )
    ## Garantir que se saia de um local apenas 1 vez
    model.addConstrs(
        gurobipy.quicksum(chosen_route[i, j] for i in range(location_count - 1) if i != j) == 1
        for j in range(1, location_count)
    )

    ## Garantir que não haja sub-rotas
    for i in range(0, location_count - 1):
        for j in range(1, location_count): 
            if i == j: 
                continue

            location_i = location_data[i]
            location_i_coords = (location_i[0], location_i[1])
            location_i_service_time = location_i[2]

            location_j = location_data[j]
            location_j_coords = (location_j[0], location_j[1])
            
            ## Considerando como tempo entre locais a distância euclidiana entre eles
            time_between_locations = get_distance(location_i_coords, location_j_coords)

            model.addConstr(
                arrival_time[j] >= 
                    arrival_time[i] +
                    time_between_locations +
                    location_i_service_time 
                    ## Usamos uma constante grande para garantir que a restrição seja satisfeita
                    ##quando a rota não for escolhida, isto é, chosen_route[i, j] == 0
                    - M * (1 - chosen_route[i,j]) 
            )
        
    ## Garantir que o tempo de atraso em cada local seja maior ou igual ao tempo de chegada menos o tempo máximo permitido
    for i in range(1, location_count - 1):
        location_i = location_data[i]
        deadline = location_i[3]
        expected_delay_time = arrival_time[i] - deadline
        
        # Definindo a variável auxiliar para o tempo de atraso esperado
        delay_aux = model.addVar(vtype=gurobipy.GRB.CONTINUOUS, name=f'delay_aux_{i}', lb=0)
        model.addConstr(delay_aux == expected_delay_time)
        
        # Garantindo que o tempo de atraso seja maior ou igual ao tempo de atraso esperado ou 0
        model.addConstr(delay_time[i] >= delay_aux)
             
    model.optimize()

    if model.status != gurobipy.GRB.OPTIMAL:
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
        [(i, j) for i in range(location_count) for j in range(location_count) if chosen_route[i, j].X > 0.5],
        # Tempos de chegada em cada local
        [arrival_time[i].X for i in range(location_count)],
        # Tempo de atraso em cada local
        [delay_time[i].X for i in range(location_count)]
    )