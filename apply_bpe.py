# python apply_bpe.py -input=D:/mt_data/korean-english-park.train.ko

import re
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-input', help="input path")
parser.add_argument('-output', help="output path")
args = parser.parse_args()

def process_line(data):
    '''out = ("\r\n ") bpe ("\r\n ")를 리턴한다'''
    out = ""
    leading_whitespace = len(data)-len(data.lstrip("\r\n "))
    if leading_whitespace:
        out += data[:leading_whitespace]

    out += segment(data)

    trailing_whitespace = len(data)-len(data.rstrip('\r\n '))
    if trailing_whitespace:
        out += data[-trailing_whitespace:]

    return out

def segment(data):
    segments = segment_token(data.strip("\r\n ").split(' '))
    return segments

def segment_token(data):
    output = []
    for word in data:
        if not word:
            continue
        new_word = [segment for segment in _isolated_glossaries(word)]
        print(new_word)
    return output

def _isolated_glossaries(data):
    word_segments = [data]
    for gloss in glossaries:
        word_segments = [out_segments for segment in word_segments for out_segments in isolate_glossary(segment, gloss)]
    return word_segments

def isolate_glossary(data1, data2):
    ### re.match(a,b) : a와 매칭되는 것을 b에서 찾는다
    ### ^ : 처음, $ : 끝
    ### re.search(a,b) : a를 b에서 찾는다
    ## data2가 data1에는 있지만 단독 단어는 아니다 => 그 경우에만 분할하겠다
    if re.match('^' + data2 + '$', data1) or not re.search(data2, data1):
        return [data1]
    else:
        segments = re.split(r'({})'.format(data2), data1)
        segments, ending = segments[:-1], segments[-1]
        segments = list(filter(None, segments))  # Remove empty strings in regex group.
        return segments + [ending.strip('\r\n ')] if ending != '' else segments

if __name__ == "__main__":
    input = open(args.input, 'r', encoding='utf8').readlines()
    glossaries = []
    for line in input:
        process_line(line)












cache = {}

def get_pairs(word):
    """Return set of symbol pairs in a word.
    word is represented as tuple of symbols (symbols being variable-length strings)
    """
    pairs = set()
    prev_char = word[0]
    for char in word[1:]:
        pairs.add((prev_char, char))
        prev_char = char
    return pairs

def encode(orig, bpe_codes, bpe_codes_reverse, vocab, separator, version, cache, glossaries=None):
    """Encode word based on list of BPE merge operations, which are applied consecutively"""

    if orig in cache:
        return cache[orig]

    if re.match('^({})$'.format('|'.join(glossaries)), orig):
        cache[orig] = (orig,)
        return (orig,)

    if version == (0, 1):
        word = tuple(orig) + ('</w>',)
    elif version == (0, 2): # more consistent handling of word-final segments
        word = tuple(orig[:-1]) + ( orig[-1] + '</w>',)
    else:
        raise NotImplementedError

    pairs = get_pairs(word)

    if not pairs:
        return orig
    bpe_codes =  dict([(('다', '.'),1), (('방', '침'),2), (('이', '다'),3), (('침', '이'),4)])

    while True:
        bigram = min(pairs, key = lambda pair: bpe_codes.get(pair, float('inf')))
        if bigram not in bpe_codes:
            break
        first, second = bigram
        new_word = []
        i = 0
        while i < len(word):
            try:
                j = word.index(first, i)
                new_word.extend(word[i:j])
                i = j
            except:
                new_word.extend(word[i:])
                break

            if word[i] == first and i < len(word)-1 and word[i+1] == second:
                new_word.append(first+second)
                i += 2
            else:
                new_word.append(word[i])
                i += 1
        new_word = tuple(new_word)
        word = new_word
        if len(word) == 1:
            break
        else:
            pairs = get_pairs(word)

    # don't print end-of-word symbols
    if word[-1] == '</w>':
        word = word[:-1]
    elif word[-1].endswith('</w>'):
        word = word[:-1] + (word[-1].replace('</w>',''),)

    if vocab:
        word = check_vocab_and_split(word, bpe_codes_reverse, vocab, separator)

    cache[orig] = word
    return word