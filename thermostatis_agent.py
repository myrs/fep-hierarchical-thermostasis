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
                 learn_r_a=None,
                 temp_viable_range=10, dt=0.1, learn_r=0.1):
        # sigma (variances)
        self.s_z_0 = s_z_0
        self.s_z_1 = s_z_1
        self.s_w_0 = s_w_0
        self.s_w_1 = s_w_1

        # learning rate
        self.learn_r = learn_r
        self.learn_r_a = learn_r_a if learn_r_a else learn_r
        # 0.5 will produce too much noise
        self.dt = dt
        self.T0 = 30
        self.temp_viable_mean = 30
        self.temp_viable_range = temp_viable_range

        # action bound -- agent can't set action more or less than this
        self.temp_change_action_bound = action_bound
        self.temp_change_environment_initial = temp_const_change_initial

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
        # $$ temperature params $$
        # start with temperature at T0
        self.temp = [self.T0]
        # overall change of temperature
        self.temp_change = [0]
        # change of temperature, generated by the environment
        self.temp_change_environment = [self.temp_change_environment_initial]
        self.temp_change_instant_update = [0]
        # change of temperature, generated by the action
        self.temp_change_action = [0]
        # $$ light params $$
        # overall light
        self.light_change = [0]
        # light change generated by the environment
        self.light_change_instant = [0]
        self.light_change_environment = [0]
        # light change generated by the movement
        self.light_change_movement = []
        # sense of light
        self.ex_sense = []
        # $$ movement params $$
        self.velocity_action = [0]
        self.velocity = [0]

        # action (interoceptive)
        # temperature change set by action
        # TODO here should be some non-linearity!
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
        """ update world parameters """

        # an agent lives in the water world where
        # a temperature changes at each timestep
        # at some time this rate of change can be adjusted

        if self.time == 50:
            # jump to 2
            new_temp_chage_desired = 3
        elif self.time == 100:
            # jump to 5
            new_temp_chage_desired = 5
        elif self.time == 150:
            # jump to -1
            new_temp_chage_desired = -1
        elif self.time == 200:
            # jump to -6
            new_temp_chage_desired = -6
        elif self.time == 250:
            # jump to 0
            new_temp_chage_desired = 0
        else:
            new_temp_chage_desired = self.temp_change_environment[-1]

        temp_change_instant_update = new_temp_chage_desired - self.temp_change_environment[-1]

        self.temp_change_instant_update.append(temp_change_instant_update)

    def upd_velocity(self):
        # update velocity with friction
        # TODO simulate friction!
        # velocity = 0.9 * self.velocity[-1]
        # velocity = self.velocity[-1]
        velocity = self.velocity_action[-1]

        self.velocity.append(velocity)

    def upd_light_change(self):
        """ Light change is composed of the light change
        due to the environment and light change due to the movement of the
        agent in the environment (set by its velocity) """

        # light change due to the environment is updated by the
        light_change_environment = self.light_change_environment[-1]
        # instant change of light (Euler integrated)
        light_change_environment += self.light_change_instant[-1] * self.dt
        self.light_change_environment.append(light_change_environment)

        # the light change due to velocity (Euler integrated)
        # TODO a coefficient can be different, now assuming 1:1
        # self.light_change_movement.append(self.velocity[-1] * self.dt)
        self.light_change_movement.append(self.velocity[-1])

        # combined light change is light change due to environment
        light_change = self.light_change_environment[-1]
        # and light change due to the movement
        light_change += self.light_change_movement[-1]

        self.light_change.append(light_change)

    def upd_temp_change(self):
        """ Change in temperature or the organism is composed of 
        the change in temperature due to the environment and the change
        of temperature, generated by the agent.
        """

        # as agent moves though the world, the change of temperature
        # is affected by instant changes in change in temperature
        # and by movement of the agent
        # by adding velocity effect (Euler integrated)
        temp_change_environment = self.temp_change_environment[-1]
        # first update by instant change in temperature change (Euler integrating)
        temp_change_environment += self.temp_change_instant_update[-1]
        # update movement effect by adding Euler integrated velocity
        # TODO a coefficient or function can be different
        # -- now assuming 1:1 relationship
        # temp_change_environment += self.velocity[-1]
        temp_change_environment += self.velocity[-1] * self.dt
        self.temp_change_environment.append(temp_change_environment)

        # total temperature change is change due to the environment
        # and change produced by the organism
        temp_change = self.temp_change_environment[-1] + self.temp_change_action[-1]

        self.temp_change.append(temp_change)

    def upd_temp(self):
        # update temperature with the current temperature update
        upd = self.temp_change[-1]
        # Euler integrating it
        upd *= self.dt

        self.temp.append(self.temp[-1] + upd)

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
        action = self.temp_change_action[-1] + upd

        # action must be bound by some plausible constraints
        # e.g. temperature can't change more than action bound at each timestep
        if abs(action) > self.temp_change_action_bound:
            action = np.sign(action) * self.temp_change_action_bound

        # update action
        self.temp_change_action.append(action)

    def upd_no_action(self):
        # if agent is not acting update it's variables anyway
        self.temp_change_action.append(self.temp_change_action[-1])

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

        ax[2][0].plot(timeline, self.temp_change_environment[1:])
        ax[2][0].plot(timeline, self.temp_change_action[1:])
        diff = np.array(self.temp_change_environment[1:]) + \
            np.array(self.temp_change_action[1:])
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
        self.act_time = act_time

        plt.ion()

        self.steps = int(sim_time / self.dt)
        print(f'Simulating {self.steps} steps')

        for step in range(self.steps):
            self.time = step * self.dt
            # update world
            self.update_world()
            self.upd_velocity()
            self.upd_temp_change()
            self.upd_temp()
            self.upd_light_change()

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
        # ex_sense = self.light_change[-1]
        ex_sense = self.light_change[-1] + get_noise()
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

        # test -- only less light before temperature drop
        # TODO change the light corresponding to the change
        # of temperature over the whole time line

        # change in light starts before the temperature drop
        if int(self.time) == 175:
            # change by -0.7 (to -0.7)
            light_change_instant = -0.7
        elif int(self.time) == 225:
            # change by +0.7 (to 0)
            light_change_instant = 0.7
        else:
            light_change_instant = 0

        # TEST
        # light_change_instant = 0

        self.light_change_instant.append(light_change_instant)

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
        ax[0].plot(timeline, self.light_change[1:])
        ax[0].set_title('Light change')

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

    def __init__(self, aex_s_z_0=0.1, aex_s_z_1=0.1, aex_s_w_0=0.1, aex_s_w_1=0.1,
                 aex_action_bound=0.5, supress_action=False, learn_r_aex=None,
                 supress_desired_temp_inference=False,
                 **kwargs):
        super().__init__(**kwargs)

        self.learn_r_aex = self.learn_r if learn_r_aex is None else learn_r_aex

        # sigma (variances)
        self.aex_s_z_0 = aex_s_z_0
        self.aex_s_w_0 = aex_s_w_0

        # action bound
        self.aex_action_bound = aex_action_bound

        self.supress_action = supress_action
        self.supress_desired_temp_inference = supress_desired_temp_inference

    def reset(self):
        super().reset()

        # active exteroceptive errors
        self.aex_e_z_0 = [0]
        self.aex_e_w_0 = [0]

        # mu
        self.aex_mu = [0]

        # variational free energy
        self.aex_vfe = []

        # action
        self.aex_action = [0]

    def update_world(self):
        super().update_world()

        if self.time < self.act_time:
            self.velocity_action.append(0)
            return

        if not self.supress_action:
            self.velocity_action.append(self.aex_action[-1] + get_noise())

    def upd_aex_mu(self):
        upd = -self.learn_r_ex * \
            (+self.aex_e_z_0[-1] / self.aex_s_z_0 +
             -self.aex_e_w_0[-1] / self.aex_s_w_0
             )
        upd *= self.dt

        self.aex_mu.append(self.aex_mu[-1] + upd)

    def upd_aex_err_w_0(self):
        # my expected dynamics is that environment temperature change
        # needs to be explained
        # setting point is when the inferred change int light
        # corresponds to the change in temperature
        
        # BASELINE
        # self.aex_e_w_0.append(self.temp_change_environment[-1] - self.aex_mu[-1])

        # All temperature change - predicted internal temperature change
        # !!! this actually does not make sense. Because mu' is a bad estimate
        # self.aex_e_w_0.append(self.sense_d1[-1] - self.mu_d1[-1] - self.aex_mu[-1])
        # self.aex_e_w_0.append(self.sense_d1[-1] - self.aex_mu[-1])

        # Just Temperature change
        # self.aex_e_w_0.append(self.sense_d1[-1] - self.aex_mu[-1])
        # 
        # self.aex_e_w_0.append(self.sense_d1[-1] - self.temp_change_action[-1] - self.mu_d1[-1] - self.aex_mu[-1])
        
        self.aex_e_w_0.append(self.sense_d1[-1] - self.temp_change_action[-1] - self.aex_mu[-1])
        
        # self.aex_e_w_0.append(self.mu_d2[-1] - self.aex_mu[-1])

    def upd_aex_err_z_0(self):
        """ error between sensation and generated sensation
        sensation: change in light
        generated by: change in temperature of the environment
        """
        self.aex_e_z_0.append(self.ex_sense[-1] - (-self.aex_mu[-1]))

    def upd_aex_vfe(self):
        def sqrd_err(err, sigma):
            return np.power(err, 2) / sigma

        # vfe is very similar to interoception, but precision is set
        # for exteroception case
        aex_vfe = 0.5 * (sqrd_err(self.aex_e_z_0[-1], self.aex_s_z_0)
                         + sqrd_err(self.aex_e_w_0[-1], self.aex_s_w_0))

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
        # about how temperature change causes light change
        self.upd_aex_mu()

        # update errors
        self.upd_aex_err_z_0()
        self.upd_aex_err_w_0()

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
        ax[0][0].plot(timeline, self.light_change[1:])
        ax[0][0].set_title('Light change')

        ax[1][0].plot(timeline, self.aex_mu[1:])
        ax[1][0].set_title('$\\mu$ over time \n(inferred external temperature change)')
        ax[1][0].legend(['$\\mu$'], loc='upper right')

        ax[2][0].plot(timeline, self.velocity[1:])
        ax[2][0].set_title('velocity')

        ax[0][1].plot(timeline, self.aex_vfe)
        ax[0][1].set_title('Active Exteroception VFE')
        ax[0][1].set_ylim(-0.1, 500)

        ax[1][1].plot(timeline, self.aex_e_z_0[1:])
        ax[1][1].plot(timeline, self.aex_e_w_0[1:])
        ax[1][1].set_ylim(-10, 10)
        ax[1][1].set_title('Exteroception and model error')
        ax[1][1].legend(['aex_z_0', 'aex_w_0'], loc='upper right')

        ax[2][1].plot(timeline, self.light_change[1:])
        ax[2][1].plot(timeline, self.aex_action[1:])
        diff = np.array(self.light_change[1:]) + np.array(self.aex_action[1:])
        ax[2][1].plot(timeline, diff, lw=0.75, ls='--')
        ax[2][1].legend(['light change', 'action', 'diff'], loc='upper right')
        ax[2][1].set_title('Light change and action')

        plt.show()


class ProprioceptiveAgent(ActiveExteroception):
    """An agent now has an actual proprioceptive model
       and this model is recruited by the agent to actually
       act on the environment

       In this iteration of the agent it's also shown, 
       how proprioceptive information can be used by agent
       to predict how much of the observed change in light
       is explained away by proprioceptive feeling"""

    def __init__(self, pr_s_z_0=0.1, pr_s_w_0=0.1, learn_r_pr=None,
                 pr_action_bound=10, supress_action=False,
                 supress_desired_temp_inference=False, **kwargs):
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
        self.pr_e_z_0 = [0]
        self.pr_e_w_0 = [0]

        # brain state mu
        self.pr_mu = [0]

        self.pr_action = [0]
        self.pr_action_effect_on_light = []

        # variational free energy
        self.pr_vfe = []

    def upd_pr_err_w_0(self):
        # internally I want the error to be 0
        self.pr_e_w_0.append(0 - self.pr_mu[-1])

    def upd_pr_err_z_0(self):
        # error between sensation and generated sensations
        # how agent's proprioceptive sensation (e.g. velocity)
        # explains the light change error
        # the received from the higher level

        # light change that is needed to be explained
        # weighted by the variance of the error
        # and transformed to 'units' of proprioception
        # (in this case the transformation is 1:1)

        # THIS seems to be the error! We can divide by variance
        # or maybe we need to figure out where we compensate then
        # light_change_error = 1 * (self.aex_e_z_0[-1] / self.aex_s_z_0)
        light_change_error = self.aex_e_z_0[-1]

        # agent believes that changing velocity by 10
        # it can explain 10 units of light change error
        # generative model is 10 velocities are needed to change the light by 1
        # 1 velocity changes light by 0.1
        # if I move upward the light will increase
        # self.pr_e_z_0.append(light_change_error - (-0.1 * self.pr_mu[-1]))
        self.pr_e_z_0.append(light_change_error - (-self.pr_mu[-1]))

    def upd_aex_err_z_0(self):
        # updated function for calculating
        # the sensory prediction error on the active exteroception layer
        # predictions about sensory data are dictated by the error

        # DEFAULT
        predicted = self.ex_sense[-1]
        # what exteroceptive layer predicts
        # predicted = self.ex_sense[-1] - 0.1 * (-self.ex_mu[-1] + 30)
        # predicted = self.ex_sense[-1] - 0.1 * (-self.ex_mu[-1] + 30)

        # self.aex_e_z_0.append(predicted - 1.0 * (-self.mu_d1[-1]))
        self.aex_e_z_0.append(predicted - (-self.aex_mu[-1]))

    def upd_ex_err_z_0(self):
        # updated function for calculating
        # the sensory prediction error on the desired temperature inference layer
        # predictions from the proprioceptive layer are now
        # subtracted as they were already explain

        # how an agent believes proprioception explains the light change
        # as the movement generated is inverse to the light change,
        # it needs to be without minus

        # DEFAULT
        # proprioception_prediction = 0

        # OPTION -- efference copy
        proprioception_prediction = self.velocity_action[-1]
        # proprioception_prediction = self.pr_e_w_0[-1]
        # what active exteroceptive layer predicts (about light change)
        # proprioception_prediction = -self.pr_mu[-1]
        # proprioception_prediction = -self.pr_mu[-1]
        # proprioception error
        # proprioception_prediction = self.pr_e_z_0[-1]
  
        self.ex_e_z_0.append(self.ex_sense[-1]
                             - 0.1 * (-self.ex_mu[-1] + 30)
                             - proprioception_prediction)

    def upd_pr_mu(self):
        upd = -self.learn_r_pr * (
            +self.pr_e_z_0[-1] / self.pr_s_z_0
            -self.pr_e_w_0[-1] / self.pr_s_w_0)
        upd *= self.dt

        self.pr_mu.append(self.pr_mu[-1] + upd)

    def upd_pr_vfe(self):
        def sqrd_err(err, sigma):
            return np.power(err, 2) / sigma

        pr_vfe = 0.5 * (sqrd_err(self.pr_e_z_0[-1], self.pr_s_z_0)
                        + sqrd_err(self.pr_e_w_0[-1], self.pr_s_w_0))

        self.pr_vfe.append(pr_vfe)

    def upd_action(self):
        # action of the ExteroceptiveAgent and not ActiveExteroceptive will be called!
        # we need to override the ActiveExteroceptive one
        ExteroceptiveAgent.upd_action(self)

        # assume that agent can indicate the velocity directly (derivative is 0.1)
        # TODO is it 0.1 or just 1? * 0.1 * (self.pr_e_z_0[-1] / self.pr_s_z_0)
        # !!TODO try a slower learning rate for action!
        upd = -self.learn_r_pr * 1 * (self.pr_e_z_0[-1] / self.pr_s_z_0)
        upd *= self.dt
        # leaky integration
        # pr_action = self.pr_action[-1] - self.pr_action[-1] * 0.1 * self.dt + upd
        # add update
        pr_action = self.pr_action[-1] + upd
        # noise is proportionate to action and integrated over time

        # action must be bound by some plausible constraints
        # e.g. can't move faster than some limit
        if abs(pr_action) > self.pr_action_bound:
            pr_action = np.sign(pr_action) * self.pr_action_bound

        # pr_action += get_noise()  * self.pr_action[-1] * self.dt
        pr_action += get_noise() * pr_action * self.dt

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

        # light change is updated with action
        # changing the current light change
        if not self.supress_action:
            self.velocity_action.append(self.pr_action[-1])


    def plot_results(self):
        ExteroceptiveAgent.plot_results(self)

        fig, ax = plt.subplots(3, 2, constrained_layout=True)

        timeline = [s * self.dt for s in range(self.steps)]

        # change in light
        ax[0][0].plot(timeline, self.light_change[1:])
        ax[0][0].set_title('Light change')

        ax[1][0].plot(timeline, self.pr_mu[1:])
        ax[1][0].set_title('mu over time (inferred change in velocity)')
        ax[1][0].legend(['mu', 'mu\''], loc='upper right')

        ax[2][0].plot(timeline, self.velocity[1:])
        ax[2][0].set_title('velocity')

        ax[0][1].plot(timeline, self.aex_vfe)
        ax[0][1].plot(timeline, self.pr_vfe)
        ax[0][1].legend(['active exteroception', 'proprioception'], loc='upper right')
        ax[0][1].set_title('Active Exteroception and proprioception VFE')
        ax[0][1].set_ylim(-0.1, 500)

        ax[1][1].plot(timeline, self.aex_e_z_0[1:])
        ax[1][1].plot(timeline, self.pr_e_z_0[1:])
        ax[1][1].plot(timeline, self.pr_e_w_0[1:])
        ax[1][1].set_ylim(-10, 10)
        ax[1][1].set_title('Exteroception and proprioception errors')
        ax[1][1].legend(['aex_e_z_0', 'pr_e_z_0', 'pr_e_w_0'], loc='upper right')

        ax[2][1].plot(timeline, self.temp_change[1:])
        ax[2][1].plot(timeline, self.pr_action[1:])
        diff = np.array(self.temp_change[1:]) + np.array(self.pr_action[1:])
        ax[2][1].plot(timeline, diff, lw=0.75, ls='--')
        ax[2][1].legend(['temperature change', 'action', 'diff'], loc='upper right')
        ax[2][1].set_title('Light change and action')

        plt.show()
