import feedparser
from datetime import datetime
import re
import random

BRIDGING_SENTENCES = [
    "They say: ",
    "Their abstract starts by saying: ",
    "Their paper begins with the following. "
]

def clean(raw_html):
    return re.sub(re.compile('<.*?>'), '', raw_html)

# test_url = 'http://epjquantumtechnology.springeropen.com/articles/most-recent/rss.xml'
# entries = feedparser.parse(test_url).entries

test_url = 'https://arxiv.org/rss/astro-ph.EP'
try:
    articles = feedparser.parse(test_url).entries
except Exception as e:
   print("I'm sorry. I wasn't able to find anything on that.")

summary = ""

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
        print(released)
        print(clean(article.title))
        print(clean(article_summary))
        print(clean(article.authors[0]['name']))
        print(datetime.strptime(article.published, '%a, %d %b %Y %H:%M:%S GMT'))
