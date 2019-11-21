# ---------------------------------------------------------------
# -- Register Access Layer --
#
# Abstracts direct Register Access. Uses Serial Library
#
# Author: Melvin Strobl
# ---------------------------------------------------------------

import sys #exit script


#----------------------------------------------------------
# Parsing Address which can be either passed in hex or dec
# and returns an int.
#----------------------------------------------------------
def parseHexDecParam(param):
    pParam = None
    try:
        pParam = int(param, 10)
        return pParam
    except ValueError:
        pass
    except TypeError:
        pass
    try:
        pParam = int(param, 16)
        return pParam
    except ValueError:
        pass
    except TypeError:
        pass
    try:
        pParam = int(param)
        return pParam
    except ValueError:
        sys.exit('Unable to parse param in hex or dec')
    except TypeError:
        sys.exit('Unable to parse param in hex or dec')
    except Exception as e:
        sys.exit('Error when parsing param: '+str(e))

    return pParam

def parseHexDecParams(params):
    pParams = 0

    it=0
    for param in reversed(params):  #lsb is transmitted first
        pParams = pParams + parseHexDecParam(param)

        it = it + 1
    return pParams

#----------------------------------------------------------
# Helper Fct for handling files
#----------------------------------------------------------
def readFile(filePath):
    try:
        with open(filePath) as f:
            lines = f.readlines()
        f.close()
    except:
        raise Exception('Unable to open file: '+str(filePath))

    length = lines.__len__()

    return {'length':length,
            'lines':lines}

def writeFile(filePath, content):
    try:
        with open(filePath, "w") as f:
            f.write(content)
        f.close()
    except Exception as e:
        raise Exception('Unable to open file: '+str(filePath) + '\n' + str(e.message))

def printBar(current, max, size):
    sys.stdout.write('\r')
    j = (current + 1) / max
    sys.stdout.write("[%s%s] %d%%" % ('='*int(size*j), '-'*int(size-size*j), 100*j))
    sys.stdout.flush()


def last(self):
     out=self.popitem()
     self[out[0]]=out[1]
     return out

def toByteArray(self, string):
    pass

def str2bool(v):
    if type(v) == bool:
        return v
    return v.lower() in ("yes", "true", "t", "1")