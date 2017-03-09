

import shelve
import os

path = os.path.dirname(os.path.realpath(__file__))
print path

integralTypes = ("compEllipIntE", "compEllipIntK")
dbPath = os.path.join(path, "compIntValues")
print dbPath
print '------'


def readFiles():
    """
    """
    intVals = {}
    for intType in integralTypes:
        fileName = os.path.join(path, intType + ".txt")
        intVals[intType] = {}
        print fileName
        for line in open(fileName, 'r'):
            dataPair = line.split(" ")
            xVal = dataPair[0]
            yVal = dataPair[1]
            intVals[intType][xVal] = yVal
    integrals = shelve.open(dbPath)
    for key in intVals.keys():
        integrals[key] = intVals[key]
    integrals.close()


if __name__ == "__main__":
    readFiles()
