import numpy as _np
import plotly.express as _px

from scipy.interpolate import griddata as _griddata
from scipy.interpolate import RBFInterpolator as _RBFInterpolator


def simple_temporal_plot(df, y):
    fig = _px.line(df, x='time', y=y,)
    fig.update_layout(
        height=500,
        margin={
            'r': 0, 'l': 0, 't': 0, 'b': 0
        },
        legend=dict(x=-0.1, y=1, xanchor="center"),
    )
    return fig


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


def input_check(string):
    if string is None:
        while string != 'q':
            string = input(f'Set {string=}, to quit - q:')
            string = string.strip()
    return string
