import unittest

from test import naive_syllable_count


class TestSyllableCount(unittest.TestCase):

    def test_naive_syllable_count(self):
        self.assertEqual(naive_syllable_count('Þetta hér á sko að hafa tólf atkvæði'), 12)

    def test_naive_multi_count(self):
        '''tests 2+ vowels in a row'''
        self.assertEqual(naive_syllable_count('Auður'), 2) 

if __name__ == '__main__':
    unittest.main()