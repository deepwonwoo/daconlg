import argparse, os
import numpy as np
import pandas as pd
from pathlib import Path
from pandas import DataFrame


class custor_Env:
    """
    [summary]
     state :
       vector of size : (4 + 12)
       (BLK_1,BLK_2,BLK_3,BLK_4) - order per day
       (PRT_1,PRT_2,PRT_3,PRT_4,MOL_1,MOL_2,MOL_3,
        MOL_4,BLK_1,BLK_2,BLK_3,BLK_4) - stock

     Action :
       2D vector of size (24 * 8)
       (24hours)*(PRT_1,PRT_2,PRT_3,PRT_4,Event_A,MOL_A,Event_B,MOL_B)
    """

    def __init__(self, args):
        self.load_data(args)
        self.state = None
        self.action = None
        self.state_dim = (16,)
        self.action_dim = (24, 8)
        self.current_step = 0
        self.max_steps = len(self.df_order)

    def reset(self):
        self.state = np.random.randint(low=0, high=1, size=self.state_dim)
        return np.array(self.state)

    def step(self, action):

        submission = self.make_submission(action)

        self.current_step = (
            self.current_step + 1 if self.current_step < self.max_steps - 1 else 0
        )

        self.state = np.concatenate(
            (self.df_order.iloc[self.current_step][1:], self.df_stock.iloc[0])
        )

        score, out = self.get_score(submission)

        done = False

        return self.state, score, done, {"submission": submission}

    def load_data(self, args):
        self.df_order = pd.read_csv(
            os.path.join(Path(__file__).resolve().parent, args.order_path)
        )
        self.df_order.iloc[:, 0] = pd.to_datetime(self.df_order.iloc[:, 0])
        self.df_order.set_index(self.df_order["time"], inplace=True)

        self.df_stock = pd.read_csv(
            os.path.join(Path(__file__).resolve().parent, args.stock_path)
        )

    def make_submission(self, action):
        submission = {
            "time": [],
            "PRT_1": [],
            "PRT_2": [],
            "PRT_3": [],
            "PRT_4": [],
            "Event_A": [],
            "MOL_A": [],
            "Event_B": [],
            "MOL_B": [],
        }

        for i in range(24):
            submission["time"].append(
                str(self.df_order.iloc[self.current_step][0]) + f" {i:0>2d}:00:00"
            )
            submission["PRT_1"].append(0)
            submission["PRT_2"].append(0)
            submission["PRT_3"].append(0)
            submission["PRT_4"].append(0)
            submission["Event_A"].append("CHECK_1")
            submission["MOL_A"].append(0)
            submission["Event_B"].append("CHECK_1")
            submission["MOL_B"].append(0)

        df = DataFrame(submission)

        return df

    def subprocess(self, df):
        out = df.copy()
        column = "time"

        out.index = pd.to_datetime(out[column])
        out = out.drop([column], axis=1)
        out.index.name = column
        return out

    def add_stock(self, df, df_stock):
        df_out = df.copy()
        for column in df_out.columns:
            df_out.iloc[0][column] = df_out.iloc[0][column] + df_stock.iloc[0][column]
        return df_out

    def get_state(self, data):
        if "CHECK" in data:
            return int(data[-1])
        elif "CHANGE" in data:
            return int(data[-1])
        else:
            return np.nan

    def order_rescale(self, df, df_order):

        df_rescale = df.drop(df.columns, axis=1)
        dt = pd.Timedelta(hours=18)
        for column in ["BLK_1", "BLK_2", "BLK_3", "BLK_4"]:
            for time in df_order.index:
                df_rescale.loc[time + dt, column] = df_order.loc[time, column]
        df_rescale = df_rescale.fillna(0)
        return df_rescale

    def cal_schedule_part_1(self, df):

        columns = ["PRT_1", "PRT_2", "PRT_3", "PRT_4"]
        df_set = df[columns]
        df_out = df_set * 0

        p = 0.985
        dt = pd.Timedelta(days=23)
        end_time = df_out.index[-1]

        for time in df_out.index:
            out_time = time + dt
            if end_time < out_time:
                break
            else:
                for column in columns:
                    set_num = df_set.loc[time, column]
                    if set_num > 0:
                        out_num = np.sum(np.random.choice(2, set_num, p=[1 - p, p]))
                        df_out.loc[out_time, column] = out_num

        df_out["MOL_1"] = 0.0
        df_out["MOL_2"] = 0.0
        df_out["MOL_3"] = 0.0
        df_out["MOL_4"] = 0.0
        df_out["BLK_1"] = 0.0
        df_out["BLK_2"] = 0.0
        df_out["BLK_3"] = 0.0
        df_out["BLK_4"] = 0.0
        return df_out

    def cal_schedule_part_2(self, df, line="A"):
        if line == "A":
            columns = ["Event_A", "MOL_A"]
        elif line == "B":
            columns = ["Event_B", "MOL_B"]
        else:
            columns = ["Event_A", "MOL_A"]

        schedule = df[columns].copy()

        schedule["state"] = 0
        schedule["state"] = schedule[columns[0]].apply(lambda x: self.get_state(x))
        schedule["state"] = schedule["state"].fillna(method="ffill")
        schedule["state"] = schedule["state"].fillna(0)

        schedule_process = schedule.loc[schedule[columns[0]] == "PROCESS"]
        df_out = schedule.drop(schedule.columns, axis=1)
        df_out["PRT_1"] = 0.0
        df_out["PRT_2"] = 0.0
        df_out["PRT_3"] = 0.0
        df_out["PRT_4"] = 0.0
        df_out["MOL_1"] = 0.0
        df_out["MOL_2"] = 0.0
        df_out["MOL_3"] = 0.0
        df_out["MOL_4"] = 0.0

        p = 0.975
        times = schedule_process.index
        for i, time in enumerate(times):
            value = schedule.loc[time, columns[1]]
            state = int(schedule.loc[time, "state"])
            df_out.loc[time, "PRT_" + str(state)] = -value
            if i + 48 < len(times):
                out_time = times[i + 48]
                df_out.loc[out_time, "MOL_" + str(state)] = value * p

        df_out["BLK_1"] = 0.0
        df_out["BLK_2"] = 0.0
        df_out["BLK_3"] = 0.0
        df_out["BLK_4"] = 0.0
        return df_out

    def cal_stock(self, df, df_order):
        df_stock = df * 0

        blk2mol = {}
        blk2mol["BLK_1"] = "MOL_1"
        blk2mol["BLK_2"] = "MOL_2"
        blk2mol["BLK_3"] = "MOL_3"
        blk2mol["BLK_4"] = "MOL_4"

        cut = {}
        cut["BLK_1"] = 506
        cut["BLK_2"] = 506
        cut["BLK_3"] = 400
        cut["BLK_4"] = 400

        p = {}
        p["BLK_1"] = 0.851
        p["BLK_2"] = 0.901
        blk_diffs = []
        for i, time in enumerate(df.index):
            month = time.month
            if month == 4:
                p["BLK_3"] = 0.710
                p["BLK_4"] = 0.700
            elif month == 5:
                p["BLK_3"] = 0.742
                p["BLK_4"] = 0.732
            elif month == 6:
                p["BLK_3"] = 0.759
                p["BLK_4"] = 0.749
            else:
                p["BLK_3"] = 0.0
                p["BLK_4"] = 0.0

            if i == 0:
                df_stock.iloc[i] = df.iloc[i]
            else:
                df_stock.iloc[i] = df_stock.iloc[i - 1] + df.iloc[i]
                for column in df_order.columns:
                    val = df_order.loc[time, column]
                    if val > 0:
                        mol_col = blk2mol[column]
                        mol_num = df_stock.loc[time, mol_col]
                        df_stock.loc[time, mol_col] = 0

                        blk_gen = int(mol_num * p[column] * cut[column])
                        blk_stock = df_stock.loc[time, column] + blk_gen
                        blk_diff = blk_stock - val

                        df_stock.loc[time, column] = blk_diff
                        blk_diffs.append(blk_diff)
        return df_stock, blk_diffs

    def cal_score(self, blk_diffs):
        # Block Order Difference
        blk_diff_m = 0
        for item in blk_diffs:
            if item < 0:
                blk_diff_m = blk_diff_m + abs(item)
        score = blk_diff_m
        return score

    def get_score(self, df):
        df = self.subprocess(df)
        out_1 = self.cal_schedule_part_1(df)
        out_2 = self.cal_schedule_part_2(df, line="A")
        out_3 = self.cal_schedule_part_2(df, line="B")
        out = out_1 + out_2 + out_3
        out = self.add_stock(out, self.df_stock)
        order = self.order_rescale(out, self.df_order)
        out, blk_diffs = self.cal_stock(out, order)
        score = self.cal_score(blk_diffs)
        return score, out


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--order_path", default="data/order.csv")
    parser.add_argument("--stock_path", default="data/stock.csv")
    args = parser.parse_args()

    env = custor_Env(args)

    state = env.reset()

    # print(f"state : {state}")

    action = np.random.randint(10, size=(24, 8))
    # print(f"action : {action}")

    s, r, d, i = env.step(action)

    # print(f"s : {s} ")
    # print(f"submission : {i['submission']} ")

    score, out = env.get_score(i["submission"])

    print(out)
    print(score)
