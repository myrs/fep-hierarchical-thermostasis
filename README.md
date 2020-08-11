# Hierarchical thermostatic agent based on free energy principle

## Authors
Mikhail Yaroshevskiy

## High-level description
This project tends to implement (roughly) the hierarchical model of active inference, presented by Pezzulo et at. in ["Active Inference, homeostatic regulation and adaptive behavioural control"](http://dx.doi.org/10.1016/j.pneurobio.2015.09.001). Starting with simple interoceptive active inference behaviour (autonomic reflex) and adding more layers of hierarchy (unconditional and Pavlovian reflexes, goal-directed behaviour) to allow an agent to use more information about the world and be more adaptive. This project looks at the FEP from adaptive systems point of view, parting from Ashby's ideas of homeostatic regulation rather then (passive) Helmholtzian perspective of perception as inference (following the point of view of Anil Seth in ["The Cybernetic Bayesian Brain"](https://www.doi.org/10.15502/9783958570108)).

## Current progress
### Purely interoceptive agent
The simplest interoceptive agent resembles a thermostat. This agent uses FEP based on maths behind simple dynamical generative model presented in ["The free energy principle for action and perception: A mathematical
review"](http://dx.doi.org/10.1016/j.jmp.2017.09.004) by Buckley et al. in chapter 7.

An agent lives in a world where the only thing it needs to care about is maintaining its temperature inside a viable interval. It can sense the current temperature and change of this temperature. It acts setting the  desired change of temperature directly. Though, as agent is bounded by physics of its body, it can only set this change inside a boundary (±5.8 °C per time step). It's viable range is 30 ±10 °C.

Initial temperature of an agent is set to the mean of the viable range (30 °C). An agent is given a small time (50 time steps) to infer the current temperature (as it's assumed to be unknown at the beginning of the simulation). After this, the world is simulated such way an agent experiences a change of temperature at each timestep in a following way:
* time steps from 50 to 100: +2 °C per time step
* time steps from 101 to 150: +5 °C per time step
* time steps from 151 to 200: -1 °C per time step
* time steps from 201 to 250: -6 °C per time step
* time steps from 251 to 300: 0 °C per time step (agent is not experiencing a change in temperature)

Simulation ends at the time step 300.

From the provided simulation it can be observed that an agent can effectively deal with changes of temperature (both constant and sudden) and maintain itself in a viable interval for most of the environmental disturbances. The twist comes from the fact that at time steps from 201 to 250 an agent experiences a change of -6 °C per step, while it can only regulate the temperature by +5.8 °C per step. This means, the temperature of an agent will be dropping (-0.2 °C per step) despite its affords, and eventually will go out of the viable boundaries (be less than 20 °C). Effectively and sadly, our agent would cease to exist.

### Adding exteroception
As mentioned above, this project is inspired in (and roughly follows the) hierarchical model of active inference, presented by Pezzulo et at. in "Active Inference, homeostatic regulation and adaptive behavioural control". While an agent would die in the simulated world acting purely on its interoceptive inference, the hope should come from implementing (a next hierarchical level of) exteroception. It is hypothesised that this should allow an agent to have an unconditioned reflex: when provided with an exteroceptive cue (e.g. change in light), an agent should make it's temperature higher *in advance* in order to survive the following drop (or rise) of the temperature. Such next level should provide the underlying interoceptive layer with a different generative model (new settling point), altering this way the underlying interoceptive behaviour. In other words, an agent feelings of cold and hot are not absolute, but dictated by the higher (exteroceptive) level of the hierarchy, allowing it to be more adaptive.

To implement this proposal, we extend an agent with the exteroceptive layer, giving it an ability to perform an unconditioned (autonomic) reflex based on both *exteroceptive* and *interoceptive* inference. An agent is now given a sense of luminosity change per step. It is assumed that in the world where an agent is situated, a drop of temperature is preceded by a luminosity drop (and vise versa). A generative model of perception is given to an agent, with which it can infer which *desired temperature* generates the change in luminosity. This inferred desired temperature is then passed to the lower, interoceptive level, to set the desired dynamics of an agent. The provided simulation shows, how an agent can now effectively survive the drop of temperature by making its own temperature higher *in advance* once the luminosity starts to drop. Effectively, an agent now will survive in this world -- the task that was impossible with interoceptive inference only.

### Next steps
Further steps would include adding more layers of hierarchy to allow conditioned (aka Pavlovian) and goal-directed behaviour an allowing an agent to move in the environment in order to be more adaptive.

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

Run `ipython3` and then execute the following lines to see the results of a simulation of the interoceptive thermostasis agent:
```
from thermostatis_agent import *
# initialize Agent's world
ia = InteroceptiveAgent()
# run a simulation
ia.simulate_perception()
```

To see results for the exteroceptive agent, change `InteroceptiveAgent` to `ExteroceptiveAgent`.
