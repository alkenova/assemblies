import gc
import json
import os
import time
import uuid
from pathlib import Path

from assembly_calculus import Area, Stimulus, BrainRecipe, bake, Connectome, Assembly
from assembly_calculus.utils import protecc_ram, Logger

import matplotlib.pyplot as plt

# Merge simulation
# ================
#
# We compare different merge strategies, and plot it all in a graph
# describing the "merge efficiency" of every strategy

"""
Parameter Selection
"""
# Number of samples per graph point
AVERAGING_SIZE = 25
# Size of Stimulus
STIMULUS_SIZE = 100
# Size of areas
AREA_SIZE = 1000

TESTS = (
    (1, (1, 3, 5, 10, 25, 100, 250)),
    (3, (1, 3, 5, 10, 25, 100, 250)),
    (5, (1, 3, 5, 10, 25, 100, 250)),
    (10, (1, 3, 5, 10, 25, 100, 250)),
    (25, (1, 3, 5, 10, 25, 50, 100, 250)),
    (50, (1, 3, 5, 10, 25, 50, 100, 250)),
    (100, (1, 3, 5, 10, 25, 50, 100, 250)),
    (250, (1, 3, 5, 10, 25, 50, 100, 250)),
    (500, (1, 3, 5, 10, 25, 50, 100, 250)),
)

"""
Setup
"""""
# Generate a unique identifier for saving the graph
uid = uuid.uuid4()

# Save test information
base_path = Path(os.path.dirname(__file__)).resolve() / 'artifacts'
if not base_path.is_dir():
    base_path.mkdir()
base_path = base_path / f'{uid}'
base_path.mkdir()

with open(base_path / 'parameters.txt', 'w') as f:
    f.write(json.dumps({
        'AVERAGING_SIZE': AVERAGING_SIZE,
        'STIMULUS_SIZE': STIMULUS_SIZE,
        'AREA_SIZE': AREA_SIZE
    }))
with open(base_path / 'tests.txt', 'w') as f:
    f.write(json.dumps(TESTS, indent=4))

# Redirect console to logfile
Logger(base_path / 'log').__enter__()

# Protect RAM from program using up all memory
# Allows program to use only half of free memory
protecc_ram(0.75)

# Create graph for presenting the results
fig, ax = plt.subplots()
plt.title('Assemblies Merge')
ax.set_xscale('log')
plt.xlabel('t (Repeat Parameter)')
plt.ylabel('Overlap %')

##################################################################################################################


"""
Simulation
"""

# Create basic brain model
stimulus = Stimulus(STIMULUS_SIZE)
area1 = Area(AREA_SIZE)
area2 = Area(AREA_SIZE)
area3 = Area(AREA_SIZE)
area4 = Area(AREA_SIZE)
assembly1 = Assembly([stimulus], area1)
assembly2 = Assembly([stimulus], area2)

print(f"Writing simulation to {base_path}")
begin_time = time.time()
for merge_stabilization, repeats in TESTS:
    recipe = BrainRecipe(area1, area2, area3, area4, stimulus, assembly1, assembly2)
    # Define assembly out of recipe,
    # that way merge can done manually!
    assembly3 = (assembly1 | assembly2) >> area3

    # Define brain "active" recipe
    with recipe:
        # Manual merge process by interleaved projects
        for _ in range(merge_stabilization):
            assembly1 >> area3
            assembly2 >> area3

    # Dictionary for storing results
    overlap_per_repeat = {}
    for t in repeats:
        print(f"Beginning simulation with merge_stabilization={merge_stabilization}, t={t}:", flush=True)

        # Averaging loop
        values = []
        specific_sim_start = time.time()
        for _ in range(AVERAGING_SIZE):
            # Create brain from recipe
            with bake(recipe, 0.1, Connectome, train_repeat=t, effective_repeat=3) as brain:
                def overlap(A, B):
                    assert len(A) == len(B)
                    return len(set(A) & set(B)) / len(A)


                # Project assembly for the first time
                (assembly1 | assembly2) >> area3
                # Store winners
                first_winners = area3.winners

                brain.winners[area3] = list()

                # Project assembly for the second time
                (assembly1 | assembly2) >> area3
                # Store winners
                second_winners = area3.winners

                # Compute the overlap between first and second projection winners
                values.append(overlap(first_winners, second_winners) * 100)

            # helps my computer deal with the RAM usage (not necessary)
            gc.collect()

        # Compute average overlap
        overlap_value = sum(values) / len(values)
        overlap_per_repeat[t] = overlap_value

        print(f"\tOverlap: {overlap_value}%")
        print(f"\tCurrent simulation took {time.time() - specific_sim_start}s")
        print(f"\tElapsed time: {time.time() - begin_time}s", flush=True)

    # Add current observations to graph
    x, y = zip(*overlap_per_repeat.items())
    ax.plot(x, y, label=f"{merge_stabilization} MS")

    # Present graph
    lgd = fig.legend(loc='lower right')

    # Save graph to file
    fig.savefig(base_path / 'graph.pdf')
    lgd.remove()

end_time = time.time()
print(f"Simulation took {end_time - begin_time}s", flush=True)
