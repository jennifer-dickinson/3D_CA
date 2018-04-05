# Three Dimensional Collision Avoidance

The purpose of this program is to provide an easy way to simulate collision avoidance in autonomous unmanned aerial vehicles(UAV) and provide an easy to work with modular platform to implement and test collision avoidance algorithms.

```
    Copyright (C) 2017  Jennifer Salas

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
```


## Author
3D_CA was developed as part of the undergraduate research experience at Auburn University during the Summer 2016 SMART UAV research program.

The script was written by Jennifer Salas.

Email:[jennysalas@me.com](mailto:jennysalas@me.com)

## Running the script

To run, simply clone the repository and the run the ``` launch.py ``` file at root of the folder. For more information on commandline paramaters run ``` launch.py -h ``` or view the usage section at the bottom of ```README.md```.


### Dependencies
```
- Python 3.6.0
- Matplotlib 2.0.0
- FFMPEG 3.2.4

```
## File Overview

### Default Values: defaultValues.py
This file includes values for variables used throughout the program including physical constants used to model the planes in flight, simulator constants  such as number of plane and waypoints, and collision parameters.

### Launch file: launch.py
This file is used to launch simulation and displays the final status of all planes to the screen when finished

### Movement: simulator.py
This file contains the functions that every plane will use to model there own physical movement.

### Plane Generator: planes.py
This file contains the class definition of plane and functions to build plane objects. Each plane has an id, goal waypoint, and communicator

### Common functions: standardFuncs.py
This file holds functions used to setup the plane simulation environment, angle conversion functions, and telemetry retrieval.

### Video Output: animation.py
This file contains the method to export the simulated mission into video format. It currently represents the data in 2d format.

### Vector Math: vMath.py
This file contains the implementation for 3d vector objects to be used in the simulation.

## Package overview

### Algorithms
A directory of anti-collision algorithms.

### Logs
A simple directory that keeps holds log copies of previous simulations. Named by date and time.

### Maneuvers
A directory of non-collision-avoidance algorithms.

## Usage
```
launch.py [-h] [-c] [-ca] [-a] [-cd] [-s] [-p] [-w] [-l ] [-crd] [-cfd]
                 [-del] [-g ] [-maxa] [-minr] [-maxr] [-wpd] [-samplewp]
                 [-settings DISPLAY] [-seed SEED]
```
```
optional arguments:
  -a , -algorithm       [ ALGORITHM ] choose anti-collision algorithm of
                        'APF', or 'IPN', 'APF' by default
  -ca , -collision-avoidance 
                        [ True | False ] enable collision avoidance
                        algorithms, False by default
  -cd , -collision-detectance 
                        [ True | False ] UAVs will crash when in close
                        proximity of each other, True by default
  -cfd , -conflict-distance 
                        [ FLOAT ] set conflict distance, default is SPEED * 2
  -crd , -crash-distance 
                        [ FLOAT ] set crash distance in meters, 2.00m by
                        default
  -del , -delay         [ FLOAT ] number of seconds between calculations,
                        0.10s by default
  -g  , -grid           [ INT INT ] size of grid in meters, 100mx100m by
                        default
  -h, --help            show this help message and exit
  -l  , -location       [ LONGITUDE LATITUDE ] select a location to simulate,
                        default is 32.606°, -85.488° (Auburn University)
  -maxa , -max-elevation-angle 
                        [ FLOAT ] set the maximum angle of elevation in
                        degrees, 15° by default
  -maxr , -max-turn-radius 
                        [ FLOAT ] set the maximum turning radius inmeters
                        24.01m by default
  -minr , -min-turn-radius 
                        [ FLOAT ] set the minimum turning radius in meters,
                        28.64m by default
  -p , -planes          [ INT ] set number of planes, 10 planes by default
  -s , -speed           [ FLOAT ] set UAV speed in meters per second, 12.00m/s
                        by default
  -samplewp             use a sample set of 10 planes and 64 waypoints per
                        plane, otherwise random waypoints are generated for
                        assigned number of planes
  -seed SEED            [INT] Provide a seed to test previous results.
  -settings DISPLAY     display current settings
  -w , -waypoints       [ INT ] set number of waypoints, 10 waypoints by
                        default
  -wpd , -waypoint-distance 
                        [ INT ] the distance required to "reach" a waypoint,
                         2 meters by default
```