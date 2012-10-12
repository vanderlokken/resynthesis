import random

from ga_adsr import Adsr
from oscillator import Oscillator


class SoundSource:

    def __init__(self):
        pass

    @staticmethod
    def spawn():
        new_sound_source = SoundSource()
        new_sound_source._frequency = 20 + random.random() * 1000
        new_sound_source._adsr = Adsr.spawn()
        return new_sound_source

    def cross(self, other):
        new_sound_source = SoundSource()
        new_sound_source._frequency = (self._frequency + other._frequency) * 0.5
        new_sound_source._adsr = self._adsr.cross(other._adsr)
        return new_sound_source

    def mutate(self):
        new_sound_source = SoundSource()
        new_sound_source._frequency = self._frequency * 0.5 + (20 + random.random() * 1000) * 0.5
        new_sound_source._adsr = self._adsr.mutate()
        return new_sound_source

    @property
    def oscillator(self):
        return Oscillator(self._frequency)

    def envelope(self, overall_time):
        return self._adsr.envelope(overall_time)
