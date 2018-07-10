import re
import os
import sys

def gen_line_reg(s):
    '''
        Build a regular expression, given a human-friendly
        semi regular expression.

        Note that if no user input is given, None is supplied 
        to this function.
    '''
    if s is None:
        s = r'(?P<file>.*)'
    else:
        # Build the proper regular expression
        s = s.replace('r', r'(?P<reader>.*)')
        s = s.replace('i', r'(?P<file>.*)')
    # add any file extension
    s += r'\..*'
    return re.compile(s)

def gen_index_line(rm, fn):
    '''
        Given the matched groups and the text filename, 
        generate a single line to be written to the index 
        on the format

        <text_file> \t <audio_file> \t <reader_id>
    
        where the reader id might be missing, based on the 
        regex match
    '''
    wav_fn = fn.replace(fn[fn.find('.'):], '.wav')
    if len(rm.groups()) == 2:
        # Reader id was captured
        return '%s\t%s\t%s' \
            % (fn, wav_fn, rm.group('reader'))
    else:
        # Reader id is missing
        return '%s\t%s' \
            % (fn, wav_fn)


class ReverseIndexHandler:
    '''
        A convinience class to both reduce computations
        and verbosity that does basically what the two
        functions above achieve.
    '''
    def __init__(self, semi_reg):
        self._reg = gen_line_reg(semi_reg)

    def get_line(self, fn):
        return gen_index_line(self._reg.search(fn), fn)

def paths_for_index(wav_dir, text_dir, out_dir):
    paths = {}
    paths['wavs'] = wav_dir
    paths['text'] = text_dir
    paths['out_file'] = os.path.join(out_dir, 'line_index.tsv')
    return paths

class IndexHandler:
    '''
        Handle for different dataset interfaces index
        read-offs. If ind is None we are running on a 
        custom dataset where ind are indices for at least
        the text and audio filenames in each line of the index 
        file.
    '''
    def __init__(self, dataset, ind):
        if ind is not None:
            # Running on a custom dataset
            self._audio_fid_indx = ind['wav_ind']
            self._token_fid_indx = ind['txt_ind']
            if 'reader_ind' in ind:
                self._reader_indx = ind['reader_ind']
            else:
                self._reader_indx = None
        else:
            if dataset == 'TTS_icelandic_Google_m' or dataset == 'TTS_icelandic_Google_f':
                self._audio_fid_indx = 0
                self._token_fid_indx = 0
                self._reader_indx = 1
            elif dataset == 'ivona_speech_data':
                self._token_fid_indx = 0
                self._audio_fid_indx = 1
                self._reader_indx = 2
            else:
                print('The given dataset: %s , is not supported' % dataset)
                sys.exit()
        
        self._fid = None
        self._reader = 'Reader'
        self._token_xtsn = ''
        self._audio_xtsn = '.wav'
    
    def set_current(self, line):
        vals = line.strip().split('\t')
        self._audio_fid = vals[self._audio_fid_indx]
        self._token_fid = vals[self._token_fid_indx]
        if self._reader_indx is not None:
            self._reader = vals[self._reader_indx]
    def get_reader(self):
        '''
            If the index of the reader is not known (e.g. if it
            is not mentioned in the index file), this will simply
            return `reader`
        '''
        return self._reader

    def get_audio_fid(self):
        return self._append_xtsn(self._audio_fid, self._audio_xtsn)
    
    def get_token_fid(self):
        return self._append_xtsn(self._token_fid, self._token_xtsn)

    def _append_xtsn(self, fid, xtsn):
        if fid[len(fid)-len(xtsn):] == xtsn:
            return fid
        else:
            return fid + xtsn
    
    def set_token_extension(self, xtsn):
        self._token_xtsn = xtsn