import numpy
import scipy.fftpack

from genetic_algorithm import GeneticAlgorithm
from ga_sound import Sound


class Spectrum:

    def __init__(self, samples):

        amplitudes = scipy.fftpack.rfft(
            numpy.array(map(float, samples)) * numpy.hanning(len(samples)))

        self._magnitudes = numpy.abs(amplitudes)

    @property
    def magnitudes(self):
        return self._magnitudes


class SynthesisAlgorithm(GeneticAlgorithm):

    def __init__(self, reference_pcm_audio):
        self._reference_pcm_audio = reference_pcm_audio
        self._reference_spectrum_list = self._spectrum_list(reference_pcm_audio)

    @staticmethod
    def _spectrum_list(pcm_audio, window_size=4096):

        window_count = len(pcm_audio.samples) / window_size
        window = lambda index: \
            pcm_audio.samples[index * window_size : (index + 1) * window_size]

        return [Spectrum(window(index)) for index in range(window_count)]

    def _fit(self, sound):

        generated_pcm_audio = sound.to_pcm_audio(self._reference_pcm_audio)
        generated_spectrum_list = self._spectrum_list(generated_pcm_audio)

        ranks = []

        for spectrum1, spectrum2 in zip(
                self._reference_spectrum_list, generated_spectrum_list):

            similarity =\
                numpy.minimum(spectrum1.magnitudes * spectrum2.magnitudes, spectrum1.magnitudes**2).sum()

            difference =\
                (numpy.abs(spectrum2.magnitudes - spectrum1.magnitudes)*spectrum2.magnitudes).sum()

            ranks.append(similarity - difference)

        return numpy.average(ranks)

    def report(self, sound):

        generated_pcm_audio = sound.to_pcm_audio(self._reference_pcm_audio)
        generated_spectrum_list = self._spectrum_list(generated_pcm_audio)

        number = 0

        ranks = []

        for spectrum1, spectrum2 in zip(
                self._reference_spectrum_list, generated_spectrum_list):

            spectrum = open("report/%d.csv" % number, "w")
            print >> spectrum, ";".join(str(v) for v in spectrum1.magnitudes)
            print >> spectrum, ";".join(str(v) for v in spectrum2.magnitudes)
            spectrum.close()

            number += 1

            similarity =\
                numpy.minimum(spectrum1.magnitudes * spectrum2.magnitudes, spectrum1.magnitudes**2).sum()

            difference =\
                (numpy.abs(spectrum2.magnitudes - spectrum1.magnitudes)*spectrum2.magnitudes).sum()

            ranks.append(similarity - difference)


        rf = open("report/ratings.txt", "w")
        for i, (r) in enumerate(ranks):
            print >> rf, r
        print >> rf, "avg:", numpy.average(ranks)
        rf.close()

    @staticmethod
    def _spawn():
        return Sound.spawn()

    @staticmethod
    def _cross(first_sound, second_sound):
        return first_sound.cross(second_sound)

    @staticmethod
    def _mutate(sound):
        return sound.mutate()


def synthesize(reference_pcm_audio):

    # sa = SynthesisAlgorithm(reference_pcm_audio)
    # so = Sound.spawn()
    # so._master_volume = 0.002 * Sound._max_volume
    # so._sound_sources[0]._frequency = 391
    # so._sound_sources[0]._adsr._times = [0, 0.6, 0.8, 1]
    # so._sound_sources[0]._adsr._amplitudes = [1, 1, 1, 0]
    # so._sound_sources[1]._frequency = 195
    # so._sound_sources[1]._adsr._times = [0, 0.25, 0.5, 0.5]
    # so._sound_sources[1]._adsr._amplitudes = [0.0, 0, 0, 0]

    # sa.report(so)

    # return so.to_pcm_audio(reference_pcm_audio)

    algorithm = SynthesisAlgorithm(reference_pcm_audio)

    best = algorithm()

    algorithm.report(best)

    return best.to_pcm_audio(reference_pcm_audio)
