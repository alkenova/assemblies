from __future__ import annotations
from typing import Iterable, Dict, List, TYPE_CHECKING

from ..brain import Brain, Area, Stimulus

if TYPE_CHECKING:
    from ..assemblies import Projectable


# TODO: Remove preserve_brain and do it in outer scope
def fire_many(brain: Brain, projectables: Iterable[Projectable], area: Area, preserve_brain: bool = False):
    """
    This function works by creating a "Parent tree", (Which is actually a directed acyclic graph) first,
    and then by going from the top layer, which will consist of stimuli, and traversing down the tree
    while firing each layer to areas its relevant descendant inhibit.
    For example, "firing" an assembly, we will first climb up its parent tree (Assemblies of course may have
    multiple parents, such as results of merge. Then we iterate over the resulting list in reverse, while firing
    each layer to the relevant areas, which are saved in a dictionary format:
    The thing we will project: areas to project it to

    :param brain: the brain in which the firing happens
    :param projectables: a list of projectable objects to be projected
    :param area: the area into which the objects are projected
    :param preserve_brain: a boolean deteremining whether we want the brain to be changed in the process
    """
    # TODO 2: instead of keeping `original_plasticity` and restoring, this is a classic use for context! (for example: `with brain.disable_plasticity():` )
    # Response: We will use it if it is implemented for us, but out of our scope
    original_plasticity = brain.connectome.plasticity
    if preserve_brain:
        brain.connectome.plasticity = False
    # construct the firing hierarchy
    layers = construct_firing_order(projectables, area)
    # now, fire each layer:
    changed_areas = fire_layered_areas(brain, layers)
    if preserve_brain and not original_plasticity:
        brain.connectome.plasticity = True
    return changed_areas


def construct_firing_order(projectables: Iterable[Projectable], area: Area) -> List[Dict[Projectable, List[Area]]]:
    """
    Construct the "firing hierarchy", by going up the "parenthood" tree
    :param projectables: a list of projectable objects to be projected
    :param area: the area into which the objects are projected
    :return: Layered firing tree
    """
    from ..assemblies import Projectable, Assembly
    # initialize layers with the lowest level in the tree
    layers: List[Dict[Projectable, List[Area]]] = [{projectable: [area] for projectable in projectables}]
    # climb upwards until the current layers' parents are all stimuli (so there's no more climbing)
    while any(isinstance(projectable, Assembly) for projectable in layers[-1]):
        prev_layer: Iterable[Assembly] = (ass for ass in layers[-1].keys() if not isinstance(ass, Stimulus))
        current_layer: Dict[Projectable, List[Area]] = {}
        for ass in prev_layer:
            for parent in ass.parents:
                # map parent to all areas into which this parent needs to be fired
                current_layer[parent] = current_layer.get(ass, []) + [ass.area]

        layers.append(current_layer)

    # reverse the layers list to fire all parents the top to the original assemblies we've entered
    layers = layers[::-1]
    return layers


def fire_layered_areas(brain: Brain, firing_order: List[Dict[Projectable, List[Area]]]):
    """
    Fire layers of projectables one by one
    :param brain: Brain in which to to fire
    :param firing_order: Layers of projectables, and corresponding areas (to fire into)
    :return: Original winners of affected areas
    """
    from ..assemblies import Assembly
    changed_areas: Dict[Area, List[int]] = {}
    for layer in firing_order:
        stimuli_mappings: Dict[Stimulus, List[Area]] = {stim: areas
                                                        for stim, areas in
                                                        layer.items() if isinstance(stim, Stimulus)}
        assembly_mapping: Dict[Area, List[Area]] = {}
        # TODO: why such complex logic instead of using `layer.keys()` instead of `layer.items()`?
        # Response: To get the value as well in the iterator itself
        for ass, areas in filter(lambda t: (lambda assembly, _: isinstance(assembly, Assembly))(*t), layer.items()):
            # map area to all areas into which this area needs to be fired
            assembly_mapping[ass.area] = assembly_mapping.get(ass.area, []) + areas

        mapping = {**stimuli_mappings, **assembly_mapping}
        for areas in mapping.values():
            for area in areas:
                if area not in changed_areas:
                    changed_areas[area] = brain.winners[area]

        brain.next_round(subconnectome=mapping, replace=True)   # fire this layer of objects

    return changed_areas


# TODO: This function should belong to brain.py, and probably implemented otherwise.
#       This is because it is very likely that changes will be made that will make
#       this function behave poorly - perhaps not remember to revert some structure
#       will be added later on. It would be a bitch to debug.
# Response: API Team can move this to brain.py (their choice)
#           We chose not to do as a content manager for efficiency
#           If an efficient content manager will be implemented, of course we will use it (again, out of our scope)
def revert_changes(brain: Brain, *changed_areas: Dict[Area, List[int]]):
    """
    Changes the winners of areas in the given brain as dictated in the changed_areas dictionary
    :param brain: a brain
    :param changed_areas: a dictionary mapping between areas and their previous winners
    """
    changed_areas = changed_areas[::-1]
    changes = changed_areas[0]
    for change in changed_areas:
        changes.update(change)
    for area in changes:
        brain.connectome.winners[area] = changes[area]
