# python learn_bpe.py -input=D:/mt_data/korean-english-park.train.ko -output=D:/mt_data/korean-english-park.train.ko.bpe_result -symbol_count=2000

import re
import argparse
from collections import Counter, defaultdict

parser = argparse.ArgumentParser()
parser.add_argument('-input', help="input path")
parser.add_argument('-output', help="output path")
parser.add_argument('-symbol_count', type=int, help="a_number_of_new_symbol")
args = parser.parse_args()

def get_vocabulary(data):
    '''띄어쓰기 기반으로 vocab 생성'''
    vocab = Counter()
    for i, line in enumerate(data):
        for word in line.strip('\n').split(' '):
            if word:
                vocab[word] += 1
    vocab = [(tuple(word), count) for (word, count) in vocab.items()]
    return vocab

def get_pair_statistics(data):
    '''
    stats : (pair, 빈도수) 반환
    index_inform : vocab에서 (pair : voca내 index) 반환
    '''
    stats = Counter()
    index_inform = defaultdict(list)
    for idx, (word, count) in enumerate(data):
        first_char = word[0]
        for second_char in word[1:]:
            stats[first_char, second_char] += count
            index_inform[first_char, second_char].append(idx)
            first_char = second_char
    return stats, index_inform

def replace_pair(pair, vocab, indices):
    """('A', 'B') pair를 'AB'로 변환하여 새로운 voca 반환"""
    first, second = pair
    pair_str = ''.join(pair)
    pattern = re.compile(r'(?<!\S)' + re.escape(first + ' ' + second) + r'(?!\S)')
    for j in indices[pair]:
        word, freq = vocab[j]
        new_word = ' '.join(word)
        new_word = pattern.sub(pair_str, new_word)
        new_word = tuple(new_word.split(' '))
        vocab[j] = (new_word, freq)
    return vocab

def learn_bpe(infile, outfile, count):
    '''bpe 학습'''
    outfile.write('# bpe version 0.1 by kh-mo\n')
    vocab = get_vocabulary(infile)

    for i in range(count):
        stats, index_inform = get_pair_statistics(vocab)
        most_frequent = max(stats.items(), key=lambda x: x[1])[0]
        outfile.write('{0} {1}\n'.format(*most_frequent))
        vocab = replace_pair(most_frequent, vocab, index_inform)
        if i % 100 == 0:
            print("count :", i)

if __name__ == "__main__":
    input = open(args.input, 'r', encoding='utf8').readlines()
    with open(args.output, 'w', encoding='utf8') as out:
        learn_bpe(input, out, args.symbol_count)

#
# input = open("D:/mt_data/korean-english-park.train.ko", 'r', encoding='utf8').readlines()
# infile = input
# data = vocab
# data = sorted_vocab
