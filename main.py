import time
import parametro
import modelo_a
import modelo_b
import resolucao
import gc

if __name__ == "__main__":
    instances = parametro.read_instances()

    print("🔄 Iniciando resolução sequencial das instâncias...")
    start = time.time()

    for instance_name, location_data in instances:
        print(f"\n📦 Instância: {instance_name}")

        res_a = modelo_a.solve(location_data)
        res_b = modelo_b.solve(location_data)

        resolucao.log_solution(instance_name, res_a, res_b)

        # Exibir rota graficamente se houver solução viável
        if res_a is not None:
            _, _, _, _, _, route_a, _, _ = res_a
            resolucao.plot_resolucao('Resolução (modelo A)', location_data, route_a)

        # Limpeza de memória
        del res_a, res_b
        gc.collect()

    end = time.time()
    total_time = end - start

    print(f"\n✅ Tempo total de execução: {total_time:.2f} segundos")
