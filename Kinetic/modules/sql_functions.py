import pandas as _pd
import mph as _mph
import comsol as _comsol

import db_structure as _db_structure


def get_solves(conditious):
    """
    Get
    """
    string = 'select * from solve \n where \n'
    for key, diap in conditious.items():
        string += f'{diap[0]} <= {key} and {key} <= {diap[1]} \n and \n'

    querry = string[:-8]
    with _db_structure.db:
        columns = [i.name for i in _db_structure.db.get_columns('solve')]
        cursor = _db_structure.db.execute_sql(querry)
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
    with _db_structure.db:
        _db_structure.Solve.insert(note).execute()


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
        value in _comsol.model_parameters(model).items()
        if 'light' not in key
    }
    params['name'] = name
    params['desc'] = desc

    notes = []
    for light_value in light_sweep:
        note = {}
        note.update(params)
        note['light'] = light_value
        df = _comsol.evaluate_expressions(model, i)
        note['data'] = df.to_json(index=True)
        notes.append(note)

        i += 1

    assert _db_structure.db.is_connection_usable(), 'Database not connected'
    _db_structure.Solve.insert_many(notes).execute()
