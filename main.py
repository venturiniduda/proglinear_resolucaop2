import parametro
import modelo_a
import modelo_b
import restricao
import multiprocessing
import resolucao

if __name__ == "__main__":
    instances = parametro.read_instances()

    with multiprocessing.Pool() as pool:
        results = pool.map(modelo_a.solve, list(map(lambda x: x[1], instances)))

        for instance, result in zip(instances, results):
            instance_name, _ = instance
            resolucao.log_solution(instance_name, result)
