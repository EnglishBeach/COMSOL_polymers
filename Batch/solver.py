import pandas as _pd
import numpy as _np
import re as _re
from tqdm import tqdm as _tqdm
import mph as _mph

from itertools import product as _product
from scipy.interpolate import RBFInterpolator as _RBFInterpolator
from scipy.interpolate import griddata as _griddata
from db_structure import Solve, db





# SQL
def get_solves(conditious):
    string = 'select * from solve \n where \n'
    for key, diap in conditious.items():
        string += f'{diap[0]} <= {key} and {key} <= {diap[1]} \n and \n'

    querry = string[:-8]

    with db:
        columns = [i.name for i in db.get_columns('solve')]
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
def sweep_to_sql(
    model: _mph.Model,
    name,
    desc=None,
):
    _, light_sweep = model.outer('Data')
    i = 1
    params = {
        key: float(value)
        for key,
        value in model_parameters(model).items()
        if 'light' not in key
    }
    params['name'] = name
    params['desc'] = desc

    notes = []
    for light_value in light_sweep:
        note = {}
        note.update(params)
        note['light'] = light_value
        df = evaluate_expressions(model, i)
        note['data'] = df.to_json(index=True)
        notes.append(note)

        i += 1

    assert db.is_connection_usable(), 'Database not connected'
    Solve.insert_many(notes).execute()


def sweep(
    model: _mph.Model,
    tuning_params,
    name=None,
    desc=None,
):
    name = input_check(name)
    desc = input_check(desc)

    tuning_list = _tqdm(iterable=tuning_params)

    i = 0
    for changed_params in tuning_list:
        model_parametrs(
            model=model,
            changed_params=changed_params,
        )
        model.clear()
        tuning_list.set_description('{:10}'.format('Solving...'))
        model.solve()
        tuning_list.set_description('{:10}'.format('Saving...'))
        sweep_to_sql(
            model=model,
            name=name + f'#{i}',
            desc=desc,
        )
        i += 1


# To plots
def collect_dfs(datas,dfs,diap):
    result=_pd.DataFrame()
    for i in range(len(datas)):
        df= dfs[i]
        params = datas.loc[i][diap]
        df[diap] =list(params)
        result=_pd.concat([result,df])
    return result


def combinations_dict(diap: dict):
    keys = list(diap.keys())
    values = [diap[key] for key in keys]
    combinations = list(_product(*values))
    result = [dict(zip(keys, comb)) for comb in combinations]
    return result