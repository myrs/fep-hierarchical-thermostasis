# a simple agent using dynamical generative model of FEP
# that can control it's own temperature
# directly
import numpy as np
from matplotlib import pyplot as plt


def get_noise():
    return np.random.normal() * 0.1


class InteroceptiveAgent:
    """Interoceptive agent that acts upon the interoceptive
       information only (temperature and temperature change)"""

    def __init__(self, s_z_0=0.1, s_z_1=0.1, s_w_0=0.1, s_w_1=0.1,
                 action_bound=5.8, temp_const_change_initial=0,
                 temp_viable_range=10, dt=0.1, learn_r=0.1):
        # sigma (variances)
        self.s_z_0 = s_z_0
        self.s_z_1 = s_z_1
        self.s_w_0 = s_w_0
        self.s_w_1 = s_w_1

        # learning rate
        self.learn_r = learn_r
        self.learn_r_a = self.learn_r
        # 0.5 will produce too much noise
        self.dt = dt
        self.T0 = 30
        self.temp_viable_mean = 30
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

        # action
        self.action = [0]
        # temperature change set by action
        # TODO here should be some non-linearity!
        self.temp_change = [0]
        self.temp_const_change = [self.temp_const_change_initial]
        self.temp_relative_change = [0]
        self.temp_desire = [self.temp_viable_mean]

        # brain state mu
        self.mu = [0]
        self.mu_d1 = [0]
        self.mu_d2 = [0]

        # variational free energy
        self.vfe = []

    def generate_senses(self):
        self.generate_sense()
        self.generate_sense_d1()

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

        if self.time == 50:
            temp_const_change = 2
        elif self.time == 100:
            temp_const_change = 5
        elif self.time == 150:
            temp_const_change = -1
        elif self.time == 200:
            temp_const_change = -6
        elif self.time == 250:
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
        self.e_w_0.append(self.mu_d1[-1] + self.mu[-1] - self.temp_desire[-1])

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

        vfe = 0.5 * (sqrd_err(self.e_z_0[-1], self.s_z_0) +
                     sqrd_err(self.e_z_1[-1], self.s_z_1) +
                     sqrd_err(self.e_w_0[-1], self.s_w_0) +
                     sqrd_err(self.e_w_1[-1], self.s_w_1))

        self.vfe.append(vfe)

    def upd_action(self):
        # TODO action is noisy! Add noise here but not forget about integration
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

    def upd_no_action(self):
        # if agent is not acting update it's variables anyway
        self.action.append(self.action[-1])

    def interoception(self):
        # update interoception
        #   --> update errors
        self.upd_err_z_0()
        self.upd_err_z_1()
        self.upd_err_w_0()
        self.upd_err_w_1()

        #  --> update recognition dynamics
        self.upd_mu_d2()
        self.upd_mu_d1()
        self.upd_mu()

        #  update free energy
        self.upd_vfe()

    def active_inference(self):
        self.temp_desire.append(self.temp_viable_mean)
        self.interoception()

    def plot_results(self):
        fig, ax = plt.subplots(3, 2, constrained_layout=True)

        timeline = [s * self.dt for s in range(self.steps)]

        ax[0][0].plot(timeline, self.temp[1:])
        ax[0][0].plot(timeline, self.temp_desire[1:], ls='--', lw=0.75, c='green')
        ax[0][0].set_title('Organism temperature')
        min_temp = self.temp_viable_mean - self.temp_viable_range
        max_temp = self.temp_viable_mean + self.temp_viable_range
        ax[0][0].plot(timeline, np.ones_like(timeline) *
                      min_temp, lw=0.75, ls='--', c='red')
        ax[0][0].plot(timeline, np.ones_like(timeline) *
                      max_temp, lw=0.75, ls='--', c='red')
        ax[0][0].legend(['temp', 'desired temp', 'viable range'], loc='lower left')
        ax[0][0].set_ylim(10, 45)

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

    def simulate(self, sim_time=300, act_time=50):
        self.reset()

        plt.ion()

        self.steps = int(sim_time / self.dt)
        print(f'Simulating {self.steps} steps')

        for step in range(self.steps):
            self.time = int(step * self.dt)
            # update world
            self.update_world()
            self.upd_temp_change()
            self.upd_temp()

            # generate sensations
            self.generate_senses()

            # perform active inference
            self.active_inference()

            #  act
            if step * self.dt > act_time:
                self.upd_action()

            else:
                self.upd_no_action()

        self.plot_results()


class MockExteroceptiveAgent(InteroceptiveAgent):
    """Proof of concept of the exteroceptive agent:
       desired temperature is set directly"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def exteroception(self):
        # an agent sets it's desired temperature
        # based on exteroception
        # mocking exteroceptive inference
        if self.time >= 120 and self.time <= 200:
            # set the temperature high enough to survive upcoming cold
            self.temp_desire.append(self.temp_viable_mean + 7)
        else:
            self.temp_desire.append(self.temp_viable_mean)

    def active_inference(self):
        # update exteroception
        self.exteroception()
        self.interoception()


class ExteroceptiveAgent(InteroceptiveAgent):
    """Exteroceptive agent that infers the desired temperature
       and passes it down to the interoceptive layer"""

    def __init__(self, ex_s_z_0=0.01, ex_s_w_0=100000, **kwargs):
        # variance is set to be very high for internal model
        # as it does not matter in this case
        super().__init__(**kwargs)

        self.learn_r_ex = self.learn_r

        # sigma (variances)
        self.ex_s_z_0 = ex_s_z_0
        self.ex_s_w_0 = ex_s_w_0

    def reset(self):
        super().reset()

        # exteroceptive sense
        self.luminance_change = [0]
        self.ex_sense = []

        # exteroceptive errors
        self.ex_e_z_0 = []
        self.ex_e_w_0 = []

        # brain state mu
        self.ex_mu = [0]
        self.ex_mu_d1 = [0]

        # variational free energy
        self.ex_vfe = []

    def generate_senses(self):
        super().generate_senses()
        self.generate_ex_sense()

    def generate_ex_sense(self):
        ex_sense = self.luminance_change[-1] + get_noise()
        self.ex_sense.append(ex_sense)

    def upd_ex_err_z_0(self):
        # error between sensation and generated sensations
        self.ex_e_z_0.append(self.ex_sense[-1] - 0.1 * (-self.ex_mu[-1] + 30))

    def upd_ex_err_w_0(self):
        # error between model and generation of model
        # here: model of dynamics at 1st derivative
        # and it's generation for the 1st derivative
        self.ex_e_w_0.append(self.ex_mu_d1[-1] + self.ex_mu[-1])

    def upd_ex_mu_d1(self):
        upd = -self.learn_r_ex * (self.ex_e_w_0[-1] / self.ex_s_w_0)
        upd *= self.dt

        self.ex_mu_d1.append(self.ex_mu_d1[-1] + upd)

    def upd_ex_mu(self):
        upd = -self.learn_r_ex * \
            (0.1 * self.ex_e_z_0[-1] / self.ex_s_z_0 +
             self.ex_e_w_0[-1] / self.ex_s_w_0)
        upd += self.ex_mu_d1[-2]
        upd *= self.dt

        self.ex_mu.append(self.ex_mu[-1] + upd)

    def upd_ex_vfe(self):
        def sqrd_err(err, sigma):
            return np.power(err, 2) / sigma

        ex_vfe = 0.5 * (sqrd_err(self.ex_e_z_0[-1], self.ex_s_z_0) +
                        sqrd_err(self.ex_e_w_0[-1], self.ex_s_w_0))

        self.ex_vfe.append(ex_vfe)

    def exteroception(self):
        # an agents performs exteroception
        # that updates the desired temperature
        # setting new set point for the underlying
        # interoceptive inference

        #   --> update errors
        self.upd_ex_err_z_0()
        self.upd_ex_err_w_0()

        #  --> update recognition dynamics
        self.upd_ex_mu_d1()
        self.upd_ex_mu()

        #  update free energy
        self.upd_ex_vfe()

    def update_world(self):
        # update world as in Interoceptive Agent
        super().update_world()

        # test -- only less luminance before temperature drop
        # TODO change the luminance corresponding to the change
        # of temperature over the whole time line

        # change in luminance starts before the temperature drop
        if self.time >= 175 and self.time <= 225:
            luminance_change = -0.7
        else:
            luminance_change = 0

        self.luminance_change.append(luminance_change)

    def active_inference(self):
        # exteroception first
        self.exteroception()
        # pass the prior about desired temperature to the interoception
        # generative model
        self.temp_desire.append(self.ex_mu[-1])
        # then perform interoception
        self.interoception()

    def plot_results(self):
        super().plot_results()

        fig, ax = plt.subplots(4, 1, constrained_layout=True)

        timeline = [s * self.dt for s in range(self.steps)]

        # change in light
        ax[0].plot(timeline, self.luminance_change[1:])
        ax[0].set_title('Luminance change')

        ax[1].plot(timeline, self.ex_mu[1:])
        ax[1].plot(timeline, self.ex_mu_d1[1:])
        ax[1].set_title('mu over time (inferred desired temperature)')
        ax[1].legend(['mu', 'mu\''], loc='upper right')

        ax[2].plot(timeline, self.ex_vfe)
        ax[2].set_title('Exteroception VFE')
        ax[2].set_ylim(-0.1, 500)

        ax[3].plot(timeline, self.ex_e_z_0)
        ax[3].plot(timeline, self.ex_e_w_0)
        ax[3].set_ylim(-10, 10)
        ax[3].set_title('Exteroception error')
        ax[3].legend(['e_z_0', 'e_w_0', ], loc='upper right')

        plt.show()


class ActiveExteroception(ExteroceptiveAgent):
    """An agent now lives in the world where it can act
       In this world an agent can move up and down.
       Where moving up increases the amount of light 
       and, therefore, the temperature,
       while moving down has the contrary effect.

       The generative model of interoception is re-used for
       exteroceptive active inference. 

       As a result, an agent can both regulate it's temperature
       interoceptive and exteroceptively. At the same time,
       the generative dynamic, specifying a settling point resides on a level
       above. On a next level of the hierarchy the desired temperature is inferred."""

    def __init__(self, aex_s_z_0=0.1, aex_s_w_0=0.1, aex_s_w_1=0.1,
                 aex_action_bound=0.5, supress_action=False, learn_r_aex=None,
                 supress_desired_temp_inference=False,
                 **kwargs):
        super().__init__(**kwargs)

        self.learn_r_aex = self.learn_r if learn_r_aex is None else learn_r_aex

        # sigma (variances)
        self.aex_s_z_0 = aex_s_z_0
        self.aex_s_w_0 = aex_s_w_0
        self.aex_s_w_1 = aex_s_w_1

        # action bound
        self.aex_action_bound = aex_action_bound

        self.supress_action = supress_action
        self.supress_desired_temp_inference = supress_desired_temp_inference

    def reset(self):
        super().reset()

        # active exteroceptive errors
        self.aex_e_z_0 = []

        # variational free energy
        self.aex_vfe = []

        # action
        self.aex_action = [0]

    def update_world(self):
        super().update_world()

        # luminance change is updated with action
        # changing the current luminance change
        if not self.supress_action:
            self.luminance_change[-1] += self.aex_action[-1]

    def upd_temp_change(self):
        # for this simple agent temp_change is just action
        # update temperature by constant (e.g. world is heating constantly)
        super().upd_temp_change()

        if not self.supress_action:
            self.temp_change[-1] += -1 * self.aex_action[-1] / 1.0

    def upd_aex_err_z_0(self):
        # error between sensation and generated sensations
        # is difference between sensed temperature change
        # and the generation of this change (first derivative of mu)
        # TODO the only thing this can do is reduce temperature change to 0
        # it won't bring to the desired temperature
        # because there is not dynamics to specify it
        self.aex_e_z_0.append(self.ex_sense[-1] - -1.0 * (self.mu_d1[-1]))

    def upd_aex_vfe(self):
        def sqrd_err(err, sigma):
            return np.power(err, 2) / sigma

        # vfe is very similar to interoception, but precision is set
        # for exteroception case
        aex_vfe = 0.5 * (sqrd_err(self.aex_e_z_0[-1], self.aex_s_z_0) +
                         sqrd_err(self.e_w_0[-1], self.aex_s_w_0) +
                         sqrd_err(self.e_w_1[-1], self.aex_s_w_1))

        self.aex_vfe.append(aex_vfe)

    def upd_action(self):
        super().upd_action()
        # sensation change over action is always 1
        upd = -self.learn_r_aex * 1 * (self.aex_e_z_0[-1] / self.aex_s_z_0)
        upd *= self.dt
        aex_action = self.aex_action[-1] + upd

        # action must be bound by some plausible constraints
        # e.g. can't move faster than some limit
        if abs(aex_action) > self.aex_action_bound:
            aex_action = np.sign(aex_action) * self.aex_action_bound

        # update action
        self.aex_action.append(aex_action)

    def upd_no_action(self):
        super().upd_no_action()
        self.aex_action.append(self.aex_action[-1])

    def active_exteroception(self):
        # an agents performs action
        # based on it's exteroceptive inference
        # about how temperature change causes luminance change

        # update errors
        self.upd_aex_err_z_0()

        # update free energy
        self.upd_aex_vfe()

    def active_inference(self):
        # exteroception first
        self.exteroception()

        # pass the prior about desired temperature to the generative model
        if not self.supress_desired_temp_inference:
            self.temp_desire.append(self.ex_mu[-1])
        else:
            self.temp_desire.append(self.temp_viable_mean)

        # then perform interoception
        self.interoception()
        # and active exteroception
        self.active_exteroception()

    def plot_results(self):
        super().plot_results()

        fig, ax = plt.subplots(3, 2, constrained_layout=True)

        timeline = [s * self.dt for s in range(self.steps)]

        # change in light
        ax[0][0].plot(timeline, self.luminance_change[1:])
        ax[0][0].set_title('Luminance change')

        ax[1][0].plot(timeline, self.mu[1:])
        ax[1][0].plot(timeline, self.mu_d1[1:])
        ax[1][0].set_title('mu over time (inferred temperature)')
        ax[1][0].legend(['mu', 'mu\''], loc='upper right')

        ax[2][0].plot(timeline, self.aex_vfe)
        ax[2][0].set_title('Active Exteroception VFE')
        ax[2][0].set_ylim(-0.1, 500)

        ax[0][1].plot(timeline, self.aex_e_z_0)
        ax[0][1].plot(timeline, self.e_w_0)
        ax[0][1].plot(timeline, self.e_w_1)
        ax[0][1].set_ylim(-10, 10)
        ax[0][1].set_title('Exteroception and model error')
        ax[0][1].legend(['e_z_0', 'e_w_0', 'e_w_1'], loc='upper right')

        ax[1][1].plot(timeline, self.temp_const_change[1:])
        ax[1][1].plot(timeline, self.aex_action[1:])
        diff = np.array(self.temp_const_change[1:]) + np.array(self.aex_action[1:])
        ax[1][1].plot(timeline, diff, lw=0.75, ls='--')
        ax[1][1].legend(['luminance change', 'action', 'diff'], loc='upper right')
        ax[1][1].set_title('Luminance change and action')

        plt.show()


class ProprioceptiveAgent(ActiveExteroception):
    """An agent now has an actual proprioceptive model
       and this model is recruited for the agent to actually
       act on the environment

       It is also show, that proprioceptive predictions about 
       how much proprioceptive information can explain the change of light"""

    def __init__(self, pr_s_z_0=0.01, pr_s_w_0=100000, learn_r_pr=None,
                 pr_action_bound=10, supress_action=False, 
                 supress_desired_temp_inference=False, **kwargs):
        # variance is set to be very high for internal model
        # as it does not matter in this case
        super().__init__(**kwargs)

        self.learn_r_pr = self.learn_r if learn_r_pr is None else learn_r_pr

        # sigma (variances)
        self.pr_s_z_0 = pr_s_z_0
        self.pr_s_w_0 = pr_s_w_0

        self.pr_action_bound = pr_action_bound
        self.supress_action = supress_action
        self.supress_desired_temp_inference = supress_desired_temp_inference

    def reset(self):
        super().reset()

        # proprioceptive errors
        self.pr_e_z_0 = []
        self.pr_e_w_0 = []

        # brain state mu
        self.pr_mu = [0]
        self.pr_mu_d1 = [0]

        self.pr_action = [0]
        self.pr_action_effect_on_luminance = []

        # variational free energy
        self.pr_vfe = []

    def upd_pr_err_z_0(self):
        # error between sensation and generated sensations
        # what light change do I need to explain away
        # how can I generate it with action (moving)

        # light change i need to explain
        light_change = 1 * (self.aex_e_z_0[-1] / self.aex_s_z_0)

        # generative model is 10 velocities are needed to change the light by 1
        # 1 velocity changes light by 0.1
        # if I move upward the light will increase
        self.pr_e_z_0.append(light_change - -0.1 * self.pr_mu[-1])

    def upd_pr_err_w_0(self):
        # error between model and generation of model
        # here: model of dynamics at 1st derivative (inferred velocity)
        # and it's generation for the 1st derivative (generated velocity)
        self.pr_e_w_0.append(self.pr_mu_d1[-1] + self.pr_mu[-1])

    def upd_ex_err_z_0(self):
        # the way exteroceptive error is calculated needs to be changed
        # now predicted luminance from the lower level
        # needs to be subtracted
        # as it is already explained on a lower level

        # how I believe proprioception explains the light change
        # proprioception_prediction = -0.1 * self.pr_mu[-1]
        proprioception_prediction = -0.1 * self.pr_mu[-1]
        # proprioception_prediction = 0

        self.ex_e_z_0.append(self.ex_sense[-1]
                             + 0.1 * (self.ex_mu[-1] - 30)
                             + proprioception_prediction)

    def upd_pr_mu_d1(self):
        upd = -self.learn_r_pr * (self.pr_e_w_0[-1] / self.pr_s_w_0)
        upd *= self.dt

        self.pr_mu_d1.append(self.pr_mu_d1[-1] + upd)

    def upd_pr_mu(self):
        upd = -self.learn_r_pr * \
            (0.1 * self.pr_e_z_0[-1] / self.pr_s_z_0 +
             self.pr_e_w_0[-1] / self.pr_s_w_0)
        upd += self.pr_mu_d1[-2]
        upd *= self.dt

        self.pr_mu.append(self.pr_mu[-1] + upd)

    def upd_pr_vfe(self):
        def sqrd_err(err, sigma):
            return np.power(err, 2) / sigma

        pr_vfe = 0.5 * (sqrd_err(self.pr_e_z_0[-1], self.pr_s_z_0) +
                        sqrd_err(self.pr_e_w_0[-1], self.pr_s_w_0))

        self.pr_vfe.append(pr_vfe)

    def upd_action(self):
        # action of the ExteroceptiveAgent and not ActiveExteroceptive will be called!
        # we need to override the ActiveExteroceptive one
        ExteroceptiveAgent.upd_action(self)

        # assume that agent can indicate the velocity directly (derivative is 0.1)
        # TODO is it 0.1 or just 1?
        upd = -self.learn_r_aex * 0.1 * (self.pr_e_z_0[-1] / self.pr_s_z_0)
        upd *= self.dt
        pr_action = self.pr_action[-1] + upd

        # action must be bound by some plausible constraints
        # e.g. can't move faster than some limit
        if abs(pr_action) > self.pr_action_bound:
            pr_action = np.sign(pr_action) * self.pr_action_bound

        # update action
        self.pr_action.append(pr_action)

    def upd_no_action(self):
        # no_action of the ExteroceptiveAgent and not ActiveExteroceptive will be called!
        # we need to override the ActiveExteroceptive one
        ExteroceptiveAgent.upd_no_action(self)
        self.pr_action.append(self.pr_action[-1])

    def proprioception(self):
        #   --> update errors
        self.upd_pr_err_z_0()
        self.upd_pr_err_w_0()

        #  --> update recognition dynamics
        self.upd_pr_mu_d1()
        self.upd_pr_mu()

        #  update free energy
        self.upd_pr_vfe()

    def active_inference(self):
        # exteroception first
        self.exteroception()

        # pass the prior about desired temperature to the generative model
        if not self.supress_desired_temp_inference:
            self.temp_desire.append(self.ex_mu[-1])
        else:
            self.temp_desire.append(self.temp_viable_mean)

        # then perform interoception
        self.interoception()
        # and active exteroception
        self.active_exteroception()
        # and then proprioception (with the corresponding action)
        self.proprioception()

    def update_world(self):
        # update_world of the ExteroceptiveAgent and not ActiveExteroceptive will be called!
        # we need to override the ActiveExteroceptive one
        ExteroceptiveAgent.update_world(self)

        # luminance change is updated with action
        # changing the current luminance change
        if not self.supress_action:
            # translate action to actual change of environment
            # affect of action is translated to luminance change
            # TODO action is noisy! Add noise here but not forget about integration
            action_effect_on_luminance = self.pr_action[-1] * 0.1
            self.pr_action_effect_on_luminance.append(action_effect_on_luminance)

            self.luminance_change[-1] += action_effect_on_luminance

    def upd_temp_change(self):
        ExteroceptiveAgent.upd_temp_change(self)

        if not self.supress_action:
            # temperature changes depending on the actual action taken
            # assumed relationship between luminance and temperature change is
            # 1 : 1
            self.temp_change[-1] += -1 * self.pr_action_effect_on_luminance[-1] / 1.0

    def plot_results(self):
        ExteroceptiveAgent.plot_results(self)

        fig, ax = plt.subplots(3, 2, constrained_layout=True)

        timeline = [s * self.dt for s in range(self.steps)]

        # change in light
        ax[0][0].plot(timeline, self.luminance_change[1:])
        ax[0][0].set_title('Luminance change')

        ax[1][0].plot(timeline, self.pr_mu[1:])
        ax[1][0].plot(timeline, self.pr_mu_d1[1:])
        ax[1][0].set_title('mu over time (inferred change in velocity)')
        ax[1][0].legend(['mu', 'mu\''], loc='upper right')

        ax[2][0].plot(timeline, self.aex_vfe)
        ax[2][0].plot(timeline, self.pr_vfe)
        ax[1][0].legend(['active exteroception', 'proprioception'], loc='upper right')
        ax[2][0].set_title('Active Exteroception and proprioception VFE')
        ax[2][0].set_ylim(-0.1, 500)

        # ax[0][1].plot(timeline, self.aex_e_z_0)
        # ax[0][1].plot(timeline, self.e_w_0)
        # ax[0][1].plot(timeline, self.e_w_1)
        # ax[0][1].set_ylim(-10, 10)
        # ax[0][1].set_title('Exteroception and Proprioception errors')
        # ax[0][1].legend(['e_z_0', 'e_w_0', 'e_w_1'], loc='upper right')

        ax[0][1].plot(timeline, self.pr_e_z_0)
        ax[0][1].plot(timeline, self.pr_e_w_0)
        ax[0][1].set_ylim(-10, 10)
        ax[0][1].set_title('Proprioception errors')
        ax[0][1].legend(['e_z_0', 'e_w_0'], loc='upper right')

        ax[1][1].plot(timeline, self.temp_change[1:])
        ax[1][1].plot(timeline, self.pr_action[1:])
        diff = np.array(self.temp_change[1:]) + np.array(self.pr_action[1:])
        ax[1][1].plot(timeline, diff, lw=0.75, ls='--')
        ax[1][1].legend(['luminance change', 'action', 'diff'], loc='upper right')
        ax[1][1].set_title('Luminance change and action')

        plt.show()
