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

import argumentsplitter
import planeSimulator


def main():
    args = argumentsplitter.argParser()

    if args.seed:
        seed = args.seed
    else:
        seed = random.random()

    random.seed(seed)

    print("Simulating UAV flights using seed %f.... this may take a while." % seed)

    object = planeSimulator.PlaneCollection(args)
    # try:

    # Not sure why, this is the only way to make sure the deconstructor is called for PlaneCollection class
    raise AttributeError


if __name__ == '__main__':
    main()
