import math
import gurobipy as gp

M = 10 ** 7 #constante grande para restrição condicional (ativa e desativa restrição do tempo de chegada dependendo se uma rota foi escolhida)

# função para calcular a distância euclidiana (reta):
def get_distance(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2) #calcula distancia entre os dois pontos (x,y) -> tempo de deslocamento 

# função principal 
def solve(location_data): #coloca ponto de 'start' no final para mostrar que ele deve voltar ao ponto inicial // e conta numero de locais (retorno tb)
    location_data.append(location_data[0])  # volta ao ponto inicial
    location_count = len(location_data)
    
    #criar modelo 
    model = gp.Model()
    model.setParam('TimeLimit', 3600)  # limite de tempo de 1 hr 
    model.setParam('LogFile', './resultados/gurobi.log') #caminho p log 

    # variáveis de decisão:
    chosen_route = model.addVars(location_count, location_count, vtype=gp.GRB.BINARY, name='chosen_route')   #1 se a rota vai de i e j, 0 se não (binária 1)
    arrival_time = model.addVars(location_count, vtype=gp.GRB.CONTINUOUS, name='arrival_time', lb=0) #tempo de chegada no local i 
    delay_time = model.addVars(location_count, vtype=gp.GRB.CONTINUOUS, name='delay_time', lb=0) #quanto passou do prazo no local j 
    max_delay = model.addVar(vtype=gp.GRB.CONTINUOUS, name='max_delay', lb=0) #qual maior atraso entre todos os lugares (contínua 2,3,4 )

    # função objetivo: encontra e a rota que minimize o maior atraso 
    model.setObjective(max_delay, sense=gp.GRB.MINIMIZE)        #minimiza o valor da variavel max_delay - pq ao inves de somar os atrasos 
                                                                      #queremos evitar q qqlr lugar fique mt atrasado (pequenos atrasos em todos p evitar um grande atraso em um)
    
    # restrições: 

    # Cada local (exceto depósito 0) sai exatamente 1 vez
    model.addConstrs(
        gp.quicksum(chosen_route[i, j] for j in range(location_count) if i != j) == 1
        for i in range(1, location_count)
    )

    # Cada local (exceto depósito 0) chega exatamente 1 vez
    model.addConstrs(
        gp.quicksum(chosen_route[i, j] for i in range(location_count) if i != j) == 1
        for j in range(1, location_count)
    )

    # Do depósito (0) sai exatamente 1 vez (início da rota)
    model.addConstr(
        gp.quicksum(chosen_route[0, j] for j in range(1, location_count)) == 1
    )

    # Para depósito (0) chega exatamente 1 vez (fim da rota)
    model.addConstr(
        gp.quicksum(chosen_route[i, 0] for i in range(1, location_count)) == 1
    )

    # garantir que não haja sub-rotas (MTZ)
    for i in range(0, location_count - 1):     
        for j in range(1, location_count): 
            if i == j: 
                continue             #garante que o tempo de chegada no ponto j leve em conta o tempo de: chegada ao ponto anterior (i), serviço no ponto i, deslocamento entre i e j 

            location_i = location_data[i]
            location_i_coords = (location_i[0], location_i[1])
            location_i_service_time = location_i[2]

            location_j = location_data[j]
            location_j_coords = (location_j[0], location_j[1])
            
            time_between_locations = get_distance(location_i_coords, location_j_coords)

            model.addConstr(
                arrival_time[j] >= 
                    arrival_time[i] +              #so ativa a restraição se i -> j foi escolhida na chosen_route
                    time_between_locations +
                    location_i_service_time 
                    - M * (1 - chosen_route[i, j])
            )

    ## Atrasos e cálculo do atraso máximo
    for i in range(1, location_count - 1): #força max_delay seja maior ou igual a qualquer atraso indiv (delay_time[i]) de cada lugar 
        location_i = location_data[i]       #max_delay é o maior valor entre todos os atrasos 
        deadline = location_i[3]            #se atraso = 1,2,3 ... max_delay = gurobi escolhe 3 e otimizador encontra uma nova rota ex:2.5
        
        expected_delay_time = arrival_time[i] - deadline
        
        # Variável auxiliar para tempo de atraso
        delay_aux = model.addVar(vtype=gp.GRB.CONTINUOUS, name=f'delay_aux_{i}', lb=0)
        model.addConstr(delay_aux == expected_delay_time)
        model.addConstr(delay_time[i] >= delay_aux)
        model.addConstr(max_delay >= delay_time[i])

    # Configurar solver: ativa cortes GMI
    model.setParam('GomoryPasses', 1)
    model.optimize()

    #delay_aux = arrival_time[i] tempo que passou do prazo 
    #delay_time[i] >= delay_aux define o atraso real como no minimo esse valor (ou zero)
    #max_delay >= delay_time[i] força que max_delay seja maior entre todos delay_time]

    if model.status != gp.GRB.OPTIMAL:
        return None

    #otimiza resultado 
    return (
        model.ObjVal,  # valor da função objetivo (maior atraso)
        model.ObjBound, #bound inferior
        model.Runtime,  #tempo de execução
        model.MIPGap,   # gap 
        model.NodeCount, #nós 
        [(i, j) for i in range(location_count) for j in range(location_count) if chosen_route[i, j].X > 0.5], #arcos usados 
        [arrival_time[i].X for i in range(location_count)], #tempo de chegada 
        [delay_time[i].X for i in range(location_count)],  #atrasos em cada local 
        max_delay.X  #valor do atraso maximo 
    )

"""resumo: função objetivo maior atraso
evita grandes atrasados isolados 
"""
