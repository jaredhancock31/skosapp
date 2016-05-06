#!/usr/bin/env python
import rdflib
import skos as pyskos
import logging
import json
import sys
import requests
from requests.auth import HTTPBasicAuth
from collections import OrderedDict
from constants import *


logging.basicConfig(level=logging.INFO)     # use logging during the parsing process
AUTH = HTTPBasicAuth('ppuser', 'infoneer')
CORPUS_URL = "http://infoneer.poolparty.biz/PoolParty/api/corpusmanagement/" \
          "1DBC67E1-7669-0001-8A4A-F4B06F409540/results/" \
          "concepts?corpusId=corpus:7183eaa9-ddac-4a8f-82b6-1e62a31610fa&startIndex="


# TODO sort method
class SkosTool(object):

    """
     TODO doc
    """

    def __init__(self, rdf_path=None):
        self.rdf_file = rdf_path
        self.__g = rdflib.Graph()
        self.__g.parse(location=rdf_path, format='application/rdf+xml')
        self.__loader = pyskos.RDFLoader(self.__g, max_depth=1, flat=True)
        self.__sorted = False
        self.concepts = self.__loader.getConcepts()  # composition of the 'collections.MutableSet'

        # setup separate dict (with same keys) with a skeleton to house our calculated metrics
        self.metrics = {uri: {PREF_LABEL: '',
                              IMPORTANCE_SCORE: 0,
                              NUM_RELATIONS: 0,
                              NUM_EXTERNAL: 0,
                              FREQUENCY: 0} for uri in self.concepts}

    def parse(self):
        """
        TODO write docs
        """

        for uri in self.concepts:
            concept = self.concepts[uri]

            # TODO remove this buuuuullshit
            print uri,  type(uri)

            # set prefLabel in metrics dict
            if self.metrics[uri][PREF_LABEL] is '':
                self.metrics[uri][PREF_LABEL] = concept.prefLabel

            # gather and increment relation data in metric table
            if concept.related:
                for r in concept.related:
                    self.metrics[r][NUM_RELATIONS] += 1
                    self.metrics[r][IMPORTANCE_SCORE] += REL_SCORE_FACTOR

            if concept.synonyms:
                self.metrics[concept.uri][IMPORTANCE_SCORE] += EXTERNAL_LINK_FACTOR
                self.metrics[concept.uri][NUM_EXTERNAL] = len(concept.synonyms)

    def __normalize_on_max(self, max_score=None):
        """
        using the highest-scoring concept in the metrics dict, normalize all importance scores to keep them all
        below 1.00
        :param max_score: highest importance score
        """
        if max_score is None:
            max_score = max(float(d[IMPORTANCE_SCORE]) for d in self.metrics.values())
            for concept in self.metrics:
                previous = self.metrics[concept][IMPORTANCE_SCORE]
                self.metrics[concept][IMPORTANCE_SCORE] = round(previous / max_score, 4)
        else:
            for concept in self.metrics:
                previous = self.metrics[concept][IMPORTANCE_SCORE]
                self.metrics[concept][IMPORTANCE_SCORE] = round(previous / max_score, 4)


    def __normalize_on_sum(self, total=None):
        """
        using the sum of the set of importance scores, normalize so each score is a percentage out of 100
        :param total: total importance of the set
        """
        if total is not None:
            for concept in self.metrics:
                previous = self.metrics[concept][IMPORTANCE_SCORE]
                self.metrics[concept][IMPORTANCE_SCORE] = round(previous / total, 4)


    def get_metrics(self):
        """
        return metrics dict
        :return: dict of metrics
        """
        return self.metrics


    def sort(self):
        """
        sort based on highest importance score (descending order)
        """
        # TODO determine normalization better, you lazy ass
        self.__normalize_on_max()
        self.metrics = OrderedDict(sorted(self.metrics.items(), key=lambda t: t[1][IMPORTANCE_SCORE], reverse=True))
        self.__sorted = True


    # TODO remove before prod
    def is_sorted(self):
        return self.__sorted


    def __parse_corpus_response(self, response):
        """
        parse json response into dict with concept uri as key, and term-frequency as value
        :param response: api response
        :return: dict of concepts and their frequencies
        """
        concepts = {}
        for con in response:
            name = con['conceptUri']['uri'].encode('utf-8')
            freq = con['frequency']
            concepts[name] = freq
            # concepts[name.lower()] = freq
        return concepts


    def __query_corpus(self, idx=0):
        """
        Query PP API for extracted concepts and their term frequencies. Only 20 concepts per request allowed.
        :param idx: index from which to retrieve extracted concepts from api
        :return: json representation of concept and its corpus data
        """
        url = CORPUS_URL + str(idx)

        result = requests.get(url, auth=AUTH)

        if result.text == '[]' or result.text == '[ ]':
            return None
        else:
            return json.loads(result.text)



    def get_corpus_data(self):
        """
        Using the PP API, query the corpus with the current thesaurus to extract term frequency
        :return:
        """
        print 'inside get_corpus_data'
        idx = 0
        response = self.__query_corpus(idx)
        extracted_concepts = {}
        while response is not None:
            extracted_concepts = self.__parse_corpus_response(response)
            for concept in extracted_concepts:
                freq = extracted_concepts.get(concept)
                if concept in self.metrics:
                    # print 'heres a match between the two dicts' + concept
                    self.metrics[concept][FREQUENCY] = freq
                    self.metrics[concept][IMPORTANCE_SCORE] = (FREQ_SCORE_FACTOR * freq)
            idx += 20
            response = self.__query_corpus(idx)





