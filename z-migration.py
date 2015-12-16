#!/usr/bin/env python

"A tool for migrating notebooks between instances of Apache Zeppelin."

"""
The MIT License (MIT)
Copyright (c) 2015 Market6

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import logging

from getopt import getopt, GetoptError
from json import loads, dump
from random import choice
from os import listdir
from shutil import copytree
from string import ascii_uppercase, digits
from sys import argv, exit

__author__ = 'Trevor "rawkintrevo" Grant'
__copyright__ = "Copyright 2015, Market6"
__credits__ = ["Trevor Grant"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Trevor Grant"
__email__ = "trevor.grant@market6.com"
__status__ = "Release candidate"

def generate_new_notebook_id():
    return ''.join(choice(ascii_uppercase + digits) for _ in range(9))

def port_notebook(source_notebook_id, source_notebook_dir, target_notebook_dir, target_conf_file_path):
    ## check for name duplicates to be safe
    target_notebook_id = source_notebook_id
    logging.info("migrating notebook: %s", source_notebook_id)
    while target_notebook_id in listdir(target_notebook_dir):
        target_notebook_id = generate_new_notebook_id()
    if source_notebook_id != target_notebook_id:
        logging.info("notebook '%s' already existed in target directory, changing source name to '%s'", source_notebook_id, target_notebook_id )
    ## Finally, copy the specific notebook directory
    try:
        copytree(source_notebook_dir + "/" + source_notebook_id, target_notebook_dir + "/" + target_notebook_id)
    except IOError as e:
        logging.warn("Skipping %s", source_notebook_id)
        logging.exception(e)
        return 1
    ## Ensure note.json id just in case they aren't samesies
    target_notebook_path = target_notebook_dir + "/" + target_notebook_id + "/note.json"
    try:
        note_json = loads(open(target_notebook_path).read())
    except IOError as e:
        logging.warn("Skipping %s", source_notebook_id)
        logging.exception(e)
        return 1
    if note_json['id'] != target_notebook_id:
        # dump note_json on the target forcing an overwrite
        logging.info("updating note.json with new id")
        note_json['id'] = target_notebook_id
        with open(target_notebook_path, 'w') as outfile:
            logging.info("writing updated note.json to %s", target_notebook_path)
            dump(note_json, outfile)
    # Load conf JSON
    conf_json = loads(open(target_conf_file_path).read())
    terps = conf_json['interpreterBindings'][ conf_json['interpreterBindings'].keys()[0] ]
    conf_json['interpreterBindings'][target_notebook_id] = terps
    with open(target_conf_file_path, 'w') as outfile:
        logging.info("updating configuration file at target")
        dump(conf_json, outfile)
    return 0



def main(argv):
    logging.basicConfig(filename= "z-migration.log", format='%(levelname)s:%(message)s', level=logging.INFO)
    logging.info("Started with args: %s", argv)
    help_str = """z-migration.py -s <sourcedir> -t <targetdir> -c <confpath> -i <sourcenotebookid> \n
example: $python z-migration.py -s ../z2/notebook -t ../z1/notebook -c ../z1/conf/interpreter.json
"""
    source_notebook_ids = None
    try:
        opts, args = getopt(argv,"hs:t:c:i",["source_dir=","target_dir=","conf_path", "notebookid"])
    except GetoptError:
        print help_str
        exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print help_str
            exit()
        elif opt in ("-s", "--source_dir"):
            source_notebook_dir = arg
        elif opt in ("-t", "--target_dir"):
            target_notebook_dir = arg
        elif opt in ("-c", "--conf_path"):
            target_conf_file_path = arg
        elif opt in ("-i", "--notebookid"):
            source_notebook_ids = [arg]
    if source_notebook_ids is None:
        source_notebook_ids = listdir(source_notebook_dir)
    logging.info("porting notebook(s): %s", source_notebook_ids)
    counter = 0
    for nb_id in source_notebook_ids:
        print "porting", nb_id
        counter += port_notebook(nb_id, source_notebook_dir, target_notebook_dir, target_conf_file_path)
    print "Job complete. Don't forget to restart Zeppelin!"
    if counter > 0:
        print "%i notebooks were skipped. Be sure to check the log file and your target context, empty notebooks and other wierd things have been known to generate issues."
    exit(0)

if __name__ == "__main__":
   main(argv[1:])

