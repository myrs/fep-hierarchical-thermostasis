# a simple agent using dynamical generative model of FEP
# that can control it's own temperature
# directly
import numpy as np
from matplotlib import pyplot as plt


def get_noise():
    return np.random.normal() * 0.1


class TermosatWorld:

    def __init__(self, s_z_0=0.1, s_z_1=0.1, s_w_0=0.1, s_w_1=0.1,
                 action_bound=5.8, temp_const_change_initial=0,
                 temp_viable_range=10):
        # sigma (variances)
        self.s_z_0 = s_z_0
        self.s_z_1 = s_z_1
        self.s_w_0 = s_w_0
        self.s_w_1 = s_w_1

        # learning rate
        self.learn_r = 0.1
        self.learn_r_a = 0.1
        # 0.5 will produce too much noise
        self.dt = 0.1
        self.T0 = 36
        self.temp_desire = 36
        self.temp_viable_range = temp_viable_range

        # action bound -- agent can't set action more or less than this
        self.action_bound = action_bound
        self.temp_const_change_initial = temp_const_change_initial

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
        # start with temperature at T0
        self.temp = [self.T0]

        # position and temp_change
        # self.temp_change = [0]

        # action
        self.action = [0]
        # temperature change set by action
        # TODO here should be some non-linearity!
        self.temp_change = [0]
        self.temp_const_change = [self.temp_const_change_initial]
        self.temp_relative_change = [0]

        # brain state mu
        self.mu = [0]
        self.mu_d1 = [0]
        self.mu_d2 = [0]

        # variational free energy
        self.vfe = []

    def generate_sense(self):
        sense = self.temp[-1] + get_noise()
        self.sense.append(sense)

    def generate_sense_d1(self):
        """ change in sensation is felt change in temperature """
        sense_d1 = self.temp_change[-1] + get_noise()

        self.sense_d1.append(sense_d1)

    def update_world(self):
        """ update world parameters (temperature, T0)
            an agent lives in """

        # an agent lives in a world where the temperature changes
        # over time
        # it rises during first 50 steps
        # then stays the same during next 50 steps
        # and lowers strongly during next 50 steps

        # this is to show an agent won't survive just with
        # and autonomic reflex

        if self.time == 10:
            temp_const_change = 2
        elif self.time == 50:
            temp_const_change = 5
        elif self.time == 100:
            temp_const_change = -1
        elif self.time == 150:
            temp_const_change = -6
        elif self.time == 200:
            temp_const_change = 0
        else:
            temp_const_change = self.temp_const_change[-1]

        relative_change = self.temp_const_change[-1] - temp_const_change
        self.temp_relative_change.append(relative_change)

        self.temp_const_change.append(temp_const_change)

    def upd_temp(self):
        # update temperature with the current temperature update
        upd = self.temp_change[-1]
        upd *= self.dt

        self.temp.append(self.temp[-1] + upd)

    def upd_temp_change(self):
        # for this simple agent temp_change is just action
        # update temperature by constant (e.g. world is heating constantly)
        upd = self.temp_const_change[-1]
        upd += self.action[-1]

        self.temp_change.append(upd)

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
        upd *= self.dt

        self.mu_d2.append(self.mu_d2[-1] + upd)

    def upd_mu_d1(self):
        upd = -self.learn_r * (-self.e_z_1[-1] / self.s_z_1 +
                               self.e_w_0[-1] / self.s_w_0 + self.e_w_1[-1] / self.s_w_1)
        upd += self.mu_d2[-2]
        upd *= self.dt

        self.mu_d1.append(self.mu_d1[-1] + upd)

    def upd_mu(self):
        upd = -self.learn_r * \
            (-self.e_z_0[-1] / self.s_z_0 + self.e_w_0[-1] / self.s_w_0)
        upd += self.mu_d1[-2]
        upd *= self.dt

        self.mu.append(self.mu[-1] + upd)

    def upd_vfe(self):
        def sqrd_err(err, sigma):
            return np.power(err, 2) / sigma

        vfe = 0.5 * (sqrd_err(self.e_z_0[-1], self.s_z_0) + sqrd_err(self.e_z_1[-1], self.s_z_1) +
                     sqrd_err(self.e_w_0[-1], self.s_w_0) + sqrd_err(self.e_w_1[-1], self.s_w_1))

        self.vfe.append(vfe)

    def upd_action(self):
        # sensation change over action is always 1
        upd = -self.learn_r_a * 1 * (self.e_z_1[-1] / self.s_z_1)
        upd *= self.dt
        action = self.action[-1] + upd

        # action must be bound by some plausible constraints
        # e.g. temperature can't change more than action bound at each timestep
        if abs(action) > self.action_bound:
            action = np.sign(action) * self.action_bound

        # update action
        self.action.append(action)

    def simulate_perception(self, sim_time=100, act_time=25):

        self.reset()

        plt.ion()

        steps = int(sim_time / self.dt)
        print(steps)

        for step in range(steps):
            self.time = int(step * self.dt)
            # update world
            self.update_world()
            self.upd_temp()

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

            self.upd_temp_change()

            #  update agent after step act_at
            if step * self.dt > act_time:
                self.upd_action()

            else:
                # if agent is not acting update it's variables anyway
                self.action.append(self.action[-1])

            #  update free energy
            self.upd_vfe()

        fig, ax = plt.subplots(3, 2, constrained_layout=True)

        timeline = [s * self.dt for s in range(steps)]

        ax[0][0].plot(timeline, self.temp[1:])
        ax[0][0].set_title('Organism temperature')
        min_temp = self.temp_desire - self.temp_viable_range
        max_temp = self.temp_desire + self.temp_viable_range
        ax[0][0].plot(timeline, np.ones_like(timeline) *
                      min_temp, lw=0.75, ls='--', c='red')
        ax[0][0].plot(timeline, np.ones_like(timeline) *
                      max_temp, lw=0.75, ls='--', c='red')
        ax[0][0].legend(['temperature', 'viable'], loc='upper right')

        ax[1][0].plot(timeline, self.temp_change[1:])
        ax[1][0].plot(timeline, np.zeros_like(timeline), lw=0.75, ls='--')
        ax[1][0].set_title('Organism temperature change')

        ax[2][0].plot(timeline, self.temp_const_change[1:])
        ax[2][0].plot(timeline, self.action[1:])
        diff = np.array(self.temp_const_change[1:]) + np.array(self.action[1:])
        ax[2][0].plot(timeline, diff, lw=0.75, ls='--')
        ax[2][0].legend(['temp change', 'action', 'diff'], loc='upper right')
        ax[2][0].set_title('External temperature change and action')

        ax[0][1].plot(timeline, self.mu[1:])
        ax[0][1].plot(timeline, self.mu_d1[1:])
        ax[0][1].plot(timeline, self.mu_d2[1:])
        ax[0][1].set_title('mu over time')
        ax[0][1].legend(['mu', 'mu\'', 'mu\'\''], loc='upper right')

        ax[1][1].plot(timeline, self.vfe)
        ax[1][1].set_title('VFE')
        ax[1][1].set_ylim(-0.1, 500)

        ax[2][1].plot(timeline, self.e_z_0)
        ax[2][1].plot(timeline, self.e_z_1)
        ax[2][1].plot(timeline, self.e_w_0)
        ax[2][1].plot(timeline, self.e_w_1)
        ax[2][1].set_ylim(-10, 10)
        ax[2][1].set_title('Error')
        ax[2][1].legend(['e_z_0', 'e_z_1', 'e_w_0', 'e_w_1'], loc='upper right')

        plt.show()
