import random

import numpy

from ga_sound_source import SoundSource
from pcm_audio import PcmAudio


class Sound:

    _max_volume = 2**15 - 1

    def __init__(self):
        pass

    @staticmethod
    def spawn():
        new_sound = Sound()
        new_sound._sound_sources = [SoundSource.spawn(), SoundSource.spawn()]
        new_sound._master_volume = random.random() * Sound._max_volume
        return new_sound

    def cross(self, other):
        new_sound = Sound()
        new_sound._sound_sources = [first_source.cross(second_source) for first_source, second_source in zip(self._sound_sources, other._sound_sources)]
        new_sound._master_volume = (self._master_volume + other._master_volume) * 0.5
        return new_sound

    def mutate(self):
        new_sound = Sound()
        new_sound._sound_sources = [source.mutate() for source in self._sound_sources]
        new_sound._master_volume = (self._master_volume + random.random() * Sound._max_volume) * 0.5
        return new_sound

    def to_pcm_audio(self, reference_pcm_audio):

        oscillators = [source.oscillator for source in self._sound_sources]
        envelopes = [source.envelope(reference_pcm_audio.duration) for source in self._sound_sources]

        sample_count = len(reference_pcm_audio.samples)
        sample_duration = reference_pcm_audio.duration / sample_count

        samples = []

        for oscillator, envelope in zip(oscillators, envelopes):
            if len(samples) == 0:
                samples = oscillator.get_output(sample_count, sample_duration) * envelope.get_output(sample_count, sample_duration)
            else:
                samples += oscillator.get_output(sample_count, sample_duration) * envelope.get_output(sample_count, sample_duration)

        samples = numpy.clip(samples * self._master_volume, -self._max_volume, self._max_volume)

        return PcmAudio(reference_pcm_audio.sampling_rate, list(samples))
