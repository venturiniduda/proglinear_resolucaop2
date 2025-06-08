import time
import parametro
import modelo_a
import modelo_b
import resolucao
import gc
from concurrent.futures import ThreadPoolExecutor
import multiprocessing

def process_instance(instance_data, selected_model):
    instance_name, location_data = instance_data

    print(f"\n🔄 Processando instância: {instance_name}")

    res_a = res_b = None

    if selected_model in ('1', '3'):
        res_a = modelo_a.solve(location_data)
        if res_a is not None:
            _, _, _, _, _, route_a, _, _ = res_a
            resolucao.plot_resolucao(instance_name, location_data, route_a)

    if selected_model in ('2', '3'):
        res_b = modelo_b.solve(location_data)
        if res_b is not None:
            _, _, _, _, _, route_b, _, _, _ = res_b
            resolucao.plot_resolucao(f"{instance_name}_b", location_data, route_b)

    resolucao.log_solution(instance_name, res_a, res_b, selected_model)

    # Limpeza de memória
    del res_a, res_b
    gc.collect()

if __name__ == "__main__":
    instances = parametro.read_instances()

    # Solicita a escolha do modelo
    escolha = ''
    while escolha not in ('1', '2', '3'):
        print("\nQual modelo deseja executar?")
        print("1 - Modelo A")
        print("2 - Modelo B")
        print("3 - Ambos")
        escolha = input("Digite a opção desejada (1, 2 ou 3): ").strip()

    start = time.time()

    num_threads = multiprocessing.cpu_count()

    # Executa com múltiplas threads
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        executor.map(lambda inst: process_instance(inst, escolha), instances)

    end = time.time()
    print(f"\n✅ Tempo total de execução: {end - start:.2f} segundos")
