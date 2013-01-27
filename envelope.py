import numpy


class Envelope:

    class Point:
        def __init__(self, time, value):
            self.time = time
            self.value = value

        def __repr__(self):
            return "(time=%f, value=%f)" % (self.time, self.value)

    def __init__(self, initial_value=1.0):

        self.__points = list()
        self.add_point(Envelope.Point(0, initial_value))

    def add_point(self, point):

        self.__points.append(point)

    def get_output(self, sample_count, sample_duration):

        self.__points.sort(key=lambda point: point.time)

        x = numpy.fromiter((point.time for point in self.__points), numpy.float)
        y = numpy.fromiter((point.value for point in self.__points), numpy.float)

        time_points = numpy.linspace(0, sample_count * sample_duration, sample_count)

        return numpy.interp(time_points, x, y)
