import os as _os
import numpy as _np
from tqdm import tqdm as _tqdm
import pandas as _pd
from scipy.interpolate import RBFInterpolator,griddata


from structure import Const, Solve, db

# Default configs
DIR_PATH = r'D:\WORKS\COMSOL_polymers'

CONST_DEFAULT = {
    'Ke': 1E+9,
    'KH': 1E+9,
    'Kr': 1E+9,
    'Kdisp': 1E+9,
    'KqH': 2000,
    'Ks': 2,
    'Kd': 0.05,
    'Kc': 1,
    'Kp': 0.001,
    'KrD': 1E+9,
    'Kph': 1E-5,
}
CONST_LIGHT_LIST = list(CONST_DEFAULT.keys()) + ['light']

offline_command = f'comsolbatch -inputfile System_batch.mph'
offline_command += f'-paramfile io\\params.csv'
offline_command += f'-methodcall solve_full'
offline_command += f'-nosave'
offline_command += f'-batchlog system_batch.log'

def check(string):
    if string is None:
        while string != 'q':
            string = input(f'Set {string=}, to quit - q:')
            string = string.strip()
    return string


def df_from_comsol():
    with open(DIR_PATH + r'\Batch\io\Data.csv', 'r') as file:
        lines = file.readlines()
    lines = lines[4:]

    lines[:] = (line.replace('\n', '') for line in lines[:])
    lines[0] = lines[0].replace('% ', '')

    data = [line.split(',') for line in lines]
    return _pd.DataFrame(data=data[1:], columns=data[0]).astype(float)


def solve():
    # Create params file
    const_list = list(CONST_DEFAULT.keys())
    with open('params.csv', 'w+') as file:
        file.writelines(' '.join([key for key in const_list]) + '\n')
        if isinstance(CONST_DEFAULT[const_list[0]], tuple|list):
            for i in range(len(CONST_DEFAULT[const_list[0]])):
                file.writelines(
                    ' '.join([str(CONST_DEFAULT[key])
                              for key in const_list]) + '\n', )
        else:
            file.writelines(
                ' '.join([str(CONST_DEFAULT[key])
                          for key in const_list]) + '\n', )
    # Solve
    _os.chdir('D:\\Works\\COMSOL_polymers\\Batch')
    _os.system(offline_command)


def write(name, desc, df):

    grouped_frames = []
    nonconst_keys = [i for i in df.columns if i not in CONST_LIGHT_LIST]
    name = check(name)
    desc = check(desc)

    with db:
        i = 0
        groups = _tqdm(iterable=df.groupby(by=CONST_LIGHT_LIST))
        for const_values, frame in groups:
            # Solve
            func_frame = frame[nonconst_keys]
            func_frame = func_frame.reset_index(drop=True)
            grouped_frames.append(func_frame)
            solve = Solve.create(
                name=name + f'_#{i}',
                desc=desc,
                data=func_frame.to_json(index=True),
            )

            # Consts
            _zipped = zip(CONST_LIGHT_LIST, const_values)
            _consts_q = [{
                'solve': solve,
                'name': key,
                'value': value,
            } for key,value in _zipped] # yapf:disable
            Const.insert_many(_consts_q).execute()
            i += 1

    return grouped_frames

def get_solves(conditious):
    string = 'select * from pivot \n where \n'
    for key, diap in conditious.items():
        string += f'{diap[0]} <= {key} and {key} <= {diap[1]} \n and \n'

    querry = string[:-8]

    with db:
        columns = [i.name for i in db.get_columns('pivot')]
        # columns.remove('data')
        cursor = db.execute_sql(querry)
        result = cursor.fetchall()
    df = _pd.DataFrame(columns=columns, data=result)


    datas = df['data']
    data_df_list = []
    for data in datas:
        data_df_list.append( _pd.read_json(data[1:-1].replace('\\','')))

    del df['data']
    return df,data_df_list



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
        Z = griddata(
            points=(x, y),
            values=z,
            xi=(X, Y),
            method=method,
            **kwargs,
        )

    elif method == 'rbf':
        XYi = _np.stack((X, Y))
        XY_line = XYi.reshape(2, -1).T

        interpol = RBFInterpolator(
            _np.vstack((x, y)).T,
            z,
            **kwargs,
        )
        Z = interpol(XY_line).reshape(grid_points, grid_points)

    return X, Y, Z

def solve_and_write(name=None, desc=None):
    solve()
    df = df_from_comsol()
    df_list = write(name, desc, df)
    return df_list
