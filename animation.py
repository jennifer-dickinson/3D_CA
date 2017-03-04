"""
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
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.animation as manimation

import standardFuncs
import defaultValues
import sys


def write(planes):
    maxlength = len(max(planes, key=len))

    sgrid = defaultValues.GRID_SIZE
    loc = defaultValues.OUR_LOCATION
    agrid = standardFuncs.generateGrid(sgrid[0] * 3, sgrid[1] * 3, loc)

    lLat = (agrid[0][0])
    uLat = (agrid[0][1])

    lLon = (agrid[1][0])
    uLon = (agrid[1][1])

    FFMpegWriter = manimation.writers['ffmpeg']
    metadata = dict(title='Movie Test', artist='Matplotlib',
                    comment='Movie support!')
    writer = FFMpegWriter(fps=15, metadata=metadata)

    fig = plt.figure()
    ax = plt.axes(xlim=(lLat, uLat), ylim=(lLon, uLon))

    n, = plt.plot([], [], 'bo')

    aLat = int((uLat - lLat) * standardFuncs.LATITUDE_TO_METERS) // 2
    aLon = int((uLon - lLon) * standardFuncs.LONGITUDE_TO_METERS) // 2
    plt.xticks([lLat, uLat], ["West\n%im" % -aLat, "East\n%im" % aLat])
    plt.yticks([lLon, uLon], ["South\n%im\n" % -aLon, "North\n%im\n" % aLon],
               rotation=90)
    plt.xlabel("Three Dimensional Collision Avoidance")

    fig.subplots_adjust(bottom=.15)

    print("")
    with writer.saving(fig, "writer_test.mp4", 100):
        for i in range(maxlength + 1):
            x0 = []
            y0 = []
            for plane in planes:
                if i >= len(plane):
                    point = plane[-1]
                    if point['wpflag']:
                        continue
                else:
                    point = plane[i]

                x0.append(point['Latitude'])
                y0.append(point['Longitude'])

            n.set_data(x0, y0)
            writer.grab_frame()

            message = "Generating video... %2.2f%%" % (i / maxlength * 100)
            sys.stdout.write('\r' + str(message) + ' ' * 20)
            sys.stdout.flush()  # important
    print("")


if '__main__' == __name__:
    write(defaultValues.samplepath)
