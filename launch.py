import argumentsplitter
import planeSimulator


def main():
    args = argumentsplitter.argParser()

    print("Simulating UAV flights.... this may take a while.")

    planeSimulator.PlaneCollection(args)


if __name__ == '__main__':
    main()
