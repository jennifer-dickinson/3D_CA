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
