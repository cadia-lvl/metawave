import os

def config_paths(dataset, base_dir, out_dir):
    paths = {}
    if dataset == 'TTS_icelandic_Google_m':
        paths['wavs'] = os.path.join(base_dir, 'ismData', 'wavs')
        paths['text'] = os.path.join(base_dir, 'ismData', 'tokens')
        paths['index'] = os.path.join(base_dir, 'ismData', 'line_index.tsv')
    
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