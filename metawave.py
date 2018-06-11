import argparse
import os

from datasets import config_paths, config_custom_paths
from commands import write_summary, run, check

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    subparsers.required = True
    
    # Running whole meta run
    parser_run = subparsers.add_parser('run', help='Initial run for a supported dataset')
    parser_run.add_argument('--sample_rate', default=22000,
        help='Sample rate of .wav (default=22000)')
    parser_run.add_argument('--dataset', required=True, choices=['TTS_icelandic_Google_m'])
    parser_run.add_argument('--base_dir', required=True,
        help='The absolute path to the base directory of the dataset')
    parser_run.add_argument('--out_dir', default='',
        help='The absolute path for the output home directory. If not specified, it is saved to'+ 
        ' the base directory.')

    # Running a meta run on a custom dataset
    parser_run = subparsers.add_parser('custom_run', help='Initial run for a custom dataset')
    parser_run.add_argument('--sample_rate', default=22000,
        help='Sample rate of .wav (default=22000)')
    parser_run.add_argument('--wav_dir', required=True,
        help='The absolute path to the wav directory of the dataset')
    parser_run.add_argument('--text_dir', required=True,
        help='The absolute path to the text directory of the dataset')
    parser_run.add_argument('--index_path', required=True,
        help='The absolute path to the index file of the dataset')
    parser_run.add_argument('--out_dir', default='',
        help='The absolute path for the output home directory. If not specified, it is saved to'+ 
        ' the base directory.')
    
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
            run(int(args.sample_rate), paths)
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
        print('A new meta file will be written at ', paths['out_file'])
        choice = None
        while choice not in ['y', 'n', '']:
            choice = input('This will overwrite any previous files at that lociation. Continue [(y), n] ? ')
        if choice == '' or choice == 'y':
            print('Starting the info run')
            run(int(args.sample_rate), paths)
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
        print('A new summary directory will be added here', summary_dir)
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