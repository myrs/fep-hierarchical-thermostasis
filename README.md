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

### Adding active exteroception
Pezzulo et at. have proposed, that "at the higher levels of the hierarchy ... representations become *amodal or multimodal* – providing descending predictions in the exteroceptive, autonomic and proprioceptive domains". This extension aims to roughly implement this idea and show it's viability. 

While our agent already has interoceptive and exteroceptive sensors, it can only act interoceptively (by setting the desired temperature based on exteroception and setting it's temperature change based on interoception). We can easily imagine a world, where adding exteroceptive action could be beneficial for our agent and which would make it more adaptive (an evolution would definitely do so eventually). We can now assume an agent lives in water environment. In this environment it observes more sunlight in warmer places (closer to the light) and less sunlight in colder places (further from the light). Now an agent equipped with this simple relationship relationship thought a generative model show be able to act in the world and find better temperature regimes acting exteroceptively. In other words, it would seek to find such exteroceptive dynamics (change in light) that would better explain it's brain variable (temperature change) through acting (setting the change in light). Here two things are worth a more detailed explanation. First, the right generative model would be such, that encodes the inverse relationship between the internal temperature change and change in light. This was our agent would seek darker places (less light) when it's body gets hotter and vise versa. Second, and more importantly, it seems there is a big assumption when we say that the agent can change the light directly. Indeed, and agent is actually moving up and down in the water, which is what changing the light intensity. Out point here is that the agent (to some extent, see *Next steps*) does not need to know *how* it is changing the light intensity in order to control it! It only need to know *that* it has the ability to change the intensity of light. Now, how is it really changed is the task of the (underlying) reflex arc. While this reflex arc is out of scope of the simulation at this step, it's important to stress that once the right command is given (from the higher level of the hierarchy), such reflex arc will perform it, leading to the effective change in lighting. Summarising, an organism does not really to know *how it happens* to *make it happen* at this point.

#### Discussion
Importantly, the implementation of this version of the agent shows "how more complex controllers could have developed from earlier (less flexible) controllers" (Pezzulo et al.). Elegance here manifests in reusing already existing exteroceptive sensations (change of the level of light) and already existing recognition dynamics (inferring the interoceptive *brain variable* -- a change in the organism's temperature). Indeed, this seems to us to be a good proof for the argument if favour of non-modular architectures versus traditional "classical sandwich" architectures ("The modularity of action and perception revisited using control theory and active inference"). Optimal control proposes the separation of optimal perception and optimal action modules which works from the engineering point of view, but it's difficult to imagine an agent that would have evolved such separate controllers in an effective manner (c.f. the problem of the hen and the egg). On contrary, our case shows that an agent can gradually evolve new behaviour, reusing (part of the) already existing controllers and (supposedly) corresponding neural structures in the brain and the body. This seems to be more plausible implementation of how the evolution have worked out the emergence of more and more complex species. In other words, complex and effective perception arised not from the necessity of control. Instead, they arised *together* from the necessity of maintaining the organism's internal variables in a viable interval and the opportunities (and treats) of the environment and organism is situated in.

While this work suggest a possible plausible implementation of this principles, it remains unclear *how* it could have been done.

### Next steps
The next step is to add proprioception to show, how an agent can use proprioceptive information to infer how much of the light change happens because of exteroceptive action vs how much is generated by the environment itself. Further steps would include adding more layers of hierarchy to allow conditioned (aka Pavlovian) and goal-directed behaviour an allowing an agent to move in the environment in order to be more adaptive.

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
