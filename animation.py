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
    agrid = standardFuncs.generateGrid(sgrid[0], sgrid[1], loc)

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

    center, = plt.plot([uLat - lLat], [uLon - lLon], '+', mew=10, ms=20)

    l, = plt.plot([], [], 'ro')

    # plt.axis('equal')
    plt.xticks([lLat, uLat], ["West\n0m", "East\n%im" % int((uLat - lLat) * standardFuncs.LATITUDE_TO_METERS)])
    plt.yticks([lLon, uLon], ["South\n0m", "North\n%im" % int((uLon - lLon) * standardFuncs.LONGITUDE_TO_METERS)],
               rotation=90)
    plt.xlabel("Three Dimensional Collision Avoidance")
    # plt.ylabel()

    fig.subplots_adjust(bottom=.15)

    x0, y0 = 0, 0
    with writer.saving(fig, "writer_test.mp4", 100):
        for i in range(maxlength):
            x0 = []
            y0 = []
            for plane in planes:
                if i >= len(plane):
                    point = plane[-1]
                else:
                    point = plane[i]

                x0.append(point['Latitude'])
                y0.append(point['Longitude'])

            l.set_data(x0, y0)
            writer.grab_frame()

            message = "Generating video... %2.2f%%" % ((i + 1) / maxlength * 100)

            sys.stdout.write('\r' + str(message) + ' ' * 20)
            sys.stdout.flush()  # important


if '__main__' == __name__:
    write(defaultValues.samplepath)
