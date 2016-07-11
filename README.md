# Three Dimensional Collision Avoidance

The purpose of this program is to provide an easy way to simulate centralized and decentralized collision avoidance in autonomous unmanned aerial vehicles(UAV) and provide an easy to work with modular platform to implement and test collision avoidance algorithms.

## File Overview

### Centralized Communication : centralizedCommList.py
This file includes the methods for creating a centralized plane communication synchronizer. In centralized communication a single synchrnizer will keep track of the telemetry of all plane objects and perform all collision avoidance tasks.

### decentralizedComm : decentralizedComm.py
This file includes the methods for creating a decentralized plane communication synchronizer. In decentralized communication every indivudal plane will maintain their own map of other plane objects and perform all collision avoidance tasks for themselves.

### Default Values: defaultValues.py
This file includes values for variables used throughout the program including physical constants used to model the planes in flight, simulator constanst such as number of plane and waypoints, and collision parameters.

### Launch file: launch.py
This file is used to launch simulation and displays the final status of all planes to the screen when finished

### movementSimulator.py
This file contains the functions that every plane will use to model there own physical movement.

### Plane Generator: planeGenerator.py
This file contains the class definition of plane and functions to build plane objects. Each plane has an id, goal waypoint, and communicator

### Common functions: standardFuncs.py
This file holds funtions used to setup the plane simulation environment, angle conversion functions, and telemetry retrieval.


### Vector Math: vMath.py
This file contains the implementation for 3d vector objects to be used in the simulation.

##Package overview

###Algorithms

###Logs

###maneuvers
