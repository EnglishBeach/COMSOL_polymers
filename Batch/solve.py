import numpy as np
import os
import pandas as pd

path = r'D:\WORKS\COMSOL_polymers'

default_values = {
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
const_keys = list(default_values.keys()) + ['light']

offline_command = f'comsolbatch -inputfile System_batch.mph'
offline_command += f'-paramfile io\\params.csv'
offline_command += f'-methodcall solve_full'
offline_command += f'-nosave'
offline_command += f'-batchlog system_batch.log'


def solve_offline(data_full):
    keys = list(default_values.keys())
    with open('params.csv', 'w+') as file:
        file.writelines(' '.join([key for key in keys]) + '\n')
        if isinstance(default_values[keys[0]], tuple|list):
            for i in range(len(default_values[keys[0]])):
                file.writelines(
                    ' '.join([str(default_values[key])
                              for key in keys]) + '\n', )
        else:
            file.writelines(
                ' '.join([str(default_values[key]) for key in keys]) + '\n', )

    os.chdir('D:\\Works\\COMSOL_polymers\\Batch')

    os.system(offline_command)
