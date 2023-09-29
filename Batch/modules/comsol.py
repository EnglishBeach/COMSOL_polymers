import pandas as _pd
import numpy as _np
import re as _re
from tqdm import tqdm as _tqdm
import mph as _mph

from scipy.interpolate import RBFInterpolator as _RBFInterpolator
from scipy.interpolate import griddata as _griddata


def model_parametrs(model: _mph.Model, changed_params: dict = {}):
    for key, value in changed_params.items():
        model.parameter(name=key, value=value)
    return model.parameters()


def evaluate_expressions(
    model: _mph.Model,
    outer_number=1,
    expresions: list = [],
    comsol_dataset='Data',
):
    reaction_node = model / 'physics' / 'Reaction Engineering'
    _reaction_node_children = [i.name() for i in reaction_node.children()]

    if expresions ==[]:
        expresions = _re.findall(
            string='\n'.join(_reaction_node_children),
            pattern='Species: (.*)',
        )
        comsol_expressions = ['reaction.c_' + specie for specie in expresions]
    else:
        comsol_expressions = expresions

    row_data = model.evaluate(
        ['t'] + comsol_expressions,
        dataset=comsol_dataset,
        outer=outer_number,
    )

    return _pd.DataFrame(row_data, columns=['Time'] + expresions)


