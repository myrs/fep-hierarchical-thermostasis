# Hierarchical thermostatic agent based on free energy principle

## Authors
Mikhail Yaroshevskiy

## High-level description
This project tends to implement (roughly) the hierarchical model of active inference, presented by Pezzulo et at. in ["Active Inference, homeostatic regulation and adaptive behavioural control"](http://dx.doi.org/10.1016/j.pneurobio.2015.09.001). Starting with simple interoceptive active inference behaviour (autonomic reflex) and adding more layers of hierarchy (unconditional and Pavlovian reflexes, goal-directed behaviour) to allow an agent to use more information about the world and be more adaptive. This project looks at the FEP from adaptive systems point of view, parting from Ashby's ideas of homeostatic regulation rather then (passive) Helmholtzian perspective of perception as inference (following the point of view of Anil Seth in ["The Cybernetic Bayesian Brain"](https://www.doi.org/10.15502/9783958570108)).

## Current progress
Currently a simple thermostat agent is implemented using FEP based on maths behind simple dynamical generative model presented in ["The free energy principle for action and perception: A mathematical
review"](http://dx.doi.org/10.1016/j.jmp.2017.09.004) by Buckley et al. in chapter 7.

This agent lives in a world where the only thing it needs to care about is maintaining its temperature inside a viable interval. It can sense the current temperature and change of this temperature. It acts setting the  desired change of temperature directly. Though, as agent is bounded by physics of its body, it can only set this change inside a boundary (e.g. ±5 °C per time step).

Initial agent temperature is set to the desired temperature (36 °C). An agent is given a small time to infer the current temperature (as it's assumed to be unknown at the beginning of the simulation). After this the world is simulated such way that agent experiences a change of temperature at each timestep in a following way:
* time steps from 10 to 50: 2 °C per time step
* time steps from 50 to 100: 5 °C per time step
* time steps from 100 to 150: -1 °C per time step
* time steps from 150 to 200: -6 °C per time step
* time steps from 200 to 250: 0 °C per time step (agent is not experiencing a change in temperature)

Simulation ends at the time step 250.

An agent can change it's temperature in a boundary of ±5.8 °C. It's viable range is 36 ±10 °C. 

From the provided simulation it can be observed that an agent can effectively deal with changes of temperature (both constant and sudden) and maintain itself in a viable interval for most of the environmental disturbances. At this point of project the important point to make is that this agent is unable to deal with a change of the temperature when it's outside of the boundaries. Recall that at time steps from 150 to 200 it is -6 °C per step, while an agent can only regulate it until 5.8 °C per step. Effectively and sadly, our agent would cease to exist.

## Next steps

This project is inspired in (and roughly follows the) hierarchical model of active inference, presented by Pezzulo et at. in "Active Inference, homeostatic regulation and adaptive behavioural control". While the above described agent would die in this world acting purely on its interoceptive inference, the hope should come from implementing (a next hierarchical level of) proprioceptive behaviour. Such proprioceptive behaviour should allow this agent to have an unconditioned reflex: when provided with an exteroceptive cue (e.g. level of light), an agent should make it's temperature higher *in advance* in order to survive the following drop (or rise) of temperature. Such next level should provide the underlying interoceptive layer with a different generative model, providing the underlying interoceptive behaviour with a different settling point. In other words, the agent feeling of what is cold and hot are not absolute, but dictated by the higher level of the hierarchy, allowing it to be more adaptive. Further steps would include adding more layers of hierarchy to allow conditioned (aka Pavlovian) and goal-directed behaviour.

## Running the project

### Prerequisites
Instructions are given for unix-based systems (MacOS, Linux) and can differ slightly for Windows

#### Essentials
`Python 3.8` or higher with `pip`. These should be installed on most systems, if not, detailed guides depending on operating system can be found [here](https://www.makeuseof.com/tag/install-pip-for-python/) or elsewhere

#### Creating virtual environment (optional but highly recommended)
From project folder run 
```python3 -m venv .env-fep-hierarchical-thermostasis```
to create a virtual environment (or use you preferred name).

To activate the environment, run:
 ```source .env-fep-hierarchical-thermostasis/bin/activate```

#### Installing python libraries
Run 
```pip3 install -r requirements.txt```
to install python libraries, used in this project.

### Running project
For now the project can be run using python interactive console `python3` (`ipython3` recommended).

Run `ipython3` and then execute the following lines to see the results of a simulation of the simple thermostat agent:
```
from simple_thermostat_agent import *
# initialize world
wt = TermosatWorld(s_z_0=.1, s_z_1=.1, s_w_0=.1, s_w_1=.1, action_bound=5.8)
# run a simulation
wt.simulate_perception()
```
