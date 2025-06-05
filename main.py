import time
import parametro
import modelo_a
import modelo_b
import resolucao
import gc
from concurrent.futures import ThreadPoolExecutor
import multiprocessing

def process_instance(instance_data):
    instance_name, location_data = instance_data

    res_a = modelo_a.solve(location_data)
    res_b = modelo_b.solve(location_data)

    resolucao.log_solution(instance_name, res_a, res_b)

    if res_a is not None:
        _, _, _, _, _, route_a, _, _ = res_a
        resolucao.plot_resolucao(instance_name, location_data, route_a)

    if res_b is not None:
        _, _, _, _, _, route_b, _, _, _ = res_b
        resolucao.plot_resolucao(f"{instance_name}_b", location_data, route_b)

    # Limpeza de memória
    del res_a, res_b
    gc.collect()

if __name__ == "__main__":
    instances = parametro.read_instances()
    start = time.time()

    # Define o número de threads como o número de núcleos lógicos
    num_threads = multiprocessing.cpu_count()

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        executor.map(process_instance, instances)

    end = time.time()
    print(f"\n✅ Tempo total de execução: {end - start:.2f} segundos")
