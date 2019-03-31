# python apply_bpe.py -input=D:/mt_data/korean-english-park.train.ko -output=D:/mt_data/korean-english-park.train.ko.apply_bpe_result

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
    output = []
    flow = data.strip("\r\n ").split(' ')
    for word in flow:
        if not word:
            continue # 공백 제거 목적

        segments = [segment for segment in _isolated_glossaries(word)]

        for item in segments[:-1]:
            output.append(item + separator)
        output.append(segments[-1])
    return ' '.join(output)

def _isolated_glossaries(data):
    '''glossaries 내 단어는 살려서 분할'''
    word_segments = [data]
    for gloss in glossaries:
        word_segments = [out_segments for data in word_segments for out_segments in isolate_glossary(data, gloss)]
    return word_segments

def isolate_glossary(data1, data2):
    '''
    re.match(a,b) : a와 b가 매칭되는 것을 찾는다
    ^ : 처음, $ : 끝
    re.search(a,b) : a를 b에서 찾는다
    data2가 data1에는 있지만 단독 단어는 아니다 => 그 경우에만 분할하겠다
    '''
    if re.match('^' + data2 + '$', data1) or not re.search(data2, data1):
        return [data1]
    else:
        segments = re.split(r'({})'.format(data2), data1)
        segments, ending = segments[:-1], segments[-1]
        segments = list(filter(None, segments))  # Remove empty strings in regex group.
        return segments + [ending.strip('\r\n ')] if ending != '' else segments

if __name__ == "__main__":
    input = open(args.input, 'r', encoding='utf8').readlines()
    glossaries = ["개인","부분"]
    separator = "@@"
    with open(args.output, 'w', encoding='utf8') as out:
        for line in input:
            out.write(process_line(line))
