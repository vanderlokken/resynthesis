from StringIO import StringIO

import numpy

from algorithm import GeneticAlgorithm, Population
from sound import get_sound_factory


def resynthesize(reference_pcm_audio):

    algorithm = GeneticAlgorithm()
    algorithm.generations_without_improvement_limit = 20
    algorithm.score_improvement_threshold = 0.0025

    best_score = None
    pcm_audio = None
    sounds = []

    for index in xrange(20):

        genome_factory = get_sound_factory(reference_pcm_audio, pcm_audio)
        population = Population(genome_factory, 80)
        best_sound = algorithm.run(population)

        if best_score is not None and best_sound.score < best_score:
            print "The algorithm failed to produce a better sound on this step"
            break

        print best_sound
        pcm_audio = best_sound.to_pcm_audio()
        pcm_audio.to_wave_file("debug%d.wav" % index)

        best_score = best_sound.score

        sounds.append(best_sound)

    construct_csound_file(sounds, pcm_audio)

    return pcm_audio


def construct_csound_file(sounds, pcm_audio, filename="out.csd"):

    signed_short_max = 2**15 - 1

    sound_duration = pcm_audio.duration
    sound_amplitude = pcm_audio.samples.max() / signed_short_max

    # We assume that a frequency of a partial with the maximal energy is a base
    # sound frequency

    def energy(sound):
        sound._base_pcm_audio = None
        return numpy.abs(sound.to_pcm_audio().samples).sum()

    sounds = sorted(sounds, key=energy, reverse=True)

    sound_frequency = sounds[0]._frequency

    # Construct instrument code
    code_stream = StringIO()

    print >> code_stream, "aResult = 0"

    for sound in sounds:
        signal = (
            "aSignal oscils {amplitude}, iFrequency * {freqency_ratio:.2f}, "
            "{normalized_phase:.2f}"
            .format(
                amplitude=1,
                freqency_ratio=sound._frequency / sound_frequency,
                normalized_phase=sound._phase / (2 * numpy.pi)
            )
        )
        print >> code_stream, signal

        sound._sort_amplitude_envelope_points()

        envelope = "aEnvelope linseg 0"
        previous_point_time = 0
        for point in sound._amplitude_envelope_points:
            envelope = (
                "{envelope}, "
                "iDuration * {duration:.3f}, "
                "iAmplitude * {amplitude:.3f}"
                .format(
                    envelope=envelope,
                    duration=point.time / sound_duration - previous_point_time,
                    amplitude=(point.value / signed_short_max) / sound_amplitude
                )
            )
            previous_point_time = point.time / sound_duration
        envelope = "{envelope}, iDuration * {duration:.3f}, 0".format(
            envelope=envelope, duration=1 - previous_point_time)
        print >> code_stream, envelope

        print >> code_stream, "aResult = aResult + aSignal * aEnvelope"

    print >> code_stream, "out aResult"

    instrument_code = code_stream.getvalue()

    code_stream.close()

    # Construct score
    score = "i 1 0 {duration:.2f} {amplitude:.2f} {frequency:.1f}".format(
        duration=sound_duration,
        amplitude=sound_amplitude,
        frequency=sound_frequency)

    with open("template.csd", "r") as template_file:
        template = template_file.read()

    output = template
    output = output.replace("; %instrument_code%", instrument_code)
    output = output.replace("; %score%", score)

    with open(filename, "w") as output_file:
        print >> output_file, output
