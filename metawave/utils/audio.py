import re

import librosa
import matplotlib.pyplot as plt
import numpy as np
import pyworld as pw


def prep_wav(path, sr):
    '''
        Load an audio file at the given path
        and trim the audio at start and end.
    '''
    return trim_audio(load_wav(path, sr))

def load_wav(path, sr):
    '''
        Loads the .wav at the given path with the given
        samplerate. The .wav is down-sampled if needed.
    '''
    return librosa.core.load(path, sr=sr, dtype=np.float64)[0]

def trim_audio(audio):
    '''
        Trims leading and trailing from an audio signal.
        The default threshold is 60 db.
    '''
    audio_tr, _ = librosa.effects.trim(audio)
    return audio_tr

def naive_syllable_count(text):
    '''
        Returns the syllable count in a string as the number 
        of occurrences of 1 or more Icelandic vowels in a string.
    '''
    return len(re.findall('[aáeéiíoóuúyýæö]+', text))

def speech_rate(audio, text):
    '''
        Returns the speech rate, given the audio. text pair
        defined as (number of syllables / speech duration).

        Since this is estimated on the trimmed audio, it is likely
        that the rate will be over-estimated in single sentence utterances
        with no pauses.
    '''
    return naive_syllable_count(text) / get_duration(audio)

def get_duration(audio):
    '''
        Returns the duration in seconds of the given audio
    '''
    return librosa.get_duration(audio)

def zero_xing_F0(audio):
    '''
        Buggy and does not work well. Avoid using.
    '''
    zero_crossings = librosa.core.zero_crossings(audio)
    xings = 0
    for val in zero_crossings:
        if val: xings += 1
    return 22000 * 0.5 * xings / len(zero_crossings)

def dio_F0(audio, sr, exclude_silence=True):
    '''
        Uses the Distributed Inline-filter Operation adapted from
        the World package to estimate F0 on 5ms frames.

        If exclude_silence is set to True, 0 Hz values are excluded
        in the F0 average calculation
    '''
    _F0, t = pw.dio(audio, sr)
    F0 = pw.stonemask(audio, _F0, t, sr)
    sp = pw.cheaptrick(audio, F0, t, sr)
    # ap = pw.d4c(audio, F0, t, sr) for aperiodicity
    # y = pw.synthesize(F0, sp, ap, sr)

    avgF0 = 0.0
    num_used = 0
    for i in range(F0.shape[0]):
        if F0[i] > 0.0 or not exclude_silence:
            avgF0 += F0[i]
            num_used += 1
    return avgF0/num_used

def aperiodicity(audio, sr):
    _F0, t = pw.dio(audio, sr)
    F0 = pw.stonemask(audio, _F0, t, sr)
    sp = pw.cheaptrick(audio, F0, t, sr)
    ap = pw.d4c(audio, F0, t, sr)
    return ap
