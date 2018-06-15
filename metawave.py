import argparse
import os
from commands import check, gen_index, outliers, run, write_summary

from utils.datasets import config_custom_paths, config_paths
from utils.index import paths_for_index

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    subparsers.required = True
    
    # Running whole meta run
    parser_run = subparsers.add_parser('run', help='Initial run for a supported dataset')
    parser_run.add_argument('--sample_rate', default=22000,
        help='Sample rate of .wav (default=22000)')
    parser_run.add_argument('--dataset', required=True, choices=['TTS_icelandic_Google_m', 'ivona_speech_data'])
    parser_run.add_argument('--base_dir', required=True,
        help='The absolute path to the base directory of the dataset')
    parser_run.add_argument('--out_dir', default='',
        help='The absolute path for the output root directory. If not specified, it is saved to'+ 
        ' the base directory.')
    parser_run.add_argument('--num_samples', default=None, help='If not indicated, all samples are used')

    # Running a meta run on a custom dataset
    parser_crun = subparsers.add_parser('custom_run', help='Initial run for a custom dataset')
    parser_crun.add_argument('--sample_rate', default=22000,
        help='Sample rate of .wav (default=22000)')
    parser_crun.add_argument('--wav_dir', required=True,
        help='The absolute path to the wav directory of the dataset')
    parser_crun.add_argument('--text_dir', required=True,
        help='The absolute path to the text directory of the dataset')
    parser_crun.add_argument('--index_path', required=True,
        help='The absolute path to the index file of the dataset')
    parser_crun.add_argument('--out_dir', required=True,
        help='The absolute path for the output root directory.')
    parser_crun.add_argument('--token_xtsn', required=True, default='.token',
        help='The file extension of text tokens, e.g. ".txt"')
    parser_crun.add_argument('--reader_ind',
        help='Index of reader in line index')
    parser_crun.add_argument('--wav_ind', default='1',
        help='Index of reader in line index')
    parser_crun.add_argument('--txt_ind', default='0',
        help='Index of reader in line index')
    parser_crun.add_argument('--num_samples', default=None, help='If not indicated, all samples are used')

    # Running summary
    parser_summary = subparsers.add_parser('summary', help='Generate a summary for a dataset.')
    parser_summary.add_argument('--meta_path', required=True,
        help='Absolute path to the meta file')
    parser_summary.add_argument('--out_path', required=True,
        help='Absolute path to the path for the output directory')
    parser_summary.add_argument('--outlier_threshold', default=3,
        help='The number of standard deviations needed to determine if a sample'+
            'is an outlier. (default=3)')

    # Running a check
    parser_check = subparsers.add_parser('check', help='Get a short summary for a single <wav, text> pair')
    parser_check.add_argument('--wav_path', required=True,
        help='Absolute path to the .wav file')
    parser_check.add_argument('--text_path', required=True,
        help='Absolute path to the respective token file')
    parser_check.add_argument('--sample_rate', default=22000,
        help='Sample rate of .wav (default=22000)')

    # Running a gen_index
    parser_index = subparsers.add_parser('gen_index', help='Create an index for an index-less dataset')
    parser_index.add_argument('--wav_dir', required=True,
        help='The absolute path to the wav directory of the dataset')
    parser_index.add_argument('--text_dir', required=True,
        help='The absolute path to the text directory of the dataset')    
    parser_index.add_argument('--out_dir', required=True,
        help='Absolute path to the output directory for the index.')
    parser_index.add_argument('--name_reg', required=False, default='',
        help='Re for file names, ex: .*_r_i or i-r. Note: no file extension. See readme.')

    # Running outliers
    parser_outliers = subparsers.add_parser('outliers', help='Generate a file index of outliers as well as'+\
        ' other outlier information')
    parser_outliers.add_argument('--meta_path', required=True,
        help='The absolute path to the meta file of the dataset')
    parser_outliers.add_argument('--out_path', required=True,
        help='The absolute path to the base directory of the output files')
    parser_outliers.add_argument('--outlier_threshold', default=3,
        help='The number of standard deviations needed to determine if a sample'+
        'is an outlier. (default=3)')


    args = parser.parse_args()
    if args.command == 'run':
        # configure paths based on chosen dataset
        paths = config_paths(args.dataset, args.base_dir, args.out_dir)
        print('A new meta file will be written at ', paths['out_file'])
        choice = None
        while choice not in ['y', 'n', '']:
            choice = input('This will overwrite any previous files at that lociation. Continue [(y), n] ? ')
        if choice == '' or choice == 'y':
            print('Starting the info run')
            num_samples = args.num_samples
            if num_samples is not None:
                num_samples = int(num_samples)
            run(int(args.sample_rate), paths, args.dataset, ind=None, num_samples=num_samples)
            choice = None
            while choice not in ['y', 'n', '']:
                choice = input('Do you want to write a summary as well [(y), n] ? ')
            if choice == '' or choice == 'y':
                meta_path = paths['out_file']
                sp = os.path.join(os.path.split(meta_path)[0], 'summary')
                summary_path = input('Absolute path of summary (default: %s): '% sp) or sp
                outlier_thresh = int(input('Outlier threshold (default: %d): '% 3) or '3')
                write_summary(meta_path, summary_path, outlier_thresh)
            else:
                print('Quitting')
        else:
            print('Quitting')

    elif args.command == 'custom_run':
        paths = config_custom_paths(args.wav_dir, args.text_dir, args.index_path, args.out_dir)
        # handle indexes
        ind = {}
        ind['wav_ind'] = args.wav_ind
        ind['txt_ind'] = args.txt_ind
        if 'reader_ind' in args:
            ind['reader_ind'] = args.reader_ind
        print('A new meta file will be written at ', paths['out_file'])
        choice = None
        while choice not in ['y', 'n', '']:
            choice = input('This will overwrite any previous files at that lociation. Continue [(y), n] ? ')
        if choice == '' or choice == 'y':
            print('Starting the info run')
            num_samples = args.num_samples
            if num_samples is not None:
                num_samples = int(num_samples)
            run(int(args.sample_rate), paths, None, ind=ind, token_xtsn=args.token_xtsn, num_samples=num_samples)
            choice = None
            while choice not in ['y', 'n', '']:
                choice = input('Do you want to write a summary as well [(y), n] ? ')
            if choice == '' or choice == 'y':
                meta_path = paths['out_file']
                sp = os.path.join(os.path.split(meta_path)[0], 'summary')
                summary_path = input('Absolute path of summary (default: %s): '% sp) or sp
                outlier_thresh = int(input('Outlier threshold (default: %d): '% 3) or '3')
                write_summary(meta_path, summary_path, outlier_thresh)
            else:
                print('Quitting')
        else:
            print('Quitting')
    
    elif args.command == 'summary':
        summary_dir = os.path.join(args.out_path, 'meta_summary')
        print('A new summary directory will be added to: ', summary_dir)
        choice = None
        while choice not in ['y', 'n', '']:
            choice = input('This will overwrite any previous metafiles in that directory. Continue [(y), n] ? ')
        if choice == '' or choice == 'y':
            print('Starting the summary run')
            write_summary(args.meta_path, summary_dir, int(args.outlier_threshold))
        else:
            print('Quitting')

    elif args.command == 'check':
        check(args.wav_path, args.text_path, int(args.sample_rate))

    elif args.command == 'gen_index':
        paths = paths_for_index(args.wav_dir, args.text_dir, args.out_dir)
        print('A new line index will be added at: ', paths['out_file'])
        choice = None
        while choice not in ['y', 'n', '']:
            choice = input('This will overwrite any previous indexfile at that location. Continue [(y), n] ? ')
        if choice == '' or choice == 'y':
            print('Starting index generation')
            gen_index(paths, args.name_reg)
        else:
            print('Quitting')
    
    elif args.command == 'outliers':
        print('Outlier files will be generated at ', args.out_path)
        choice = None
        while choice not in ['y', 'n', '']:
            choice = input('Continue [(y), n] ? ')
        if choice == '' or choice == 'y':
            print('Starting outlier generation')
            outliers(args.meta_path, args.out_path, int(args.outlier_threshold))
        else:
            print('Quitting')
