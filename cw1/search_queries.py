
# Inf2-IADS Coursework 1, October 2019
# Python source file: search_queries.py


# PART B: PROCESSING SEARCH QUERIES

import index_build

# We find hits for queries using the index entries for the search terms.
# Since index entries for common words may be large, we don't want to
# process the entire index entry before commencing a search.
# Instead, we process the index entry as a stream of items, each of which
# references an occurrence of the search term.

# For example, the (short) index entry

#    'ABC01,23,DEF004,056,789\n'

# yields a stream which successively yields the items

#    ('ABC',1), ('ABC',23), ('DEF',4), ('DEF',56), ('DEF',789), None, None, ...

# Item streams also support peeking at the next item without advancing.

class ItemStream:
    def __init__(self,entryString):
        self.entryString = entryString
        self.pos = 0
        self.doc = 0
        self.comma = 0
    def updateDoc(self):
        if self.entryString[self.pos].isalpha():
            self.doc = self.entryString[self.pos:self.pos+3]
            self.pos += 3
    def peek(self):
        if self.pos < len(self.entryString):
            self.updateDoc()
            self.comma = self.entryString.find(',',self.pos)
                    # yields -1 if no more commas after pos
            line = int(self.entryString[self.pos:self.comma])
                    # magically works even when comma == -1, thanks to \n
            return (self.doc,line)
        # else return None
    def next(self):
        e = self.peek()
        if self.comma == -1:
            self.pos = len(self.entryString)
        else:
            self.pos = self.comma + 1
        return e


# STUDENT CODE goes here.

from time import sleep

class HitStream():
    def __init__(self, itemStreams, lineWindow, minRequired):
        if not itemStreams:
            raise Exception("No streams suppied.")
        
        self.itemStreams = itemStreams
        self.lineWindow = lineWindow
        self.minRequired = minRequired

        # positions in the corresponding itemstreams
        self.line = 0
        # Assuming they always all start with the same document
        self._docs = sorted(index_build.CorpusFiles.keys())
        self.doc = self._docs.pop(0)

    def next(self):
        # repeat this until it finds a match or all the streams end
        while True:
            # For checking whether we need to search the next document
            next_doc = []
            lines = []
            # store those streams that are still in this doc (used later)
            streams_in_doc = []
            # find next line in one of the streams (still in the same document)
            for s in range(len(self.itemStreams)):
                stream = self.itemStreams[s]
                pk = stream.peek()
                if pk:
                    d, l = stream.peek()
                    if d == self.doc:
                        next_doc.append(False)
                        lines.append((s, l))
                        streams_in_doc.append(stream)
                    else:
                        next_doc.append(True)
                    # print(lines, next_doc)
            
            # if all streams are now in a different document, go to the next document
            if all(next_doc):
                # check if there even is a document to search left
                # (although this shouldn't ever happen) # TODO dead code
                if not self._docs:
                    return None
                else:
                    # go to next document, reset line to 0
                    self.doc = self._docs.pop(0)
                    continue

            # if the same file => increment line where we're looking
            # also store which stream it was that had the min line
            minStream, self.line = sorted(lines, key=lambda x: x[1])[0]
            # print("minStream:", minStream, "| Looking around line:", self.line)

            # count how many streams have an entry within our bounds
            # only go through the streams not yet pointing to another document
            # (so we don't have to loop through those that are potentially already in another)
            count = 0
            for stream in streams_in_doc:
                pk = stream.peek()
                if pk:
                    d, l = stream.peek()
                    if self.line <= l <= self.line + self.lineWindow - 1:
                        count += 1

            # increment the stream that had the min value
            self.itemStreams[minStream].next()

            # print("-->", count)
            if count >= self.minRequired:                
                return (self.doc, self.line)
            
            # TODO here it searches for matches in the other streams
            # print("D:", self.doc, "W:", self.line)
            count = 0
            sleep(0.1)



# Displaying hits as corpus quotations:

import linecache

def displayLines(startref,lineWindow):
    # global CorpusFiles
    if startref is not None:
        doc = startref[0]
        docfile = index_build.CorpusFiles[doc]
        line = startref[1]
        print ((doc + ' ' + str(line)).ljust(16) +
               linecache.getline(docfile,line).strip())
        for i in range(1,lineWindow):
            print (' '*16 + linecache.getline(docfile,line+i).strip())
        print ('')

def displayHits(hitStream,numberOfHits,lineWindow):
    for i in range(0,numberOfHits):
        startref = hitStream.next()
        if startref is None:
            print('-'*16)
            break
        displayLines(startref,lineWindow)
    linecache.clearcache()
    return hitStream


# Putting it all together:

currHitStream = None

currLineWindow = 0

def advancedSearch(keys,lineWindow,minRequired,numberOfHits=5):
    indexEntries = [index_build.indexEntryFor(k) for k in keys]
    if not all(indexEntries):
        message = "Words absent from index:  "
        for i in range(0,len(keys)):
            if indexEntries[i] is None:
                message += (keys[i] + " ")
        print(message + '\n')
    itemStreams = [ItemStream(e) for e in indexEntries if e is not None]
    if len(itemStreams) >= minRequired:
        global currHitStream, currLineWindow
        currHitStream = HitStream (itemStreams,lineWindow,minRequired)
        currLineWindow = lineWindow
        displayHits(currHitStream,numberOfHits,lineWindow)

def easySearch(keys,numberOfHits=5):
    global currHitStream, currLineWindow
    advancedSearch(keys,1,len(keys),numberOfHits)

def more(numberOfHits=5):
    global currHitStream, currLineWindow
    displayHits(currHitStream,numberOfHits,currLineWindow)

# End of file
