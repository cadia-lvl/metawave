import os

def config_paths(dataset, base_dir, out_dir):
    paths = {}
    if dataset == 'TTS_icelandic_Google_m':
        paths['wavs'] = os.path.join(base_dir, 'ismData', 'wavs')
        paths['text'] = os.path.join(base_dir, 'ismData', 'tokens')
        paths['index'] = os.path.join(base_dir, 'ismData', 'line_index.tsv')
    paths['out_file'] = out_dir
    return paths