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
import random
import sys

import argumentsplitter
import planeSimulator


# import threading


def exceptionHandler(exception_type, exception, traceback):
    print("%s: %s\n" % (exception_type.__name__, exception))


sys.excepthook = exceptionHandler

def main():
    args = argumentsplitter.argParser()

    if args.seed:
        seed = args.seed
    else:
        seed = int(random.random() * 10 ** 5)

    # random.seed(seed)

    print("Simulating UAV flights using seed %i.... this may take a while.\n" % seed)

    # lock = threading.RLock()

    object = planeSimulator.PlaneCollection(args)

    # lock.acquire()

    # Not sure why, this is the only way to make sure the deconstructor is called for PlaneCollection class
    raise AttributeError("manually raised for PlaneCollection deconstructor")


if __name__ == '__main__':
    main()
