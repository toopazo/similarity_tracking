"""_summary_
"""

import numpy as np
import pandas as pd
import random
import matplotlib.pyplot as plt

# math.random() static method returns a floating-point, pseudo-random number that's greater than or equal to 0 and less than 1,


class TraGen:
    def __init__(self, num_trajectories: int, num_samples: int) -> None:

        self.max_x = 10
        self.max_y = 10
        self.max_vel = 2

        self.key_pos_list = "pos"
        self.key_des_list = "des"

        self.num_trajectories = num_trajectories
        self.num_samples = num_samples
        self.pos_len = 2
        self.des_len = 4

        self.data = {}
        for ti in range(0, num_trajectories):
            pos_step = [random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5)]
            pos0 = np.array([1, 2]) + pos_step
            pos_list = [pos0]

            # des0 = np.array([ti + 1, ti + 1, ti + 1])
            des0 = np.ones((self.des_len)) * (ti + 1)
            des_list = [des0]

            pos = pos0
            for si in range(1, num_samples):
                pos_step = np.array(
                    [1.5 * random.uniform(-0.2, 0.8), 1.5 * random.uniform(-0.2, 0.8)]
                )
                pos = pos + pos_step
                pos_list.append(pos)

                des_step = random.uniform(-0.1, 0.1) * 2
                des_step = des0 + des_step
                des_list.append(des_step)

                _ = si

            self.data[ti] = {
                self.key_pos_list: pos_list,
                self.key_des_list: des_list,
            }

    def print_trajectory(self, data: dict) -> None:
        pos_list = data[self.key_pos_list]
        des_list = data[self.key_des_list]
        ndec = 4
        print(f"pos traj {[(round(e[0], ndec), round(e[1], ndec)) for e in pos_list]}")
        # print(f"des traj {des_list}")

    def plot_pos_trajectory(self):
        # print(self.data)

        fig, ax = plt.subplots()

        for i in range(0, self.num_trajectories):
            x_list = []
            y_list = []
            datai = self.data[i]
            pos_list = datai[self.key_pos_list]
            for xy in pos_list:
                x_list.append(xy[0])
                y_list.append(xy[1])

            ax.plot(x_list, y_list, "-*")

        ax.set(
            xlabel="x position",
            ylabel="y position",
            # title=f"Starting point {self.pos0}",
            xlim=[0, self.max_x],
            ylim=[0, self.max_y],
        )
        ax.grid()

        fig.savefig("plot_pos_trajectory.png")
        # plt.show()

    def plot_des_trajectory(self):
        # print(self.data)

        fig, ax = plt.subplots()

        for i in range(0, self.num_trajectories):

            datai = self.data[i]
            des_list = datai[self.key_des_list]

            norm_list = []
            for des in des_list:
                norm_list.append(np.linalg.norm(des))

            sample_list = list(range(0, self.num_samples))
            ax.plot(sample_list, norm_list, "-*")

        ax.set(
            xlabel="i-th sample",
            ylabel="des norm",
            # title=f"Starting point {self.pos0}",
            xlim=[0, self.num_samples],
            ylim=[0, self.num_trajectories * 3],
        )
        ax.grid()

        fig.savefig("plot_des_trajectory.png")
        # plt.show()


if __name__ == "__main__":
    tg = TraGen(3, 5)
    tg.plot_pos_trajectory()
    tg.plot_des_trajectory()
