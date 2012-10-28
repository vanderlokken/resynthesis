from pyevolve.GSimpleGA import GSimpleGA

from sound import Sound


def resynthesize(reference_pcm_audio):
    sound = Sound(reference_pcm_audio)

    # v = 0.013 * 2**15
    # sound._frequency = 391
    # sound._time_points = [0, 0.6, 0.8, 1, 1]
    # sound._amplitudes = [v, v/2, v/4, 0, 0]
    # print sound
    # print Sound._evaluate(sound)
    # return sound.to_pcm_audio()

    algorithm = GSimpleGA(sound)
    algorithm.setPopulationSize(60)
    algorithm.setGenerations(40)
    algorithm.setCrossoverRate(0.8)
    algorithm.setMutationRate(0.2)
    algorithm.evolve(freq_stats=1)
    best_sound = algorithm.bestIndividual()

    # print best_sound

    return best_sound.to_pcm_audio()
