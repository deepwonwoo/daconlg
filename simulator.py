import os
import argparse
import numpy as np
import pandas as pd
from env import custor_Env

parser = argparse.ArgumentParser()
parser.add_argument("--order_path", default="data/order.csv")
parser.add_argument("--stock_path", default="data/stock.csv")
args = parser.parse_args()


env = custor_Env(args)


# hyper-parameters for RL training
N_epiosde = 1

if __name__ == "__main__":

    for eps in range(N_epiosde):
        state = env.reset()

        for st in range(env.max_steps):
            action = np.random.randint(10, size=(24, 8))
            state, reward, done, info = env.step(action)
            # print(state)
            print(reward)
            # print(f"submission : {info['submission']} ")
