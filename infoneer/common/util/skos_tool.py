#!/usr/bin/env python
import rdflib
import skos as pyskos
import logging
from collections import OrderedDict
from constants import *


logging.basicConfig(level=logging.INFO)     # use logging during the parsing process


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
        if max_score is not None:
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
        self.metrics = OrderedDict(sorted(self.metrics.items(), key=lambda t: t[1][IMPORTANCE_SCORE], reverse=True))
        self.__sorted = True


    # TODO remove before prod
    def is_sorted(self):
        return self.__sorted



