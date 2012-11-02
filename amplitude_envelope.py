import numpy


class AmplitudeEnvelope:

    def __init__(self, amplitude=1.0):

        self.__points = list()
        self.add_point(0, amplitude)

    def add_point(self, time, amplitude):

        self.__points.append((time, amplitude))

    def get_output(self, sample_count, sample_duration):

        self.__points.sort(key=lambda point: point[0])

        x = numpy.array([point[0] for point in self.__points])
        y = numpy.array([point[1] for point in self.__points])

        time_points = numpy.linspace(0, sample_count * sample_duration, sample_count)

        return numpy.interp(time_points, x, y)
