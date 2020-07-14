# -*- coding: utf-8 -*-
"""
Created on Wed Jun 24 21:45:26 2020

@author: Guy
"""


import os, sys, json, argparse
from subprocess import Popen

# if sys.version_info[0] == 2:
#     import ConfigParser as configparser
# else:
#     import configparser

# Access configuration data 
# config = configparser.ConfigParser()
# config_location = os.path.join(configdir, 'MundiTools.cfg')
# config.read(config_location) # config_path

parser = argparse.ArgumentParser(description='Run simple ESA SNAP graph file or operator.')
parser.add_argument('--outdir', type = str, default = None, help = 'Optional output directory in which to save products.')
parser.add_argument('-o', '--outfile', type = str, default = None, help = 'Output product filename. If this is not set, then this shall be created from the input filename and operations.')
parser.add_argument('-i', '--infile', type = str, default = None, help = 'Input file name.')
parser.add_argument('-g', '--graph', type = str, default = None, help = 'ESA SNAP XML graph file path.')
parser.add_argument('-e', '--op', type = str, default = None, help = 'ESA SNAP operator.')
parser.add_argument('-p', '--properties', type = str, default = r'D:\Imagery\Scripts\Mci.S2.properties', help = 'ESA SNAP GPT command properties text file path.')
parser.add_argument('-d', '--dimap', type = bool, default = 'store_true', help = 'Input files are BEAM DIMAP.')
parser.add_argument('--gpt', type = str, default = r'C:\Program Files\snap\bin\gpt', help = 'ESA SNAP XML graph file path.')
parser.add_argument('--overwrite', type = bool, default = False, help = 'Overwrite any existing files.')

args = parser.parse_args()

with open('operator.json', 'r') as json_data:
    operators = json.load(json_data)



if not (args.op or args.graph):
    print('ERROR: No operator (-e/--op) or graph file (-g/--graph) file selected. Please select a valid value. Exiting.')
    sys.exit()
elif args.graph:
    if not os.path.isfile(args.graph):
        print('ERROR: Graph {} does not exist on disk. Please check the file path. Exiting.')
        sys.exit()
elif args.op:
    if not args.op in operators.keys():
        print('ERROR: Invalid ESA SNAP operator. Valid operator names can be determined from "gpt -h". Please select a valid value. Exiting.')
        sys.exit()


if args.outfile:
    if os.path.isdir(os.path.dirname(args.outfile)):
        args.outdir = os.path.dirname(args.outfile)

if args.infile:
    if os.path.ispath(args.infile):
        args.indir = os.path.dirname(args.infile)
    else:
        print('ERROR: {} is not a valid file path. Exiting.'.format(args.indir))
        sys.exit()
else:
    print('ERROR: -i/--infile not set. Exiting.'.format(args.indir))
    sys.exit()
        
if not args.outdir:
    args.outdir = os.path.join(args.indir, 'output')
    print('WARNING: -o/--outdir not set, using: {}'.format(args.outdir))
    
if not os.path.isdir(args.outdir):
    try:
        os.mkdir(args.outdir)
        print('Created on disk: {}'.format(args.outdir))
    except:
        print('ERROR: --outdir {} does not exist and cannot be created. Please fix.'.format(args.outdir))
        sys.exit()


def procscene():
    if args.op:
        proclist = [args.gpt, args.op, '-p', args.properties, '-SsourceProduct="{}"'.format(args.infile), '-t', '"{}"'.format(args.outfile)]
    else:
        proclist = [args.gpt, args.graph, '-Pfile="{}"'.format(args.infile), '-Ptarget', '"{}"'.format(args.outfile)]
    p = Popen(proclist)
    print(p.communicate())

def parsegraph():
    concat = ''
    with open(args.graph, 'r') as lines:
        for line in lines:
            if '<operator>' in line:
                i = line.find('<operator>') + 10
                j = line.find('</operator>')
                oper = line[i:j]
                if not oper in operators.keys():
                    print('ERROR: Invalid ESA SNAP operator "{}" in graph file. Valid operator names can be determined from "gpt -h". Please select a valid value. Exiting.'.format(oper))
                elif not (operators[oper]['Ignore'] == 'True' or oper in concat):
                    concat += '_{}'.format(operators[oper]['Abbreviation'])
    return concat

def makeoutfilename():
    if args.graph:
        concat = parsegraph()
    elif args.op:
        if operators[args.op]['Ignore'] == '':
            concat = '_{}'.format(operators[args.op]['Abbreviation'])
    else:
        concat = ''
    basefilename = os.path.basefile(args.infile)
    if '.' in basefilename:
        i = basefilename.find('.')
        basefilename = basefilename[:i]
    outfilename = os.path.join(args.outdir, '{}{}.dim'.format(basefilename, concat))
    return outfilename


         

def main():
    if not args.outfile:
        args.outfile = makeoutfilename()
    print('Input data file: {}'.format(args.infile))
    print('Output data file: {}'.format(args.outfile))
    if args.graph:
        outproc = args.graph
    else:
        outproc = args.op
    print('Now processing using: {}'.format(outproc))
    procscene()
        
    

if __name__ == '__main__':
    main()
