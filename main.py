import parametro
import modelo_a
import modelo_b
import restricao
import multiprocessing
import resolucao

if __name__ == "__main__":
    instances = parametro.read_instances()

    with multiprocessing.Pool() as pool:
        resultado_a = pool.map(modelo_a.solve, list(map(lambda x: x[1], instances)))
        resultado_b = pool.map(modelo_b.solve, list(map(lambda x: x[1], instances)))

        for instance, res_a, res_b in zip(instances, resultado_a, resultado_b):
            instance_name, location_data = instance
            resolucao.log_solution(instance_name, res_a, res_b)

            # Para utilizar somente o res_b do retorno da função do modelo:
            _, _, _, _, _, route_a, _, _ = res_a
            resolucao.plot_resolucao('Resolução',location_data, route_a)
