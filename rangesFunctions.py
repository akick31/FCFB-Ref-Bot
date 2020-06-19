import xlrd

rangesWorkbook = xlrd.open_workbook(r'ranges.xlsx')
ranges = rangesWorkbook.sheet_by_index(0)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 18 23:59:04 2020

@author: apkick
"""

"""
Get the matchup's result column

"""
def getResultColumn(colNum):
    resultColumn = []
    for i in range(ranges.nrows):
        resultColumn.append(ranges.cell_value(i, colNum))
    return resultColumn

"""
Get the matchup's time column

"""
def getTimeColumn(colNum):
    timeColumn = []
    for i in range(ranges.nrows):
        timeColumn.append(ranges.cell_value(i, colNum+1))
    return timeColumn

"""
Get the matchup's min range column

"""
def getMinRangeColumn(colNum):
    minColumn = []
    for i in range(ranges.nrows):
        minColumn.append(ranges.cell_value(i, colNum+2))
    return minColumn

"""
Get the matchup's max range column

"""
def getMaxRangeColumn(colNum):
    maxColumn = []
    for i in range(ranges.nrows):
        maxColumn.append(ranges.cell_value(i, colNum+3))
    return maxColumn
        
"""
Check to see if the string can be an int

"""
def representsInt(string):
    try: 
        int(string)
        return True
    except ValueError:
        return False

"""
Get the matchup's play result and time

"""
def getPlayResult(resultColumn, timeColumn, minColumn, maxColumn, difference):  
    for i in range(len(minColumn)):
        if(representsInt(minColumn[i]) == True and representsInt(maxColumn[i]) == True 
           and int(minColumn[i]) <= difference and int(maxColumn[i]) >= difference):
            return {0: resultColumn[i], 1: int(timeColumn[i])}
    return {0: "DID NOT FIND PLAY", 1: "DID NOT FIND TIME"}
              
if __name__ == '__main__':
    resultColumn = getResultColumn(0)
    timeColumn = getTimeColumn(0)
    minColumn = getMinRangeColumn(0)
    maxColumn = getMaxRangeColumn(0)
    print(minColumn)
    difference = 377
    result = getPlayResult(resultColumn, timeColumn, minColumn, maxColumn, difference)
    print(result[0])
    print(result[1])
