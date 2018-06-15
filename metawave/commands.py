import csv
import mmap
import os
import re
import sys
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
            outfile = open(paths['out_file'], 'w')
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
        print('The index file was not found')
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

def write_summary(meta_path, summary_dir, outlier_threshold):
    '''
        Given the path to the metafile created by the runner,
        write a summary on a per-speaker basis.
    '''
    os.makedirs(summary_dir, exist_ok=True)
    plot_dir = os.path.join(summary_dir, 'plots')
    reader_dir = os.path.join(plot_dir, 'readers')
    os.makedirs(plot_dir, exist_ok=True)
    os.makedirs(reader_dir, exist_ok=True)
    F0_dict = defaultdict(list)
    spr_dict = defaultdict(list)
    result_dict = defaultdict(dict)
    id_dict = defaultdict(list)
    total_F0 = []
    total_spr = []
    num_samples = 0
    with open(meta_path, 'r') as meta:
        for line in meta:
            num_samples += 1
            [file_id, reader, spr, f0] = line.split('\t')
            spr_dict[reader].append(float(spr))
            id_dict[reader].append(file_id)
            total_spr.append(spr_dict[reader][-1])
            F0_dict[reader].append(float(f0))
            total_F0.append(F0_dict[reader][-1])
            result_dict[reader] = defaultdict(dict)
    raw_dict = {'f0': F0_dict, 'spr': spr_dict}
    num_speakers = len(F0_dict)
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

    # Draw gauss plots for F0
    fig = plt.figure()
    ax = plt.subplot(111)
    for reader, res in result_dict.items():
        # plot F0 over the 'typical' speech frequency range 50-500Hz            
        plt.plot(np.linspace(50, 500, num=600), gaussian(np.linspace(50, 500, num=600), 
            res['f0']['avg'], res['f0']['stddev']), label=reader)

    plt.xlabel('F0 (Hz)')
    plt.ylabel('Probability')
    plt.title('F0 distribution of readers')
    lgnd = ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.savefig(os.path.join(plot_dir, 'F0_all'), bbox_extra_artists=(lgnd,), bbox_inches='tight')
    plt.cla()

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
    plt.xlabel('Speech rate')
    plt.title('Speech rate (syllable/sec)')
    plt.margins(left=55)
    plt.savefig(os.path.join(plot_dir, 'speech_rate_all'))
    plt.cla()

    # draw a scatter plot for all samples
    fig = plt.figure()
    ax = plt.subplot(111)
    for reader, vals in spr_dict.items():
        plt.scatter(vals, F0_dict[reader], s=0.4, label=reader)
    
    plt.xlabel('Speech rate (syll/sec)')
    plt.ylabel('F0 (Hz)')
    lgnd = ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.savefig(os.path.join(plot_dir, 'reader_compare'), bbox_extra_artists=(lgnd,), bbox_inches='tight')
    plt.cla()

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
        plt.savefig(os.path.join(reader_dir, '%s-info' % reader.replace('.','')))
    
    # find outliers on per-reader basis
    outlier_file = open(os.path.join(summary_dir, 'outliers.log'), 'w')
    outlier_index = open(os.path.join(summary_dir, 'outlier_index.txt'), 'w')
    outlier_info = defaultdict(list)
    num_outliers = 0
    for reader, vals in F0_dict.items():
        ind = 0
        for val in vals:
            if np.abs(val - result_dict[reader]['f0']['avg']) > result_dict[reader]['f0']['stddev'] * outlier_threshold:
                num_outliers += 1
                diff = np.abs(val - result_dict[reader]['f0']['avg'])
                outlier_info[reader].append('%s. F0 is %0.3f and is %0.3f away from the average: %0.3f' 
                    % (id_dict[reader][ind], val, diff, result_dict[reader]['f0']['avg']))
                outlier_index.write('%s \n' % id_dict[reader][ind])
            ind += 1
    
    for reader, vals in spr_dict.items():
        ind = 0
        for val in vals:
            if np.abs(val - result_dict[reader]['spr']['avg']) > result_dict[reader]['spr']['stddev'] * outlier_threshold:
                num_outliers += 1
                diff = np.abs(val - result_dict[reader]['spr']['avg'])
                outlier_info[reader].append('%s. SR is %0.3f and is %0.3f away from the average: %0.3f' 
                    % (id_dict[reader][ind], val, diff, result_dict[reader]['spr']['avg']))
                outlier_index.write('%s \n' % id_dict[reader][ind])
            ind += 1
    
    # write out outlier info reader wise:
    for reader, vals in outlier_info.items():
        outlier_file.write('-------------------------------------------\n')
        outlier_file.write('Outliers for %s \n' % reader)
        for val in vals:
            outlier_file.write('%s \n' % val)
    
    # write the summary
    with open(os.path.join(summary_dir,'summary.log'), 'w') as out_file:
        out_file.write('===========================================\n')
        out_file.write('Summary - Meta information \n')
        out_file.write('===========================================\n')
        out_file.write('Number of samples: %d \n' %num_samples)
        out_file.write('Number of speakers: %d \n' % num_speakers)
        out_file.write('Number of samples per speaker:\n')
        for reader, vals in F0_dict.items():
            out_file.write('%s : %d\n' %(reader, len(vals)))
        out_file.write('===========================================\n')
        for reader, res in result_dict.items():
            out_file.write('Speaker: %s \n' % reader)
            out_file.write('Speech rate: %0.3f +- %0.3f \n' % (res['spr']['avg'], res['spr']['stddev']))
            out_file.write('Fundm. freq: %0.3f +- %0.3f \n' % (res['f0']['avg'], res['f0']['stddev']))
        out_file.write('===========================================\n')
        out_file.write('Number of outliers: %d \n' % num_outliers)
        out_file.write('Per speaker: \n')
        for reader, vals in outlier_info.items():
            out_file.write('%s : %d \n' %(reader, len(vals)))
    print('Finished, the summary is now available at ', summary_dir)

def outliers(meta_path, out_path, thresh):
    outlier_file = open(os.path.join(out_path, 'outliers.log'), 'w')
    outlier_index = open(os.path.join(out_path, 'outlier_index.txt'), 'w')
    F0_dict = defaultdict(list)
    spr_dict = defaultdict(list)
    result_dict = defaultdict(dict)
    id_dict = defaultdict(list)
    total_F0 = []
    total_spr = []
    with open(meta_path, 'r') as meta:
        for line in meta:
            [file_id, reader, spr, f0] = line.split('\t')
            spr_dict[reader].append(float(spr))
            id_dict[reader].append(file_id)
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
    outlier_info = defaultdict(list)
    num_outliers = 0
    for reader, vals in F0_dict.items():
        ind = 0
        for val in vals:
            if np.abs(val - result_dict[reader]['f0']['avg']) > result_dict[reader]['f0']['stddev'] * thresh:
                num_outliers += 1
                diff = np.abs(val - result_dict[reader]['f0']['avg'])
                outlier_info[reader].append('%s. F0 is %0.3f and is %0.3f away from the average: %0.3f' 
                    % (id_dict[reader][ind], val, diff, result_dict[reader]['f0']['avg']))
                outlier_index.write('%s \n' % id_dict[reader][ind])
            ind += 1
    for reader, vals in spr_dict.items():
        ind = 0
        for val in vals:
            if np.abs(val - result_dict[reader]['spr']['avg']) > result_dict[reader]['spr']['stddev'] * thresh:
                num_outliers += 1
                diff = np.abs(val - result_dict[reader]['spr']['avg'])
                outlier_info[reader].append('%s. SR is %0.3f and is %0.3f away from the average: %0.3f' 
                    % (id_dict[reader][ind], val, diff, result_dict[reader]['spr']['avg']))
                outlier_index.write('%s \n' % id_dict[reader][ind])
            ind += 1
    # write out outlier info reader wise:
    for reader, vals in outlier_info.items():
        outlier_file.write('-------------------------------------------\n')
        outlier_file.write('Outliers for %s \n' % reader)
        for val in vals:
            outlier_file.write('%s \n' % val)

def num_lines(file_path):
    fp = open(file_path, "r+")
    buf = mmap.mmap(fp.fileno(), 0)
    count = 0
    while buf.readline():
        count += 1
    return count
