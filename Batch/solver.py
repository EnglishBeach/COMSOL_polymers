import pandas as _pd
import numpy as _np
from tqdm import tqdm as _tqdm

from scipy.interpolate import RBFInterpolator, griddata
from structure import Const, Solve, db

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

# SQL
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
        data_df_list.append(_pd.read_json(data[1:-1].replace('\\', '')))

    del df['data']
    return df, data_df_list

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