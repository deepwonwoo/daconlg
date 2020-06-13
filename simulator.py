import os
import argparse
import numpy as np
import pandas as pd
from env import custor_Env
from pandas import DataFrame
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--order_path', dest='data/order.csv', default=False)
parser.add_argument('--stock_path', dest='test', default=False)
args = parser.parse_args()


df_order = pd.read_csv(os.path.join(
    Path(__file__).resolve().parent, 'data/order.csv'))
df_order.iloc[:, 0] = pd.to_datetime(df_order.iloc[:, 0])

"""
    for i, row in order.iterrows():
    create_submission(row['time'])

def get_submission(submission, order_date,):
    submission = {'time': [], 'PRT_1': [], 'PRT_2': [], 'PRT_3': [],
                  'PRT_4': [], 'Event_A': [], 'MOL_A': [], 'Event_B': [], 'MOL_B': []}
    for i in range(24):
        submission['time'].append(order_date + f" {i:0>2d}:00:00")
        submission['PRT_1'].append(0)
        submission['PRT_2'].append(0)
        submission['PRT_3'].append(0)
        submission['PRT_4'].append(0)
        submission['Event_A'].append(0)
        submission['MOL_A'].append(0)
        submission['Event_B'].append(0)
        submission['MOL_B'].append(0)
    return DataFrame(submission)
"""


env = custor_Env()


# hyper-parameters for RL training
N_epiosde = 1
N_steps_per_episode = 1


if __name__ == '__main__':

    for eps in range(N_epiosde):

        state = env.reset()
