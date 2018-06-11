# Metawave
Metawave is a command line tool for generating speeker meta information from TTS datasets. This tool can be used for analyzing and comparing speekers in multi-speeker TTS datasets. Metawave can generate a list of outliers in the dataset that are potentially better left out in TTS training.

## Installing
Metawave is a python 3.6 application and to run it, all dependencies need to be installed first via `pip install -r requirements.txt`

## Usage
All running of the app is through `metawave.py` and it has 3 modes:

1. `./metawave.py --run` : For gathering the initial meta-information and optionally generates a summary as well.
2. `./metawave.py --custom_run` : Can be used for unsupported datasets
3. `./metawave.py --summary` : Can only be called after doing a `--run`. This summary generates information about each speaker and a list of outliers amongst other things.
4. `./metawave.py --check` : A handy tool to get quick information ona single `<text, audio>` pair.

Each mode has some required parameters which can be listed via `./metawave --<mode> -h`

## Issues and future work
Since the directory structure of each dataset can be different, the only supported dataset now is `TTS_icelandic_Google_m`. However, for unsupported datasets, you can run metawave by supplying `--wav_dir`, `--text_dir` and `--index_path` to the `--custom_run` command.
