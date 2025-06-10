import time
import instancias.parametro as parametro
import modelo_a
import modelo_b
import resolucao
import gc
from concurrent.futures import ThreadPoolExecutor
import multiprocessing

def process_instance(instance_data):
    """
    Processa uma única instância, resolvendo os modelos A e B,
    registrando a solução e limpando a memória.
    """
    instance_name, location_data = instance_data
    print(f"🚀 Processando instância: {instance_name}...")

    # --- Resolução do Modelo A ---
    print(f"   - Resolvendo Modelo A para {instance_name}...")
    start_a = time.time()
    res_a = modelo_a.solve(location_data)
    end_a = time.time()
    if res_a:
        print(f"   - Modelo A finalizado em {end_a - start_a:.2f}s. Atraso Total: {res_a[0]:.2f}")
    else:
        print(f"   - Modelo A não encontrou solução para {instance_name} no tempo limite.")

    # --- Resolução do Modelo B ---
    print(f"   - Resolvendo Modelo B para {instance_name}...")
    start_b = time.time()
    res_b = modelo_b.solve(location_data)
    end_b = time.time()
    if res_b:
        print(f"   - Modelo B finalizado em {end_b - start_b:.2f}s. Maior Atraso: {res_b[0]:.2f}")
    else:
        print(f"   - Modelo B não encontrou solução para {instance_name} no tempo limite.")

    # --- Logging e Geração de Gráficos ---
    print(f"   - Gerando arquivos de resultado para {instance_name}...")
    resolucao.log_solution(instance_name, res_a, res_b)

    if res_a:
        route_a = res_a[5] 
        resolucao.plot_resolucao(f"{instance_name}_A", location_data, route_a)

    if res_b:
        route_b = res_b[5]
        resolucao.plot_resolucao(f"{instance_name}_B", location_data, route_b)

    del res_a, res_b
    gc.collect()
    print(f"✅ Instância {instance_name} finalizada.\n")

if __name__ == "__main__":
    print("--- INICIANDO SCRIPT DE RESOLUÇÃO ---")
    
    instances = parametro.read_instances()
    print(f"🔍 Encontradas {len(instances)} instâncias.")
    
    if not instances:
        print("\n‼️ ERRO CRÍTICO: Nenhuma instância foi encontrada.")
        print("   Verifique se a pasta 'instancias' existe no mesmo diretório que o script.")
        exit()
    
    total_start_time = time.time()
    
    # Executa em paralelo usando todos os núcleos da CPU
    num_threads = multiprocessing.cpu_count()
    print(f"\n--- INICIANDO PROCESSAMENTO PARALELO COM {num_threads} THREADS ---")
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        executor.map(process_instance, instances)

    total_end_time = time.time()
    print(f"\n🎉 Tempo total de execução de todas as instâncias: {total_end_time - total_start_time:.2f} segundos")