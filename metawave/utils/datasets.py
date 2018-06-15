import os

from .common import GOOGLE_ID, IVONA_ID

def config_paths(dataset, base_dir, out_dir):
    '''
        Used for known datasets to reduce input
        arguments for user
    '''
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
        paths['token_xtsn'] = '.txt'

    if out_dir == '':
        out_dir = base_dir
    paths['out_file'] = os.path.join(out_dir, 'meta.tsv')
    return paths

def config_custom_paths(wav_dir, text_dir, index_path, out_dir):
    '''
        Used for custom datasets where each
    '''
    paths = {}
    paths['wavs'] = wav_dir
    paths['text'] = text_dir
    paths['index'] = index_path
    paths['out_file'] = os.path.join(out_dir, 'meta.tsv')
    return paths
