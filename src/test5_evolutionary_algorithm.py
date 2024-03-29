import models.genetic_algorithm as gam
from models.simulation import Simulation_test_5


EVAL_INDIVIDUAL_IN_SIMULATION_MAX_AVERAGE = 0
EVAL_INDIVIDUAL_IN_SIMULATION_TOTAL = 1
EVAL_INDIVIDUAL_IN_SIMULATION_WEIGTHED_MEAN = 2

MULTIPOINT_XOVER = 0
INTERMEDIATE_XOVER = 1
GEOMETRIC_XOVER = 2

GET_WEIGHTS_FIT_PROPORTIONAL = 0
GET_WEIGHTS_BY_RANKING = 1

simulation = Simulation_test_5()

pop_size = 30
number_of_turns = simulation.get_new_control_object().GetDimension()
maximum_waiting_time = 90
average_passing_time = 3
speed = 30
obs_time = 10
max_iterations = 50

for i in range(5):
    gam.genetic_algorithm(simulation, pop_size, number_of_turns,
                      maximum_waiting_time, average_passing_time, speed, obs_time, max_iterations,
                      eval_method=EVAL_INDIVIDUAL_IN_SIMULATION_WEIGTHED_MEAN, weight_method=GET_WEIGHTS_BY_RANKING, xover_method=MULTIPOINT_XOVER)
