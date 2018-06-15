import unittest
import re

from metawave.utils.audio import naive_syllable_count
from metawave.utils.index import gen_line_reg, gen_index_line

class TestSyllableCount(unittest.TestCase):

    def test_naive_syllable_count(self):
        self.assertEqual(naive_syllable_count('Þetta hér á sko að hafa tólf atkvæði'), 12,
            msg='Naive syllable count failed for single syllables')

    def test_naive_multi_count(self):
        '''tests 2+ vowels in a row'''
        self.assertEqual(naive_syllable_count('Auður'), 2,
            msg='Naive syllable count failed for a double syllable') 

class TestRegEx(unittest.TestCase):

    def test_simple_names(self):
        name_re = '.*-i-r'
        reg = gen_line_reg(name_re)
        good_files = ['text-001-reader7.txt', 'text-001-reader7.token']
        bad_files = ['text_001_001.txt', '001.txt']
        for f in good_files:
            match = reg.search(f)
            self.assertEqual(match.group('file'), '001',
                msg='File id token failed for a valid filename')
            self.assertEqual(match.group('reader'), 'reader7',
                msg='User id token failed for a valid filename')
        for f in bad_files:
            match = reg.search(f)
            self.assertEqual(match, None,
                msg='A match was found in an unvalid filename')
    
    def test_full_id(self):
        # If the name_reg is not specified, the full file name
        # for tokens is used as ids for each <text, audio> pair
        # (excluding the file extension)
        name_re = None
        reg = gen_line_reg(name_re)
        # assert that the regex matches <anything>.*
        self.assertEqual(reg, re.compile(r'(?P<file>.*)\..*'), 
            msg='Regular expression not correct for no user input')
        filename = 'file101.token'
        match = reg.search(filename)
        self.assertEqual(match.group('file'), 'file101',
            msg='File id token failed for a valid full id regex')
        self.assertEqual(len(match.groups()), 1,
            msg='Number of reg groups not 1 for a full id filename')
    
    def test_basic_index(self):
        # run a comprehensive run and check for expected output
        name_re1 = 'r_.*-i'
        name_re2 = ''
        reg1 = gen_line_reg(name_re1)
        reg2 = gen_line_reg(name_re2)        
        f1 = 'reader1_dataset-001.token'
        f2 = 'dataset_999.token'
        match = reg1.search(f1)
        actual = gen_index_line(match, f1)
        expected = 'reader1_dataset-001.token\treader1_dataset-001.wav\treader1'
        self.assertEqual(actual, expected)
        match = reg2.search(f2)
        actual = gen_index_line(match, f2)
        expected = 'dataset_999.token\tdataset_999.wav'
        self.assertEqual(actual, expected)

if __name__ == '__main__':
    unittest.main()