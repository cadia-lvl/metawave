import argparse
import csv
import re
import os
import mmap
from collections import defaultdict

from tqdm import tqdm
import numpy as np
import pylab as plt

from datasets import config_paths
from util import speech_rate, prep_wav, dio_FO

class Runner:
    '''
        The command line runner for running a whole dataset
        meta run.
    '''
    def __init__(self, sr, paths, dataset):
        self._sr = sr
        self._paths = paths
        self._outfile = open(self._paths['out_file'], 'w')
    
    def run(self):
        with open(self._paths['index'], encoding='utf-8') as f:
            # run through each line in the index file
            for line in tqdm(f, total=num_lines(self._paths['index'])):
                [file_id, reader, line_id, text] = line.strip().split('\t')
                token = ''
                with open(os.path.join(self._paths['text'], file_id+'.token'), 'r') as f:
                    for line in f: token += line.lower()
                audio = prep_wav(os.path.join(self._paths['wavs'], file_id+'.wav'), self._sr)
                spr = speech_rate(audio, token)
                F0 = dio_FO(audio, self._sr, exclude_silence=True)
                self._outfile.write(file_id+'\t'+reader+'\t %10.4f \t %10.4f \n' % (spr, F0))
        print('Meta has finished writing and is available at ', self._paths['out_file'])

# Other utilities
def gaussian(x, mu, sig):
    return np.exp(-(x - mu) ** 2 / (2 * sig ** 2))


def write_summary(meta_path, summary_dir):
    '''
        Given the path to the metafile created by the runner,
        write a summary on a per-speaker basis.
    '''
    os.makedirs(summary_dir, exist_ok=True)

    F0_dict = defaultdict(list)
    spr_dict = defaultdict(list)
    result_dict = defaultdict(dict)
    total_F0 = []
    total_spr = []
    with open(meta_path, 'r') as meta:
        for line in meta:
            [file_id, reader, spr, f0] = line.split('\t')
            spr_dict[reader].append(float(spr))
            total_spr.append(spr_dict[reader][-1])
            F0_dict[reader].append(float(f0))
            total_F0.append(F0_dict[reader][-1])
            result_dict[reader] = defaultdict(dict)
    raw_dict = {'f0': F0_dict, 'spr': spr_dict}

    for key, obj in raw_dict.items():
        for reader, vals in obj.items():
            result_dict[reader][key]['avg'] = np.average(vals)
            result_dict[reader][key]['stddev'] = np.std(vals)
            result_dict[reader][key]['var']= np.var(vals)
    # add the dataset total to the 'total' reader
    result_dict['all'] = defaultdict(dict)
    for key, obj in {'f0':total_F0, 'spr':total_spr}.items():
        result_dict['all'][key]['avg'] = np.average(obj)
        result_dict['all'][key]['stddev'] = np.std(obj)
        result_dict['all'][key]['var'] = np.var(obj)
    
    order = {
        'f0': ['avg', 'stddev', 'var'],
        'spr': ['avg', 'stddev', 'var']
    }
    with open(os.path.join(summary_dir,'index.tsv'), 'w') as out_file:
        for reader, res in result_dict.items():
            line = reader
            for key, obj in order.items():
                for inner in obj:
                    line += '\t %10.4f' % res[key][inner]
            out_file.write(line+'\n')

    # Draw gauss plots for F0
    for reader, res in result_dict.items():
        # plot F0 over the 'typical' speech frequency range 50-500Hz            
        plt.plot(np.linspace(50, 500, num=600), gaussian(np.linspace(50, 500, num=600), 
            res['f0']['avg'], res['f0']['stddev']), label=reader)
        plt.legend(loc='upper right')
        plt.title('F0 distribution of readers')
        plt.tight_layout()
    plt.savefig(os.path.join(summary_dir, 'F0_all'))

    # Draw bar plots for Speech rate
    sprs = []
    stddevs = []
    readers = []
    for reader, res in result_dict.items():
        sprs.append(res['spr']['avg'])
        stddevs.append(res['spr']['stddev'])
        readers.append(reader)
    width = 0.35
    ind = np.arange(len(sprs))
    plt.barh(ind, sprs, xerr=stddevs)
    plt.yticks(ind + width / 2, readers)
    plt.title('Speech rate (syllable/sec)')
    plt.margins(left=55)
    plt.savefig(os.path.join(summary_dir, 'speech_rate_all'))
    # draw histograms for speech rate and F0 for each reader
    for reader, vals in spr_dict.items():
        fig = plt.figure()
        ax1 = fig.add_subplot(121)
        ax1.hist(vals, bins=50, facecolor='green', alpha=0.5, edgecolor='gray')
        ax1.grid(True)
        ax1.set_title('Speech rate (syll/sec)')
        ax2 = fig.add_subplot(122)
        ax2.hist(F0_dict[reader], bins=50, facecolor='green', alpha=0.5, edgecolor='gray')
        ax2.set_title('F0 (Hz)')
        ax2.grid(True)
        fig.suptitle('Info for %s' %reader)
        plt.savefig(os.path.join(summary_dir, '%s-info' % reader.replace('.','')))


def num_lines(file_path):
    fp = open(file_path, "r+")
    buf = mmap.mmap(fp.fileno(), 0)
    count = 0
    while buf.readline():
        count += 1
    return count

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command', help='run or summary')
    subparsers.required = True
    
    # Running whole meta run
    parser_run = subparsers.add_parser('run')
    parser_run.add_argument('--sample_rate', default=22000,
        help='Sample rate of recording')
    parser_run.add_argument('--dataset', required=True, choices=['TTS_icelandic_Google_m'])
    parser_run.add_argument('--base_dir', required=True,
        help='The absolute path to the base directory of the dataset')
    parser_run.add_argument('--out_dir', default='',
        help='The absolute path for the output. If not specified, it is saved to'+ 
        'the base directory. Ex: /home/info.log')
    
    # Running summary
    parser_summary = subparsers.add_parser('summary')
    parser_summary.add_argument('--meta_path', required=True,
        help='Absolute path to the meta file')
    parser_summary.add_argument('--out_path', required=True,
        help='Absolute path to the path for the output directory')
    
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
            runner = Runner(int(args.sample_rate), paths, args.dataset)
            runner.run()
        else:
            print('Quitting')
    
    elif args.command == 'summary':
        summary_dir = os.path.join(args.out_path, 'meta_summary')
        print('A new summary directory will be added here', summary_dir)
        choice = None
        while choice not in ['y', 'n', '']:
            choice = input('This will overwrite any previous files In that directory. Continue [(y), n] ? ')
        if choice == '' or choice == 'y':
            print('Starting the summary run')     
        write_summary(args.meta_path, summary_dir)


       