# Hierarchical thermostatic agent based on free energy principle

## Authors
Mikhail Yaroshevskiy

## High-level description
This project tends to implement (roughly) the hierarchical model of active inference, presented by Pezzulo et at. in ["Active Inference, homeostatic regulation and adaptive behavioural control"](http://dx.doi.org/10.1016/j.pneurobio.2015.09.001). We start with an agent having simple interoceptive active inference behaviour (autonomic reflex) which is then extended to have exteroceptive sensors and exteroceptive action. We then show why proprioception is also important to produce effective and adaptive behaviour. Proposed agent can be further extended with more layers of hierarchy (unconditional and Pavlovian reflexes, goal-directed behaviour) to allow an agent to use more information about the world and be more adaptive. This project looks at the FEP from adaptive systems point of view, parting from Ashby's ideas of homeostatic regulation rather then (passive) Helmholtzian perspective of perception as inference (following the point of view of Anil Seth in ["The Cybernetic Bayesian Brain"](https://www.doi.org/10.15502/9783958570108)).

## Current progress
### Purely interoceptive agent
#### Description
The simplest interoceptive agent resembles a thermostat. This agent uses FEP based on maths behind simple dynamical generative model presented in ["The free energy principle for action and perception: A mathematical
review"](http://dx.doi.org/10.1016/j.jmp.2017.09.004) by Buckley et al. in chapter 7.

An agent lives in a world where the only thing it needs to care about is maintaining its temperature inside a viable interval. It can sense the current temperature and a change of this temperature. It acts setting the  desired change of temperature directly. Though, as agent is bounded by physics of its body, it can only set this change inside a boundary (±5.8 °C per time step). It's viable range is 30 ±10 °C.

Initial temperature of an agent is set to the mean of the viable range (30 °C). An agent is given a small warm up time (50 time steps) to infer the current temperature (as it's assumed to be unknown at the beginning of the simulation). After this, the world is simulated such way an agent experiences a change of temperature dictated by the environment <img src="https://latex.codecogs.com/png.latex?%5Cdpi%7B120%7D%20%5Cinline%20%5Cdot%7BT_e%7D" alt="\dot{T_e}"> at each timestep in a following way:

<img src="https://latex.codecogs.com/png.latex?%5Cdpi%7B120%7D%20%5Cdot%7BT_e%7D%20%3D%20%5Cleft%5C%7B%20%5Cbegin%7Bmatrix%7D%200%2C%20%26%20step%20%5Cleq%2050%20%5C%5C%202%2C%20%26%20step%20%3E%2050%20%5Cleq%20100%20%5C%5C%205%2C%20%26%20step%20%3E%20100%20%5Cleq%20150%20%5C%5C%20-1%2C%20%26%20step%20%3E%20150%20%5Cleq%20200%20%5C%5C%20-6%2C%20%26%20step%20%3E%20200%20%5Cleq%20250%20%5C%5C%200%2C%20%26%20step%20%3E%20250%20%5Cend%7Bmatrix%7D%20%5Cright." alt="\dot{T_e} = 
\left\{
\begin{matrix}
0, & step \leq 50 \\
2, & step > 50 \leq 100 \\ 
5, & step > 100 \leq 150 \\
-1, & step > 150 \leq 200 \\
-6, & step > 200 \leq 250 \\
0, & step > 250
\end{matrix}
\right.">

After timestep 250 and agent is given a cool down time (temperature change is 0) till the end of the simulation at the time step 300.

As organism can change its own temperature, that actual temperature change at each timestep <img src="https://latex.codecogs.com/png.latex?%5Cinline%20%5Cdot%7BT%7D" alt='\dot{T}'> is a sum of the change of temperature dictated by the environment <img src="https://latex.codecogs.com/png.latex?%5Cdpi%7B120%7D%20%5Cinline%20%5Cdot%7BT_e%7D" alt="\dot{T_e}"> and change of temperature produced be the organism <img src="https://latex.codecogs.com/png.latex?%5Cdpi%7B120%7D%20%5Cinline%20%5Cdot%7BT_o%7D" alt="\dot{T_o}">:

<img src="https://latex.codecogs.com/png.latex?%5Cdpi%7B120%7D%20%5Cdot%7BT%7D%20%3D%20%5Cdot%7BT_e%7D%20&plus;%20%5Cdot%7BT_o%7D" alt="\dot{T} = \dot{T_e} + \dot{T_o}">

#### Model
We then construct an agent's generative model, where <img src="https://latex.codecogs.com/png.latex?%5Cdpi%7B120%7D%20%5Cinline%20%5Cmu" atl="\mu"> represents environmental variable, namely the organisms' temperature. Here an important point to make is that while this temperature is internal to an organism, it is still an environmental (although *interoceptive*) variable for the model. As an organism prefers to have a temperature, corresponding to it's desired temperature, its beliefs about environmental dynamics should be encoded such way it has a settling point at the desired temperature (Buckley et al., 2017):

<img src="https://latex.codecogs.com/png.latex?%5Cdpi%7B120%7D%20%5Cfrac%7Bd%5Cmu%7D%7Bdt%7D%20%3D%20f%28%5Cmu%29%20%5Ctext%7B%2C%20where%20%7Df%28%5Cmu%29%20%5Cequiv%20-%5Cmu%20&plus;%20T_%7Bdesire%7D" alt="\frac{d\mu}{dt} = f(\mu) \text{, where }f(\mu) \equiv -\mu + T_{desire}">

For now it is logical to assume that the desired temperature is static and set it to the mean of the viable interval (i.e. <img src="https://latex.codecogs.com/png.latex?%5Cdpi%7B120%7D%20%5Cinline%20T_%7Bdesire%7D%20%3D%2030" alt="T_{desire} = 30">) but for the sake of the further extensions of an agent we should remember that <img src="https://latex.codecogs.com/png.latex?%5Cdpi%7B120%7D%20%5Cinline%20T_%7Bdesire%7D" alt="T_{desire}"> can take any values. The generative model up to second order can be then written as:

<img src="https://latex.codecogs.com/png.latex?%5Cdpi%7B120%7D%20%5Cinline%20%5Cbegin%7Bmatrix%7D%20%7B%5Cmu%7D%27%20%3D%20-%5Cmu%20&plus;%20T_%7Bdesire%7D%20&plus;%20w%20%5C%5C%20%7B%5Cmu%7D%27%27%20%3D%20-%7B%5Cmu%7D%27%20&plus;%20w%27%20%5C%5C%5Cend%7Bmatrix%7D" alt="\begin{matrix}
{\mu}' = -\mu + T_{desire} + w
\\ 
{\mu}'' = -{\mu}' + w'
\\\end{matrix}">

It is logical to assume that agent believes its sensory data is generated directly by <img src="https://latex.codecogs.com/png.latex?%5Cdpi%7B120%7D%20%5Cinline%20%5Cmu" atl="\mu">. Then the generation of sensory data up to second order can be described as:

<img src="https://latex.codecogs.com/png.latex?%5Cdpi%7B120%7D%20%5Cbegin%7Bmatrix%7D%20%5Cphi%20%3D%20g%28%5Cmu%29%20&plus;%20z%20%5Ctext%7B%2C%20where%20%7D%20g%28%5Cmu%29%20%5Cequiv%20%5Cmu%20%5C%5C%20%7B%5Cphi%7D%27%20%3D%20%7B%5Cmu%7D%27%20&plus;%20z%27%20%5C%5C%5Cend%7Bmatrix%7D" alt="\begin{matrix}
\phi = g(\mu) + z \text{, where } g(\mu) \equiv \mu
\\ 
{\phi}' = {\mu}' + z'
\\\end{matrix}">

Laplace-encoded free energy, error terms and recognition dynamic of the agent would be the same as for an agent, described by (Buckley et al., 2017):

*Laplace-encoded free energy*:

<img src="https://latex.codecogs.com/png.latex?%5Cdpi%7B120%7D%20E%28%5Cwidetilde%7B%5Cmu%7D%2C%20%5Cwidetilde%7B%5Cphi%7D%29%20%3D%20%5Cfrac%7B1%7D%7B2%7D%20%5Cleft%20%5B%20%5Cfrac%7B%7B%5Cvarepsilon_%7Bz%5B0%5D%7D%7D%5E%7B2%7D%7D%7B%7B%5Csigma_%7Bz%5B0%5D%7D%7D%5E%7B2%7D%7D%20&plus;%20%5Cfrac%7B%7B%5Cvarepsilon_%7Bz%5B1%5D%7D%7D%5E%7B2%7D%7D%7B%7B%5Csigma_%7Bz%5B1%5D%7D%7D%5E%7B2%7D%7D%20&plus;%20%5Cfrac%7B%7B%5Cvarepsilon_%7Bw%5B0%5D%7D%7D%5E%7B2%7D%7D%7B%7B%5Csigma_%7Bw%5B0%5D%7D%7D%5E%7B2%7D%7D%20&plus;%20%5Cfrac%7B%7B%5Cvarepsilon_%7Bw%5B1%5D%7D%7D%5E%7B2%7D%7D%7B%7B%5Csigma_%7Bw%5B1%5D%7D%7D%5E%7B2%7D%7D%20%5Cright%20%5D" alt="E(\widetilde{\mu}, \widetilde{\phi}) = 
\frac{1}{2}
\left [ 
\frac{{\varepsilon_{z[0]}}^{2}}{{\sigma_{z[0]}}^{2}} +
\frac{{\varepsilon_{z[1]}}^{2}}{{\sigma_{z[1]}}^{2}} +
\frac{{\varepsilon_{w[0]}}^{2}}{{\sigma_{w[0]}}^{2}} +
\frac{{\varepsilon_{w[1]}}^{2}}{{\sigma_{w[1]}}^{2}}
\right ]">

*where error terms are:*

<img src="https://latex.codecogs.com/png.latex?%5Cdpi%7B120%7D%20%5Cbegin%7Bmatrix%7D%20%5Cvarepsilon_%7Bz%5B0%5D%7D%20%3D%20%5Cphi%20-%20%5Cmu%20%5C%5C%20%5Cvarepsilon_%7Bz%5B1%5D%7D%20%3D%20%7B%5Cphi%7D%27%20-%20%7B%5Cmu%7D%27%20%5C%5C%20%5Cvarepsilon_%7Bw%5B0%5D%7D%20%3D%20%7B%5Cmu%7D%27%20&plus;%20%5Cmu%20-%20T_%7Bdesire%7D%20%5C%5C%20%5Cvarepsilon_%7Bw%5B1%5D%7D%20%3D%20%7B%5Cmu%7D%27%27%20&plus;%20%5Cmu%27%20%5C%5C%5Cend%7Bmatrix%7D" alt="\begin{matrix}
\varepsilon_{z[0]} = \phi - \mu \\
\varepsilon_{z[1]} = {\phi}' - {\mu}' \\
\varepsilon_{w[0]} = {\mu}' + \mu - T_{desire} \\
\varepsilon_{w[1]} = {\mu}'' + \mu'
\\\end{matrix}">

*Then, recognition dynamics is:*

<img src="https://latex.codecogs.com/png.latex?%5Cdpi%7B120%7D%20%5Cbegin%7Bmatrix%7D%20%5Cdot%7B%5Cmu%7D%20%3D%20%5Cmu%27%20-%20%5Ckappa_%7B%5Calpha%7D%5Cleft%20%5B%20-%5Cfrac%7B%5Cvarepsilon_%7Bz%5B0%5D%7D%7D%7B%5Csigma_%7Bz%5B0%5D%7D%7D%20&plus;%20%5Cfrac%7B%5Cvarepsilon_%7Bw%5B0%5D%7D%7D%7B%5Csigma_%7Bw%5B0%5D%7D%7D%20%5Cright%20%5D%20%5C%5C%20%5Cdot%7B%5Cmu%27%7D%20%3D%20%5Cmu%27%27%20-%20%5Ckappa_%7B%5Calpha%7D%5Cleft%20%5B%20-%5Cfrac%7B%5Cvarepsilon_%7Bz%5B1%5D%7D%7D%7B%5Csigma_%7Bz%5B1%5D%7D%7D%20&plus;%20%5Cfrac%7B%5Cvarepsilon_%7Bw%5B0%5D%7D%7D%7B%5Csigma_%7Bw%5B0%5D%7D%7D%20&plus;%20%5Cfrac%7B%5Cvarepsilon_%7Bw%5B1%5D%7D%7D%7B%5Csigma_%7Bw%5B1%5D%7D%7D%20%5Cright%20%5D%20%5C%5C%20%5Cdot%7B%5Cmu%27%27%7D%20%3D%20-%20%5Ckappa_%7B%5Calpha%7D%20%5Cfrac%7B%5Cvarepsilon_%7Bw%5B1%5D%7D%7D%7B%5Csigma_%7Bw%5B1%5D%7D%7D%20%5C%5C%5Cend%7Bmatrix%7D" alt="\begin{matrix}
\dot{\mu} = \mu' - \kappa_{\alpha}\left [
-\frac{\varepsilon_{z[0]}}{\sigma_{z[0]}} + 
\frac{\varepsilon_{w[0]}}{\sigma_{w[0]}}
\right ]
\\
\dot{\mu'} = \mu'' - \kappa_{\alpha}\left [
-\frac{\varepsilon_{z[1]}}{\sigma_{z[1]}} + 
\frac{\varepsilon_{w[0]}}{\sigma_{w[0]}} +
\frac{\varepsilon_{w[1]}}{\sigma_{w[1]}}
\right ]
\\
\dot{\mu''} = - \kappa_{\alpha} \frac{\varepsilon_{w[1]}}{\sigma_{w[1]}}
\\\end{matrix}">

As it was mentioned above, an agent believes it can change the temperature of its body directly. While this could seem biologically implausible at a first glance, for simplicity we just keep unaware of how actually the temperature is changed assuming an underlying biologically plausible way of doing it (e.g. by sweating to cool down or shivering to warn up). In terms of active inference we need to find how the free energy changes with respect to action:

<img src="https://latex.codecogs.com/png.latex?%5Cdpi%7B120%7D%20%5Cdot%7Ba%7D%20%3D%20-%5Ckappa_%7B%5Calpha%7D%5Cleft%20%5B%20%5Cfrac%7Bd%5Cphi%27%7D%7Bda%7D%20%5Cfrac%7B%5Cpartial%20E%7D%7B%5Cpartial%5Cphi%27%7D%20%5Cright%20%5D" alt="\dot{a} = -\kappa_{\alpha}\left [ \frac{d\phi'}{da} \frac{\partial E}{\partial\phi'} \right ]">

where <img src=https://latex.codecogs.com/png.latex?%5Cinline%20%5Cdpi%7B120%7D%20%5Cfrac%7B%5Cpartial%20E%7D%7B%5Cpartial%5Cphi%27%7D" alt="\frac{\partial E}{\partial\phi'}"> can be derived taking partial derivative of the Laplace-encoded free energy (TODO link to formula) and <img src="https://latex.codecogs.com/png.latex?%5Cdpi%7B120%7D%20%5Cinline%20%5Cfrac%7Bd%5Cphi%27%7D%7Bda%7D" alt="\frac{d\phi'}{da}"> term is known as the inverse model. For our agent it is equal to *1* as it can set the temperature change directly. This way, the minimisation of free energy through action can be written as:

<img src="https://latex.codecogs.com/png.latex?%5Cdpi%7B120%7D%20%5Cbegin%7Bmatrix%7D%20%5Cdot%7Ba%7D%20%3D%20-%5Ckappa_%7B%5Calpha%7D%20%5Cast%201%20%5Cast%20%5Cfrac%7B%5Cvarepsilon_%7Bz%5B1%5D%7D%7D%7B%5Csigma_%7Bz%5B1%5D%7D%7D%20%5C%5C%20%5Cdot%7Ba%7D%20%3D%20-%5Ckappa_%7B%5Calpha%7D%20%5Cfrac%7B%5Cvarepsilon_%7Bz%5B1%5D%7D%7D%7B%5Csigma_%7Bz%5B1%5D%7D%7D%20%5C%5C%5Cend%7Bmatrix%7D" alt="\begin{matrix}
\dot{a} = -\kappa_{\alpha} \ast 1 \ast \frac{\varepsilon_{z[1]}}{\sigma_{z[1]}} \\
\dot{a} = -\kappa_{\alpha} \frac{\varepsilon_{z[1]}}{\sigma_{z[1]}}
\\\end{matrix}">


#### Results
From the provided simulation (Figure 1) it can be observed that an agent can effectively deal with changes of temperature (both constant and sudden) and maintain itself in a viable interval for most of the environmental disturbances. The twist comes from the fact that at time steps from 201 to 250 an agent experiences a change of -6 °C per step, while it can only regulate the temperature by +5.8 °C per step. This means, the temperature of an agent will be dropping (-0.2 °C per step) despite its affords, and eventually will go out of the viable boundaries (be less than 20 °C). Effectively and sadly, our agent would cease to exist.

![Figure 1.](images/interoceptive_agent.png?raw=true)

*Figure 1. Simple interoceptive-only agent. An agent is shown to be able to regulate its temperature in principle. Despite this, it fails to do so when the temperature is dropping faster (steps 200 to 250) than its physiological ability to heat itself. In the simulated environment our an agent would cease to exist.*

### Adding exteroception
#### Description
As mentioned above, this project is inspired in (and roughly follows the) hierarchical model of active inference, presented by Pezzulo et at. in "Active Inference, homeostatic regulation and adaptive behavioural control". While an agent would die in the simulated world acting purely on its interoceptive inference, the hope should come from implementing (a next hierarchical level of) exteroception. It is hypothesised that this should allow an agent to have an unconditioned (autonomic) reflex: when provided with an exteroceptive cue (e.g. change in light), an agent should make it's temperature higher *in advance* in order to survive the following drop (or rise) of the temperature. Such next level should provide the underlying interoceptive layer with a different generative model (new settling point), altering this way the underlying interoceptive behaviour. In other words, an agent feelings of cold and hot are not absolute, but dictated by the higher (exteroceptive) level of the hierarchy, allowing it to be more adaptive.

To implement this proposal, we extend the world to include a new dynamics: a change in light over time <img src="https://latex.codecogs.com/png.latex?%5Cinline%20%5Cdot%7BL%7D" alt='\dot{L}'> is followed (with some shift in time) by a change in temperature <img src="https://latex.codecogs.com/png.latex?%5Cinline%20%5Cdot%7BT%7D" alt='\dot{T}'>. While the change in temperature dynamics remains the same as in the first version of the world,
the following dynamics of the change in light is implemented:

<img src="https://latex.codecogs.com/png.latex?%5Cdpi%7B120%7D%20%5Cdot%7BL%7D%20%3D%20%5Cleft%5C%7B%20%5Cbegin%7Bmatrix%7D%200%2C%20%26%20step%20%5Cleq%20175%20%5C%5C%20-0.7%2C%20%26%20step%20%3E%20175%20%5Cleq%20225%20%5C%5C%200%2C%20%26%20step%20%3E%20225%20%5C%5C%20%5Cend%7Bmatrix%7D%20%5Cright." alt="\dot{L} = 
\left\{
\begin{matrix}
0, & step \leq 175 \\
-0.7, & step > 175 \leq 225 \\ 
0, & step > 225 \\
\end{matrix}
\right.">

As it can be seen, the drop in light (from time steps 175 to 225) now indicates the further (from times steps 200 to 250) drop in temperature. It's worth to mention that here, for the sake of the simplicity of showing how the model works and the following discussion, we don't simulate such dynamics for all changes in temperature that our agent experiences throughout the simulation, but focus on the provided example. 

#### Model
Now, in order to show how our agent can use this new information available to it, we extend an agent with the exteroceptive layer that perceives the change of light in time: <img src="https://latex.codecogs.com/png.latex?%5Cinline%20%5Cdpi%7B120%7D%20%5Cphi%20%3D%20%5Cdot%7BT%7D" alt="\phi = \dot{T}">. Again, here we skip the details of how exactly this information becomes available to an agent, but assume that there could be some underlying neural network (or brain) structure which is capable of performing this task. Next, a generative model of perception is given to an agent, with which it can infer which *desired temperature* generates the change in light. We assume there is a simple linear relationship our agent has learned during the evolution. It consists in agent's belief that at the desired temperature at the mean of the viable range (30 °C) it expects the change in light to be 0 and that a rise of a desired temperature to 1°C would correspond to a drop in change in light of 0.1 conventional units. Agent's belief about sensory data are then as:

<img src="https://latex.codecogs.com/png.latex?%5Cdpi%7B120%7D%20%5Cphi%20%3D%20g%28%5Cmu%29%20&plus;%20z%20%5Ctext%7B%2C%20where%20%7D%20g%28%5Cmu%29%20%5Cequiv%200.1%28-%5Cmu%20&plus;%2030%29" alt="\phi = g(\mu) + z \text{, where } g(\mu) \equiv 0.1(-\mu + 30)">

Here environmental variable <img src="https://latex.codecogs.com/png.latex?%5Cdpi%7B120%7D%20%5Cinline%20%5Cmu" atl="\mu"> represents the desired temperature and we consider only dynamics of the first order. Maybe the most crucial fact we want to underline is that our agent does not have any preference over the environmental variable. In other words, the generative model for environmental dynamics can be ignored -- an agent only cares about inferring the correct desired temperature. We can then discard model prediction errors <img src="https://latex.codecogs.com/png.latex?%5Cinline%20%5Cdpi%7B120%7D%20%5Cvarepsilon_%7Bz%5Bi%5D%7D" alt="\varepsilon_{z[i]}"> completely, which would have the same effect if the model prediction errors would be given an extremely low precision (Buckley et al., 2017). This layer becomes more close in this sense to the simple perceptual inference through "least mean square estimation on sensory data" (Buckley et al., 2017). Laplace-encoded free energy, error terms and recognition dynamic of the agent would be then:

*Laplace-encoded energy:*

<img src="https://latex.codecogs.com/png.latex?%5Cdpi%7B120%7D%20E%28%5Cwidetilde%7B%5Cmu%7D%2C%20%5Cwidetilde%7B%5Cphi%7D%29%20%3D%20%5Cfrac%7B1%7D%7B2%7D%20%5Cfrac%7B%7B%5Cvarepsilon_%7Bz%5B0%5D%7D%7D%5E%7B2%7D%7D%7B%7B%5Csigma_%7Bz%5B0%5D%7D%7D%5E%7B2%7D%7D" alt="E(\widetilde{\mu}, \widetilde{\phi}) = 
\frac{1}{2}
\frac{{\varepsilon_{z[0]}}^{2}}{{\sigma_{z[0]}}^{2}}">

*where error term is:*

<img src="https://latex.codecogs.com/png.latex?%5Cdpi%7B120%7D%20%5Cvarepsilon_%7Bz%5B0%5D%7D%20%3D%20%5Cphi%20-%200.1%28-%5Cmu%20&plus;%2030%29" alt="\varepsilon_{z[0]} = \phi - 0.1(-\mu + 30)">

*and recognition dynamics is:*

<img src="https://latex.codecogs.com/png.latex?%5Cdpi%7B120%7D%20%5Cdot%7B%5Cmu%7D%20%3D%20%5Cmu%27%20-%20%5Ckappa_%7B%5Calpha%7D%5Cleft%20%5B%200.1%5Cfrac%7B%5Cvarepsilon_%7Bz%5B0%5D%7D%7D%7B%5Csigma_%7Bz%5B0%5D%7D%7D%20%5Cright%20%5D" alt="\dot{\mu} = -\kappa_{\alpha}\left [
0.1\frac{\varepsilon_{z[0]}}{\sigma_{z[0]}}
\right ]">

Recall that the equation of environmental dynamic **[TODO link to equation]** of our simple interoceptive agent already allows to set an arbitrary desired temperature <img src="https://latex.codecogs.com/png.latex?%5Cdpi%7B120%7D%20%5Cinline%20T_%7Bdesire%7D" alt="T_{desire}"> instead of a constant value. Now the inferred at the implemented exteroception layer desired temperature is effectively passed to this lower interoception layer providing it with a settling point and setting this way an environmental model of our agent in a hierarchical way **[TODO rephrase]**.

A schematic representation of an agent is given in Figure 2.

![Figure 2.](images/exteroceptive_layer_diagram.png)

*Figure 2. A schematic representation of the agent with two layers: exteroceptive and underlying interoceptive layer. While interoceptive layer does all the 'hard job' of actually maintaining a temperature of an agent, exteroceptive layer infers the desired temperature based on the exteroceptive (change in light) information. This gives an agent more information about the world (and, importantly, information that can be obtained only from the external environment) while it still recruits (and reuses) an existing interoceptive model to maintain homeostasis.*

#### Results

The provided simulation (Figure 2) shows, how an agent can now effectively survive the drop of temperature by making its own temperature higher *in advance* once the luminosity starts to drop. Effectively, an agent now will survive in this world -- the task that was impossible with interoceptive inference only.

![Figure 3.](images/exteroceptive_passive_agent.png)

*Figure 3. An agent with exteroception. The world where an agent lives is assumed to experience a drop in light before temperature starts to drop and vise versa. An agent is extended to infer the desired temperature through the change in light. When light start to drop from the timestep 175, the desired temperature of the agent grows. This allows the agent to survive the following drop in temperature from the time steps 200 to 250.*

### Adding active exteroception
#### Description
Pezzulo et at. have proposed, that "at the higher levels of the hierarchy ... representations become *amodal or multimodal* – providing descending predictions in the exteroceptive, autonomic and proprioceptive domains". This extension aims to roughly implement this idea and show it's viability. 

While our agent already has interoceptive and exteroceptive sensors, it can only act interoceptively (by setting the desired temperature based on exteroception and setting it's temperature change based on interoception). We can easily imagine a world, where adding exteroceptive action could be beneficial for our agent and which would make it more adaptive (an evolution would definitely do so eventually). We can now assume an agent lives in water environment. In this environment it observes more sunlight in warmer places (closer to the light) and less sunlight in colder places (further from the light). Now an agent equipped with this simple relationship thought a generative model show be able to act in the world and find better temperature regimes acting exteroceptively. In other words, it would seek to find such exteroceptive dynamics (change in light) that would better explain its brain variable (temperature change) through acting (setting the change in light). Here two things are worth a more detailed explanation. First, the right generative model would be such, that encodes the inverse relationship between the internal temperature change and change in light. This way our agent would seek darker places (less light) when its body gets hotter and vise versa. Second, and more importantly, it seems there is a big assumption when we say that the agent can change the light directly. Indeed, an agent is actually moving up and down in the water, which is what changing the light intensity. Out point here is that the agent (to some extent, see *Next steps*) does not need to know *how* it is changing the light intensity in order to control it! It only need to know *that* it has the ability to change the intensity of light. Now, how is it really changed is the task of the (underlying) reflex arc. While this reflex arc is out of the scope of the simulation at this step, it's important to stress that once the right command is given (from the higher level of the hierarchy), such reflex arc will perform it, leading, effectively, to the change in lighting. Summarising, an organism does not really need to know *how* the change in light it happens to *make* it happen at this level of abstraction.

#### Model
As proposed above, we extend an agent with a generative model of how its change in temperature <img src="https://latex.codecogs.com/png.latex?%5Cinline%20%5Cdpi%7B120%7D%20%7B%5Cmu%5E%7Bi%7D%7D%27" alt="{\mu^{i}}'"> generates the change in light over time <img src="https://latex.codecogs.com/png.latex?%5Cinline%20%5Cdot%7BL%7D" alt='\dot{L}'>. We assume here that an agent has already learn (e.g. through evolution) that a change in light generates the change in temperature in a linear way: a rise change in temperature by *1°C* corresponds to drop in light by 1 conventional unit. It can be observed that the model is *inverse* by its nature. Indeed this makes sense as if an agent experiences a rise in temperature it would seek less light: going deeper will eventually make its temperature drop (and this is something an agent desires):

<img src="https://latex.codecogs.com/png.latex?%5Cdpi%7B120%7D%20%5Cphi%20%3D%20g%28%5Cmu%29%20&plus;%20z%20%5Ctext%7B%2C%20where%20%7D%20g%28%5Cmu%29%20%5Cequiv%20-%7B%5Cmu%5E%7Bi%7D%7D%27" alt="\phi = g(\mu) + z \text{, where } g(\mu) \equiv -{\mu^{i}}''">

Importantly, here we reuse the environmental variable <img src="https://latex.codecogs.com/png.latex?%5Cinline%20%5Cdpi%7B120%7D%20%7B%5Cmu%5E%7Bi%7D%7D%27" alt="{\mu^{i}}'"> (superscript *i* meaning interoceptive), namely the change in temperature which is already *provided* by the interoceptive layer of the hierarchy. In a sense, an agent *reuses* the recognition dynamics of the interoceptive layer. Laplace-encoded free energy, error terms and recognition dynamic of the agent would be then:

*Laplace-encoded energy:*

<img src="https://latex.codecogs.com/png.latex?%5Cdpi%7B120%7D%20E%28%5Cwidetilde%7B%5Cmu%7D%2C%20%5Cwidetilde%7B%5Cphi%7D%29%20%3D%20%5Cfrac%7B1%7D%7B2%7D%20%5Cleft%20%5B%20%5Cfrac%7B%7B%5Cvarepsilon_%7Bz%5B0%5D%7D%7D%5E%7B2%7D%7D%7B%7B%5Csigma_%7Bz%5B0%5D%7D%7D%5E%7B2%7D%7D%20&plus;%20%5Cfrac%7B%7B%5Cvarepsilon_%7Bw%5B0%5D%7D%7D%5E%7B2%7D%7D%7B%7B%5Csigma_%7Bw%5B0%5D%7D%7D%5E%7B2%7D%7D%20&plus;%20%5Cfrac%7B%7B%5Cvarepsilon_%7Bw%5B1%5D%7D%7D%5E%7B2%7D%7D%7B%7B%5Csigma_%7Bw%5B1%5D%7D%7D%5E%7B2%7D%7D%20%5Cright%20%5D" alt="E(\widetilde{\mu}, \widetilde{\phi}) = 
\frac{1}{2}
\left [ 
\frac{{\varepsilon_{z[0]}}^{2}}{{\sigma_{z[0]}}^{2}} +
\frac{{\varepsilon_{w[0]}}^{2}}{{\sigma_{w[0]}}^{2}} +
\frac{{\varepsilon_{w[1]}}^{2}}{{\sigma_{w[1]}}^{2}}
\right ]">

*where error term for exteroceptive sense of change in light is:*

<img src="https://latex.codecogs.com/png.latex?%5Cdpi%7B120%7D%20%5Cvarepsilon_%7Bz%5B0%5D%7D%20%3D%20%5Cphi%20-%20%28-%7B%5Cmu%5E%7Bi%7D%7D%27%29" alt="\varepsilon_{z[0]} = \phi - (-{\mu^{i}}')">

and model errors <img src="https://latex.codecogs.com/png.latex?%5Cinline%20%5Cdpi%7B120%7D%20%5Cvarepsilon_%7Bz%5Bi%5D%7D" alt="\varepsilon_{z[i]}"> and variances <img src="https://latex.codecogs.com/png.latex?%5Cinline%20%5Cdpi%7B120%7D%20%5Csigma_%7Bz%5Bi%5D%7D" alt="\sigma_{z[i]}"> are the same as in the interoceptive model.

To provide an agent with the inverse model, as before we need to define how free energy will change with action:

<img src="https://latex.codecogs.com/png.latex?%5Cdpi%7B120%7D%20%5Cdot%7Ba%7D%20%3D%20-%5Ckappa_%7B%5Calpha%7D%5Cleft%20%5B%20%5Cfrac%7Bd%5Cphi%7D%7Bda%7D%20%5Cfrac%7B%5Cpartial%20E%7D%7B%5Cpartial%5Cphi%7D%20%5Cright%20%5D" alt="\dot{a} = -\kappa_{\alpha}\left [ \frac{d\phi}{da} \frac{\partial E}{\partial\phi} \right ]">

This time the inverse model is <img src="https://latex.codecogs.com/png.latex?%5Cinline%20%5Cdpi%7B120%7D%20%5Cfrac%7Bd%5Cphi%7D%7Bda%7D" alt="\frac{d\phi}{da}"> and as before the first term <img src="https://latex.codecogs.com/png.latex?%5Cdpi%7B120%7D%20%5Cinline%20%5Cfrac%7B%5Cpartial%20E%7D%7B%5Cpartial%5Cphi%7D" alt="\frac{\partial E}{\partial\phi}"> is calculated as a partial derivate of the Laplace-encoded free energy over the sensory information. As for now we assume an agent can change the light directly ignoring *how* it is done (discussion and the solution of this assumption follow below), <img src="https://latex.codecogs.com/png.latex?%5Cinline%20%5Cdpi%7B120%7D%20%5Cfrac%7Bd%5Cphi%7D%7Bda%7D" alt="\frac{d\phi}{da}"> term becomes *1* and the dynamical update of the action can be formulated as:

<img src="https://latex.codecogs.com/png.latex?%5Cdpi%7B120%7D%20%5Cdot%7Ba%7D%20%3D%20-%5Ckappa_%7B%5Calpha%7D%20%5Cfrac%7B%5Cvarepsilon_%7Bz%5B0%5D%7D%7D%7B%5Csigma_%7Bz%5B0%5D%7D%7D" alt="\dot{a} = -\kappa_{\alpha} \frac{\varepsilon_{z[0]}}{\sigma_{z[0]}}">

#### Results

The results of an agent acting both interoceptively and exteroceptively are shown in Figure 4.

![Figure 4.](images/exteroceptive_active_agent.png)

*Figure 4. An agent with active exteroception. The world is assumed to be a water environment where the water is warmer closer to the light and vise versa. An agent already senses the changes in light from the previous implementation and already has the internal (recognition) dynamics to infer a change in temperature. Now, an agent is also able to infer how a change in temperature generates the change in light and acts in order to move in a right direction (e.g. if agent feels getting colder it will seek getting closer to the light). The problem of this implementation can be easily seen in both figures A (baseline) and B (slower learning rate): an agent does no know what part of the change in light is due to environment and what part corresponds to its own action. As the two models are trying to predict the change in light at the same moment (through desired temperature and through the change in temperature) an agent is not able to infer the correct desired temperature (c.f. Figure 2) and a correct action at the same time. While setting a slower learning rate for active exteroceptive process (Figure B) allows to tackle the problem partially, it should be still important for an agent to have the ability to separate this sensory information.*

#### Discussion
Importantly, the implementation of this version of the agent shows "how more complex controllers could have developed from earlier (less flexible) controllers" (Pezzulo et al.). Elegance here manifests in reusing the already existing exteroceptive sensations (change of the level of light) and already existing recognition dynamics (inferring the interoceptive *brain variable* -- a change in the organism's temperature). Indeed, this seems to us to be a good proof for the argument if favour of non-modular architectures versus traditional "classical sandwich" architectures ("The modularity of action and perception revisited using control theory and active inference"). Optimal control proposes the separation of optimal perception and optimal action modules which works from the engineering point of view, but it's difficult to imagine an agent that would have evolved such separate controllers in an effective manner (c.f. the problem of the hen and the egg). On contrary, our case shows that an agent can gradually evolve new behaviour, reusing (part of the) already existing controllers and (supposedly) corresponding neural structures in the brain and the body. This seems to be a more plausible implementation of how the evolution have worked out the emergence of more and more complex species. In other words, complex and effective perception does not arise from the necessity of control. Instead, perception and control developed (and are still evolving) *together* from the necessity of maintaining the organism's internal variables in a viable interval and the opportunities (and treats) of the environment and organism is situated in.

While the model is shown to be useful, it has an important restriction. Specifically, an agent does not know how much the sensed change in light corresponds to the environment (recall it's getting darker before the temperature start to fall) and how much of it is generated by its exteroceptive action (recall an agent can regulate the change of light by moving in the water up and down). One of the solutions comes from the control theory: we could add an *efference copy* of action. Having this copy an agent would know explicitly how much of the sensed change of light was generated by the action of the agent. It can be then subtracted from the sensed changed of light at exteroceptive layer inferring how desired temperature generates the change of light. When it's done, this layer would only predict the change of light generated by the environment (recall change generated by the environment = all change of light - change of light generated by the action of the agent). The problem is, this would lead us to the closed loop system that would accumulate the error through time as the agent does not really has the exact information about it's action. A plausible solution that comes in mind would be to make one layer (e.g. exteroceptive layer inferring light change from desired temperature) to predict the sensory data on the other layer (exteroceptive layer inferring light change form change in temperature). But the problem in this case is that either one of the layers would be dominating predictions of the other or they would be both competing for a better minimization of the error. In both cases, an organism would not know *why* it should chose to change the desired temperature or to act exteroceptively (changing the light change). The questions of either proprioception should be the solution or the precision modulation will be answered in the next version of the agent.

### Adding proprioception
As is was discussed above, our active exteroception agent is not able to *know* what part of the luminance change corresponds to the environment (and should affect its desired temperature) and what part corresponds to its own behaviour in this environment (and should result in agent seeking specific change in luminance).

As a solution to this problem we propose to give an agent a sense of proprioception. In this case, an agent senses a movement (TODO: acceleration?) of its *body*. The way the agent senses the change in light on the exteroceptive layer, inferring change in light through desired temperature and on a layer, inferring change in light through change in temperature (active exteroception) now changes. Desired temperature layer now receives a prediction (about change in light) from the active exteroceptive layer which is subtracted from the sense of change in light (as it is already predicted by the underlying layer). Similarly, active exteroceptive layer now receives only the error of prediction from the upper (inferring desired temperature) layer -- in other words, it senses only the change in light which is *cannot be predicted (explained away)* by the higher layer and needs to be predicted on this one. This way effectively allows an agent to accomplish the goal of separating the change in light in two underlying causes -- generated by the environment and generated by an agent itself -- in a predictive coding way. The results are shown in Figure 4, where it can be clearly seen that the agent is correctly inferring the desired temperature (cf. Figure 2) while also acting exteroceptively, changing its position in the environment and thus changing the desired level of light. I can be seen, that our agent now is more efficient in staying away from the boundaries of viability: by both resisting the change in temperature thought interoception and acting exteroceptively.

![Figure 5.](images/proprioceptive_agent.png)

*Figure 5. Proprioceptive agent with predictive coding. It is shown that an agent can now effectively differentiate what causes the change in light: environment or its own actions. This is done through proprioceptive layer generating prediction about change in light and applying predictive coding scheme between two exteroceptive layers rather than through an efference copy. The desired temperature is correctly inferred after timestep 175. After timestep 200 it can be observed how an agent regulates the temperature through acting in the world.*

#### Discussion
While the proposed scheme works, it's not entirely clear why an agent produces small action even after the temperature change settles (after step 250). It seems like an agent's action update deviates from the proprioception (error) update. While proprioceptive sensory error is 0 and predicted by the proprioceptive layer change in light is 0 as well, an agent is performing a small amount of action. This action produces the change in light that is then explained by the level, inferring the desired temperature. While this change in temperature is effective counter-acted by interoceptive action, it seems it should not be there from in the first place. Next step would be to find why this effect appears and how it should be eliminated.

![Figure 6.](images/action_error.png)

*Figure 6. While there is not error in proprioceptive prediction, an agent is still acting. This produces the change in luminance (and, therefore, temperature) and makes the agent act interoceptively to maintain its temperature. This effect is undesirable and should should be solved*

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
To see results for the proprioceptive agent, change `InteroceptiveAgent` to `ProprioceptiveAgent`.
