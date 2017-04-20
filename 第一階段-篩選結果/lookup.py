import argparse
import collections
import datetime
import os
import sqlite3
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'mylibs'))
from project_config import project_config
from lookup_db import lookup_db

YEAR_BEGIN = 1911
YEAR_CURRENT = datetime.datetime.now().year - YEAR_BEGIN

# change the working directory
try:
    os.chdir(os.path.dirname(__file__))
except:
    pass

parser = argparse.ArgumentParser(description='A database lookup utility for CAAC website.')
parser.add_argument(
    '--year',
    type=int,
    default=YEAR_CURRENT,
    help='The year of data to be processed. (ex: 2017 or 106 is the same)',
)
parser.add_argument(
    '--admissionIds',
    default='',
    help='Admission IDs that are going to be looked up. (separate by commas)',
)
parser.add_argument(
    '--departmentIds',
    default='',
    help='Department IDs that are going to be looked up. (separate by commas)',
)
parser.add_argument(
    '--output',
    default='result.xlsx',
    help='The file to output results. (.xlsx file)',
)
parser.add_argument(
    '--outputFormat',
    default='',
    help='Leave it blank or "NthuEe"',
)
args = parser.parse_args()

year = args.year - YEAR_BEGIN if args.year >= YEAR_BEGIN else args.year

results = {
    # '准考證號': [ '系所編號', ... ],
    # ...
}

dbFilepath = os.path.join(project_config.resultDir.format(year), 'sqlite3.db')
resultFilepath = args.output if os.path.splitext(args.output)[1].lower() == '.xlsx' else args.output + '.xlsx'

if not os.path.isfile(dbFilepath):
    raise Exception('DB file does not exist: {}'.format(dbFilepath))

conn = sqlite3.connect(dbFilepath)

# universityMap = {
#     '001': '國立臺灣大學',
#     ...
# }
cursor = conn.execute('''
    SELECT id, name
    FROM universities
''')
universityMap = {
    university[0]: university[1]
    for university in cursor.fetchall()
}

# departmentMap = {
#     '001012': '中國文學系',
#     ...
# }
cursor = conn.execute('''
    SELECT id, name
    FROM departments
''')
departmentMap = {
    department[0]: department[1]
    for department in cursor.fetchall()
}

# do lookup
if args.admissionIds:
    admissionIds = list(set( # list unique
        filter(len, args.admissionIds.split(','))
    ))

    result = lookup_db.lookupByAdmissionIds(conn, admissionIds)
    results.update(result)

# do lookup
if args.departmentIds:
    departmentIds = list(set( # list unique
        filter(len, args.departmentIds.split(','))
    ))

    result = lookup_db.lookupByDepartmentIds(conn, departmentIds)
    results.update(result)

conn.close()

# sort the result dict with admissionIds (ascending)
results = collections.OrderedDict(sorted(results.items()))

# delete the old xlsx file
if os.path.isfile(resultFilepath):
    os.remove(resultFilepath)

# write result to a xlsx file
writeOutMethod = 'writeOutResult{}'.format(args.outputFormat)
try:
    getattr(lookup_db, writeOutMethod)(
        resultFilepath,
        universityMap,
        departmentMap,
        results,
        args,
    )
except:
    raise Exception('Unknown option: --outputFormat={}'.format(args.outputFormat))

print(results)
