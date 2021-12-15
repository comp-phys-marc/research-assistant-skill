# -*- coding: utf-8 -*-

import logging
import ask_sdk_core.utils as ask_utils

import feedparser
import random
import re

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from functools import partial, wraps
from datetime import datetime

from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

PROMPT_PHRASES = [
    "Would you like to hear an update on another topic? ",
    "That's all I have on the topic for now. Is there anything else you'd like to know? ",
    "Let me know if you need anything else. "
]

ACKS = [
    "Got it. ",
    "Ok. ",
    "Alright. "
]

BRIDGING_SENTENCES = [
    "They say: ",
    "Their abstract starts by saying: ",
    "Their paper begins with the following. "
]

FEEDS = {
    'classical physics': {
        'rss': 'https://arxiv.org/rss/physics.class-ph',
        'journal': 'Physics Archive'
    },
    'chemical physics': {
        'rss': 'https://arxiv.org/rss/physics.chem-ph',
        'journal': 'Physics Archive'
    },
    'biological physics': {
        'rss': 'https://arxiv.org/rss/physics.bio-ph',
        'journal': 'Physics Archive'
    },
    'mathematical physics': {
        'rss': 'https://arxiv.org/rss/math-ph',
        'journal': 'Physics Archive'
    },
    'space physics': {
        'rss': 'https://arxiv.org/rss/physics.space-ph',
        'journal': 'Physics Archive'
    },
    'high energy physics': {
        'rss': 'https://arxiv.org/rss/hep-th',
        'journal': 'High Energy Physics Archive'
    },
    'quantum gravity': {
        'rss': 'https://arxiv.org/rss/gr-qc',
        'journal': 'Physics Archive'
    },
    'statistical mechanics': {
        'rss': 'https://arxiv.org/rss/cond-mat.stat-mech',
        'journal': 'Condensed Matter Archive'
    },
    'systems and control': {
        'rss': 'https://arxiv.org/rss/cs.SY',
        'journal': 'Computer Science Archive'
    },
    'symbolic computation': {
        'rss': 'https://arxiv.org/rss/cs.SC',
        'journal': 'Computer Science Archive'
    },
    'operating systems': {
        'rss': 'https://arxiv.org/rss/cs.OS',
        'journal': 'Computer Science Archive'
    },
    'evolutionary computing': {
        'rss': 'https://arxiv.org/rss/cs.NE',
        'journal': 'Computer Science Archive'
    },
    'multiagent systems': {
        'rss': 'https://arxiv.org/rss/cs.MA',
        'journal': 'Computer Science Archive'
    },
    'information theory': {
        'rss': 'https://arxiv.org/rss/cs.IT',
        'journal': 'Computer Science Archive'
    },
    'human computer interaction': {
        'rss': 'https://arxiv.org/rss/cs.HC',
        'journal': 'Computer Science Archive'
    },
    'game theory': {
        'rss': 'https://arxiv.org/rss/cs.GT',
        'journal': 'Computer Science Archive'
    },
    'graphics': {
        'rss': 'https://arxiv.org/rss/cs.GR',
        'journal': 'Computer Science Archive'
    },
    'formal languages': {
        'rss': 'https://arxiv.org/rss/cs.FL',
        'journal': 'Computer Science Archive'
    },
    'emerging technologies': {
        'rss': 'https://arxiv.org/rss/cs.ET',
        'journal': 'Computer Science Archive'
    },
    'data structures and algorithms': {
        'rss': 'https://arxiv.org/rss/cs.DS',
        'journal': 'Computer Science Archive'
    },
    'discrete mathematics': {
        'rss': 'https://arxiv.org/rss/cs.DM',
        'journal': 'Computer Science Archive'
    },
    'digital libraries': {
        'rss': 'https://arxiv.org/rss/cs.DL',
        'journal': 'Computer Science Archive'
    },
    'cluster computing': {
        'rss': 'https://arxiv.org/rss/cs.DC',
        'journal': 'Computer Science Archive'
    },
    'databases': {
        'rss': 'https://arxiv.org/rss/cs.DB',
        'journal': 'Computer Science Archive'
    },
    'computers and society': {
        'rss': 'https://arxiv.org/rss/cs.CY',
        'journal': 'Computer Science Archive'
    },
    'pattern recognition': {
        'rss': 'https://arxiv.org/rss/cs.CV',
        'journal': 'Computer Science Archive'
    },
    'cryptography': {
        'rss': 'https://arxiv.org/rss/cs.CR',
        'journal': 'Computer Science Archive'
    },
    'computational geometry': {
        'rss': 'https://arxiv.org/rss/cs.CE',
        'journal': 'Computer Science Archive'
    },
    'computational engineering': {
        'rss': 'https://arxiv.org/rss/cs.CE',
        'journal': 'Computer Science Archive'
    },
    'computational complexity': {
        'rss': 'https://arxiv.org/rss/cs.CC',
        'journal': 'Computer Science Archive'
    },
    'hardware architecture': {
        'rss': 'https://arxiv.org/rss/cs.AR',
        'journal': 'Computer Science Archive'
    },
    'artificial intelligence': {
        'rss': 'https://arxiv.org/rss/cs.AI',
        'journal': 'Computer Science Archive'
    },
    'galactic astrophysics': {
        'rss': 'https://arxiv.org/rss/astro-ph.GA',
        'journal': 'Astrophysics Archive'
    },
    'solar astrophysics': {
        'rss': 'https://arxiv.org/rss/astro-ph.SR',
        'journal': 'Astrophysics Archive'
    },
    'planetary astrophysics': {
        'rss': 'https://arxiv.org/rss/astro-ph.EP',
        'journal': 'Astrophysics Archive'
    },
    'cosmology': {
        'rss': 'https://arxiv.org/rss/astro-ph.CO',
        'journal': 'Astrophysics Archive'
    },
    'computation and language': {
        'rss': 'https://arxiv.org/rss/cs.CL',
        'journal': 'Computer Science Archive'
    },
    'quantum physics': {
        'rss': 'https://arxiv.org/rss/quant-ph',
        'journal': 'Quantum Physics Archive'
    },
    'quantum algebra': {
        'rss': 'https://arxiv.org/rss/math.QA',
        'journal': 'Mathematics Archive'
    },
    'quantum technology': {
        'rss': 'https://epjquantumtechnology.springeropen.com/articles/most-recent/rss.xml',
        'journal': 'E.P.J. Quantum Technology'
    },
    'complex systems': {
        'rss': 'https://casmodeling.springeropen.com/articles/most-recent/rss.xml',
        'journal': 'Complex Adaptive Systems Modeling'
    },
    'cybersecurity': {
        'rss': 'https://cybersecurity.springeropen.com/articles/most-recent/rss.xml',
        'journal': 'Cybersecurity'
    },
    'big data': {
        'rss': 'https://journalofbigdata.springeropen.com/articles/most-recent/rss.xml',
        'journal': 'Journal of Big Data'
    },
    'cloud computing': {
        'rss': 'https://journalofcloudcomputing.springeropen.com/articles/most-recent/rss.xml',
        'journal': 'Journal of Cloud Computing'
    },
    'human centered computing': {
        'rss': 'https://hcis-journal.springeropen.com/articles/most-recent/rss.xml',
        'journal': 'Human-centric Computing and Information Sciences'
    },
    'network science': {
        'rss': 'https://appliednetsci.springeropen.com/articles/most-recent/rss.xml',
        'journal': 'Applied Network Science'
    },
    'brain informatics': {
        'rss': 'https://braininformatics.springeropen.com/articles/most-recent/rss.xml',
        'journal': 'Brain Informatics'
    },
    'energy informatics': {
        'rss': 'https://energyinformatics.springeropen.com/articles/most-recent/rss.xml',
        'journal': 'Energy Informatics'
    },
    'data science': {
        'rss': 'https://epjdatascience.springeropen.com/articles/most-recent/rss.xml',
        'journal': 'E.P.J. Data Science'
    },
    'educational technology': {
        'rss': 'https://educationaltechnologyjournal.springeropen.com/articles/most-recent/rss.xml',
        'journal': 'International Journal of Educational Technology in Higher Education'
    },
    'computer vision': {
        'rss': 'https://ipsjcva.springeropen.com/articles/most-recent/rss.xml',
        'journal': 'I.P.S.J. Transactions on Computer Vision and Applications'
    },
    'internet services': {
        'rss': 'https://jisajournal.springeropen.com/articles/most-recent/rss.xml',
        'journal': 'Journal of Internet Services and Applications'
    },
    'artificial intelligence': {
        'rss': 'https://arxiv.org/rss/cs.AI',
        'journal': 'Computer Science Archive'
    },
    'applied computer vision': {
        'rss': 'https://vciba.springeropen.com/articles/most-recent/rss.xml',
        'journal': 'Visual Computing for Industry, Biomedicine, and Art'
    },
    'signal processing': {
        'rss': 'https://asp-eurasipjournals.springeropen.com/articles/most-recent/rss.xml',
        'journal': 'E.U.R.A.S.I.P. Journal on Advances in Signal Processing'
    },
    'audio processing': {
        'rss': 'https://asmp-eurasipjournals.springeropen.com/articles/most-recent/rss.xml',
        'journal': 'E.U.R.A.S.I.P. Journal on Audio, Speech, and Music Processing'
    },
    'image processing': {
        'rss': 'https://jivp-eurasipjournals.springeropen.com/articles/most-recent/rss.xml',
        'journal': 'E.U.R.A.S.I.P. Journal on Image and Video Processing'
    },
    'information security': {
        'rss': 'https://jis-eurasipjournals.springeropen.com/articles/most-recent/rss.xml',
        'journal': 'E.U.R.A.S.I.P. Journal on Information Security'
    },
    'wireless communication': {
        'rss': 'https://jwcn-eurasipjournals.springeropen.com/articles/most-recent/rss.xml',
        'journal': 'E.U.R.A.S.I.P. Journal on Wireless Communications and Networking'
    },
    'electrical systems': {
        'rss': 'https://jesit.springeropen.com/articles/most-recent/rss.xml',
        'journal': 'Journal of Electrical Systems and Information Technology'
    },
    'biotechnology': {
        'rss': 'https://jgeb.springeropen.com/articles/most-recent/rss.xml',
        'journal': 'Journal of Genetic Engineering and Biotechnology'
    },
    'nanotechnology': {
        'rss': 'https://mnsl-journal.springeropen.com/articles/most-recent/rss.xml',
        'journal': 'Micro and Nano Systems Letters'
    },
    'robotics': {
        'rss': 'https://robomechjournal.springeropen.com/articles/most-recent/rss.xml',
        'journal': 'ROBOMECH Journal'
    },
    'computational astrophysics': {
        'rss': 'https://comp-astrophys-cosmol.springeropen.com/articles/most-recent/rss.xml',
        'journal': 'Computational Astrophysics and Cosmology'
    },
    'instrumentation': {
        'rss': 'https://epjtechniquesandinstrumentation.springeropen.com/articles/most-recent/rss.xml',
        'journal': 'E.P.J. Techniques and Instrumentation'
    },
    'optics': {
        'rss': 'https://jeos.springeropen.com/articles/most-recent/rss.xml',
        'journal': 'Journal of the European Optical Society - Rapid Publications'
    },
    'social networks': {
        'rss': 'https://computationalsocialnetworks.springeropen.com/articles/most-recent/rss.xml',
        'journal': 'Computational Social Networks'
    }
}


def clean(raw_text):
    return clean_tex(clean_tags(clean_parens(raw_text)))


def truncate(raw_text): # the echo has a maximum of 8000 characters
    while len(raw_text) > 8000:
        raw_text = '.'.join(raw_text.split('.')[:-1])
    return raw_text


def clean_tex(raw_text):
    return re.sub(re.compile('\$.*?\$'), '', raw_text)


def clean_tags(raw_text):
    return re.sub(re.compile('<.*?>'), '', raw_text)


def clean_parens(raw_text):
    return re.sub(re.compile('\(.*?\)'), '', raw_text)


def construct_summary(topic_name):
    """Constructs a summary for the given topic."""

    summary = "{1} Let me check for the latest {0} articles. ".format(topic_name, ACKS[random.randint(0, 2)])

    feed = FEEDS[topic_name]

    try:
        articles = feedparser.parse(feed['rss']).entries
    except Exception as e:
        return "I'm sorry. I wasn't able to find anything on {0}."

    summary += "I found {0} recent articles in {1}. ".format(len(articles), feed['journal'])

    for article in articles:

        if '...' in article.description:
            article_summary = '.'.join(article.description.split('...')[0].split('.')[0:-1])
        else:
            article_summary = article.description

        if hasattr(article, 'published'):
            released = "was published in " + datetime.strftime(
                datetime.strptime(article.published, '%a, %d %b %Y %H:%M:%S GMT'), '%B')
        else:
            released = "was uploaded "

        summary += "An article entitled {0} {1} by {2}. {3} {4} ".format(clean(article.title), released,
                                                                         clean(article.authors[0]['name']),
                                                                         BRIDGING_SENTENCES[random.randint(0, 2)],
                                                                         clean(article_summary))

    return truncate(summary)


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""

    def can_handle(self, handler_input):
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        speak_output = "Hello, I am your research assistant. I can keep you up to date on the latest publications in \
                       many areas of research. Would you like an update now? You can ask for an update, \
                       or you can ask for help."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class ClassicalPhysicsIntentHandler(AbstractRequestHandler):
    """Handler for classical physics Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("ClassicalPhysicsIntent")(handler_input)

    def handle(self, handler_input):
        topic_name = 'classical physics'

        return (
            handler_input.response_builder
                .speak(construct_summary(topic_name))
                .ask(PROMPT_PHRASES[random.randint(0, 2)])
                .response
        )


class ChemicalPhysicsIntentHandler(AbstractRequestHandler):
    """Handler for chemical physics Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("ChemicalPhysicsIntent")(handler_input)

    def handle(self, handler_input):
        topic_name = 'chemical physics'

        return (
            handler_input.response_builder
                .speak(construct_summary(topic_name))
                .ask(PROMPT_PHRASES[random.randint(0, 2)])
                .response
        )


class BiologicalPhysicsIntentHandler(AbstractRequestHandler):
    """Handler for biological physics Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("BiologicalPhysicsIntent")(handler_input)

    def handle(self, handler_input):
        topic_name = 'biological physics'

        return (
            handler_input.response_builder
                .speak(construct_summary(topic_name))
                .ask(PROMPT_PHRASES[random.randint(0, 2)])
                .response
        )


class MathematicalPhysicsIntentHandler(AbstractRequestHandler):
    """Handler for mathematical physics Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("MathematicalPhysicsIntent")(handler_input)

    def handle(self, handler_input):
        topic_name = 'mathematical physics'

        return (
            handler_input.response_builder
                .speak(construct_summary(topic_name))
                .ask(PROMPT_PHRASES[random.randint(0, 2)])
                .response
        )


class SpacePhysicsIntentHandler(AbstractRequestHandler):
    """Handler for space physics Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("SpacePhysicsIntent")(handler_input)

    def handle(self, handler_input):
        topic_name = 'space physics'

        return (
            handler_input.response_builder
                .speak(construct_summary(topic_name))
                .ask(PROMPT_PHRASES[random.randint(0, 2)])
                .response
        )


class HighEnergyPhysicsIntentHandler(AbstractRequestHandler):
    """Handler for high energy physics Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("HighEnergyPhysicsIntent")(handler_input)

    def handle(self, handler_input):
        topic_name = 'high energy physics'

        return (
            handler_input.response_builder
                .speak(construct_summary(topic_name))
                .ask(PROMPT_PHRASES[random.randint(0, 2)])
                .response
        )


class QuantumGravityIntentHandler(AbstractRequestHandler):
    """Handler for quantum gravity Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("QuantumGravityIntent")(handler_input)

    def handle(self, handler_input):
        topic_name = 'quantum gravity'

        return (
            handler_input.response_builder
                .speak(construct_summary(topic_name))
                .ask(PROMPT_PHRASES[random.randint(0, 2)])
                .response
        )


class StatisticalMechanicsIntentHandler(AbstractRequestHandler):
    """Handler for statistical mechanics Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("StatisticalMechanicsIntent")(handler_input)

    def handle(self, handler_input):
        topic_name = 'statistical mechanics'

        return (
            handler_input.response_builder
                .speak(construct_summary(topic_name))
                .ask(PROMPT_PHRASES[random.randint(0, 2)])
                .response
        )


class SystemsAndControlIntentHandler(AbstractRequestHandler):
    """Handler for systems and control Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("SystemsAndControlIntent")(handler_input)

    def handle(self, handler_input):
        topic_name = 'systems and control'

        return (
            handler_input.response_builder
                .speak(construct_summary(topic_name))
                .ask(PROMPT_PHRASES[random.randint(0, 2)])
                .response
        )


class SymbolicComputationIntentHandler(AbstractRequestHandler):
    """Handler for symbolic computation Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("SymbolicComputationIntent")(handler_input)

    def handle(self, handler_input):
        topic_name = 'symbolic computation'

        return (
            handler_input.response_builder
                .speak(construct_summary(topic_name))
                .ask(PROMPT_PHRASES[random.randint(0, 2)])
                .response
        )


class OperatingSystemsIntentHandler(AbstractRequestHandler):
    """Handler for operating systems Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("OperatingSystemsIntent")(handler_input)

    def handle(self, handler_input):
        topic_name = 'operating systems'

        return (
            handler_input.response_builder
                .speak(construct_summary(topic_name))
                .ask(PROMPT_PHRASES[random.randint(0, 2)])
                .response
        )


class EvolutionaryComputingIntentHandler(AbstractRequestHandler):
    """Handler for evolutionary computing Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("EvolutionaryComputingIntent")(handler_input)

    def handle(self, handler_input):
        topic_name = 'evolutionary computing'

        return (
            handler_input.response_builder
                .speak(construct_summary(topic_name))
                .ask(PROMPT_PHRASES[random.randint(0, 2)])
                .response
        )


class MultiAgentSystemsIntentHandler(AbstractRequestHandler):
    """Handler for multi agent systems Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("MultiAgentSystemsIntent")(handler_input)

    def handle(self, handler_input):
        topic_name = 'multi agent systems'

        return (
            handler_input.response_builder
                .speak(construct_summary(topic_name))
                .ask(PROMPT_PHRASES[random.randint(0, 2)])
                .response
        )


class InformationTheoryIntentHandler(AbstractRequestHandler):
    """Handler for information theory Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("InformationTheoryIntent")(handler_input)

    def handle(self, handler_input):
        topic_name = 'information theory'

        return (
            handler_input.response_builder
                .speak(construct_summary(topic_name))
                .ask(PROMPT_PHRASES[random.randint(0, 2)])
                .response
        )


class HumanComputerInteractionIntentHandler(AbstractRequestHandler):
    """Handler for human computer interaction Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("HumanComputerInteractionIntent")(handler_input)

    def handle(self, handler_input):
        topic_name = 'human computer interaction'

        return (
            handler_input.response_builder
                .speak(construct_summary(topic_name))
                .ask(PROMPT_PHRASES[random.randint(0, 2)])
                .response
        )


class GameTheoryIntentHandler(AbstractRequestHandler):
    """Handler for Game Theory Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("GameTheoryIntent")(handler_input)

    def handle(self, handler_input):
        topic_name = 'game theory'

        return (
            handler_input.response_builder
                .speak(construct_summary(topic_name))
                .ask(PROMPT_PHRASES[random.randint(0, 2)])
                .response
        )


class GraphicsIntentHandler(AbstractRequestHandler):
    """Handler for graphics Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("GraphicsIntent")(handler_input)

    def handle(self, handler_input):
        topic_name = 'graphics'

        return (
            handler_input.response_builder
                .speak(construct_summary(topic_name))
                .ask(PROMPT_PHRASES[random.randint(0, 2)])
                .response
        )


class FormalLanguagesIntentHandler(AbstractRequestHandler):
    """Handler for formal languages Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("FormalLanguagesIntent")(handler_input)

    def handle(self, handler_input):
        topic_name = 'formal languages'

        return (
            handler_input.response_builder
                .speak(construct_summary(topic_name))
                .ask(PROMPT_PHRASES[random.randint(0, 2)])
                .response
        )


class EmergingTechnologiesIntentHandler(AbstractRequestHandler):
    """Handler for emerging technologies Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("EmergingTechnologiesIntent")(handler_input)

    def handle(self, handler_input):
        topic_name = 'emerging technologies'

        return (
            handler_input.response_builder
                .speak(construct_summary(topic_name))
                .ask(PROMPT_PHRASES[random.randint(0, 2)])
                .response
        )


class DataStructuresAndAlgorithmsIntentHandler(AbstractRequestHandler):
    """Handler for data structures and algorithms Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("DataStructuresAndAlgorithmsIntent")(handler_input)

    def handle(self, handler_input):
        topic_name = 'data structures and algorithms'

        return (
            handler_input.response_builder
                .speak(construct_summary(topic_name))
                .ask(PROMPT_PHRASES[random.randint(0, 2)])
                .response
        )


class DiscreteMathematicsIntentHandler(AbstractRequestHandler):
    """Handler for discrete mathematics Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("DiscreteMathematicsIntent")(handler_input)

    def handle(self, handler_input):
        topic_name = 'discrete mathematics'

        return (
            handler_input.response_builder
                .speak(construct_summary(topic_name))
                .ask(PROMPT_PHRASES[random.randint(0, 2)])
                .response
        )


class DigitalLibrariesIntentHandler(AbstractRequestHandler):
    """Handler for digital libraries Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("DigitalLibrariesIntent")(handler_input)

    def handle(self, handler_input):
        topic_name = 'digital libraries'

        return (
            handler_input.response_builder
                .speak(construct_summary(topic_name))
                .ask(PROMPT_PHRASES[random.randint(0, 2)])
                .response
        )


class ClusterComputingIntentHandler(AbstractRequestHandler):
    """Handler for Cluster Computing Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("ClusterComputingIntent")(handler_input)

    def handle(self, handler_input):
        topic_name = 'cluster computing'

        return (
            handler_input.response_builder
                .speak(construct_summary(topic_name))
                .ask(PROMPT_PHRASES[random.randint(0, 2)])
                .response
        )


class DatabasesIntentHandler(AbstractRequestHandler):
    """Handler for databases Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("DatabasesIntent")(handler_input)

    def handle(self, handler_input):
        topic_name = 'databases'

        return (
            handler_input.response_builder
                .speak(construct_summary(topic_name))
                .ask(PROMPT_PHRASES[random.randint(0, 2)])
                .response
        )


class ComputersAndSocietyIntentHandler(AbstractRequestHandler):
    """Handler for computers and society Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("ComputersAndSocietyIntent")(handler_input)

    def handle(self, handler_input):
        topic_name = 'computers and society'

        return (
            handler_input.response_builder
                .speak(construct_summary(topic_name))
                .ask(PROMPT_PHRASES[random.randint(0, 2)])
                .response
        )


class PatternRecognitionIntentHandler(AbstractRequestHandler):
    """Handler for pattern recognition Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("PatternRecognitionIntent")(handler_input)

    def handle(self, handler_input):
        topic_name = 'pattern recognition'

        return (
            handler_input.response_builder
                .speak(construct_summary(topic_name))
                .ask(PROMPT_PHRASES[random.randint(0, 2)])
                .response
        )


class CryptographyIntentHandler(AbstractRequestHandler):
    """Handler for cryptography Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("CryptographyIntent")(handler_input)

    def handle(self, handler_input):
        topic_name = 'cryptography'

        return (
            handler_input.response_builder
                .speak(construct_summary(topic_name))
                .ask(PROMPT_PHRASES[random.randint(0, 2)])
                .response
        )


class ComputationalGeometryIntentHandler(AbstractRequestHandler):
    """Handler for computational geometry Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("ComputationalGeometryIntent")(handler_input)

    def handle(self, handler_input):
        topic_name = 'computational geometry'

        return (
            handler_input.response_builder
                .speak(construct_summary(topic_name))
                .ask(PROMPT_PHRASES[random.randint(0, 2)])
                .response
        )


class ComputationalEngineeringIntentHandler(AbstractRequestHandler):
    """Handler for computational engineering Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("ComputationalEngineeringIntent")(handler_input)

    def handle(self, handler_input):
        topic_name = 'computational engineering'

        return (
            handler_input.response_builder
                .speak(construct_summary(topic_name))
                .ask(PROMPT_PHRASES[random.randint(0, 2)])
                .response
        )


class ComputationalComplexityIntentHandler(AbstractRequestHandler):
    """Handler for computational complexity Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("ComputationalComplexityIntent")(handler_input)

    def handle(self, handler_input):
        topic_name = 'computational complexity'

        return (
            handler_input.response_builder
                .speak(construct_summary(topic_name))
                .ask(PROMPT_PHRASES[random.randint(0, 2)])
                .response
        )


class HardwareArchitectureIntentHandler(AbstractRequestHandler):
    """Handler for hardware architecture Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("HardwareArchitectureIntent")(handler_input)

    def handle(self, handler_input):
        topic_name = 'hardware architecture'

        return (
            handler_input.response_builder
                .speak(construct_summary(topic_name))
                .ask(PROMPT_PHRASES[random.randint(0, 2)])
                .response
        )


class PlanetaryAstrophysicsIntentHandler(AbstractRequestHandler):
    """Handler for planetary astrophysics Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("PlanetaryAstrophysicsIntent")(handler_input)

    def handle(self, handler_input):
        topic_name = 'planetary astrophysics'

        return (
            handler_input.response_builder
                .speak(construct_summary(topic_name))
                .ask(PROMPT_PHRASES[random.randint(0, 2)])
                .response
        )


class SolarAstrophysicsIntentHandler(AbstractRequestHandler):
    """Handler for solar astrophysics Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("SolarAstrophysicsIntent")(handler_input)

    def handle(self, handler_input):
        topic_name = 'solar astrophysics'

        return (
            handler_input.response_builder
                .speak(construct_summary(topic_name))
                .ask(PROMPT_PHRASES[random.randint(0, 2)])
                .response
        )


class GalacticAstrophysicsIntentHandler(AbstractRequestHandler):
    """Handler for galactic astrophysics Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("GalacticAstrophysicsIntent")(handler_input)

    def handle(self, handler_input):
        topic_name = 'galactic astrophysics'

        return (
            handler_input.response_builder
                .speak(construct_summary(topic_name))
                .ask(PROMPT_PHRASES[random.randint(0, 2)])
                .response
        )


class CosmologyIntentHandler(AbstractRequestHandler):
    """Handler for cosmology Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("CosmologyIntent")(handler_input)

    def handle(self, handler_input):
        topic_name = 'cosmology'

        return (
            handler_input.response_builder
                .speak(construct_summary(topic_name))
                .ask(PROMPT_PHRASES[random.randint(0, 2)])
                .response
        )


class ComputationAndLanguageIntentHandler(AbstractRequestHandler):
    """Handler for computation and language Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("ComputationAndLanguageIntent")(handler_input)

    def handle(self, handler_input):
        topic_name = 'computation and language'

        return (
            handler_input.response_builder
                .speak(construct_summary(topic_name))
                .ask(PROMPT_PHRASES[random.randint(0, 2)])
                .response
        )


class QuantumPhysicsIntentHandler(AbstractRequestHandler):
    """Handler for quantum physics Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("QuantumPhysicsIntent")(handler_input)

    def handle(self, handler_input):
        topic_name = 'quantum physics'

        return (
            handler_input.response_builder
                .speak(construct_summary(topic_name))
                .ask(PROMPT_PHRASES[random.randint(0, 2)])
                .response
        )


class QuantumAlgebraIntentHandler(AbstractRequestHandler):
    """Handler for quantum algebra Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("QuantumAlgebraIntent")(handler_input)

    def handle(self, handler_input):
        topic_name = 'quantum algebra'

        return (
            handler_input.response_builder
                .speak(construct_summary(topic_name))
                .ask(PROMPT_PHRASES[random.randint(0, 2)])
                .response
        )


class QuantumTechnologyIntentHandler(AbstractRequestHandler):
    """Handler for quantum technology Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("QuantumTechnologyIntent")(handler_input)

    def handle(self, handler_input):
        topic_name = 'quantum technology'

        return (
            handler_input.response_builder
                .speak(construct_summary(topic_name))
                .ask(PROMPT_PHRASES[random.randint(0, 2)])
                .response
        )


class ComplexSystemsIntentHandler(AbstractRequestHandler):
    """Handler for complex systems Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("ComplexSystemsIntent")(handler_input)

    def handle(self, handler_input):
        topic_name = 'complex systems'

        return (
            handler_input.response_builder
                .speak(construct_summary(topic_name))
                .ask(PROMPT_PHRASES[random.randint(0, 2)])
                .response
        )


class CybersecurityIntentHandler(AbstractRequestHandler):
    """Handler for cybersecurity Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("CybersecurityIntent")(handler_input)

    def handle(self, handler_input):
        topic_name = 'cybersecurity'

        return (
            handler_input.response_builder
                .speak(construct_summary(topic_name))
                .ask(PROMPT_PHRASES[random.randint(0, 2)])
                .response
        )


class BigDataIntentHandler(AbstractRequestHandler):
    """Handler for big data Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("BigDataIntent")(handler_input)

    def handle(self, handler_input):
        topic_name = 'big data'

        return (
            handler_input.response_builder
                .speak(construct_summary(topic_name))
                .ask(PROMPT_PHRASES[random.randint(0, 2)])
                .response
        )


class CloudComputingIntentHandler(AbstractRequestHandler):
    """Handler for cloud computing Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("CloudComputingIntent")(handler_input)

    def handle(self, handler_input):
        topic_name = 'cloud computing'

        return (
            handler_input.response_builder
                .speak(construct_summary(topic_name))
                .ask(PROMPT_PHRASES[random.randint(0, 2)])
                .response
        )


class HumanCenteredComputingIntentHandler(AbstractRequestHandler):
    """Handler for human centered computing Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("HumanCenteredComputingIntent")(handler_input)

    def handle(self, handler_input):
        topic_name = 'human centered computing'

        return (
            handler_input.response_builder
                .speak(construct_summary(topic_name))
                .ask(PROMPT_PHRASES[random.randint(0, 2)])
                .response
        )


class NetworkScienceIntentHandler(AbstractRequestHandler):
    """Handler for network science Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("NetworkScienceIntent")(handler_input)

    def handle(self, handler_input):
        topic_name = 'network science'

        return (
            handler_input.response_builder
                .speak(construct_summary(topic_name))
                .ask(PROMPT_PHRASES[random.randint(0, 2)])
                .response
        )


class BrainInformaticsIntentHandler(AbstractRequestHandler):
    """Handler for brain informatics Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("BrainInformaticsIntent")(handler_input)

    def handle(self, handler_input):
        topic_name = 'brain informatics'

        return (
            handler_input.response_builder
                .speak(construct_summary(topic_name))
                .ask(PROMPT_PHRASES[random.randint(0, 2)])
                .response
        )


class EnergyInformaticsIntentHandler(AbstractRequestHandler):
    """Handler for energy informatics Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("EnergyInformaticsIntent")(handler_input)

    def handle(self, handler_input):
        topic_name = 'energy informatics'

        return (
            handler_input.response_builder
                .speak(construct_summary(topic_name))
                .ask(PROMPT_PHRASES[random.randint(0, 2)])
                .response
        )


class DataScienceIntentHandler(AbstractRequestHandler):
    """Handler for data science Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("DataScienceIntent")(handler_input)

    def handle(self, handler_input):
        topic_name = 'data science'

        return (
            handler_input.response_builder
                .speak(construct_summary(topic_name))
                .ask(PROMPT_PHRASES[random.randint(0, 2)])
                .response
        )


class EducationalTechnologyIntentHandler(AbstractRequestHandler):
    """Handler for educational technology Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("EducationalTechnologyIntent")(handler_input)

    def handle(self, handler_input):
        topic_name = 'educational technology'

        return (
            handler_input.response_builder
                .speak(construct_summary(topic_name))
                .ask(PROMPT_PHRASES[random.randint(0, 2)])
                .response
        )


class ComputerVisionIntentHandler(AbstractRequestHandler):
    """Handler for computer vision Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("ComputerVisionIntent")(handler_input)

    def handle(self, handler_input):
        topic_name = 'computer vision'

        return (
            handler_input.response_builder
                .speak(construct_summary(topic_name))
                .ask(PROMPT_PHRASES[random.randint(0, 2)])
                .response
        )


class InternetServicesIntentHandler(AbstractRequestHandler):
    """Handler for internet services Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("InternetServicesIntent")(handler_input)

    def handle(self, handler_input):
        topic_name = 'internet services'

        return (
            handler_input.response_builder
                .speak(construct_summary(topic_name))
                .ask(PROMPT_PHRASES[random.randint(0, 2)])
                .response
        )


class ArtificialIntelligenceIntentHandler(AbstractRequestHandler):
    """Handler for artificial intelligence Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("ArtificialIntelligenceIntent")(handler_input)

    def handle(self, handler_input):
        topic_name = 'artificial intelligence'

        return (
            handler_input.response_builder
                .speak(construct_summary(topic_name))
                .ask(PROMPT_PHRASES[random.randint(0, 2)])
                .response
        )


class AppliedComputerVisionIntentHandler(AbstractRequestHandler):
    """Handler for applied computer vision Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AppliedComputerVisionIntent")(handler_input)

    def handle(self, handler_input):
        topic_name = 'applied computer vision'

        return (
            handler_input.response_builder
                .speak(construct_summary(topic_name))
                .ask(PROMPT_PHRASES[random.randint(0, 2)])
                .response
        )


class SignalProcessingIntentHandler(AbstractRequestHandler):
    """Handler for signal processing Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("SignalProcessingIntent")(handler_input)

    def handle(self, handler_input):
        topic_name = 'signal processing'

        return (
            handler_input.response_builder
                .speak(construct_summary(topic_name))
                .ask(PROMPT_PHRASES[random.randint(0, 2)])
                .response
        )


class AudioProcessingIntentHandler(AbstractRequestHandler):
    """Handler for audio processing Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AudioProcessingIntent")(handler_input)

    def handle(self, handler_input):
        topic_name = 'audio processing'

        return (
            handler_input.response_builder
                .speak(construct_summary(topic_name))
                .ask(PROMPT_PHRASES[random.randint(0, 2)])
                .response
        )


class ImageProcessingIntentHandler(AbstractRequestHandler):
    """Handler for image processing Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("ImageProcessingIntent")(handler_input)

    def handle(self, handler_input):
        topic_name = 'image processing'

        return (
            handler_input.response_builder
                .speak(construct_summary(topic_name))
                .ask(PROMPT_PHRASES[random.randint(0, 2)])
                .response
        )


class InformationSecurityIntentHandler(AbstractRequestHandler):
    """Handler for information security Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("InformationSecurityIntent")(handler_input)

    def handle(self, handler_input):
        topic_name = 'information security'

        return (
            handler_input.response_builder
                .speak(construct_summary(topic_name))
                .ask(PROMPT_PHRASES[random.randint(0, 2)])
                .response
        )


class WirelessCommunicationIntentHandler(AbstractRequestHandler):
    """Handler for wireless communication Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("WirelessCommunicationIntent")(handler_input)

    def handle(self, handler_input):
        topic_name = 'wireless communication'

        return (
            handler_input.response_builder
                .speak(construct_summary(topic_name))
                .ask(PROMPT_PHRASES[random.randint(0, 2)])
                .response
        )


class ElectricalSystemsIntentHandler(AbstractRequestHandler):
    """Handler for electrical systems Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("ElectricalSystemsIntent")(handler_input)

    def handle(self, handler_input):
        topic_name = 'electrical systems'

        return (
            handler_input.response_builder
                .speak(construct_summary(topic_name))
                .ask(PROMPT_PHRASES[random.randint(0, 2)])
                .response
        )


class BiotechnologyIntentHandler(AbstractRequestHandler):
    """Handler for biotechnology Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("BiotechnologyIntent")(handler_input)

    def handle(self, handler_input):
        topic_name = 'biotechnology'

        return (
            handler_input.response_builder
                .speak(construct_summary(topic_name))
                .ask(PROMPT_PHRASES[random.randint(0, 2)])
                .response
        )


class NanotechnologyIntentHandler(AbstractRequestHandler):
    """Handler for nanotechnology Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("NanotechnologyIntent")(handler_input)

    def handle(self, handler_input):
        topic_name = 'nanotechnology'

        return (
            handler_input.response_builder
                .speak(construct_summary(topic_name))
                .ask(PROMPT_PHRASES[random.randint(0, 2)])
                .response
        )


class RoboticsIntentHandler(AbstractRequestHandler):
    """Handler for robotics Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("RoboticsIntent")(handler_input)

    def handle(self, handler_input):
        topic_name = 'robotics'

        return (
            handler_input.response_builder
                .speak(construct_summary(topic_name))
                .ask(PROMPT_PHRASES[random.randint(0, 2)])
                .response
        )


class ComputationalAstrophysicsIntentHandler(AbstractRequestHandler):
    """Handler for computational astrophysics Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("ComputationalAstrophysicsIntent")(handler_input)

    def handle(self, handler_input):
        topic_name = 'computational astrophysics'

        return (
            handler_input.response_builder
                .speak(construct_summary(topic_name))
                .ask(PROMPT_PHRASES[random.randint(0, 2)])
                .response
        )


class InstrumentationIntentHandler(AbstractRequestHandler):
    """Handler for instrumentation Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("InstrumentationIntent")(handler_input)

    def handle(self, handler_input):
        topic_name = 'instrumentation'

        return (
            handler_input.response_builder
                .speak(construct_summary(topic_name))
                .ask(PROMPT_PHRASES[random.randint(0, 2)])
                .response
        )


class OpticsIntentHandler(AbstractRequestHandler):
    """Handler for optics Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("OpticsIntent")(handler_input)

    def handle(self, handler_input):
        topic_name = 'optics'

        return (
            handler_input.response_builder
                .speak(construct_summary(topic_name))
                .ask(PROMPT_PHRASES[random.randint(0, 2)])
                .response
        )


class SocialNetworksIntentHandler(AbstractRequestHandler):
    """Handler for social networks Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("SocialNetworksIntent")(handler_input)

    def handle(self, handler_input):
        topic_name = 'social networks'

        return (
            handler_input.response_builder
                .speak(construct_summary(topic_name))
                .ask(PROMPT_PHRASES[random.randint(0, 2)])
                .response
        )


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        speak_output = "I can summarize recent publications in any of these topics for you. \
            Classical Physics, Chemical Physics, Biological Physics, Mathematical Physics, Space Physics, High Energy Physics, Quantum Gravity, Statistical Mechanics, \
            Systems And Control, Symbolic Computation, Operating Systems, Evolutionary Computing, Multi Agent Systems, Information Theory, Human Computer Interaction, \
            Game Theory, Graphics, Formal Languages, Emerging Technologies, Data Structures And Algorithms, Discrete Mathematics, Digital Libraries, Cluster Computing, \
            Databases, Computers And Society, Pattern Recognition, Cryptography, Computational Geometry, Computational Engineering, Computational Complexity, Hardware Architecture, \
            Cosmology, galactic astrophysics, \
            solar astrophysics, planetary astrophysics, computation and language, quantum physics, \
            quantum algebra, quantum technology, complex systems, cybersecurity, big data, cloud computing, \
            human centered computing, network science, brain informatics, energy informatics, \
            data science, educational technology, computer vision, internet services, artificial \
            intelligence, applied computer vision, signal processing, audio processing, image \
            processing, information security, wireless communication, electrical systems, biotechnology, \
            nanotechnology, robotics, computational astrophysics, instrumentation, optics, and social networks.\
            Right now, I summarize recent publications in several open journals. I hope that with my \
            next update, I will gain access to more journals to summarize for you."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""

    def can_handle(self, handler_input):
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""

    def can_handle(self, handler_input):
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """

    def can_handle(self, handler_input):
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """

    def can_handle(self, handler_input, exception):
        return True

    def handle(self, handler_input, exception):
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(ClassicalPhysicsIntentHandler())
sb.add_request_handler(ChemicalPhysicsIntentHandler())
sb.add_request_handler(BiologicalPhysicsIntentHandler())
sb.add_request_handler(MathematicalPhysicsIntentHandler())
sb.add_request_handler(SpacePhysicsIntentHandler())
sb.add_request_handler(HighEnergyPhysicsIntentHandler())
sb.add_request_handler(QuantumGravityIntentHandler())
sb.add_request_handler(StatisticalMechanicsIntentHandler())
sb.add_request_handler(SystemsAndControlIntentHandler())
sb.add_request_handler(SymbolicComputationIntentHandler())
sb.add_request_handler(OperatingSystemsIntentHandler())
sb.add_request_handler(EvolutionaryComputingIntentHandler())
sb.add_request_handler(MultiAgentSystemsIntentHandler())
sb.add_request_handler(InformationTheoryIntentHandler())
sb.add_request_handler(HumanComputerInteractionIntentHandler())
sb.add_request_handler(GameTheoryIntentHandler())
sb.add_request_handler(GraphicsIntentHandler())
sb.add_request_handler(FormalLanguagesIntentHandler())
sb.add_request_handler(EmergingTechnologiesIntentHandler())
sb.add_request_handler(DataStructuresAndAlgorithmsIntentHandler())
sb.add_request_handler(DiscreteMathematicsIntentHandler())
sb.add_request_handler(DigitalLibrariesIntentHandler())
sb.add_request_handler(ClusterComputingIntentHandler())
sb.add_request_handler(DatabasesIntentHandler())
sb.add_request_handler(ComputersAndSocietyIntentHandler())
sb.add_request_handler(PatternRecognitionIntentHandler())
sb.add_request_handler(CryptographyIntentHandler())
sb.add_request_handler(ComputationalGeometryIntentHandler())
sb.add_request_handler(ComputationalEngineeringIntentHandler())
sb.add_request_handler(ComputationalComplexityIntentHandler())
sb.add_request_handler(HardwareArchitectureIntentHandler())
sb.add_request_handler(PlanetaryAstrophysicsIntentHandler())
sb.add_request_handler(SolarAstrophysicsIntentHandler())
sb.add_request_handler(GalacticAstrophysicsIntentHandler())
sb.add_request_handler(CosmologyIntentHandler())
sb.add_request_handler(ComputationAndLanguageIntentHandler())
sb.add_request_handler(QuantumPhysicsIntentHandler())
sb.add_request_handler(QuantumAlgebraIntentHandler())
sb.add_request_handler(QuantumTechnologyIntentHandler())
sb.add_request_handler(ComplexSystemsIntentHandler())
sb.add_request_handler(CybersecurityIntentHandler())
sb.add_request_handler(BigDataIntentHandler())
sb.add_request_handler(CloudComputingIntentHandler())
sb.add_request_handler(HumanCenteredComputingIntentHandler())
sb.add_request_handler(NetworkScienceIntentHandler())
sb.add_request_handler(BrainInformaticsIntentHandler())
sb.add_request_handler(EnergyInformaticsIntentHandler())
sb.add_request_handler(DataScienceIntentHandler())
sb.add_request_handler(EducationalTechnologyIntentHandler())
sb.add_request_handler(ComputerVisionIntentHandler())
sb.add_request_handler(InternetServicesIntentHandler())
sb.add_request_handler(ArtificialIntelligenceIntentHandler())
sb.add_request_handler(AppliedComputerVisionIntentHandler())
sb.add_request_handler(SignalProcessingIntentHandler())
sb.add_request_handler(AudioProcessingIntentHandler())
sb.add_request_handler(ImageProcessingIntentHandler())
sb.add_request_handler(InformationSecurityIntentHandler())
sb.add_request_handler(WirelessCommunicationIntentHandler())
sb.add_request_handler(ElectricalSystemsIntentHandler())
sb.add_request_handler(BiotechnologyIntentHandler())
sb.add_request_handler(NanotechnologyIntentHandler())
sb.add_request_handler(RoboticsIntentHandler())
sb.add_request_handler(ComputationalAstrophysicsIntentHandler())
sb.add_request_handler(InstrumentationIntentHandler())
sb.add_request_handler(OpticsIntentHandler())
sb.add_request_handler(SocialNetworksIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler())

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()