import gurobipy as gp
from gurobipy import GRB
import numpy as np

# --- Leitura do arquivo com interpretação correta ---
with open("./instancias/inst_10.txt") as f:
    raw_lines = [line.strip() for line in f if line.strip()]

n_total = int(raw_lines[0])  # número total de localidades (depósito + clientes)
data = [list(map(int, line.split())) for line in raw_lines[1:]]

if len(data) != n_total:
    raise ValueError(f"Esperado {n_total} localidades, mas encontrei {len(data)}.")

# Localidades: 0 = depósito, 1..n = clientes, n+1 = depósito final (duplicado)
coords = [tuple(row[:2]) for row in data]
serv_times = [row[2] for row in data]
deadlines = [row[3] for row in data]

# Duplicar o depósito no final para facilitar o modelo
coords.append(coords[0])
serv_times.append(0)
deadlines.append(0)

n = n_total - 1  # número de clientes (exclui o depósito)
nodes = list(range(n_total + 1))  # 0..n_total (inclui depósito final)
M = 1e5

# --- Matriz de tempos (distância + tempo de serviço) ---
dij = np.zeros((n_total + 1, n_total + 1))
for i in nodes:
    for j in nodes:
        if i != j:
            dx = coords[i][0] - coords[j][0]
            dy = coords[i][1] - coords[j][1]
            dij[i][j] = np.hypot(dx, dy) + serv_times[i]

# --- Modelo ---
model = gp.Model("MinAtrasoMaximo")

x = model.addVars(nodes, nodes, vtype=GRB.BINARY, name="x")
t = model.addVars(nodes, vtype=GRB.CONTINUOUS, lb=0, name="t")
A = model.addVars(nodes, vtype=GRB.CONTINUOUS, lb=0, name="A")
u = model.addVars(nodes, vtype=GRB.CONTINUOUS, lb=1, ub=n, name="u")
Amax = model.addVar(vtype=GRB.CONTINUOUS, lb=0, name="Amax")

model.setObjective(Amax, GRB.MINIMIZE)

# --- Restrições ---
for j in range(1, n_total + 1):
    model.addConstr(gp.quicksum(x[i, j] for i in nodes if i != j) == 1)

for i in range(n_total):
    model.addConstr(gp.quicksum(x[i, j] for j in nodes if i != j) == 1)

for i in range(n_total):
    for j in range(1, n_total + 1):
        if i != j:
            model.addConstr(u[i] - u[j] + (n_total) * x[i, j] <= n)

for i in range(n_total):
    for j in range(1, n_total + 1):
        if i != j:
            model.addConstr(t[j] >= t[i] + dij[i][j] - M * (1 - x[i, j]))

for i in range(1, n_total):
    model.addConstr(A[i] >= t[i] - deadlines[i])
    model.addConstr(Amax >= A[i])

# --- Otimização ---
model.optimize()

# --- Resultados ---
if model.status == GRB.OPTIMAL:
    print(f"\nAtraso máximo: {Amax.X:.2f}")
    print("Rota:")
    for i in nodes:
        for j in nodes:
            if x[i, j].X > 0.5:
                print(f"{i} -> {j}")
else:
    print("Solução ótima não encontrada.")
