import csv
import mmap
import os
import re
import sys
import operator
import itertools
from collections import defaultdict

import numpy as np
import pylab as plt
from tqdm import tqdm

from .utils.audio import (dio_F0, get_duration, naive_syllable_count, prep_wav,
                         speech_rate)
from .utils.datasets import config_paths
from .utils.index import IndexHandler, ReverseIndexHandler
from .utils.misc import gaussian


def run(sr, paths, dataset, **kwargs):
    '''
        The command line runner for running a whole dataset
        meta run.
    '''
    i_handler = IndexHandler(dataset, kwargs['ind'])
    num_samples = kwargs['num_samples']
    if 'token_xtsn' in paths:
        # using a known dataset
        i_handler.set_token_extension(paths['token_xtsn'])
    else:
        i_handler.set_token_extension(kwargs['token_xtsn']) 
    try:
        count = 0
        with open(paths['index'], encoding='utf-8') as f:
            outfile = open(paths['out_file'], 'w+')
            # run through each line in the index file
            if num_samples is not None:
                total = num_samples
            else:
                total = num_lines(paths['index'])
            for line in tqdm(f, total=total):
                i_handler.set_current(line)
                token = ''
                try:
                    with open(os.path.join(paths['text'], i_handler.get_token_fid()), 'r') as f:
                        for line in f: token += line.lower()
                except Exception as e:
                    print('A text from the index could not be found')
                    print('Error: %s' % e)
                    sys.exit()
                try: 
                    audio = prep_wav(os.path.join(paths['wavs'], i_handler.get_audio_fid()), sr)
                except Exception as e:
                    print('An audio file from the index could not be found')
                    print('Error: %s' % e)
                    sys.exit()
                spr = speech_rate(audio, token)
                F0 = dio_F0(audio, sr, exclude_silence=True)
                outfile.write(i_handler.get_token_fid()+'\t'+i_handler.get_reader()+'\t %0.4f \t %0.4f \n' % (spr, F0))
                if num_samples is not None and count + 1 >= num_samples:
                    print('Stopping because num_samples was set to ', num_samples)
                    break
                count += 1
        print('Meta has finished writing and is available at ', paths['out_file'])
    except Exception as e:
        print('Error while reading from index file.')
        print('Error: %s' % e)
        sys.exit()

def gen_index(paths, name_reg):
    # iterate all text tokens to get filenames
    try:
        outfile = open(paths['out_file'], 'w')
    except Exception as e:
        print('Could not complete path to out_file. Path likely wrong')
        print('Error: %s' % e)
        sys.exit()    
    handler = ReverseIndexHandler(name_reg)
    for fn in os.listdir(paths['text']):
        outfile.write('%s \n' % handler.get_line(fn))
    print('Index file is ready at: ', paths['out_file'])

def check(wav_path, text_path, sr):
    '''
        Do a simple (Command line style) check on a single <wav,text>
        pair.
    '''
    token = ''
    with open(text_path, 'r') as f:
        for line in f: token += line.lower()
    audio = prep_wav(wav_path, sr)
    spr = speech_rate(audio, token)
    F0 = dio_F0(audio, sr, exclude_silence=True)

    print('------------------------------------')
    print('Text: ', token)
    print('Speek duration: %0.4f' % get_duration(audio))
    print('Number of syllables: ', naive_syllable_count(token))
    print('Speech rate: %0.4f' % spr)
    print('F0:          %0.4f' % F0)
    print('------------------------------------')

def num_lines(file_path):
    fp = open(file_path, "r+")
    buf = mmap.mmap(fp.fileno(), 0)
    count = 0
    while buf.readline():
        count += 1
    return count

def write_summary(meta_path, summary_dir, outlier_threshold):
    # OS related operations
    os.makedirs(summary_dir, exist_ok=True)
    plot_dir = os.path.join(summary_dir, 'plots')
    reader_dir = os.path.join(plot_dir, 'readers')
    os.makedirs(plot_dir, exist_ok=True)
    os.makedirs(reader_dir, exist_ok=True)

    reader_set = ReaderSet(meta_path)
    reader_set.save_hist_for_all_readers(reader_dir)
    reader_set.set_outliers(keep_size=outlier_threshold)
    reader_set.save_spr_vs_fo_scatter(path=plot_dir, also_clean=True)
    reader_set.write_index(summary_dir)
    reader_set.write_summary(summary_dir)

def outliers(meta_path, out_path, outlier_threshold):
    reader_set = ReaderSet(meta_path)  
    reader_set.set_outliers(keep_size=outlier_threshold)
    reader_set.write_index(out_path)

class ReaderSet:
    def __init__(self, meta_path):
        self._num_samples = 0
        self._num_readers = 0
        self._mean_f0 = 0.0
        self._mean_spr = 0.0
        self._readers = []
        self._num_outliers = 0
        with open(meta_path, 'r') as meta:
            f0_ttl = 0.0
            spr_ttl = 0.0
            readers = defaultdict(dict)
            for line in meta:
                self._num_samples += 1
                [file_id, reader, spr, f0] = line.split('\t')
                spr = float(spr)
                f0 = float(f0)
                readers[reader][file_id] = {'spr': spr, 'f0': f0}
                spr_ttl += spr
                f0_ttl += f0
            self._num_readers = len(readers.keys())
            self._mean_f0 = f0_ttl / self._num_samples
            self._mean_spr = spr_ttl / self._num_samples
            for reader_id, utts in readers.items():
                self._readers.append(Reader(reader_id, utts))

    def get_num_samples(self):
        return self._num_samples

    def get_num_readers(self):
        return self._num_readers
    
    def get_num_outliers(self):
        return self._num_outliers

    def get_dataform(self, clean=False):
        data = {}
        for reader in self._readers:
            data[reader._id] = reader.get_dataform(clean=clean)
        return data
    
    def get_as_list(self):
        '''
            Returns the data in the form
            [{'reader_id', 'utt_id', 'spr', 'f0' (maybe 'err')}, ...]
            for all utts for all readers
        '''
        data = [reader.get_as_list() for reader in self._readers]
        return list(itertools.chain.from_iterable(data))

    def save_spr_vs_fo_scatter(self, path, also_clean=True):
        all_data = self.get_dataform()
        fig = plt.figure()
        ax = plt.subplot(111)
        for reader, vals in all_data.items():
            sprs = []
            f0s = []
            for utt_id, utt_info in vals.items():
                sprs.append(utt_info['spr'])
                f0s.append(utt_info['f0'])
            plt.scatter(sprs, f0s, s=0.4, label=reader)
        plt.xlabel('Speech rate (syll/sec)')
        plt.ylabel('F0 (Hz)')
        lgnd = ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        sctr_xlim = plt.xlim()
        sctr_ylim = plt.ylim()
        plt.savefig(os.path.join(path, 'reader_compare'), bbox_extra_artists=(lgnd,), bbox_inches='tight')
        plt.cla()

        if also_clean:
            # Also plot a scatter plot for none outliers results
            clean_data = self.get_dataform(clean=True)
            fig = plt.figure()
            ax = plt.subplot(111)
            for reader, vals in clean_data.items():
                sprs = []
                f0s = []
                for utt_id, utt_info in vals.items():
                    sprs.append(utt_info['spr'])
                    f0s.append(utt_info['f0'])
                plt.scatter(sprs, f0s, s=0.4, label=reader)
            plt.xlabel('Speech rate (syll/sec)')
            plt.ylabel('F0 (Hz)')
            lgnd = ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
            plt.xlim(sctr_xlim)
            plt.ylim(sctr_ylim)
            plt.savefig(os.path.join(path, 'reader_compare_clean'), bbox_extra_artists=(lgnd,), bbox_inches='tight')
            plt.cla()

    def set_outliers(self, keep_size=0.9):
        '''
            Finds the mean of F0 and speech rate of the
            whole dataset and returns the keep_size part
            of the dataset with the lowest error in terms
            of those two variables
        '''
        self._num_outliers = (1 - keep_size) * self.get_num_samples()
        for reader in self._readers:
            reader.set_err(self._mean_spr, self._mean_f0)
    
        datalist = self.get_as_list()
        datalist.sort()
        for i in range(int(keep_size * self.get_num_samples()), self.get_num_samples()):
            datalist[i].make_outlier()

    def write_index(self, path):
        outlier_index = open(os.path.join(path, 'outlier_index.txt'), 'w')
        clean_index = open(os.path.join(path, 'clean_index.txt'), 'w')
        for reader in self._readers:
            for utt in reader._utts:
                if utt.is_outlier():
                    outlier_index.write('%s\tWeighted error: %0.3f\n' %(utt.get_id(), utt.get_err()))
                else:
                    clean_index.write('%s\n' %(utt.get_id()))
    
    def write_summary(self, path):
        with open(os.path.join(path,'summary.log'), 'w') as out_file:
            out_file.write('===========================================\n')
            out_file.write('Summary - Meta information \n')
            out_file.write('===========================================\n')
            out_file.write('Number of samples: %d \n' %self.get_num_samples())
            out_file.write('Number of readers: %d \n' % self.get_num_readers())
            out_file.write('Number of samples per reader:\n')
            for reader in self._readers:
                out_file.write('%s : %d\n' %(reader.get_id(), reader.get_num_samples()))
            out_file.write('===========================================\n')
            for reader in self._readers:
                out_file.write('Reader: %s \n' % reader.get_id())
                out_file.write('Speech rate: %0.3f +- %0.3f \n' % (reader.get_spr_mean(), reader.get_spr_stddev()))
                out_file.write('Fundm. freq: %0.3f +- %0.3f \n' % (reader.get_f0_mean(), reader.get_f0_stddev()))
            out_file.write('===========================================\n')
            out_file.write('Number of outliers: %d \n' % self.get_num_outliers())
            out_file.write('Per speaker: \n')
            for reader in self._readers:
                out_file.write('%s : %d \n' %(reader.get_id(), reader.get_num_outliers()))

    def save_hist_for_all_readers(self, output_dir):
        for reader in self._readers:
            reader.save_histogram(output_dir)

class Reader:
    '''
        utts is a dictionary with the format
        { utterance_id:{
                'f0': float,
                'spr': float
        }}
    '''
    def __init__(self, reader_id, utts):
        self._id = reader_id
        self._utts = [Utt(utt_id, self._id, val['f0'], val['spr']) for utt_id, val in utts.items()]
        self._num_samples = len(utts.keys())

    def get_id(self):
        return self._id
    
    def get_num_samples(self):
        return self._num_samples

    def get_num_outliers(self):
        return sum([1 if utt.is_outlier() else 0 for utt in self._utts])

    def get_dataform(self, clean=False):
        data = {}
        for utt in self._utts:
            if not clean or not utt.is_outlier():
                data.update(utt.get_dataform())
        return data

    def get_as_list(self):
        return self._utts
    
    def set_err(self, mean_spr, mean_f0):
        for utt in self._utts:
            utt.set_err(mean_spr, mean_f0)
    
    def get_all_f0(self):
        return [utt.get_f0() for utt in self._utts]

    def get_all_spr(self):
        return [utt.get_spr() for utt in self._utts]

    def get_f0_mean(self):
        return sum(self.get_all_f0())/self._num_samples
    
    def get_spr_mean(self):
        return (sum(self.get_all_spr()))/self._num_samples
    
    def get_f0_stddev(self):
        return np.std(self.get_all_f0())

    def get_spr_stddev(self):
        return np.std(self.get_all_spr())

    def save_histogram(self, output_dir):
        fig = plt.figure()
        ax1 = fig.add_subplot(121)
        ax1.hist(self.get_all_spr(), bins=50, facecolor='green', alpha=0.5, edgecolor='gray')
        ax1.grid(True)
        ax1.set_title('Speech rate (syll/sec)')
        ax2 = fig.add_subplot(122)
        ax2.hist(self.get_all_f0(), bins=50, facecolor='green', alpha=0.5, edgecolor='gray')
        ax2.set_title('F0 (Hz)')
        ax2.grid(True)
        fig.suptitle('Info for %s' %self._id)
        plt.savefig(os.path.join(output_dir, '%s-info' % self._id.replace('.','')))


class Utt:
    def __init__(self, utt_id, reader_id, f0, spr):
        self._id = utt_id
        self._reader_id = reader_id
        self._f0 = f0
        self._spr = spr
        self._err = 0
        self._is_outlier = False
    
    def set_err(self, mean_spr, mean_f0):
        self._err = (np.abs(mean_spr - self._spr)/mean_spr)**2 + \
            (np.abs(mean_f0 - self._f0)/mean_f0)**2
    
    def get_err(self):
        return self._err
    
    def get_f0(self):
        return self._f0
    
    def get_spr(self):
        return self._spr
    
    def get_dataform(self):
        return {
            self._id:{
                'spr':self._spr, 
                'f0':self._f0, 
                'err':self._err
            }}
    
    def is_outlier(self):
        return self._is_outlier

    def make_outlier(self):
        self._is_outlier = True

    def get_id(self):
        return self._id

    def __lt__(self, other):
        return self.get_err() < other.get_err()
    