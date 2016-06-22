I guess I should start putting stuff here.....

General Information:

test.py is just a file for testing different functions before actually implementing them. So far it's the only place
where things are actually being done.

main.py is *supposed* to be the initializer file. So far it just contains a few key variables and a gridgenerator.

    generateGrid(gridSize, Location)
        GridSize is in meters
        Location is list with latitude and longitude in degrees

        Returns a list for

defaultValues.py contains... you guessed it... default values.



standardFunctions.py has some pretty standard functions. You will use them throughout movement and collision avoidance
simulations

    to_cartesian(angle) converts an angle in degrees to the cartesian system

    to_cardinal(angle) converts an angle in degrees to the cardinal system (N, W, S, E, etc)
