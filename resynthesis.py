from pyevolve.GSimpleGA import GSimpleGA

from sound import Sound


def resynthesize(reference_pcm_audio):
    # sound = Sound(reference_pcm_audio)
    # sound._frequency = 390.6
    # sound._time_points = [0.056, 0.062, 0.074, 0.622, 0.895]
    # sound._amplitudes = [3660, 3720, 1106, 104, 17]
    # print sound
    # print "Rank: %.2f" % Sound._evaluate(sound)
    # pcm = sound.to_pcm_audio()

    pcm = None

    for _ in range(2):

        sound = Sound(reference_pcm_audio, pcm)

        algorithm = GSimpleGA(sound)
        algorithm.setPopulationSize(20)
        algorithm.setGenerations(50)
        algorithm.setCrossoverRate(0.8)
        algorithm.setMutationRate(0.25)
        algorithm.evolve(freq_stats=1)
        best_sound = algorithm.bestIndividual()

        print best_sound
        print "Rank: %.2f" % Sound._evaluate(best_sound)

        pcm = best_sound.to_pcm_audio()

    return pcm
