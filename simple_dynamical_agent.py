# a simple agent using dynamical generative model of FEP
# as described in The FEP for action and perception
import numpy as np
from matplotlib import pyplot as plt


def temp_at_pos(T0, v):
    return T0 / (np.power(v, 2) + 1)


def d_temp_d_pos(T0, v):
    return -T0 * 2 * v / (np.power(np.power(v, 2) + 1, 2))


def plot_temp_pos():
    x = np.linspace(0, 6, 100)
    y = [temp_at_pos(100, x_) for x_ in x]
    y_d = [d_temp_d_pos(100, x_) for x_ in x]

    plt.plot(x, y)
    plt.plot(x, y_d)
    plt.legend(['temperature(position)', 'd temperature / d position'])


class World:

    def __init__(self, s_z_0=0.1, s_z_1=0.1, s_w_0=10, s_w_1=10):
        # sigma (variances)
        self.s_z_0 = s_z_0
        self.s_z_1 = s_z_1
        self.s_w_0 = s_w_0
        self.s_w_1 = s_w_1

        # learning rate
        self.learn_r = 0.01
        self.T0 = 100
        self.temp_desire = 0

        self.reset()

    def reset(self):
        # errors
        self.e_z_0 = []
        self.e_z_1 = []
        self.e_w_0 = []
        self.e_w_1 = []

        # senses
        self.sense = []
        self.sense_d1 = []

        # position and velocity
        self.pos = [2]
        self.velocity = [0]

        # brain state mu
        self.mu = [0]
        self.mu_d1 = [0]
        self.mu_d2 = [0]

        # variational free energy
        self.vfe = []

    def generate_sense(self):
        sense = temp_at_pos(self.T0, self.pos[-1]) + np.random.normal()
        self.sense.append(sense)

    def generate_sense_d1(self):
        """ change in sensation """
        sense_d1 = d_temp_d_pos(self.T0, self.pos[-1]) * \
            self.velocity[-1] + np.random.normal()
        
        self.sense_d1.append(sense_d1)

    def upd_position(self):
        # TODO here add action or outside
        pos = self.pos[-1] + self.velocity
        self.pos.append(pos)

    def upd_temperature(self):
        self.temp = temp_at_pos(self.T0, self.pos)

    def upd_err_z_0(self):
        # error between sensation and generated sensations
        self.e_z_0.append(self.sense[-1] - self.mu[-1])

    def upd_err_z_1(self):
        # d1 of error between sensation and generated sensations
        self.e_z_1.append(self.sense_d1[-1] - self.mu_d1[-1])

    def upd_err_w_0(self):
        # error between model and generation of model
        # here: model of dynamics (1st derivative)
        # and it's generation for the 1st derivative
        self.e_w_0.append(self.mu_d1[-1] + self.mu[-1] - self.temp_desire)

    def upd_err_w_1(self):
        # error between model and generation of model
        # here: model of dynamics (1st derivative)
        # and it's generation for the 1st derivative
        self.e_w_1.append(self.mu_d2[-1] + self.mu_d1[-1])

    def upd_mu_d2(self):
        upd = -self.learn_r * (self.e_w_1[-1] / self.s_w_1)
        self.mu_d2.append(self.mu_d2[-1] + upd)

    def upd_mu_d1(self):
        upd = -self.learn_r * (-self.e_z_1[-1] / self.s_z_1 +
                               self.e_w_0[-1] / self.s_w_0 + self.e_w_1[-1] / self.s_w_1)
        self.mu_d1.append(self.mu_d1[-1] + upd)

    def upd_mu(self):
        upd = -self.learn_r * \
            (-self.e_z_0[-1] / self.s_z_0 + self.e_w_0[-1] / self.s_w_0)
        self.mu.append(self.mu[-1] + upd)

    def upd_vfe(self):
        def sqrd_err(err, sigma):
            return np.power(err, 2) / sigma

        vfe = 0.5 * (sqrd_err(self.e_z_0[-1], self.s_z_0) + sqrd_err(self.e_z_1[-1], self.s_z_1) +
                     sqrd_err(self.e_w_0[-1], self.s_w_0) + sqrd_err(self.e_w_1[-1], self.s_w_1))

        self.vfe.append(vfe)

    def simulate_perception(self, steps_n=200):

        self.reset()

        steps = range(steps_n)

        for i in range(steps_n):
            # generate sensations
            self.generate_sense()
            self.generate_sense_d1()

            # update perception
            #   --> update errors
            self.upd_err_z_0()
            self.upd_err_z_1()
            self.upd_err_w_0()
            self.upd_err_w_1()

            #   --> update recognition dynamics
            self.upd_mu_d2()
            self.upd_mu_d1()
            self.upd_mu()

            #   --> update free energy
            self.upd_vfe()

            # print(self.vfe[-1])

        # print('Final')
        # print(self.mu[-1])
        # print(self.mu_d1[-1])
        # print(self.mu_d2[-1])

        fig, ax = plt.subplots(2, 1, constrained_layout=True)

        ax[0].plot(steps, self.mu[1:])
        ax[0].plot(steps, self.mu_d1[1:])
        ax[0].plot(steps, self.mu_d2[1:])

        ax[0].set_title('mu change over iteration')

        ax[0].legend(['mu', 'mu\'', 'mu\'\''])

        ax[1].plot(steps, self.vfe)
        ax[1].set_title('VFE change over iteration')

        plt.show()