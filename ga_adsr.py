import random

from amplitude_envelope import AmplitudeEnvelope


class Adsr:

    def __init__(self):
        pass

    @staticmethod
    def spawn():
        new_adsr = Adsr()
        new_adsr._times = sorted([random.random() for _ in xrange(4)])
        new_adsr._amplitudes = [random.random() for _ in xrange(4)]
        return new_adsr

    def cross(self, other):
        new_adsr = Adsr()
        new_adsr._times = sorted([
            (first + second) * 0.5 for first, second in zip(self._times, other._times)])
        new_adsr._amplitudes = [
            (first + second) * 0.5 for first, second in zip(self._amplitudes, other._amplitudes)]
        return new_adsr

    def mutate(self):
        new_adsr = Adsr()
        new_adsr._times = sorted([
            time * 0.25 + random.random() * 0.75 for time in self._times])
        new_adsr._amplitudes = [
            amplitude * 0.5 + random.random() * 0.5 for amplitude in self._amplitudes]
        return new_adsr

    def envelope(self, overall_time):
        envelope = AmplitudeEnvelope(0)
        for time, amplitude in zip(self._times, self._amplitudes):
            envelope.add_point(time * overall_time, amplitude)
        return envelope
