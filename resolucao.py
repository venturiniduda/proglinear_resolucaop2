
import parametro
import modelo
import restricao
import multiprocessing
import solution_logger

if __name__ == "__main__":
    instances = parametro.read_instances()

    with multiprocessing.Pool() as pool:
        results = pool.map(modelo.solve, list(map(lambda x: x[1], instances)))

        for instance, result in zip(instances, results):
            instance_name, _ = instance
            solution_logger.log_solution(instance_name, result)
