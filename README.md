# Minimal allostatic agent, implemented through hierarchical active inference

## Authors
Mikhail Yaroshevskiy

## High-level description
This code is part of the MSc thesis submitted for the degree in Intelligent and Adaptive Systems in University of Sussex by Mikhail Yaroshevskiy (2020).

In this work, we show the limitations of the regulation of the essential variables (e.g. temperature) in a homeostatic way. We then show how an agent can be made more adaptive and survive not just by reacting to the environment, but by acting on dangerous tendencies of the world with anticipation. We use the active inference framework to operationalise our agent. Specifically, we develop a multi-layer generative model of the environmental dynamics where higher levels provide lower layers with set points of their dynamics. We argue, that a minimal allostatic model should have a capacity for both physiological and behavioural change to anticipate dangerous tendencies of the world. We have shown how a physiological change of an agent can be governed through environmental cue: our agent heats in advance in the world (by changing its preference about body temperature) where a decrease in light level (exteroceptive cue) is followed by temperature drop (simulating water temperature drop after sunset). This allows our agent to survive by having a dynamical trajectory of body temperature regulation (with a dynamically specified goal temperature) rather than regulating a temperature around a fixed set point. We then show that physiological allostatic change is not enough when an external unmodelled force is present in the world: in our case, we simulate a current, moving agent closer to the surface where the temperature of the world is too high to be counteracted by the body. Though, an agent that can perform a behavioural allostatic change -- act on the world -- can counteract dangerous tendencies by continuously finding better temperature regimes. Importantly, we have shown how this behaviour is guided (though dynamical set point) by the interoceptive needs of the temperature regulation and not exteroceptive sensations. It is therefore robust to noise inexact predictions of the generative model of the agent as its embodiment -- receiving feedback from the world through the body -- is what allows an agent to maintain its ultrastability.

## Agents
### Homeostasis-based agent
A simple interoceptive agent can regulate its body temperature around the fixed goal in a homeostatic way. It has limitations: while an agent is equipped with interoceptive active inference, it cannot counteract the change in temperature of its body produced by the environment once it is higher than its physiological ability of regulation. In other words, while homeostasis is effective in counteracting the present disturbances, it cannot counteract dangerous future tendencies a priori.

### Allostasis by a physiological change
We show how the limitations of the homeostasis around a fixed set point can be overcome by introducing allostatic regulation through physiological change when an agent is presented with an exteroceptive cue. Specifically, now a higher exteroceptive layer infers the goal temperature that is passed down to the interoceptive layer setting the equilibrium of its dynamics. Following the dynamical trajectory, specified by the interaction of the two layers, our agent is shown to heat in advance surviving the following temperature drop. When then expose our agent to the unmodelled external force, moving the agent closer to the surface where it experiences higher changes in temperature, an agent is shown to have a limited capability to counteract this disturbance. While it can cool itself for some time, it is not sustainable in the long term as the physiological limits of temperature regulation stop being sufficient when the temperature change becomes too high.

### Allostasis by a behavioural change
We show how effective essential variables regulation can be achieved by the agent in an allostatic way through manipulating the environment. Importantly, our agent is shown to act on the world led by its homeostatic needs (regulation of its body temperature) and not by an externally specified goal. We show that such behaviour does not necessarily need any additional exteroceptive sensation (e.g. sensing the velocity of moving through the world) when the dynamics of the action model is specified through homeostatic needs and the agent’s embodiment in the world allows to correct the noisy an inexact action.

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
from simulation import *
# simulate agent
InteroceptiveAgent().simulate()
```

To see results for the exteroceptive agent, change `InteroceptiveAgent` to `ExteroceptiveAgent`.
To see results for the active exteroception agent, change `InteroceptiveAgent` to `ActiveExteroceptiveAgent`.
