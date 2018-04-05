"""
    Copyright (C) 2018  Jennifer Salas

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
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation

import numpy

import standardFuncs
import defaultValues

def showPaths(planes):
    maxlength = len(max(planes, key=len))
    minlength = len(min(planes, key=len))

    sgrid = defaultValues.GRID_SIZE
    loc = defaultValues.OUR_LOCATION
    agrid = standardFuncs.generateGrid(sgrid[0] + 300 , sgrid[1] + 300, loc)

    lLat = agrid[0][0]
    uLat = agrid[0][1]
    lLon = agrid[1][0]
    uLon = agrid[1][1]

    fig = plt.figure()
    ax = plt.axes(xlim=(lLat, uLat), ylim=(lLon, uLon))

    planePlots = [plt.plot([], [], "bo")[0] for _ in range(len(planes))]

    aLat = int((uLat - lLat) * standardFuncs.LATITUDE_TO_METERS) // 2
    aLon = int((uLon - lLon) * standardFuncs.LONGITUDE_TO_METERS) // 2
    plt.xticks([lLat, uLat], ["West\n%im" % -aLat, "East\n%im" % aLat])
    plt.yticks([lLon, uLon], ["South\n%im\n" % -aLon, "North\n%im\n" % aLon],
               rotation=90)
    plt.xlabel("Three Dimensional Collision Avoidance")

    fig.subplots_adjust(bottom=.15)

    def init():
        for planeP in planePlots:
            planeP.set_data([],[])
        return lines

    for plane in planes:
        while len(plane) < maxlength:
            plane.append(plane[-1])


    def animate(i):
        for j,planePlot in enumerate(planePlots):
            planePlot.set_markerfacecolor('k' if i[j]["dead"] else 'b')
            planePlot.set_data(i[j]["Latitude"],i[j]["Longitude"])
            planePlot.set_marker((3,0,i[j]["bearing"]-90))

        return planePlots
    planeMat = numpy.array(planes).T

    print(planeMat.shape)

    ani = animation.FuncAnimation(fig, animate, planeMat, interval = 25, blit = True)
    plt.show()

if '__main__' == __name__:
    showPaths(defaultValues.samplepath)
