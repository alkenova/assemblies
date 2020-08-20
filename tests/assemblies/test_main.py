import gc
from os import environ

from assembly_calculus import Connectome, bake
from assembly_calculus.utils import overlap
from utils import protecc_ram


CERTAINTY_REPEAT = 25
EFFECTIVE_REPEAT = 3

if environ.get('PROTECC_MY_RAM', True):
    protecc_ram(0.75)


# TODO2: extract common magic numbers to constant
# Response: train_repeat is handcrafted per test, depends on how much stabilization is required
# TODO3: add more asserts to each test case
# Response: ???
# TODO4: remove code duplication inside tests. reuse code using methods. test code should be treated as regular code :)
# Response: Two lines code duplication per function is fine... creating a method will be more confusing.

def test_projection(recipe, assembly_a, assembly_b, area_c):
    with recipe:
        assembly_ac = assembly_a >> area_c
        assembly_bc = assembly_b >> area_c

    for _ in range(CERTAINTY_REPEAT):
        with bake(recipe, 0.1, Connectome, train_repeat=100, effective_repeat=EFFECTIVE_REPEAT) as brain:
            assembly_a >> area_c
            assert area_c.active_assembly == assembly_ac, "Separate assemblies have merged :("

            assembly_b >> area_c
            assert area_c.active_assembly == assembly_bc, "Separate assemblies have merged :("

        gc.collect()


def test_associate(recipe, assembly_a, assembly_b, area_c):
    def average_winners(assembly, times):
        winners = set()
        for _ in range(times):
            winners.update(set(assembly.sample_neurons(preserve_brain=False)))
        return winners

    with recipe:
        assembly_ac = assembly_a >> area_c
        assembly_bc = assembly_b >> area_c

    for _ in range(CERTAINTY_REPEAT):
        with bake(recipe, 0.1, Connectome, train_repeat=10, effective_repeat=EFFECTIVE_REPEAT) as brain:
            winners_a = average_winners(assembly_ac, 5)
            winners_b = average_winners(assembly_bc, 5)
            assert overlap(winners_a, winners_b) <= 0.25, "Assemblies have associated without associate"

        gc.collect()

    with recipe:
        (assembly_ac | ...).associate(assembly_bc | ...)

    for _ in range(CERTAINTY_REPEAT):
        with bake(recipe, 0.1, Connectome, train_repeat=10, effective_repeat=EFFECTIVE_REPEAT) as brain:
            winners_a = average_winners(assembly_ac, 5)
            winners_b = average_winners(assembly_bc, 5)
            assert overlap(winners_a, winners_b) > 0.25, "Assemblies haven't associated"

        gc.collect()


def test_merge(recipe, assembly_a, assembly_b, area_b, area_c):
    for _ in range(CERTAINTY_REPEAT):
        with bake(recipe, 0.1, Connectome, train_repeat=10, effective_repeat=EFFECTIVE_REPEAT) as brain:
            assembly_a >> area_c
            brain.next_round(subconnectome={area_c: [area_b]}, replace=True, iterations=brain.repeat)

            assert overlap(assembly_b.representative_neurons, area_b.winners) <= 0.10, \
                "Assemblies formed bi-directional links without merge"

        gc.collect()

    with recipe:
        (assembly_a | assembly_b) >> area_c

    for _ in range(CERTAINTY_REPEAT):
        with bake(recipe, 0.1, Connectome, train_repeat=10, effective_repeat=EFFECTIVE_REPEAT) as brain:
            assembly_a >> area_c
            brain.next_round(subconnectome={area_c: [area_b]}, replace=True, iterations=brain.repeat)

            assert overlap(assembly_b.representative_neurons, area_b.winners) > 0.10, \
                "Assemblies haven't formed bi-directional links"

        gc.collect()
