# Car and Pedestrian Simulation

A client-server web application that runs a simulation of a car and pedestrian in a 2d world, generated using the model checking tool *Prism*.

## Installation

Requirements
  - Python 3
  - Node JS
  - Node Package Manager
  - Prism Model Checker

Begin by cloning this repository, or otherwise copying its contents onto the server.

Then, install the various required packages available through the package manager (python3, nodejs, npm).

Next, install the prism model checker, following the instructions given by the website: https://www.prismmodelchecker.org/download.php

For Prism to work, it may be necessary to install the Java JDK if it is not already available. Whether Prism is working can be verified by running the `prism` executable found in the bin directory.

After that, run the command `npm install` from the main directory

Finally, put the path to the Prism executable found in the bin directory into the config.txt file.