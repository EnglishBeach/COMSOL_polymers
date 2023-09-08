import pandas as _pd
import numpy as _np
import re as _re
from tqdm import tqdm as _tqdm
import mph as _mph

from itertools import product as _product
from scipy.interpolate import RBFInterpolator as _RBFInterpolator
from scipy.interpolate import griddata as _griddata
from structure import Solve, db


# Evaluating
def model_parametrs(model: _mph.Model, changed_params: dict = {}):
    for key, value in changed_params.items():
        model.parameter(name=key, value=value)
    return model.parameters()


def evaluate_species(
    model: _mph.Model,
    outer_number,
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


# SQL


def get_solves(conditious):
    string = 'select * from solve \n where \n'
    for key, diap in conditious.items():
        string += f'{diap[0]} <= {key} and {key} <= {diap[1]} \n and \n'

    querry = string[:-8]

    with db:
        columns = [i.name for i in db.get_columns('solve')]
        # columns.remove('data')
        cursor = db.execute_sql(querry)
        result = cursor.fetchall()
    df = _pd.DataFrame(columns=columns, data=result)

    datas = df['data']
    data_df_list = []
    for data in datas:
        data_df_list.append(_pd.read_json(data[1:-1].replace('\\', '')))

    del df['data']
    return df, data_df_list


def solve_to_sql(df, params: dict, name, desc=None):
    note = params.copy()
    note['name'] = name
    note['desc'] = desc
    note['data'] = df.to_json(index=True)
    with db:
        Solve.insert(note).execute()


# TODO: logs
def solves_to_sql(
    model: _mph.Model,
    name,
    desc=None,
):
    _, light_sweep = model.outer('Data')
    i = 1
    params = {
        key: float(value)
        for key,
        value in model.parameters().items()
        if 'light' not in key
    }
    params['name'] = name
    params['desc'] = desc

    notes = []
    for light_value in light_sweep:
        note = {}
        note.update(params)
        note['light'] = light_value
        df = evaluate_species(model, i)
        note['data'] = df.to_json(index=True)
        notes.append(note)

        i += 1

    with db:
        Solve.insert_many(notes).execute()


def sweep(
    model: _mph.Model,
    variable_params,
    name=None,
    desc=None,
):
    name = check(name)
    desc = check(desc)

    params_list = _tqdm(iterable=variable_params)

    i = 0
    for changed_params in params_list:
        model_parametrs(
            model=model,
            changed_params=changed_params,
        )
        model.clear()
        params_list.set_description('{:10}'.format('Solving...'))
        model.solve()
        params_list.set_description('{:10}'.format('Saving...'))
        solves_to_sql(
            model=model,
            name=name + f'#{i}',
            desc=desc,
        )
        i += 1


# To plots
def flat2image(
    x: _np.ndarray,
    y: _np.ndarray,
    z: _np.ndarray,
    method='linear',
    grid_points=11,
    **kwargs,
):
    xi = _np.linspace(x.min(), x.max(), grid_points)
    yi = _np.linspace(y.min(), y.max(), grid_points)
    X, Y = _np.meshgrid(xi, yi)
    if method in ['linear', 'cubic', 'nearest']:
        Z = _griddata(
            points=(x, y),
            values=z,
            xi=(X, Y),
            method=method,
            **kwargs,
        )

    elif method == 'rbf':
        XYi = _np.stack((X, Y))
        XY_line = XYi.reshape(2, -1).T

        interpol = _RBFInterpolator(
            _np.vstack((x, y)).T,
            z,
            **kwargs,
        )
        Z = interpol(XY_line).reshape(grid_points, grid_points)

    return X, Y, Z


def check(string):
    if string is None:
        while string != 'q':
            string = input(f'Set {string=}, to quit - q:')
            string = string.strip()
    return string


def combinations_dict(diap: dict):
    keys = list(diap.keys())
    values = [diap[key] for key in keys]
    combinations = list(_product(*values))
    result = [dict(zip(keys, comb)) for comb in combinations]
    return result