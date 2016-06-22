# Adjust bearing of plane & check if it is in loop

# Correct angle by finding difference in current bearing and elevation to target bearing and elevation



def correct_angle(plane):
    diffBear = plane.cBearing-plane.tBearing
    diffElev = plane.cElevation-plane.tBearing


