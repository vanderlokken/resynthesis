from algorithm import GeneticAlgorithm, Population
from sound import get_sound_factory


def resynthesize(reference_pcm_audio):

    algorithm = GeneticAlgorithm()
    algorithm.generations_without_improvement_limit = 20
    algorithm.score_improvement_threshold = 0.0025

    best_score = None
    pcm_audio = None

    for index in xrange(10):

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

    return pcm_audio
