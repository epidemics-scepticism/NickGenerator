#!/usr/bin/env python3

# The MIT License
# 
# Copyright (c) 2011 Christopher Pound
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# lc.py -- language confluxer (http://www.ruf.rice.edu/~pound/lc.py)
#
# - Written by Christopher Pound (pound@rice.edu), July 1993.
# - Loren Miller suggested I make sure lc starts by picking a
#   letter pair that was at the beginning of a data word, Oct 95.
# - Cleaned it up a little bit, March 95; more, September 01
# - Python version, Jul 09
# - Python version, 2016 [ cacahuatl ]
# - Use SystemRandom, 2016 [ cacahuatl ]
# - Add generate_nick() to mimic tails bash script functionality [ cacahuatl ]
#
# The datafile should be a bunch of words from some language
# with minimal punctuation or garbage (# starts a comment).

import re
from optparse import OptionParser
from random import SystemRandom
random = SystemRandom()

class nick:
    def __init__(self, **dict):
        """Set up a new pseudolanguage"""
        dict.setdefault('name', '')
        self.name = dict['name']
        self.parsed = False
        self.data = {}
        self.inits = {}
        self.pairs = {}

    def incorporate(self, files):
        """Load list of files for this pseudolanguage into self.data"""
        self.parsed = False
        for f in files:
            words = []
            with open(f) as text:
                for line in text:
                    line = line.strip()
                    line = re.sub(r"#.*", "", line)
                    words.extend(re.split(r"\s+", line))
                self.data[f] = words

    def delete(self, files):
        """Delete a list of languages from self.data"""
        self.parsed = False
        for f in files:
            del self.data[f]

    def parse(self):
        """Parse pseudolanguage's data into self.inits and self.pairs"""
        if not self.parsed:
            self.inits.clear()
            self.pairs.clear()
            for f in self.data:
                for word in self.data[f]:
                    word += ' '
                    if len(word) > 3:
                        if word[0:2] in self.inits:
                            self.inits[word[0:2]].append(word[2:3])
                        else:
                            self.inits[word[0:2]] = [word[2:3]]
                    pos = 0
                    while pos < len(word)-2:
                        if word[pos:pos+2] in self.pairs:
                            self.pairs[word[pos:pos+2]].append(word[pos+2])
                        else:
                            self.pairs[word[pos:pos+2]] = [word[pos+2]]
                        pos = pos + 1
            self.parsed = True

    def generate(self, number, min, max):
        """Generate list of words of min and max lengths"""
        self.parse()
        wordlist = []
        while len(wordlist) < number:
            word = random.choice(list(self.inits.keys()))
            while word.find(' ') == -1:
                word += random.choice(self.pairs[word[-2:]])
            word = word.strip()
            if len(word) >= min and len(word) <= max:
                wordlist.append(word)
        return wordlist

    def prob(self,p):
        return bool(p > random.randint(0,99))

    def transform_leet(self,nick):
        return nick[0:1] + nick[1:].replace('e','3').replace('i','1').replace('o','0')

    def transform_suffix(self, nick):
        if self.prob(50):
            return nick + "_"
        else:
            return nick + "^"

    def transform_case(self, nick):
        return nick.lower()

    def transform_nick(self, nick):
        if self.prob(90):
            nick = self.transform_case(nick)
        if self.prob(5):
            nick = self.transform_suffix(nick)
        if self.prob(5):
            nick = self.transform_leet(nick)
        return nick

    def generate_nick(self, number, min, max):
        """Generate a nick in the style of tails"""
        nicks = self.generate(number, min, max)
        results = []
        for nick in nicks:
            results.append(self.transform_nick(nick))
        return results

if __name__ == "__main__":
    from sys import argv
    from os.path import dirname
    usage = "usage: %prog [options] datafile1 [datafile2 ...]"
    parser = OptionParser(usage=usage, version="%prog 1.1")
    parser.add_option("-g", "--generate", type="int", dest="num",
                     help="Generate specified number of words", default=1)
    parser.add_option("--min", type="int", dest="min", default=4,
                     help="Set the minimum length of each word")
    parser.add_option("--max", type="int", dest="max", default=10,
                     help="Set the maximum length of each word")
    (options, args) = parser.parse_args()
    if len(args) < 1:
        args.append(dirname(argv[0]) + "/firstnames.txt")
    n = nick()
    n.incorporate(args)
    for nick in n.generate_nick(options.num, options.min, options.max):
        print('{}'.format(nick))
