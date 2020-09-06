from collections import namedtuple
from typing import List, Callable, Union

from assembly_calculus.learning.components.model import LearningModel
from simulations.learning.strategy import Strategy
from simulations.learning.simulation_utils import SimulationUtilsFactory


TrainedModel = namedtuple('Model', ['model', 'test_set'])


def linear_training_set_size_function(input_size: int):
    return input_size * 50


def _create_model(strategy: Strategy,
                  input_size: int,
                  output_values_or_function: Union[List[int], Callable],
                  training_set_size_function: Callable,
                  noise: float) -> TrainedModel:

    simulation_utils = SimulationUtilsFactory.init_utils(strategy, input_size)
    brain = simulation_utils.create_brain(n=10000, k=100, p=0.01, beta=0.05)

    input_stimuli = simulation_utils.create_input_stimuli(brain, k=100)

    sequence = simulation_utils.create_sequence(brain, input_stimuli)
    sequence.display_connections_graph()
    training_set = simulation_utils.create_training_set(output_values_or_function, training_set_size_function, noise)

    model = LearningModel(brain=brain,
                          sequence=sequence,
                          input_stimuli=input_stimuli)
    
    model.train_model(training_set=training_set, number_of_sequence_cycles=1)
    test_set = simulation_utils.create_test_set(output_values_or_function)

    return TrainedModel(model=model, test_set=test_set)


def create_1_to_1_model(output_values_or_function: Union[List[int], Callable], noise=0.) -> TrainedModel:
    """
    :param output_values_or_function: the model's function or its output values list (by order)
    :param noise: the probability of noise (during the learning)
    :return: the trained model and a set to test it with. The proper usage for testing:
        trained_model.model.test_model(trained_model.test_set)
    """
    return _create_model(strategy=Strategy.Layered,
                         input_size=1,
                         output_values_or_function=output_values_or_function,
                         training_set_size_function=linear_training_set_size_function,
                         noise=noise)


def create_2_to_1_model(output_values_or_function: Union[List[int], Callable], noise=0.) -> TrainedModel:
    """
    :param output_values_or_function: the model's function or its output values list (by order)
    :param noise: the probability of noise (during the learning)
    :return: the trained model and a set to test it with. The proper usage for testing:
        trained_model.model.test_model(trained_model.test_set)
    """
    return _create_model(strategy=Strategy.Layered,
                         input_size=2,
                         output_values_or_function=output_values_or_function,
                         training_set_size_function=linear_training_set_size_function,
                         noise=noise)


def create_many_to_1_model(input_size: int,
                           output_values_or_function: Union[List[int], Callable],
                           noise=0.) -> TrainedModel:
    """
    :param input_size: the size of the model function's input
    :param output_values_or_function: the model's function or its output values list (by order)
    :param noise: the probability of noise (during the learning)
    :return: the trained model and a set to test it with. The proper usage for testing:
        trained_model.model.test_model(trained_model.test_set)
    """
    return _create_model(strategy=Strategy.Simple,
                         input_size=input_size,
                         output_values_or_function=output_values_or_function,
                         training_set_size_function=linear_training_set_size_function,
                         noise=noise)


if __name__ == '__main__':
    trained_model = create_2_to_1_model([0, 1, 1, 0])
    print(trained_model.model.test_model(trained_model.test_set).accuracy)
