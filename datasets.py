import os

GOOGLE_ID = 'TTS_icelandic_Google_m'
IVONA_ID = 'ivona_speech_data'

def config_paths(dataset, base_dir, out_dir):
    paths = {}
    if dataset == GOOGLE_ID:
        paths['wavs'] = os.path.join(base_dir, 'ismData', 'wavs')
        paths['text'] = os.path.join(base_dir, 'ismData', 'tokens')
        paths['index'] = os.path.join(base_dir, 'ismData', 'line_index.tsv')
        paths['token_xtsn'] = '.token'
    elif dataset == IVONA_ID:
        paths['wavs'] = os.path.join(base_dir, 'Kristjan_export')
        paths['text'] = os.path.join(base_dir, 'ivona_txt')
        paths['index'] = os.path.join(base_dir, 'line_index.tsv')

    if out_dir == '':
        out_dir = base_dir
    paths['out_file'] = os.path.join(out_dir, 'meta.tsv')
    return paths

def config_custom_paths(wav_dir, text_dir, index_path, out_dir):
    paths = {}
    paths['wavs'] = wav_dir
    paths['text'] = text_dir
    paths['index'] = index_path
    paths['out_file'] = os.path.join(out_dir, 'meta.tsv')
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
        if dataset == IVONA_ID:
            self._fid_indx = 0
            self._reader_indx = 1
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