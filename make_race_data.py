# -*- coding: utf-8 -*-

import sys
sys.path.append('demog-text-removal/src/data')

import os
import io
import pandas as pd
import codecs
import click
import logging
from data_utils import get_attr_sentiments, to_file, get_data, get_race, \
    mention_split
from twitter_utils import happy, sad
from twitter_utils import normalize_text
from twitter_utils import MENTION
from tqdm import tqdm
from xml.etree import ElementTree as etree
from make_data import MIN_SENTENCE_LEN
from data_utils import CONF_LEVEL


logger = logging.getLogger('main')
logger.setLevel(logging.INFO)

SEED = 16

CLASS = 40000
TRAIN = 50000
DEV = 2000
TEST = 2000


def extract_text(text):
    try:
        toks = normalize_text(text)
    except:
        return []
    return toks


def is_feasible(toks):
    # text = normalize_text(rec['text'])
    if len(toks) < MIN_SENTENCE_LEN:
        return False
    if len(set(toks)) == 1 and toks[0] == MENTION:
        return False
    return True


def find_sentiment(df, emotions, other_emotions, col):
    df['found_sentiment'] = False
    for sentiment in tqdm(emotions):
        df.loc[df['text'].str.contains(
            sentiment, na=False), 'found_sentiment'] = True

    def check_others(rec):
        if not rec['found_sentiment']:
            return False
        try:
            t = rec.toks
            # there's more than one sentiment emoji
            if not set(t).isdisjoint(other_emotions):
                return False
        except:
            pass
        return True

    df[col] = False
    df.loc[df[['found_sentiment', 'toks']].apply(
        check_others, axis=1), col] = True
    df.drop('found_sentiment', axis=1, inplace=True)
    return df


@click.command()
@click.argument('input_file_path', type=str)
@click.argument('output_obj_file_path', type=str)  # all data entries extracted.
@click.argument('output_folder', type=str)  # output folder for putting all generated dataset splits.
def main(input_file_path, output_obj_file_path, output_folder):
    tqdm.pandas()

    print('loading raw data file: ' + input_file_path)
    df = get_data(input_file_path)
    df = df.sample(frac=1, axis=1, random_state=SEED).reset_index(drop=True)

    df['is_white'] = False
    df['is_aa'] = False
    df.loc[(df.wh > CONF_LEVEL), 'is_white'] = True
    df.loc[(df.aa > CONF_LEVEL), 'is_aa'] = True

    df = df[
        (df.is_white | df.is_aa)
    ]

    print('cleaning up texts')
    df['toks'] = df['text'].progress_apply(extract_text)
    df = df[df['toks'].progress_apply(is_feasible)]

    print('extracting sentiments')
    # df['is_happy'] = find_sentiment(df, happy, sad)
    df = find_sentiment(df, happy, sad, 'is_happy')
    df = find_sentiment(df, sad, happy, 'is_sad')
    df = df[
        (df.is_happy) | (df.is_sad)]

    print('write csv file')
    df.to_pickle(output_obj_file_path)
    # df = pd.read_pickle(output_csv_file_path)

    # write text file
    print("write text file")
    output_text_file_path = os.path.join(output_folder, 'twitter.txt')
    # with open(output_text_file_path, 'w') as f:
    with codecs.open(output_text_file_path, 'w', 'utf-8') as f:
        for _, rec in df.iterrows():
            # toks = eval(rec['toks'])
            # f.write(u' '.join(toks))
            # try:
            f.write(' '.join(rec['toks']).decode('utf-8', errors='ignore'))
            f.write('\n')
            # except:

    print('write dat file')
    output_dat_file_path = os.path.join(output_folder, 'twitter.dat')
    # with open(output_dat_file_path, 'w') as f:
    with codecs.open(output_dat_file_path, 'w', 'utf-8') as f:
        for _, rec in df.iterrows():
            if rec['is_happy']:
                sentiment = 'happy'
            if rec['is_sad']:
                sentiment = 'sad'
            if rec['is_white']:
                race = 'white'
            if rec['is_aa']:
                race = 'aa'
            obj = etree.Element('LINE', attrib={
                'SENTIMENT': sentiment,
                'RACE': race
            })
            f.write(etree.tostring(obj))
            f.write('\n')

    def write_text_to_file(df, file):
        with codecs.open(file, 'w', 'utf-8') as f:
            for _, rec in df.iterrows():
                f.write(' '.join(rec['toks']).decode('utf-8', errors='ignore'))
                f.write('\n')

    for race in ['white', 'aa']:
        df_part = df[df['is_' + race]]
        beg = 0
        write_text_to_file(
            df_part[beg:beg+CLASS], os.path.join(output_folder, '{}_only.{}.txt'.format(race, 'class')))
        beg += CLASS
        write_text_to_file(
            df_part[beg:beg+TRAIN], os.path.join(output_folder, '{}_only.{}.txt'.format(race, 'train')))
        beg += TRAIN
        write_text_to_file(
            df_part[beg:beg+DEV], os.path.join(output_folder, '{}_only.{}.txt'.format(race, 'dev')))
        beg += DEV
        write_text_to_file(
            df_part[beg:beg+TEST], os.path.join(output_folder, '{}_only.{}.txt'.format(race, 'test')))


if __name__ == "__main__":
    main()
