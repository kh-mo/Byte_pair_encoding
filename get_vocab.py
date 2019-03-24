# python get_vocab.py -input=D:/mt_data/korean-english-park.train.ko -output=D:/mt_data/vocab

import argparse
from collections import Counter

parser = argparse.ArgumentParser()
parser.add_argument("-input")
parser.add_argument("-output")
args = parser.parse_args()

def get_vocab(infile, outfile):
    c = Counter()
    for line in infile:
        for word in line.strip('\r\n ').split(' '):
            if word:
                c[word] += 1

    for key, f in sorted(c.items(), key=lambda x: x[1], reverse=True):
        outfile.write(key+" "+ str(f) + "\n")

if __name__ == "__main__":
    input = open(args.input, 'r', encoding='utf8').readlines()
    with open(args.output, 'w', encoding='utf8') as out:
        get_vocab(input, out)
    print("Done.")