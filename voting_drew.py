import csv
import time
def getData():
    with open('TestCase_Last_Place_Tie.csv', newline='') as file:
        reader = csv.DictReader(file)
        myList = list()
        keys = list()
        myDict = dict()
        index = 0
        for row in reader:
           if index ==0:
               for val in row.values():
                   keys.append(val)

           elif index > 1:
               index2 = 0
               myDict = dict()
               for val in row.values():
                   myDict[keys[index2]]=val
                   index2+=1
               myList.append(myDict)
               for key in keys:
                   if "-" not in key:
                       myDict.pop(key)
                   else:
                       splitList = key.split('- ')
                       myDict[splitList[1].lower()] = myDict.pop(key)
           index += 1
        return myList, list(myDict.keys())
def removeAbstain(data):
    data[:] = [e for e in data if e.get("abstain") != '1']
    return data

def getFirstCounts(data, keys, counting = 1):
    counts = dict()
    for key in keys:
        counts[key] = 0
    for row in data:
        for key in keys:
            row[key] = int (row[key])
            if row [key] == counting:
                counts [key] += 1
    return counts

def getMax(counts, keys):
    maxVal = 0
    maxName = 'None'
    for key in keys:
        if counts[key] > maxVal :
            maxVal = counts[key]
            maxName = key
    return maxName, maxVal

def getMin(counts, keys, counting = 2):
    minVal = 9999
    minName = 'None'
    tiedValues = list()
    for key in keys:
        if counts[key] == minVal:
            tiedValues.append(key)
        if counts[key] < minVal:
            minVal = counts[key]
            minName = key
            tiedValues.clear()
    if (len (tiedValues) == 1 and len (counts) == 2) :
        print("An absolute tie for FIRST PLACE occured between  " + tiedValues[0] +" and " + minName)
        # time.sleep(10)
    if (counting > len(keys) and len(tiedValues) > 0):
        print("An absolute tie occured for LAST PLACE between " + tiedValues[0] +" and " + minName)
        # time.sleep(10)
    if len(tiedValues) != 0:
        print("There was a tie when trying to remove " + str(len(tiedValues)+1) + " candidates in layer " + str(counting-1))
        tiedValues.append(minName)
        counts2 = getFirstCounts(data, keys, counting=counting)
        minName = getMin(counts2, tiedValues, counting+1)
    return minName

def removeMin(data, minName, keys):
    keys.remove(minName)
    for row in data:
        val = row.pop(minName)
        for key in keys:
            if row[key] > val:
                row[key]-=1
    return data, keys


data, keys = getData()
data = removeAbstain(data)
counts = getFirstCounts(data, keys)
maxName, maxValue = getMax(counts, keys)
while (data.__len__()>= 2*maxValue):
    minName = getMin(counts, keys)
    data, keys = removeMin(data, minName, keys)
    data = removeAbstain(data)
    counts = getFirstCounts(data, keys)
    maxName, maxValue = getMax(counts, keys)
print("Winner is " + maxName)
time.sleep(360)