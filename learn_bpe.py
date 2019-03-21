# python learn_bpe.py -input=D:/mt_data/korean-english-park.train.ko -output=D:/mt_data/korean-english-park.train.ko.bpe_result

import argparse
from collections import Counter, defaultdict

parser = argparse.ArgumentParser()
parser.add_argument('-input', help="input path")
parser.add_argument('-output', help="output path")
args = parser.parse_args()

def get_vocabulary(data):
    '''띄어쓰기 기반으로 vocab 생성'''
    vocab = Counter()
    for i, line in enumerate(data):
        for word in line.strip('\n').split(' '):
            vocab[word] += 1
    return vocab

def learn_bpe(infile, outfile):
    outfile.write('# bpe version 0.1 by kh-mo')
    vocab = get_vocabulary(infile)
    vocab = dict([(tuple(word), count) for (word, count) in vocab.items()]) ### get_vocabulary에 녹아있으면 안되는 이유?
    sorted_vocab = sorted(vocab.items(), key=lambda x:x[1], reverse=True)

    stats, indices = get_pair_statistics(sorted_vocab)
    most_frequent = max(stats, key=lambda x: (stats[x], x))
    outfile.write('{0} {1}\n'.format(*most_frequent))

if __name__ == "__main__":
    input = open(args.input, 'r', encoding='utf8').readlines()
    with open(args.output, 'w', encoding='utf8') as out:
        learn_bpe(input, out)
