#!/usr/bin/env/python

""" EcoCor Extractor This script extracts frequencies of words from a given word list in
text segments. As input a JSON object is passed over an API which saves the text segment
and their IDs and optionally a URL to the word list on which basis the frequencies are
extracted. It returns a JSON in which for each word the frequency per text segment is
saved.

Input Format: {"segments": [{"segment_id":"xyz", "text":"asd ..."}, ...], "language":"de",
"word_list":{"url":"http://..."}}
WordList Format: [{"word":abc, "wikidata_ID":"Q12345","category":"plant"}]
Output Format: [{"word":"xyz", "wikidata_ID":"Q12345","category":"plant",
"overall_frequency":1234, "segment_frequencies":{segment_id:1234,...}}] 
-> only of words that appear at least once in the text

This scripts requires `spacy` to be installed. Additionally the spacy models
for English and German must be downloaded: `de_core_news_sm`, `en_core_web_sm` """

import sys
from pydantic.networks import HttpUrl
import requests
from collections import Counter
from enum import Enum

import spacy
from pydantic import BaseModel


class Language(str, Enum):
    EN = "en"
    DE = "de"


class Segment(BaseModel):
    text: str
    segment_id: str


class WordInfo(BaseModel):
    word: str
    wikidata_ID: str
    category: str


class WordInfoFrequency(WordInfo):
    segment_frequencies: dict[str, int]
    overall_frequency: int


class UrlDescriptor(BaseModel):
    url: HttpUrl


class SegmentWordListUrl(BaseModel):
    segments: list[Segment]
    word_list: UrlDescriptor = UrlDescriptor(
        url="https://raw.githubusercontent.com/dh-network/ecocor-extractor/main/word_list/organisms_known_by_common_name.json"
    )
    language: Language


# TODO: handle exception nicer?
def read_word_list(url: str) -> list[WordInfo]:
    response = requests.get(url)
    response.raise_for_status()
    word_list = [WordInfo(**entry) for entry in response.json()]
    return word_list


def initialize_de():
    global nlp
    nlp = spacy.load("de_core_news_sm")


def initialize_en():
    global nlp
    nlp = spacy.load("en_core_web_sm")


def setup_analysis_components(language: Language):
    if language == Language.DE:
        initialize_de()
    elif language == Language.EN:
        initialize_en()


# can we get a list here? or hug magic
# language should be in ?language=de and should be read automatically here
# how is the resouce url (word list) passed?
def process_text(segments_word_list: SegmentWordListUrl) -> list[WordInfoFrequency]:
    word_list = read_word_list(segments_word_list.word_list.url)
    word_to_word_info = {}

    for entry in word_list:
        if entry.word not in word_to_word_info:
            word_to_word_info[entry.word] = []
        word_to_word_info[entry.word].append(entry.dict())

    setup_analysis_components(segments_word_list.language)
    unique_words = set([entry.word for entry in word_list])

    # annotate
    word_to_segment_frq = {}

    for i, annotated_segment in enumerate(
        nlp.pipe(
            [segment.text for segment in segments_word_list.segments],
            disable=["parser", "ner"],
        )
    ):
        lemmatized_text = [token.lemma_ for token in annotated_segment]

        # count and intersect
        vocabulary = set(lemmatized_text)
        counted = Counter(lemmatized_text)
        intersect = unique_words.intersection(vocabulary)

        # save frequencies
        for word in intersect:
            if word not in word_to_segment_frq:
                word_to_segment_frq[word] = {}
            word_to_segment_frq[word][
                segments_word_list.segments[i].segment_id
            ] = counted[word]

    result = []
    all_segment_ids = [entry.segment_id for entry in segments_word_list.segments]
    for word, segment_frq in word_to_segment_frq.items():
        segment_frq_zero_filled = {
            (seg_id if seg_id in all_segment_ids else seg_id): (
                segment_frq[seg_id] if seg_id in segment_frq else 0
            )
            for seg_id in all_segment_ids
        }
        word_infos = word_to_word_info[word]
        overall_frequency = sum(segment_frq.values())
        for word_info in word_infos:
            result.append(
                WordInfoFrequency(
                    segment_frequencies=segment_frq_zero_filled,
                    overall_frequency=overall_frequency,
                    **word_info,
                )
            )
    return result
