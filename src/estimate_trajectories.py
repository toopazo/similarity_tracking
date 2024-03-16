"""_summary_
"""

import numpy as np
import pandas as pd
import random
import matplotlib.pyplot as plt
from generate_trajectories import TraGen
from munkres import Munkres, print_matrix


class TraEstim:
    def __init__(self, num_trajectories: int, num_samples: int) -> None:
        estim_traj = TraGen(num_trajectories, num_samples)
        estim_traj.plot_pos_trajectory()
        estim_traj.plot_des_trajectory()

        pos_obs, des_obs = self._trajectories_to_observations(estim_traj)
        self.pos_obs = pos_obs
        self.des_obs = des_obs

        self.munkres = Munkres()

        print("--- check observations")
        # obs  = matrix[trajectories, samples, dimensions]
        obs1 = pos_obs[:, 1, :]
        obs0 = pos_obs[:, 0, :]
        # obs1 = des_obs[1, :, :]
        # obs0 = des_obs[0, :, :]
        print(obs1)
        print(obs0)
        print(obs1.shape)
        print(obs0.shape)
        delta = self.delta_obs(obs1, obs0, op="norm")
        # delta = self.delta_obs(obs1, obs0, op="")
        print(delta)
        print(delta.shape)

        print("--- check trajectories")
        traj0_pos0 = estim_traj.data[0][estim_traj.key_pos_list][0]
        traj0_pos1 = estim_traj.data[0][estim_traj.key_pos_list][1]
        print(traj0_pos0)
        print(traj0_pos1)
        print(traj0_pos1 - traj0_pos0)
        print(np.linalg.norm(traj0_pos1 - traj0_pos0))

        # transitions = self.chose_predecessor(obs1, obs0, op="norm")
        transitions = self.chose_predecessor(obs1, obs0, op="hungarian")
        print(transitions)
        # print(transitions[:, 0])
        print(transitions.shape)

        estim_traj = self.estimate_trajectories(observations=pos_obs, op="hungarian")
        # estim_traj = self.estimate_trajectories(observations=des_obs, op="hungarian")
        print(estim_traj)
        print(estim_traj.shape)

        self.plot_estimated_trajectories(pos_obs, estim_traj)

    def plot_estimated_trajectories(
        self, observations: np.ndarray, estim_traj: np.ndarray
    ) -> None:
        print(self.plot_estimated_trajectories.__name__)

        mshape = estim_traj.shape
        assert len(mshape) == 2
        num_bboxes_estim = mshape[0]
        num_samples_estim = mshape[1]

        mshape = observations.shape
        assert len(mshape) == 3
        num_bboxes_obs = mshape[0]
        num_samples_obs = mshape[1]
        vector_dimension_obs = mshape[2]

        assert num_bboxes_estim == num_bboxes_obs
        assert num_samples_estim == (num_samples_obs - 1)
        assert vector_dimension_obs == 2

        fig, ax = plt.subplots()

        pos_dict = {}
        for si in range(0, num_samples_estim):
            bboxes_order = estim_traj[:, si]
            for bi in range(0, num_bboxes_estim):
                bi_estim = bboxes_order[bi]
                # print(bi_estim)
                bi_estim = int(bi_estim)
                vector = observations[bi_estim, si, :].squeeze()
                x = vector[0]
                y = vector[1]
                if bi in pos_dict.keys():
                    pos_dict[bi]["x_list"].append(x)
                    pos_dict[bi]["y_list"].append(y)
                else:
                    pos_dict[bi] = {"x_list": [x], "y_list": [y]}

        for k, v in pos_dict.items():
            _ = k
            x_list = v["x_list"]
            y_list = v["y_list"]
            ax.plot(x_list, y_list, "-*")

        ax.set(
            xlabel="x position",
            ylabel="y position",
            # title=f"Starting point {self.pos0}",
            xlim=[0, 10],
            ylim=[0, 10],
        )
        ax.grid()

        fig.savefig("plot_estimated_trajectories.png")
        # plt.show()

    def estimate_trajectories(self, observations: np.ndarray, op: str) -> np.array:
        print(self.estimate_trajectories.__name__)

        # observarions = matrix[trajectories, samples, dimensions] = matrix[bboxes, samples, dimensions]
        # estim_traj = matrix[bboxes, samples, dimensions]

        num_bboxes = observations.shape[0]
        num_samples = observations.shape[1]
        # vector_dimension = observations.shape[2]

        estim_traj = np.zeros((num_bboxes, num_samples - 1))
        for si in range(1, num_samples):
            obs1 = observations[:, si, :]
            obs0 = observations[:, si - 1, :]
            transitions = self.chose_predecessor(obs1, obs0, op=op)
            print("transitions")
            print(transitions)
            # print(transitions.shape)

            previous_bbox = transitions[:, 0]
            print(previous_bbox)
            estim_traj[:, si - 1] = previous_bbox

        return np.array(estim_traj)

    def chose_predecessor(self, obs1: np.ndarray, obs0: np.ndarray, op: str) -> list:
        if op == "norm":
            return self.chose_predecessor_norm(obs1, obs0)
        elif op == "hungarian":
            return self.chose_predecessor_hungarian(obs1, obs0)
        else:
            raise RuntimeError

    def chose_predecessor_hungarian(
        self, obs1: np.ndarray, obs0: np.ndarray
    ) -> np.array:
        delta = self.delta_obs(obs1, obs0, op="norm")

        num_bboxes1 = obs1.shape[0]
        num_bboxes0 = obs0.shape[0]
        # dimensions = obs0.shape[1]

        # (num_bboxes1, dimensions) = (3, 2)
        # delta = [
        # (0,0) -> [1.18309052]
        # (0,1) -> [0.76686364]
        # (0,2) -> [0.54153291]
        # (1,0) -> [1.23593586]
        # (1,1) -> [0.36863534]
        # (1,2) -> [0.36099176]
        # (2,0) -> [2.02243821]
        # (2,1) -> [1.16541725]
        # (2,2) -> [1.22167423]
        # ]

        #  delta = matrix[bboxes1, bboxes0]
        # delta = [
        # (0,0) -> [1.18309052]    (1,0) -> [1.23593586]    (2,0) -> [2.02243821]
        # (0,1) -> [0.76686364]    (1,1) -> [0.36863534]    (2,1) -> [1.16541725]
        # (0,2) -> [0.54153291]    (1,2) -> [0.36099176]    (2,2) -> [1.22167423]
        # ]

        matrix = delta.squeeze().reshape(num_bboxes0, num_bboxes1)
        matrix = np.transpose(matrix)

        # print(delta)
        # print(matrix)

        transition_list = []

        indexes = self.munkres.compute(matrix)
        # print_matrix(matrix, msg="Lowest cost through this matrix:")
        total = 0
        for row, column in indexes:
            value = matrix[row][column]
            total += value
            # print(f"({row}, {column}) -> {value}")

            chosen_tuple = (column, row)
            transition_list.append(chosen_tuple)
        # print(f"total cost: {total}")

        return np.array(transition_list)

    def chose_predecessor_norm(self, obs1: np.ndarray, obs0: np.ndarray):
        delta = self.delta_obs(obs1, obs0, op="norm")

        num_bboxes1 = obs1.shape[0]
        # num_bboxes0 = obs0.shape[0]
        # dimensions = obs0.shape[1]

        # (num_bboxes1, dimensions) = (3, 2)
        # delta = [
        # (0,0) -> [1.18309052]
        # (0,1) -> [0.76686364]
        # (0,2) -> [0.54153291]
        # (1,0) -> [1.23593586]
        # (1,1) -> [0.36863534]
        # (1,2) -> [0.36099176]
        # (2,0) -> [2.02243821]
        # (2,1) -> [1.16541725]
        # (2,2) -> [1.22167423]
        # ]

        transition_list = []
        for obs1_i in range(0, num_bboxes1):
            i0 = obs1_i * num_bboxes1
            i1 = obs1_i * num_bboxes1 + num_bboxes1
            sub_delta = delta[i0:i1].squeeze()
            # print(f"i0 {i0}")
            # print(f"i1 {i1}")
            # print(f"sub_delta")
            # print(sub_delta)
            i = obs1_i
            j = np.argmin(sub_delta)
            # print(j)
            chosen_tuple = (j, i)
            transition_list.append(chosen_tuple)

        return np.array(transition_list)

    def delta_obs(self, obs1: np.ndarray, obs0: np.ndarray, op: str) -> np.array:
        # observarions = matrix[trajectories, samples, dimensions] = matrix[bboxes, samples, dimensions]
        # obs1 = matrix[trajectories, 1, dimensions] = matrix[trajectories, dimensions] = matrix[bboxes, dimensions]
        # obs0 = matrix[trajectories, 0, dimensions] = matrix[trajectories, dimensions] = matrix[bboxes, dimensions]
        # delta = matrix[bboxes1 * bboxes0, dimensions]
        assert len(obs1.shape) == 2
        assert len(obs0.shape) == 2
        num_bboxes1 = obs1.shape[0]
        num_bboxes0 = obs0.shape[0]
        dimensions = obs0.shape[1]

        if op == "norm":
            delta = np.zeros((num_bboxes1 * num_bboxes0, 1))
        elif op == "substract":
            delta = np.zeros((num_bboxes1 * num_bboxes0, dimensions))
        else:
            raise RuntimeError

        cnt = 0
        for obs1_i in range(0, num_bboxes1):
            vi = obs1[obs1_i, :].squeeze()
            # print(vi.shape)
            assert len(vi.shape) == 1
            assert len(vi) == dimensions

            for obs0_j in range(0, num_bboxes0):
                vj = obs0[obs0_j, :].squeeze()
                # print(vj.shape)
                assert len(vj.shape) == 1
                assert len(vj) == dimensions

                delta_ij = vi - vj
                # print(delta_ij.shape)

                if op == "norm":
                    delta[cnt, :] = np.linalg.norm(delta_ij)
                elif op == "substract":
                    delta[cnt, :] = delta_ij
                else:
                    raise RuntimeError
                cnt += 1

        return delta

    def _trajectories_to_observations(self, traj: TraGen) -> tuple:
        # self.data[ti] = {
        #     self.key_pos0: pos0,
        #     self.key_pos_list: pos_list,
        #     self.key_des_list: des_list,
        # }

        print(self._trajectories_to_observations.__name__)

        num_samples = traj.num_samples
        num_trajectories = traj.num_trajectories
        pos_len = traj.pos_len
        des_len = traj.des_len

        for ti in range(0, num_trajectories):
            v = traj.data[ti]
            traj.print_trajectory(v)

        # print(traj.data.keys())
        # pos_obs = []
        # des_obs = []
        pos_obs = np.zeros((num_trajectories, num_samples, pos_len))
        des_obs = np.zeros((num_trajectories, num_samples, des_len))
        for ti in range(0, num_trajectories):
            v = traj.data[ti]
            pos_list = v[traj.key_pos_list]
            des_list = v[traj.key_des_list]
            for si in range(0, num_samples):
                pos = pos_list[si]
                for di in range(0, pos_len):
                    pos_obs[ti, si, di] = pos[di]

                des = des_list[si]
                for di in range(0, des_len):
                    des_obs[ti, si, di] = des[di]

                # pos_obs.append(pos_list[si])
                # des_obs.append(des_list[si])
        # pos_obs = np.array(pos_obs)
        print("x obs")
        print(pos_obs[:, :, 0])
        print("y obs")
        print(pos_obs[:, :, 1])
        print(pos_obs.shape)

        print("des obs along 1st dim")
        print(des_obs[:, :, 0])
        print(des_obs.shape)

        return pos_obs, des_obs


if __name__ == "__main__":
    tg = TraEstim(num_trajectories=3, num_samples=15)
