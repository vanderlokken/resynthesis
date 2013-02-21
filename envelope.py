import numpy


class Envelope:

    class Point:
        def __init__(self, time, value):
            self.time = time
            self.value = value

        def __repr__(self):
            return "(time={time:.3f}, value={value:.3f})".format(
                time=self.time, value=self.value)

    def __init__(self):
        self.__points = list()

    def add_point(self, new_point):
        for point in self.__points:
            if point.time == new_point.time:
                point.value = new_point.value
                return
        self.__points.append(new_point)

    def get_output(self, time_points):

        self.__points.sort(key=lambda point: point.time)

        x = numpy.fromiter((point.time for point in self.__points), numpy.float)
        y = numpy.fromiter((point.value for point in self.__points), numpy.float)

        return numpy.interp(time_points, x, y)
