import argparse
import datetime
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'libs'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'mylibs'))
from caac_crawler import caac_crawler

YEAR_BEGIN = 1911

# change the working directory
try:
    os.chdir(os.path.dirname(__file__))
except:
    pass

parser = argparse.ArgumentParser(description='A crawler for CAAC website.')
parser.add_argument(
    '--year',
    type=int,
    default=datetime.datetime.now().year - YEAR_BEGIN,
    help='The year of data to be crawled. (ex: 2017 or 106 is the same)',
)
args = parser.parse_args()

year = args.year - YEAR_BEGIN if args.year >= YEAR_BEGIN else args.year

crawler = caac_crawler(year)
crawler.run()
