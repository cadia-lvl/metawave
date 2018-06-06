import argparse
import csv
import re

import crepe
import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
import pyworld as pw


'''
    sample rate of google data is 47872 Hz but here we use the default 
    22000 Hz meaning the audio is re-sampled. Each column in the audio 
    representation is therefore 1/22000th of a second.
'''
def load_wav(path, lb_params):
    return librosa.core.load(path, sr=lb_params['sr'], dtype=np.float64)[0]

def trim_audio(audio, lb_params):
    '''
        Trims leading and trailing from an audio signal.
        The default threshold is 60 db.
    '''
    audio_tr, _ = librosa.effects.trim(audio, hop_length=lb_params['hop_length'])
    return audio_tr

def load_text(path):
    text = ''
    with open(path, 'r') as token:
        for line in token:
            # lower to speed up syllable matching
            text += line.lower()
    return text

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
    duration = librosa.get_duration(audio)
    return naive_syllable_count(text) / duration, duration

def zero_xing_F0(audio, lb_params):
    '''
        Buggy and does not work well. Avoid using.
    '''
    zero_crossings = librosa.core.zero_crossings(audio)
    xings = 0
    for val in zero_crossings:
        if val: xings += 1
    return 22000 * 0.5 * xings / len(zero_crossings)

def crepe_F0(audio, lb_params, confidence_threshold=0.0, frame_length=10):
    '''
        Use the monophonic pitch tracker, CREPE, to estimate
        the average F0 of the utterance. Only frames which have
        a confidence > confidence_threshold are used in the weighted
        average.

        Works better than simple zero-crossing but can be quite fuzzy.
    '''
    time, frequency, confidence, activation = crepe.predict(audio, lb_params['sr'], step_size=frame_length)
    f = 0.0
    num_used = 0
    for i in range(len(frequency)):
        if confidence[i] > confidence_threshold:
            f += confidence[i] * frequency[i]
            num_used += 1
    return f/num_used, time, frequency, confidence

def dio_FO(audio, lb_params, exclude_silence=True):
    '''
        Uses the Distributed Inline-filter Operation adapted from
        the World package.

        If exclude_silence is set to True, 0 Hz values are excluded
        in the F0 average calculation
    '''
    _F0, t = pw.dio(audio, lb_params['sr'])
    F0 = pw.stonemask(audio, _F0, t, lb_params['sr'])
    avgF0 = 0.0
    num_used = 0
    for i in range(F0.shape[0]):
        if F0[i] > 0.0 or not exclude_silence:
            avgF0 += F0[i]
            num_used += 1
    return avgF0/num_used


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--wav_path', required=True, 
        help='Full path to wav to be analyzed')
    parser.add_argument('--text_path', required=True,
        help='Full path to the spoken text')
    parser.add_argument('--sample_rate', default=22000,
        help='Sample rate of recording')
    parser.add_argument('--n_fft', default=2048, 
        help='Number of samples per frame in STFT')
    parser.add_argument('--hop_length', default=512, 
        help='Number of samples between frames')
    args = parser.parse_args()
    
    # configure librosa parameters
    lb_params = {}
    lb_params['sr'] = int(args.sample_rate)
    lb_params['n_fft'] = int(args.n_fft)
    lb_params['hop_length'] = int(args.hop_length)

    audio = trim_audio(load_wav(args.wav_path, lb_params), lb_params)
    text = load_text(args.text_path)
    speech_rate, duration = speech_rate(audio, text)
    print(dio_FO(audio, lb_params, exclude_silence=True))
    #f0, time, frequency, confidence = crepe_F0(audio, lb_params, confidence_threshold=0.75)
    #outfile = open('test.log', 'w')
    #outfile.write('Speech rate: %03d syllables/second' % speech_rate)
    #outfile.write('Estimated fundamental frequency: %03d Hz' % f0)

