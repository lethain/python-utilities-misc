from __future__ import with_statement
import logging, sys
from optparse import OptionParser
from time import sleep
from csv import DictReader
from Queue import Queue
from threading import Thread
try:
    from xml.etree import cElementTree as ElementTree
except ImportError:
    from xml.etree import ElementTree


def manage_csv_file(file, logger, threads=10):
    q = Queue()
    workers = []
    def worker():
        while True:
            line = q.get()
            try:
                print "processing: %s\n" % line
            except Exception, e:
                logger.error("worker-thread: %s" % e)
            q.task_done()

    for i in range(threads):
        t = Thread(target=worker)
        t.setDaemon(True)
        workers.append(t)
        t.start()

    with open(file,'r') as fin:
        for line in DictReader(fin):
            q.put(line)

    q.join()


def manage_xml_file(file, logger, threads=10):
    def serialize(e):
        'Recursively serialize an ElementTree.Element'
        tag = e.tag
        text = e.text
        attributes = e.items()
        kids = e.getchildren()
        if text and not (attributes or kids):
            return text
        else:
            d = {}
            if text:
                d['_text'] = text
            for key, val in attributes:
                d[key] = val
            for kid in kids:
                tag = kid.tag
                serialized = serialize(kid)
                if d.has_key(tag):
                    val = d[tag]
                    if type(val) == type([]):
                        val.append(serialized)
                    else:
                        d[tag] = [val, serialized]
                else:
                    d[tag] = serialized
        return d        

    q = Queue()
    workers = []

    def worker():
        while True:
            data = q.get()
            try:
                print "processing: %s\n" % data
            except Exception, e:
                logger.error("worker-thread: %s" % e)
            q.task_done()

    for i in range(threads):
        t = Thread(target=worker)
        t.setDaemon(True)
        workers.append(t)
        t.start()

    item_tag = None
    reader = iter(ElementTree.iterparse(file, events=('start', 'end')))
    reader.next() # discard '<List>' type tag
    try:
        for event, elem in reader:
            if item_tag is None:
                item_tag = elem.tag
            if event=='end' and elem.tag == item_tag:
                q.put(serialize(elem))
        elem.clear()
    except SyntaxError, e:
        logger.critical("encountered invalid xml, %s" % e)

    q.join()
            
            
    

def main():
    p = OptionParser("usage: pool.py somefile.csv")
    p.add_option('-t', '--threads', dest='threads',
                help='quantity of THREADS for processing',
                metavar='THREADS')
    (options, args) = p.parse_args()
    filename = args[0]
    threads = int(options.threads) if options.threads else 10

    loggerLevel = logging.DEBUG
    logger = logging.getLogger("FileManager")
    logger.setLevel(loggerLevel)
    ch = logging.StreamHandler()
    ch.setLevel(loggerLevel)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    if filename.endswith('csv'):
        manage_csv_file(filename, logger, threads=threads)
    elif filename.endswith('xml'):
        manage_xml_file(filename, logger, threads=threads)
    else:
        print u"Cannot handle filename %s" % filename.split('.')[0]

if __name__ == '__main__':
    sys.exit(main())
