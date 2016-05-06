#!/usr/bin/env python
import rdflib
import skos as pyskos
import logging
from constants import *

logging.basicConfig(level=logging.INFO)     # use logging during the parsing process


# filename = 'res/pp_project_carproject.rdf'
# filename = 'res/pp_project_manuterms.rdf'
# g = rdflib.Graph()
# g.load(filename)
#
# g = rdflib.Graph()
# g = g.parse(location=filename, format="application/rdf+xml")
#
# # TODO, play with these args. normalize_uri=unicode might do some good, but need to do testing
# '''
# must have max_depth set to at least 1 in order to resolve external resources (i.e. exactMatch).
# going higher than 1 will add another layer of recursive calls per.
# '''
# loaded = skos.RDFLoader(g, max_depth=1, flat=True)
# # loaded.flat = True
#
# # c = loaded['http://infoneer.poolparty.biz/Processes/347']
# c = loaded['http://infoneer.poolparty.biz/Casting/364']   # successfully gets a synonym
# print c.prefLabel
# print c.synonyms
# print c.broader
# print c.related

# =========================================== end test/debug stuff ===================================================


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
                    self.metrics[r.uri][NUM_RELATIONS] += 1
                    self.metrics[r.uri][IMPORTANCE_SCORE] += REL_SCORE_FACTOR

            if concept.synonyms:
                self.metrics[concept.uri][IMPORTANCE_SCORE] += EXTERNAL_LINK_FACTOR
                self.metrics[concept.uri][NUM_EXTERNAL] = len(concept.synonyms)

    def __normalize_on_max(self, max_score=None):
        """

        :param max_score:
        :return:
        """
        if max_score is not None:
            for concept in self.metrics:
                previous = self.metrics[concept][IMPORTANCE_SCORE]
                self.metrics[concept][IMPORTANCE_SCORE] = round(previous / max_score, 4)

    def is_sorted(self):
        return self.__sorted

