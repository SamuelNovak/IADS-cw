
# Inf2-IADS Coursework 1, October 2019
# Python source file: index_build.py


# PART A: INDEXING A LARGE SET OF PLAINTEXT FILES

import buffered_io
from buffered_io import *


# Global variables

CorpusFiles = { 'CAA' : 'Carroll_Alice_in_Wonderland.txt',
                'DCC' : 'Dickens_Christmas_Carol.txt',
                'SJH' : 'Stevenson_Jekyll_and_Hyde.txt',
              # 'SCW' : 'Shakespeare_Complete_Works.txt',
              # 'TWP' : 'Tolstoy_War_and_Peace.txt'
               }
# each file should be identified by a three-letter code
# CAA, DCC, SJH are small, SCW and TCP are larger

IndexFile = 'index.txt'
# name of main index file to be generated

MetaIndex = {'' : 0}
# dictionary to be populated
# MetaIndex[k] will give line number in IndexFile for key k

MetaIndexOp = (lambda s: 0)


# Initial scan to determine number of lines in a given text file

def getFileLength(filename):
    reader = BufferedInput(filename,0.8)
    lines = 0
    chunk = reader.readchunk()
    while chunk != []:
        lines += len(chunk)
        chunk = reader.readchunk()
    reader.close()
    return lines

# Extracting list of words present in a single text line:

def getWords(s):
    t = s   # could do some translation here to process accented symbols etc.
    words,flg = [],False
    for i in range(len(t)):
        if not flg:
            if t[i].isalpha():
                # potential start of word
                flg=True
                j=i
        else:
            if not t[i].isalpha():
                # potential end of word
                flg=False
                # design decision: we ignore words of length < 4
                if i-j >= 4: 
                    words.append(t[j:i].casefold())
        # assumes some terminator like \n is present
    return words

# Generation of unsorted index entries for a given textfile

import math

def generateIndexEntries(filename,filecode,writer):
    size = getFileLength(filename)
    digits = int(math.log10(size))+1
    padCtrl = '0' + str(digits)
    reader = BufferedInput(filename,0.2)
    currline = reader.readline()
    inlineNo = 1
    outlineNo = 0
    while currline != '':
        # process currline:
        words = getWords(currline)
        for w in words:
            writer.writeline(w+':'+filecode+format(inlineNo,padCtrl)+'\n')
        outlineNo += len(words)
        # next line:
        inlineNo += 1
        currline = reader.readline()
    reader.close()
    return outlineNo  # for checking

def generateAllIndexEntries(entryfile):
    global CorpusFiles
    writer = BufferedOutput(entryfile,0.7)
    outlines = 0
    for filecode in CorpusFiles:
        outlines += generateIndexEntries(CorpusFiles[filecode],filecode,writer)
    writer.flush()
    return outlines


# Provide the following:

import os

def splitIntoSortedChunks(entryfile):
    reader = BufferedInput(entryfile,0.3)
    blockNo = 0
    chunk = reader.readchunk()
    while chunk != []:
        chunk.sort()
        blockfile = open('temp_' + str(blockNo) + '_' + str(blockNo+1),'w',
                         encoding='utf-8')
        # output file written all at once, so no need for buffering
        blockfile.writelines(chunk)
        blockfile.close()
        blockNo += 1
        chunk = reader.readchunk()
    reader.close()
    return blockNo


# STUDENT CODE goes here.

def mergeFiles(a, b, c):
    """Merge files temp_a_b and temp_b_c to create temp_a_c."""
    f_ab = BufferedInput("temp_{}_{}".format(a, b), 0.3)
    f_bc = BufferedInput("temp_{}_{}".format(b, c), 0.3)
    f_ac = BufferedOutput("temp_{}_{}".format(a, c), 0.3)

    line_ab = f_ab.readline()
    line_bc = f_bc.readline()
    # Only runs while at least one file still has contents to merge
    while line_ab or line_bc:
        if not line_ab:
            # ab is done, so it has to be bc
            f_ac.writeline(line_bc)
            line_bc = f_bc.readline()
        elif not line_bc:
            # bc is done, so it has to be ab
            f_ac.writeline(line_ab)
            line_ab = f_ab.readline()
        else:
            # both still to be merged => write the line that should be first
            if line_ab < line_bc:
                f_ac.writeline(line_ab)
                line_ab = f_ab.readline()
            else:
                f_ac.writeline(line_bc)
                line_bc = f_bc.readline()
    f_ab.close()
    f_bc.close()
    f_ac.flush()

    os.remove("temp_{}_{}".format(a, b))
    os.remove("temp_{}_{}".format(b, c))
    return "temp_{}_{}".format(a, c)


def mergeFilesInRange(a, c):
    if c - a == 2:
        # The lowest case - only two files => join them
        return mergeFiles(a, a+1, c)
    elif c - a > 2:
        # We need to divide work here
        p = (a + c) // 2
        mergeFilesInRange(a, p)
        mergeFilesInRange(p, c)
        # Here it recombines
        return mergeFiles(a, p, c)
    elif c - a == 1:
        # This is already the file
        # this portion should never run if we give the function valid arguments,
        # it just exists so that there is always a valid output (for input that
        # is invalid but still sensible (the file actually exists)
        return "temp_{}_{}".format(a, c)
    # other cases (a >= c) should never happen, and they do not have any obvious
    # solution, so they are not implemented
    
# Putting it all together:

def sortRawEntries(entryfile):
    chunks = splitIntoSortedChunks(entryfile)
    outfile = mergeFilesInRange(0,chunks)
    return outfile

# Now compile the index file itself, by 'compressing' the entries for each key
# into a single line.

def createIndexFromEntries(entryfile,indexfile):
    reader = BufferedInput (entryfile,0.4)
    writer = BufferedOutput (indexfile,0.4)
    inl = reader.readline()
    currKey, currDoc, lineBuffer = '', '', ''
    while inl != '':
        # get keyword and ref, start ref list:
        colon = inl.index(':')
        key = inl[:colon]
        doc = inl[colon+1:colon+4] # three-letter doc identifiers
        j = colon+4
        while inl[j] == '0':
            j += 1
        line = inl[j:-1]
        if key != currKey:
            # new key: start a new line in index
            if lineBuffer != '':
                writer.writeline (lineBuffer+'\n')
            currKey = key
            currDoc = ''
            lineBuffer = key + ':'
        if currDoc == '':
            # first doc for this key entry
            currDoc = doc
            lineBuffer = lineBuffer + doc + line
        elif doc != currDoc:
            # new doc within this key entry
            currDoc = doc
            lineBuffer = lineBuffer + ',' + doc + line
        else:
            lineBuffer = lineBuffer + ',' + line
        inl = reader.readline()
    # write last line and clean up
    writer.writeline (lineBuffer+'\n')
    writer.flush()
    reader.close()

# Generating the meta-index to the index as a Python dictionary.

def generateMetaIndex(indexFile):
    global MetaIndex, MetaIndexOp
    MetaIndex.clear()
    reader = BufferedInput (indexFile,0.9)
    indexline = 1
    inl = reader.readline()
    while inl != '':
        key = inl[:inl.index(':')]
        MetaIndex[key] = indexline
        indexline += 1
        inl = reader.readline()
    reader.close()
    MetaIndexOp = (lambda s: MetaIndex[s])

def buildIndex():
    rawEntryFile = 'raw_entries'
    entries = generateAllIndexEntries (rawEntryFile)
    sortedEntryFile = sortRawEntries (rawEntryFile)
    global IndexFile
    createIndexFromEntries (sortedEntryFile, IndexFile)
    generateMetaIndex (IndexFile)
    os.remove(rawEntryFile)
    os.remove(sortedEntryFile)
    print('Success! ' + str(len(MetaIndex)) + ' keys, ' +
          str(entries) + ' entries.')

# Accessing the index using 'linecache' (random access to text files by line)

import linecache

def indexEntryFor(key):
    global IndexFile, MetaIndex, MetaIndexOp
    try:
        lineNo = MetaIndexOp(key)  # allows for other meta-indexing schemes
        indexLine = linecache.getline(IndexFile,lineNo)
    except KeyError:
        return None
    colon = indexLine.index(':')
    if indexLine[:colon] == key:
        return indexLine[colon+1:]
    else:
        raise Exception('Wrong key in index line.')

# End of file
