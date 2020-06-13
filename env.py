import numpy as np


class custor_Env():
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

    def __init__(self):
        self.state = None
        self.action = None
        self.state_dim = (16,)
        self.action_dim = (24, 8)

    def reset(self):
        self.state = np.random.randint(low=0, high=1, size=self.state_dim)
        return np.array(self.state)

    def step(self, action):

        self.state = self.process(self.state, action)

        reward = 0
        done = False
        return self.state, reward, done, {}

    def process(self, state, action):

        return np.random.randint(low=0, high=1, size=self.state_dim)


if __name__ == '__main__':

    env = custor_Env()
    state = env.reset()
    print(f"state : {state}")

    action = np.random.randint((24*8))
    print(f"action : {action}")

    s, r, d, i = env.step(action)
    print(f"s r d i: {s} {r} {d} {i}")
