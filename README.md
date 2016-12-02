# Three Dimensional Collision Avoidance

The purpose of this program is to provide an easy way to simulate centralized and decentralized collision avoidance in autonomous unmanned aerial vehicles(UAV) and provide an easy to work with modular platform to implement and test collision avoidance algorithms.

## Authors
3D_CA was developed as part of the undergraduate research experience at Auburn University during the Summer 2016 SMART UAV research program.

The script was written by Jennifer Salas with contributions by Patrick Perez and William McKnight.

## Running the script
This script is meant to be as diverse as possible and therefore has no restrictions on the operating system or external library dependencies, although if needed this may change in the future. The current version uses Python 2.6.9. Attempts to upgrade to 3.5 results in slowed performance when running in decentralized mode.

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

### Optional Arguments

```optional arguments:
  -h, --help            show this help message and exit
  -dc , -centralized    choose to run in centralized mode, True by default
  -ca , -collision-avoidance
                        [ True | False ] enable collision avoidance
                        algorithms, False by default
  -a , -algorithm       [ ALGORITHM ] choose anti-collision algorithm of
                        'APF', or 'IPN', 'APF' by default
  -cd , -collision-detectance
                        [ True | False ] UAVs will crash when in close
                        proximity of each other, True by default
  -s , -speed           [ FLOAT ] set UAV speed in meters per second, 12.00m/s
                        by default
  -p , -planes          [ INT ] set number of planes, 10 planes by default
  -w , -waypoints       [ INT ] set number of waypoints, 10 waypoints by
                        default
  -l  , -location       [ LONGITUDE LATITUDE ] select a location to simulate,
                        default is 32.606°, -85.488° (Auburn University)
  -crd , -crash-distance
                        [ FLOAT ] set crash distance in meters, 2.00m by
                        default
  -cfd , -conflict-distance
                        [ FLOAT ] set conflict distance, default is SPEED * 2
  -del , -delay         [ FLOAT ] number of seconds between calculations,
                        0.20s by default
  -g  , -grid           [ INT INT ] size of grid in meters, 100mx100m by
                        default
  -maxa , -max-elevation-angle
                        [ FLOAT ] set the maximum angle of elevation in
                        degrees, 22.5° by default
  -minr , -min-turn-radius
                        [ FLOAT ] set the maximum turning radius in meters,
                        28.64m by default
  -wpd , -waypoint-distance
                        [ INT ] set the number of waypoints assigned to each
                        plane, 2 by default
  -samplewp             use a sample set of 10 planes and 64 waypoints per
                        plane, otherwise random waypoints are generated for
                        assigned number of planes
  -settings             display current settings```