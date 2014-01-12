#!/usr/bin/python
# Copyright (C) 2012 Brian J. Stucky
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from seqtrace.core.consens import *
from seqtrace.core.sequencetrace import SequenceTrace

import unittest



class TestConsensus(unittest.TestCase):
    def setUp(self):
        self.settings = ConsensSeqSettings()
        self.settings.trim_primers = False

        # Set up some simple sequence trace data.
        self.seqt1 = SequenceTrace()
        self.seqt2 = SequenceTrace()
        self.seqt3 = SequenceTrace()
        self.seqt1.basecalls = 'AAGCTACCTGACATGATTTACG'
        self.seqt2.basecalls = 'GCTCCTGNCACGAATTAC'
        self.seqt3.basecalls = 'AAGCTACCTGACATGATTTACG'
        # alignment of sequences 1 and 2:   'AAGCTACCTGACATGATTTACG'
        #                                   '--GCT-CCTGNCACGAATTAC-'

        #                    A  A   G   C   T   A  C   C   T   G   A   C   A   T   G   A   T   T   T   A   C   G
        self.seqt1.bcconf = [5, 4, 20, 24, 34, 12, 8, 30, 32, 16, 34, 40, 52, 61, 61, 61, 28, 61, 46, 32, 12, 24]
        #                           G   C   T      C   C   T   G   N   C   A   C   G   A   A   T   T   A   C
        self.seqt2.bcconf = [      20, 24, 34,    12,  8, 30, 16, 34, 40, 52, 42, 61, 61, 30, 61, 46, 32, 12    ]
        #                    A  A   G   C   T   A  C   C   T   G   A   C   A   T   G   A   T   T   T   A   C   G
        self.seqt3.bcconf = [5, 4,  0,  4,  4,  2, 8,  0,  2,  6,  4,  0,  2,  1,  1,  1,  8,  1,  6,  2,  2,  4]
        #print len(self.seqt1.getBaseCalls())
        #print len(self.seqt1.bcconf)

        # Set up trace data to use for testing the Bayesian consensus algorithm.
        self.seqt4 = SequenceTrace()
        self.seqt5 = SequenceTrace()
        self.seqt4.basecalls = 'AWAGNCACTCACAB'
        self.seqt5.basecalls = 'GNCCGTGNCADG'
        #                    A   W   A   G   N   C   A   C       T   C   A   C   A   B
        self.seqt4.bcconf = [40, 32, 4,  20, 12, 10, 12, 20,     40, 6,  34, 40, 52, 10    ]
        #                                G   N   C       C   G   T   G   N   C   A   D   G
        self.seqt5.bcconf = [            20, 8,  10,     12, 30, 10, 40, 12, 40, 52, 10, 50]

        # Trace data with all 11 IUPAC ambiguity codes for testing the single-sequence
        # and legacy consensus algorithms.
        self.seqt6 = SequenceTrace()
        self.seqt7 = SequenceTrace()
        self.seqt6.basecalls = 'WSCTAMCTKRCAYGATTHCBDAV'
        self.seqt7.basecalls = 'AWSCTAACAGRCAYGATTWCB'
        # alignment of sequences 6 and 7:   '-WSCTAMCTKRCAYGATTHCBDAV'
        #                                   'AWSCTAACAGRCAYGATTWCB---'

        #                        W   S   C   T   A   M   C   T   K   R   C   A   Y   G   A   T   T   H   C   B   D   A   V
        self.seqt6.bcconf = [    4,  20, 24, 34, 12, 8,  30, 32, 16, 34, 40, 52, 61, 61, 61, 28, 61, 6,  40, 20, 10, 34, 6]
        #                    A   W   S   C   T   A   A   C   A   G   R   C   A   Y   G   A   T   T   W   C   B            
        self.seqt7.bcconf = [5,  4,  18, 40, 30, 8,  20, 32, 28, 6,  36, 40, 7,  60, 58, 61, 34, 61, 14, 40, 12           ]

    # Test the basic ConsensSeqBuilder operations.
    def test_consensus(self):
        cons = ConsensSeqBuilder((self.seqt1,), self.settings)

        self.assertRaises(ConsensSeqBuilderError, cons.setConsensSequence, 'AATT')

        cons.setConsensSequence('   AAAAAAAATTTTTTGGCC ')
        self.assertEqual(cons.getConsensus(), '   AAAAAAAATTTTTTGGCC ')

        self.assertEqual(cons.getCompactConsensus(), 'AAAAAAAATTTTTTGGCC')

        self.assertEqual(cons.getNumSeqs(), 1)

    def test_singleConsensus(self):
        """
        Test consensus sequence construction on a single sequence trace.
        """
        self.settings.setDoAutoTrim(False)

        self.settings.setMinConfScore(30)
        cons = ConsensSeqBuilder((self.seqt1,), self.settings)
        self.assertEqual(cons.getConsensus(), 'NNNNTNNCTNACATGANTTANN')

        self.settings.setMinConfScore(20)
        cons.makeConsensusSequence()
        self.assertEqual(cons.getConsensus(), 'NNGCTNNCTNACATGATTTANG')

        self.settings.setMinConfScore(5)
        cons.makeConsensusSequence()
        self.assertEqual(cons.getConsensus(), 'ANGCTACCTGACATGATTTACG')

        self.settings.setMinConfScore(61)
        cons.makeConsensusSequence()
        self.assertEqual(cons.getConsensus(), 'NNNNNNNNNNNNNTGANTNNNN')

        # Test the special case where none of the confidence scores exceed the quality threshold.
        self.settings.setMinConfScore(10)
        cons = ConsensSeqBuilder((self.seqt3,), self.settings)
        self.assertEqual(cons.getConsensus(), 'NNNNNNNNNNNNNNNNNNNNNN')

        #                          W   S   C   T   A   M   C   T   K   R   C   A   Y   G   A   T   T   H   C   B   D   A   V
        # self.seqt6.bcconf = [    4,  20, 24, 34, 12, 8,  30, 32, 16, 34, 40, 52, 61, 61, 61, 28, 61, 6,  40, 20, 10, 34, 6]

        # Test a case with IUPAC ambiguity codes.
        self.settings.setMinConfScore(10)
        cons = ConsensSeqBuilder((self.seqt6,), self.settings)
        self.assertEqual(cons.getConsensus(), 'NSCTANCTKRCAYGATTNCBDAN')

    def test_defineBasePrDist(self):
        """
        Tests the definition of a nucleotide probability distribution derived from a base call
        and quality score.
        """
        cons = ConsensSeqBuilder((self.seqt1,), self.settings)
        nppd = {'A': 0.0, 'T': 0.0, 'G': 0.0, 'C': 0.0}

        # Define some test cases and expected results.  Includes test cases for all
        # IUPAC ambiguity codes.
        cases = [
                {'call': 'A', 'quality': 10},
                {'call': 'G', 'quality': 10},
                {'call': 'T', 'quality': 22},
                {'call': 'C', 'quality': 54},
                {'call': 'A', 'quality': 1},
                {'call': 'W', 'quality': 4},
                {'call': 'W', 'quality': 1},
                {'call': 'S', 'quality': 4},
                {'call': 'M', 'quality': 6},
                {'call': 'K', 'quality': 4},
                {'call': 'R', 'quality': 4},
                {'call': 'Y', 'quality': 20},
                {'call': 'B', 'quality': 20},
                {'call': 'D', 'quality': 4},
                {'call': 'H', 'quality': 4},
                {'call': 'V', 'quality': 1}
                ]
        results = [
                {'A': 0.9, 'T': 0.1/3, 'G': 0.1/3, 'C': 0.1/3},
                {'A': 0.1/3, 'T': 0.1/3, 'G': 0.9, 'C': 0.1/3},
                {'A': 0.006309573/3, 'T': 0.993690427, 'G': 0.006309573/3, 'C': 0.006309573/3},
                {'A': 0.000003981/3, 'T': 0.000003981/3, 'G': 0.000003981/3, 'C': 0.999996019},
                {'A': 0.205671765, 'T': 0.794328235/3, 'G': 0.794328235/3, 'C': 0.794328235/3},
                {'A': 0.300946415, 'T': 0.300946415, 'G': 0.199053585, 'C': 0.199053585},
                {'A': 0.102835883, 'T': 0.102835883, 'G': 0.397164117, 'C': 0.397164117},
                {'A': 0.199053585, 'T': 0.199053585, 'G': 0.300946415, 'C': 0.300946415},
                {'A': 0.374405678, 'T': 0.125594322, 'G': 0.125594322, 'C': 0.374405678},
                {'A': 0.199053585, 'T': 0.300946415, 'G': 0.300946415, 'C': 0.199053585},
                {'A': 0.300946415, 'T': 0.199053585, 'G': 0.300946415, 'C': 0.199053585},
                {'A': 0.005, 'T': 0.495, 'G': 0.005, 'C': 0.495},
                {'A': 0.01, 'T': 0.33, 'G': 0.33, 'C': 0.33},
                {'A': 0.200630943, 'T': 0.200630943, 'G': 0.200630943, 'C': 0.398107171},
                {'A': 0.200630943, 'T': 0.200630943, 'G': 0.398107171, 'C': 0.200630943},
                {'A': 0.068557255, 'T': 0.794328235, 'G': 0.068557255, 'C': 0.068557255},
                ]

        # Try each test case.
        for (case, result) in zip(cases, results):
            cons.defineBasePrDist(case['call'], case['quality'], nppd)

            # Verify that the probabilities sum to 1.
            self.assertAlmostEqual(sum(nppd.values()), 1.0)

            # Verify that the individual probabilities are correct.
            for base in ('A', 'T', 'G', 'C'):
                self.assertAlmostEqual(result[base], nppd[base])

    def test_calcPosteriorBasePrDist(self):
        """
        Tests the calculation of a posterior nucleotide probability distribution using Bayes'
        Theorem on two separate base calls and quality scores.
        """
        cons = ConsensSeqBuilder((self.seqt1,), self.settings)
        nppd = {'A': 0.0, 'T': 0.0, 'G': 0.0, 'C': 0.0}

        # Define some test cases and expected results.
        cases = [
                {'call1': 'A', 'qual1': 10, 'call2': 'A', 'qual2': 10},
                {'call1': 'G', 'qual1': 7.447274949, 'call2': 'G', 'qual2': 5.228787453},
                {'call1': 'G', 'qual1': 5.228787453, 'call2': 'G', 'qual2': 7.447274949},
                {'call1': 'A', 'qual1': 5.228787453, 'call2': 'T', 'qual2': 15.228787453},
                {'call1': 'T', 'qual1': 15.228787453, 'call2': 'A', 'qual2': 5.228787453},
                {'call1': 'C', 'qual1': 15.228787453, 'call2': 'T', 'qual2': 5.228787453},
                {'call1': 'W', 'qual1': 6.989700043, 'call2': 'T', 'qual2': 5.228787453},
                {'call1': 'W', 'qual1': 6.989700043, 'call2': 'G', 'qual2': 5.228787453},
                {'call1': 'W', 'qual1': 3.979400087, 'call2': 'B', 'qual2': 10},
                {'call1': 'B', 'qual1': 10, 'call2': 'D', 'qual2': 10}
                ]
        results = [
                {'A': 0.995901648, 'T': 0.001366117, 'G': 0.001366117, 'C': 0.001366117},
                {'A': 0.010135135, 'T': 0.010135135, 'G': 0.969594595, 'C': 0.010135135},
                {'A': 0.010135135, 'T': 0.010135135, 'G': 0.969594595, 'C': 0.010135135},
                {'A': 0.066037736, 'T': 0.91509434, 'G': 0.009433962, 'C': 0.009433962},
                {'A': 0.066037736, 'T': 0.91509434, 'G': 0.009433962, 'C': 0.009433962},
                {'A': 0.009433962, 'T': 0.066037736, 'G': 0.009433962, 'C': 0.91509434},
                {'A': 0.117647059, 'T': 0.823529412, 'G': 0.029411765, 'C': 0.029411765},
                {'A': 0.25, 'T': 0.25, 'G': 0.4375, 'C': 0.0625},
                {'A': 0.125, 'T': 0.375, 'G': 0.25, 'C': 0.25},
                {'A': 0.125, 'T': 0.375, 'G': 0.375, 'C': 0.125}
                ]

        # Try each test case.
        for (case, result) in zip(cases, results):
            cons.calcPosteriorBasePrDist(case['call1'], case['qual1'], case['call2'], case['qual2'], nppd)
            #print nppd
            for base in ('A', 'T', 'G', 'C'):
                self.assertAlmostEqual(result[base], nppd[base])

    def test_BayesianConsensus(self):
        """
        Test consensus sequence construction with two (forward/reverse) sequence traces using
        the Bayesian consensus algorithm.
        """
        self.settings.setDoAutoTrim(False)
        self.settings.setConsensusAlgorithm('Bayesian')

        # First, test the special case where none of the confidence scores exceed the quality threshold.
        self.settings.setMinConfScore(30)
        cons = ConsensSeqBuilder((self.seqt3, self.seqt3), self.settings)
        self.assertEqual(cons.getConsensus(), 'NNNNNNNNNNNNNNNNNNNNNN')

        cons = ConsensSeqBuilder((self.seqt4, self.seqt5), self.settings)

        # Verify that the alignment is correct.
        self.assertEqual(cons.getAlignedSequence(0), 'AWAGNCAC-TCACAB-')
        self.assertEqual(cons.getAlignedSequence(1), '---GNC-CGTGNCADG')

        #                      A   W   A   G   N   C   A   C       T   C   A   C   A   B
        # self.seqt4.bcconf = [40, 32, 4,  20, 12, 10, 12, 20,     40, 6,  34, 40, 52, 10    ]
        #                                  G   N   C       C   G   T   G   N   C   A   D   G
        # self.seqt5.bcconf = [            20, 8,  10,     12, 30, 10, 40, 12, 40, 52, 10, 50]
        expconsconf = [40, 32, 4, 44.6841, 1, 23.8739, 12, 36.4455, 30, 54.3132, 34.3809, 34, 84.7703, 108.7711, 2.0412, 50]

        # Run the tests with seqt4 first, then with seqt5 first.
        for cnt in range(2):
            if cnt == 1:
                # Swap the sequence trace order on the second pass through the loop.
                cons = ConsensSeqBuilder((self.seqt5, self.seqt4), self.settings)

            cons.makeConsensusSequence()

            # Get the consensus quality scores, rounding each to 4 decimal places.
            confvals = [round(cval, 4) for cval in cons.consconf]

            # Check that the consensus sequence is correct.
            self.assertEqual(cons.getConsensus(), 'AWNGNNNCGTGACANG')

            # Check that the consensus quality scores are correct.
            for (expconf, conf) in zip(expconsconf, confvals):
                self.assertAlmostEqual(expconf, conf)

    def test_legacyConsensus(self):
        """
        Test consensus sequence construction with two (forward/reverse) sequence traces using
        the legacy (SeqTrace 8.0) consensus algorithm.
        """
        self.settings.setDoAutoTrim(False)
        self.settings.setConsensusAlgorithm('legacy')

        # First, test the special case where none of the confidence scores exceed the quality threshold.
        self.settings.setMinConfScore(10)
        cons = ConsensSeqBuilder((self.seqt3, self.seqt3), self.settings)
        self.assertEqual(cons.getConsensus(), 'NNNNNNNNNNNNNNNNNNNNNN')

        cons = ConsensSeqBuilder((self.seqt1, self.seqt2), self.settings)

        # Verify that the alignment is correct
        self.assertEqual(cons.getAlignedSequence(0), 'AAGCTACCTGACATGATTTACG')
        self.assertEqual(cons.getAlignedSequence(1), '--GCT-CCTGNCACGAATTAC-')

        #                    A  A   G   C   T   A  C   C   T   G   A   C   A   T   G   A   T   T   T   A   C   G
        #                   [5, 4, 20, 24, 34, 12, 8, 30, 32, 16, 34, 40, 52, 61, 61, 61, 28, 61, 46, 32, 12, 24]
        #                           G   C   T       C  C   T   G   N   C   A   C   G   A   A   T   T   A   C
        #                   [      20, 24, 34,     12, 8, 30, 16, 34, 40, 52, 42, 61, 61, 30, 61, 46, 32, 12    ]

        # Run each set of tests with seqt1 first, then with seqt2 first.
        for cnt in range(2):
            if cnt == 1:
                # Swap the sequence trace order on the second pass through the loop.
                cons = ConsensSeqBuilder((self.seqt2, self.seqt1), self.settings)

            # conflicting bases: one pair unresolvable, the other resolvable; no gaps filled
            self.settings.setMinConfScore(30)
            cons.makeConsensusSequence()
            self.assertEqual(cons.getConsensus(), 'NNNNTNNCTNACANGAATTANN')
    
            # conflicting bases: neither pair resolvable; one gap filled
            self.settings.setMinConfScore(20)
            cons.makeConsensusSequence()
            self.assertEqual(cons.getConsensus(), 'NNGCTNNCTNACANGANTTANG')
    
            # two gaps filled
            self.settings.setMinConfScore(12)
            cons.makeConsensusSequence()
            self.assertEqual(cons.getConsensus(), 'NNGCTACCTGACANGANTTACG')
    
            # three gaps filled
            self.settings.setMinConfScore(5)
            cons.makeConsensusSequence()
            self.assertEqual(cons.getConsensus(), 'ANGCTACCTGACANGANTTACG')

        # Run the test case with ambiguous nucleotide codes.

        #      W   S   C   T   A   M   C   T   K   R   C   A   Y   G   A   T   T   H   C   B   D   A   V
        # [    4,  20, 24, 34, 12, 8,  30, 32, 16, 34, 40, 52, 61, 61, 61, 28, 61, 6,  40, 20, 10, 34, 6]
        #  A   W   S   C   T   A   A   C   A   G   R   C   A   Y   G   A   T   T   W   C   B            
        # [5,  4,  18, 40, 30, 8,  20, 32, 28, 6,  36, 40, 7,  60, 58, 61, 34, 61, 14, 40, 12           ]

        cons = ConsensSeqBuilder((self.seqt6, self.seqt7), self.settings)

        # Verify that the alignment is correct
        self.assertEqual(cons.getAlignedSequence(0), '-WSCTAMCTKRCAYGATTHCBDAV')
        self.assertEqual(cons.getAlignedSequence(1), 'AWSCTAACAGRCAYGATTWCB---')

        # Run the test case with seqt6 first, then with seqt7 first.
        for cnt in range(2):
            if cnt == 1:
                # Swap the sequence trace order on the second pass through the loop.
                cons = ConsensSeqBuilder((self.seqt7, self.seqt6), self.settings)

            self.settings.setMinConfScore(10)
            cons.makeConsensusSequence()
            self.assertEqual(cons.getConsensus(), 'NNSCTAACNKRCAYGATTWCBDAN')

    def test_getEndGapStarts(self):
        """
        Test the algorithms for locating the starting indices of end gaps.
        """
        cons = ConsensSeqBuilder((self.seqt2, self.seqt2), self.settings)
        
        # Define a bunch of test cases.
        # Each test case is defined as: ['aligned_sequence_1', 'aligned_sequence_2', [left_gap_start, right_gap_start]]
        gaptests = [
                # Two end gaps with overlapping bases.
                ['--C-GTAC',
                 'GCCTG---',
                 [2, 4]],
                # No overlapping bases.
                ['-----TAC',
                 'GCCTG---',
                 [5, 4]],
                # No left end gap.
                ['GC-TGTAC',
                 'GCCTG---',
                 [0, 4]],
                # No right end gap.
                ['---TGTAC',
                 'GCCTGT-C',
                 [3, 7]],
                # No end gaps.
                ['GC-TGTAC',
                 'GCCTGT-C',
                 [0, 7]],
                # Extra gaps on the ends of the alignment.
                ['--------C-GTA-C--',
                 '-----G-CCTG------',
                 [8, 10]],
                # No sequence data.
                ['--------',
                 'GCCTGTAC',
                 [-1, -1]],
                # No sequence data.
                ['--------',
                 '--------',
                 [-1, -1]]
                ]

        # Run each test case, then switch the sequence order and run them again.
        for cnt in range(2):
            for gtest in gaptests:
                if cnt == 0:
                    cons.alignedseqs[0] = gtest[0]
                    cons.alignedseqs[1] = gtest[1]
                else:
                    # switch the order the second time around
                    cons.alignedseqs[0] = gtest[1]
                    cons.alignedseqs[1] = gtest[0]

                self.assertEqual(cons.getLeftEndGapStart(), gtest[2][0])
                self.assertEqual(cons.getRightEndGapStart(), gtest[2][1])

    def test_trimEndGaps(self):
        """
        Test the trimming of the end gap portion of the sequence.
        """
        self.settings.setMinConfScore(10)
        self.settings.setDoAutoTrim(False)
        self.settings.setConsensusAlgorithm('legacy')
        cons = ConsensSeqBuilder((self.seqt2, self.seqt2), self.settings)
        
        # verify that the consensus sequence and alignment are as expected
        self.assertEqual(cons.getAlignedSequence(0), 'GCTCCTGNCACGAATTAC')
        self.assertEqual(cons.getAlignedSequence(1), 'GCTCCTGNCACGAATTAC')
        self.assertEqual(cons.getConsensus(), 'GCTCNTGNCACGAATTAC')

        # no gap to trim
        cons.trimEndGaps()
        self.assertEqual(cons.getConsensus(), 'GCTCNTGNCACGAATTAC')

        # define a bunch of test cases
        # each test case is defined as: ['aligned_sequence_1', 'aligned_sequence_2', 'trimmed_consensus']
        gaptrimtests = [
                # multi-base gap on each end
                ['----CTGACACGAATTAC',
                 'GCTCCTGACACGAA----',
                 '    NTGACACGAA    '],
                # single-base gap on each end
                ['-CTCCTGACACGAATTAC',
                 'GCTCCTGACACGAATTA-',
                 ' CTCNTGACACGAATTA '],
                # adjacent gaps
                ['--TCCTGACACGA--TAC',
                 'GC-CCTGACACGAAT---',
                 '  TCNTGACACGAAT   '],
                # both gaps in one sequence
                ['---CCTGACACGAATT--',
                 'GCTCCTGACACGAATTAC',
                 '   CNTGACACGAATT  '],
                # single base
                ['------G-----------',
                 'GCTCCTGACACGAATTAC',
                 '      G           '],
                # single-base overlap
                ['------GACACGAATTAC',
                 'GCTCCTG-----------',
                 '      G           '],
                # no overlap
                ['-------ACACGAATTAC',
                 'GCTCCTG-----------',
                 '                  '],
                # no sequence
                ['------------------',
                 'GCTCCTGACACGAATTAC',
                 '                  '],
                ]

        for cnt in range(2):
            for gttest in gaptrimtests:
                if cnt == 0:
                    cons.alignedseqs[0] = gttest[0]
                    cons.alignedseqs[1] = gttest[1]
                else:
                    # switch the order the second time around
                    cons.alignedseqs[0] = gttest[1]
                    cons.alignedseqs[1] = gttest[0]

                cons.setConsensSequence('GCTCNTGACACGAATTAC')
                cons.trimEndGaps()
                self.assertEqual(cons.getConsensus(), gttest[2])


    # Test the automatic trimming of sequence ends.
    def test_trimConsensus(self):
        # Test consensus construction with end trimming by testing a bunch of different
        # confscore/windowsize/num good bases combinations, including special cases.
        self.settings.setMinConfScore(30)
        self.settings.setDoAutoTrim(True)
        self.settings.setAutoTrimParams(6, 6)
        cons = ConsensSeqBuilder((self.seqt1,), self.settings)
        self.assertEqual(cons.getConsensus(), '          ACATGA      ')

        self.settings.setAutoTrimParams(6, 5)
        cons.makeConsensusSequence()
        self.assertEqual(cons.getConsensus(), '       CTNACATGANTTA  ')

        self.settings.setAutoTrimParams(6, 4)
        cons.makeConsensusSequence()
        self.assertEqual(cons.getConsensus(), '      NCTNACATGANTTAN ')

        self.settings.setAutoTrimParams(6, 3)
        cons.makeConsensusSequence()
        self.assertEqual(cons.getConsensus(), '   NTNNCTNACATGANTTANN')

        self.settings.setAutoTrimParams(7, 6)
        cons.makeConsensusSequence()
        self.assertEqual(cons.getConsensus(), '       CTNACATGANTTA  ')

        self.settings.setAutoTrimParams(7, 7)
        cons.makeConsensusSequence()
        self.assertEqual(cons.getConsensus(), '                      ')

        self.settings.setMinConfScore(5)
        self.settings.setAutoTrimParams(3, 2)
        cons.makeConsensusSequence()
        self.assertEqual(cons.getConsensus(), 'ANGCTACCTGACATGATTTACG')

        self.settings.setAutoTrimParams(3, 3)
        cons.makeConsensusSequence()
        self.assertEqual(cons.getConsensus(), '  GCTACCTGACATGATTTACG')

        self.settings.setMinConfScore(20)
        self.settings.setAutoTrimParams(3, 2)
        cons.makeConsensusSequence()
        self.assertEqual(cons.getConsensus(), ' NGCTNNCTNACATGATTTANG')

        self.settings.setAutoTrimParams(3, 3)
        cons.makeConsensusSequence()
        self.assertEqual(cons.getConsensus(), '  GCTNNCTNACATGATTTA  ')

        # now some special cases: window size of 1
        self.settings.setMinConfScore(30)
        self.settings.setAutoTrimParams(1, 1)
        cons.makeConsensusSequence()
        self.assertEqual(cons.getConsensus(), '    TNNCTNACATGANTTA  ')

        # window size equal to the sequence length, base count 1 more than the number of good bases
        self.settings.setAutoTrimParams(22, 13)
        cons.makeConsensusSequence()
        self.assertEqual(cons.getConsensus(), '                      ')

        # window size equal to the sequence length, base count exactly equal to the number of good bases
        self.settings.setAutoTrimParams(22, 12)
        cons.makeConsensusSequence()
        self.assertEqual(cons.getConsensus(), 'NNNNTNNCTNACATGANTTANN')


class TestModifiableConsensus(unittest.TestCase):
    def setUp(self):
        # set up some simple sequence trace data
        self.seqt1 = SequenceTrace()
        self.seqt1.basecalls = 'AAGCTACCTGACATGATTTACG'

        #                    A  A   G   C   T   A  C   C   T   G   A   C   A   T   G   A   T   T   T   A   C   G
        self.seqt1.bcconf = [5, 4, 20, 24, 34, 12, 8, 30, 32, 16, 34, 40, 52, 61, 61, 61, 28, 61, 46, 32, 12, 24]

        self.settings = ConsensSeqSettings()
        self.settings.setDoAutoTrim(False)
        self.settings.setMinConfScore(4)
        self.cons = ModifiableConsensSeqBuilder((self.seqt1,), self.settings)

        # delete test cases: [start index, end index, result]
        self.del_tests = [
                [0, 0, ' AGCTACCTGACATGATTTACG'],   # one base from the beginning
                [21, 21, ' AGCTACCTGACATGATTTAC '], # one base from the end
                [4, 10, ' AGC       CATGATTTAC '],  # several from the middle 
                [0, 21, '                      ']   # the entire sequence
                ]

        # modify test cases: [start index, end index, replacement, result]
        self.modify_tests = [
                [0, 0, 'C', 'CAGCTACCTGACATGATTTACG'],      # one base from the beginning
                [21, 21, 'A', 'CAGCTACCTGACATGATTTACA'],    # one base from the end
                [7, 10, 'TCAT', 'CAGCTACTCATCATGATTTACA'],  # several from the middle 
                [0, 21, 'AATTGGCCTGACTGACGACTAA', 'AATTGGCCTGACTGACGACTAA']   # the entire sequence
                ]

    def test_deleteBases(self):
        for testcase in self.del_tests:
            self.cons.deleteBases(testcase[0], testcase[1])
            self.assertEqual(self.cons.getConsensus(), testcase[2])

        # test again, with the start and end indexes swapped
        self.cons.makeConsensusSequence()
        for testcase in self.del_tests:
            self.cons.deleteBases(testcase[1], testcase[0])
            self.assertEqual(self.cons.getConsensus(), testcase[2])

    def test_modifyBases(self):
        for testcase in self.modify_tests:
            self.cons.modifyBases(testcase[0], testcase[1], testcase[2])
            self.assertEqual(self.cons.getConsensus(), testcase[3])

        # Test again, with the start and end indexes swapped.
        self.cons.makeConsensusSequence()
        for testcase in self.modify_tests:
            self.cons.modifyBases(testcase[0], testcase[1], testcase[2])
            self.assertEqual(self.cons.getConsensus(), testcase[3])

    def test_undoRedo(self):
        # apply all of the delete test cases
        for testcase in self.del_tests:
            self.cons.deleteBases(testcase[0], testcase[1])

        # now undo them all and test the results
        for cnt in range(len(self.del_tests) - 1, -1, -1):
            self.assertEqual(self.cons.getConsensus(), self.del_tests[cnt][2])
            self.cons.undo()
        # make sure we ended on the starting sequence
        self.assertEqual(self.cons.getConsensus(), self.seqt1.getBaseCalls())

        # now redo them all and test the results
        for testcase in self.del_tests:
            self.cons.redo()
            self.assertEqual(self.cons.getConsensus(), testcase[2])

        # apply all of the modify test cases
        self.cons.makeConsensusSequence()
        for testcase in self.modify_tests:
            self.cons.modifyBases(testcase[0], testcase[1], testcase[2])

        # now undo them all and test the results
        for cnt in range(len(self.modify_tests) - 1, -1, -1):
            self.assertEqual(self.cons.getConsensus(), self.modify_tests[cnt][3])
            self.cons.undo()
        # make sure we ended on the starting sequence
        self.assertEqual(self.cons.getConsensus(), self.seqt1.getBaseCalls())

        # now redo them all and test the results
        for testcase in self.modify_tests:
            self.cons.redo()
            self.assertEqual(self.cons.getConsensus(), testcase[3])

        # finally, test recalcConsensusSequence()
        oldseq = self.cons.getConsensus()
        self.cons.recalcConsensusSequence()
        self.assertEqual(self.cons.getConsensus(), self.seqt1.getBaseCalls())
        self.cons.undo()
        self.assertEqual(self.cons.getConsensus(), oldseq)
        self.cons.redo()
        self.assertEqual(self.cons.getConsensus(), self.seqt1.getBaseCalls())





if __name__ == '__main__':
    #unittest.main()
    suite = unittest.defaultTestLoader.loadTestsFromName(__name__)
    unittest.TextTestRunner(verbosity=2).run(suite)

