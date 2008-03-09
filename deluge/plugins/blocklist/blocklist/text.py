##
# Copyright 2007 Steve 'Tarka' Smith (tarka@internode.on.net)
# Distributed under the same terms as Deluge
##


from exceptions import Exception
import re, gzip, os
from socket import inet_aton
from struct import unpack
from zipfile import ZipFile

class TextException(Exception):
    pass

class FormatException(TextException):
    pass

class TextBase:
    
    def __init__(self, fd, regexp):
        print "TextBase loading"
        self.count = 0
        self.fd = fd
        self.re = re.compile(regexp)

    def next(self):
        self.count += 1
        
        txt = self.fd.readline()
        if txt == "":
            return False

        match = self.re.search(txt)
        if not match:
            print 'Blocklist: TextBase: Wrong file type or corrupted blocklist file.'

        try:
            g = match.groups()
        except AttributeError:
            pass
        else:
            start = ".".join(g[0:4])
            end = ".".join(g[4:8])

            return (start, end)

    def close(self):
        self.fd.close()


# This reads PeerGuardian text-formatted block-lists
class PGTextReader(TextBase):

    def __init__(self, fd):
        print "PGTextReader loading"
        regexp = ':(\d+)\.(\d+)\.(\d+)\.(\d+)-(\d+)\.(\d+)\.(\d+)\.(\d+)\s*$'
        TextBase.__init__(self, fd, regexp)


# This reads uncompressed PG text list
class TextReader(PGTextReader):

    def __init__(self, filename):
        print "TextReader loading",filename
        try:
            PGTextReader.__init__(self, open(filename, 'r'))
        except:
            print 'Wrong file type or corrupted blocklist file.'


# Reads Emule style blocklists (aka nipfilter)
class MuleReader(TextBase):

    def __init__(self, fd):
        print "MuleReader loading"
        regexp = '0*(\d+)\.0*(\d+)\.0*(\d+)\.0*(\d+)\s*-\s*0*(\d+)\.0*(\d+)\.0*(\d+)\.0*(\d+)\s*,'
        TextBase.__init__(self, fd, regexp)

class GZMuleReader(MuleReader):

    def __init__(self, filename):
        print "GZMuleReader loading",filename
        try:
            MuleReader.__init__(self, gzip.open(filename, "r"))
        except:
            print 'Wrong file type or corrupted blocklist file.'


# Reads zip files from SafePeer style files 
class PGZip(TextBase):

    def __init__(self, filename):
        # Open zip and extract first file
        try:
            self.zfd = ZipFile(filename, 'r')
        except:
            print 'Blocklist: PGZip: Wrong file type or corrupted blocklist file.'
        else:
            self.files = self.zfd.namelist()
            self.opennext()

    def opennext(self):
        self.tmp = os.tmpfile()
        f = self.files.pop()
        print "Loading file",f
        self.tmp.write(self.zfd.read(f))
        self.tmp.seek(0)
        self.reader = PGTextReader(self.tmp)

    def next(self):
        try:
            ret = self.reader.next()
            if ret == False:
                # This bit is repeated below and could be moved into a
                # new procedure.  However I'm not clear on how this
                # would effect tail recursion, so it remains
                # broken-out for now.
                if len(self.files) > 0:
                    self.opennext()
                    return self.next()
                else:
                    # End of zip
                    return False
            return ret
        
        except FormatException, e:
            print 'Blocklist: PGZip: Got format exception for zipfile: '
            # Just skip
            if len(self.files) > 0:
                self.opennext()
                return self.next()
            else:
                return False
        except AttributeError:
            pass

    def close(self):
        try:
            self.zfd.close()
        except AttributeError:
            pass
