# Metawave
Metawave is a command line tool for generating speeker meta information from TTS datasets. This tool can be used for analyzing and comparing speekers in multi-speeker TTS datasets. Metawave can generate a list of outliers in the dataset that are potentially better left out in TTS training.

## Installing
Metawave is a python 3.6 application and to run it, all dependencies need to be installed first via `pip install -r requirements.txt`

## Usage
All running of the app is through `metawave.py` and it has 3 modes:

1. `./metawave.py --run` : For gathering the initial meta-information and optionally generates a summary as well. (Requires an index file)
2. `./metawave.py --custom_run` : Can be used for unsupported datasets. (Requires an index file)
3. `./metawave.py --summary` : Can only be called after doing a `--run`. This summary generates information about each speaker and a list of outliers amongst other things.
4. `./metawave.py --check` : A handy tool to get quick information ona single `<text, audio>` pair.
5. `./metawave.py --gen_index` : For generating a line index file similar to the one in the google dataset for example.

Each mode has some required parameters which can be listed via `./metawave --<mode> -h`

## Generating an index file
If a dataset does not have an index file, one has to be created. If the reader id is encoded in the file-name, this can be specified via `--name_reg`. For example if the data has the following setup:

* `text-001-001.wav`
* `text-001-002.wav`
* ...
* `text-002-001.wav`

where the first 3 numbers are an id for the reader and the last 3 are a file id for the `<text, audio>` pair, we can supply `--name_reg .*-r-i` where `r` stands for `reader` and `i` for file id. Then the reader information will be saved. If nothing is supplied to the name regular expression, we assume that the full name of each `<text,audio>` pair is the same and the full name will be used as an id for the pair. Note that the regular expression is dependent on the file name format of the text tokens. Currently this functionality only supports those regular variables , `.*, r, i` and any delimiters. Other examples could be:

* `--name_reg r_.*_i` matches e.g. `<reader_id>_token_<file_id>`
* `--name_reg .*-i` matches e.g. `token_<file_id>` where the `<reader_id>` is not encoded in the file name.

Also note that the file extension, i.e. the `.txt` in `token.txt`, should not be included.

## Issues and future work
Since the directory structure of each dataset can be different, the only supported datasets are `TTS_icelandic_Google_m` and `ivona_speech_data`. However, for unsupported datasets, you can run metawave by supplying `--wav_dir`, `--text_dir` and `--index_path` to the `--custom_run` command. For this to work, a `line_index.tsv` where each line has `<text_fname> \t <audio_fname> \t <speeker_id>` has to exist at `index_path`.


## Using Ivona
To use Ivona as a known dataset, an index file, `line_index.tsv` has to be generated and available in the root directory of the dataset. Each line has `<text_fname> \t <audio_fname> \t <reader_id>`. In this case, the reader id references the 3 different sets in Ivona. Otherwise an index file can be generated anyway is needed and run using `custom_run`