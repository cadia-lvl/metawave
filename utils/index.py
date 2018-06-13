import re
import os
from .common import GOOGLE_ID, IVONA_ID

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
        return '%s \t %s \t %s' \
            % (fn, wav_fn, rm.group('reader'))
    else:
        # Reader id is missing
        return '%s \t %s' \
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
        read-offs
    '''
    def __init__(self, dataset):
        if dataset == GOOGLE_ID:
            self._fid_indx = 0
            self._reader_indx = 1
        elif dataset == IVONA_ID:
            self._fid_indx = 0
            self._reader_indx = 2
        self._fid = None
        self._reader = None

    def set_current(self, line):
        vals = line.strip().split('\t')
        self._fid = vals[self._fid_indx]
        self._reader = vals[self._reader_indx]

    def get_reader(self):
        return self._reader

    def get_fid(self):
        return self._fid