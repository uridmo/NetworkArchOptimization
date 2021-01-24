import numpy as np
from geneticalgorithm import geneticalgorithm as ga

from bridges.Blennerhassett import BlennerhassettBridge

solution_dictionary = {}


def f(x):
    if str(x) in solution_dictionary:
        cost = solution_dictionary[str(x)]
    else:
        cost = BlennerhassettBridge(hanger_arrangement='Unpatterned',
                                    hanger_params=x,
                                    self_stress_state='Zero-displacement',
                                    curve_fitting='Polynomial',
                                    cable_loss=False).cost
        solution_dictionary[str(x)] = cost
    print(round(cost / 10 ** 6, 3))
    return cost


algorithm_param = {'max_num_iteration': 100,
                   'population_size': 40,
                   'mutation_probability': 0.15,
                   'elit_ratio': 0.1,
                   'crossover_probability': 0.5,
                   'parents_portion': 0.3,
                   'crossover_type': 'uniform',
                   'max_iteration_without_improv': None}

varbound = np.array([[20, 130]] * 13)

model = ga(function=f, dimension=13, variable_type='int',
           variable_boundaries=varbound, algorithm_parameters=algorithm_param)

model.run()

solution = model.ouput_dict
print(solution)
