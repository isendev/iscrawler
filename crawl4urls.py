import sys
from lxml import etree
from StringIO import StringIO
import requests
import hashlib
from os.path import join, isfile
from urlparse import urlparse
from time import time, sleep
from Queue import Queue


VERB = 0

domain_hit_time = {}
MIN_HIT_DELAY = 0.2 #s

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}


def fetch_page(url):
    try:
        while time() < domain_hit_time.setdefault(url, 0) + MIN_HIT_DELAY:
            sleep(MIN_HIT_DELAY*0.5)
        resp = requests.get(url, headers=headers)
        domain_hit_time[url] = time()
    except: # Improve: enumerate specific possible exceptions
        if VERB: print 'Problem downloading',url
        return None 
    
    if resp.status_code != 200: 
        if VERB: print 'GETing %s generated HTTP error %d' % (url, resp.status_code)
        return None
    else: 
        return StringIO(resp.text)


def fetch_html_elem_tree(url):
    page = fetch_page(url)
    if page is None: return
    
    try: 
        tree = etree.parse(page, parser=etree.HTMLParser(encoding='unicode'))
    except ValueError:
        return
    if tree.getroot() is None: return 
    return tree




class crawl4urls(object):
    """Basic "breadth first" crawler. 
    (Implemented as a one-off object 
    with use syntax as a function for simplicity)"""

    def __init__(self, start_url):
        init_q = Queue()
        init_q.put(start_url)
        self.level_qs = {0: init_q}
        self.global_todo = set()
        self.linkedin_urls_seen = set()

        # Start processing link tree level-by-level 
        # (i.e. "breadth-first")
        while self.level_qs:
            self.proc_1_level()


    def proc_link(self, url, parent_url):
        # Unique new LinkedIn url found:
        if 'linkedin.com/in/' in url and url not in self.linkedin_urls_seen:
            print '\rLinked in profile found:', url
            self.linkedin_urls_seen.add(url)            
        else: # other link...
            if url[0]=='/': # qualify ref. on local domain
                scheme, netloc = urlparse(parent_url)[:2]
                url = '%s://%s%s' % (scheme, netloc, url)

        # If not already on the list of URLs to visit,
        # add to the queue of the next level of pages to process
        # (diving in immediately would make this a "depth-first" crawler)
        if url not in self.global_todo: 
            self.level_qs.setdefault(self.cur_level+1, Queue()).put(url)
            self.global_todo.add(url)


    def proc_page(self, url):
        print ('\x1b[2K\rfound: %d  lev: %d  Parsing' \
                   % (len(self.linkedin_urls_seen), self.cur_level)), url[:100],
        sys.stdout.flush()
        tree = fetch_html_elem_tree(url)
        if tree is None: return

        for link_elem in tree.xpath('//a'):
            href = link_elem.get('href')
            if href and len(href)>0: 
                self.proc_link(href, parent_url=url)
    

    def proc_1_level(self):
        self.cur_level = min(self.level_qs.keys())
        cur_q = self.level_qs.pop(self.cur_level, Queue())
        while not cur_q.empty():
            self.proc_page(cur_q.get())
        



if __name__ == '__main__':
    crawl4urls('https://duckduckgo.com/?q=dan+cardin+linkedin&t=ffab&ia=web')
