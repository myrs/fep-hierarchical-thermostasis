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

    def __init__(self, s_z_0=0.1, s_z_1=0.1, s_w_0=0.1, s_w_1=0.1):
        # sigma (variances)
        self.s_z_0 = s_z_0
        self.s_z_1 = s_z_1
        self.s_w_0 = s_w_0
        self.s_w_1 = s_w_1

        # learning rate
        self.learn_r = 0.1
        self.dt = 0.005
        self.T0 = 100
        self.temp_desire = 4

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

        # world
        self.temp = []
        self.d_temp_d_pos = []

        # position and velocity
        self.pos = [2]
        self.velocity = [0]

        # action
        self.action = [0]

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
        pos = self.pos[-1] + self.velocity[-1]
        self.pos.append(pos)

    def upd_temp(self):
        self.temp.append(temp_at_pos(self.T0, self.pos[-1]))

    def upd_d_temp_d_pos(self):
        self.d_temp_d_pos.append(d_temp_d_pos(self.T0, self.pos[-1]))

    def upd_err_z_0(self):
        # error between sensation and generated sensations
        self.e_z_0.append(self.sense[-1] - self.mu[-1])

    def upd_err_z_1(self):
        # error between first derivatives of sensation and generated sensations
        self.e_z_1.append(self.sense_d1[-1] - self.mu_d1[-1])

    def upd_err_w_0(self):
        # error between model and generation of model
        # here: model of dynamics at 1st derivative
        # and it's generation for the 1st derivative
        self.e_w_0.append(self.mu_d1[-1] + self.mu[-1] - self.temp_desire)

    def upd_err_w_1(self):
        # error between model and generation of model
        # here: model of dynamics at 2nd derivative)
        # and it's generation for the 2nd derivative
        self.e_w_1.append(self.mu_d2[-1] + self.mu_d1[-1])

    def upd_mu_d2(self):
        upd = -self.learn_r * (self.e_w_1[-1] / self.s_w_1)
        self.mu_d2.append(self.mu_d2[-1] + upd)

    def upd_mu_d1(self):
        upd = -self.learn_r * (-self.e_z_1[-1] / self.s_z_1 +
                               self.e_w_0[-1] / self.s_w_0 + self.e_w_1[-1] / self.s_w_1)
        upd += self.mu_d2[-2]


        self.mu_d1.append(self.mu_d1[-1] + upd)

    def upd_mu(self):
        upd = -self.learn_r * \
            (-self.e_z_0[-1] / self.s_z_0 + self.e_w_0[-1] / self.s_w_0)
        upd += self.mu_d1[-2] 

        self.mu.append(self.mu[-1] + upd)

    def upd_vfe(self):
        def sqrd_err(err, sigma):
            return np.power(err, 2) / sigma

        vfe = 0.5 * (sqrd_err(self.e_z_0[-1], self.s_z_0) + sqrd_err(self.e_z_1[-1], self.s_z_1) +
                     sqrd_err(self.e_w_0[-1], self.s_w_0) + sqrd_err(self.e_w_1[-1], self.s_w_1))

        self.vfe.append(vfe)

    def upd_action(self):
        upd = -self.learn_r * self.d_temp_d_pos[-1] * (self.e_z_1[-1] / self.s_z_1)
        # print(upd)
        # update interpretation 
        self.action.append(self.action[-1] + upd)
        # action interpretation
        # self.action.append(upd)

    def upd_velocity(self):
        # for this simple agent velocity is just action
        self.velocity.append(self.action[-1])

    def simulate_perception(self, steps_n=1000, act_at=200):

        self.reset()

        steps = range(steps_n)

        for step in range(steps_n):
            # update world
            self.upd_temp()
            #   --> update temperature gradient
            self.upd_d_temp_d_pos()

            # generate sensations
            self.generate_sense()
            self.generate_sense_d1()

            # update perception
            #   --> update errors
            self.upd_err_z_0()
            self.upd_err_z_1()
            self.upd_err_w_0()
            self.upd_err_w_1()

            #  --> update recognition dynamics
            self.upd_mu_d2()
            self.upd_mu_d1()
            self.upd_mu()

            #  update agent after step act_at
            if step > act_at:
                self.upd_action()
                self.upd_velocity()
                self.upd_position()
            
            else:
                # if agent is not acting update it's variables anyway
                self.action.append(self.action[-1])
                self.velocity.append(self.velocity[-1])
                self.pos.append(self.pos[-1])

            #  update free energy
            self.upd_vfe()

        fig, ax = plt.subplots(6, 1, constrained_layout=True)

        ax[0].plot(steps, self.mu[1:])
        ax[0].plot(steps, self.mu_d1[1:])
        ax[0].plot(steps, self.mu_d2[1:])
        ax[0].set_title('mu change over iteration')
        ax[0].legend(['mu', 'mu\'', 'mu\'\''])

        ax[1].plot(steps, self.vfe)
        ax[1].set_title('VFE change over iteration')

        ax[2].plot(steps, self.temp)
        # ax[2].plot(steps, self.pos[1:])
        ax[2].plot(steps, self.velocity[1:])
        ax[2].legend(['temperature', 'velocity'])
        ax[2].set_title('Temperature and velocity')

        ax[3].plot(steps, self.e_z_1)

        ax[4].plot(steps, self.d_temp_d_pos)

        ax[5].plot(steps, self.pos[1:])

        plt.show()
