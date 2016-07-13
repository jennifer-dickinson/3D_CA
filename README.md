# Three Dimensional Collision Avoidance

The purpose of this program is to provide an easy way to simulate centralized and decentralized collision avoidance in autonomous unmanned aerial vehicles(UAV) and provide an easy to work with modular platform to implement and test collision avoidance algorithms.

## Authors
3D_CA was developed as part of the undergraduate research experience at Auburn University during the Summer 2016 SMART UAV research program.

The script was written by Jennifer Salas with contributions by Patrick Perez and William McKnight.

## Running the script
This script is meant to be as diverse as possible and therefore has no restrictions on the operating system or external library dependencies, although if needed this may change in the future. The current version uses Python 3.5 and will not work with versions below 3.0 due to the queue module.

To run, simply clone the repository and the run the launch.py file at root of the folder.

## File Overview

### Centralized Communication : centralizedCommList.py
This file includes the methods for creating a centralized plane communication synchronizer. In centralized communication a single synchronizer will keep track of the telemetry of all plane objects and perform all collision avoidance tasks.

### decentralizedComm : decentralizedComm.py
This file includes the methods for creating a decentralized plane communication synchronizer. In decentralized communication every individual plane will maintain their own map of other plane objects and perform all collision avoidance tasks for themselves.

### Default Values: defaultValues.py
This file includes values for variables used throughout the program including physical constants used to model the planes in flight, simulator constants  such as number of plane and waypoints, and collision parameters.

### Launch file: launch.py
This file is used to launch simulation and displays the final status of all planes to the screen when finished

### Movement: movementSimulator.py
This file contains the functions that every plane will use to model there own physical movement.

### Plane Generator: planeGenerator.py
This file contains the class definition of plane and functions to build plane objects. Each plane has an id, goal waypoint, and communicator

### Common functions: standardFuncs.py
This file holds functions used to setup the plane simulation environment, angle conversion functions, and telemetry retrieval.

### Communication Modules

#### centralizedComm.py


#### decentralizedComm.py


### Vector Math: vMath.py
This file contains the implementation for 3d vector objects to be used in the simulation.

## Package overview

### Algorithms

### Logs

### Maneuvers
