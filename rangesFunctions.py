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
Get the column number to find the result

"""
def getColNum(offensivePlaybook, defensivePlaybook, playType):
    # Passing values
    if((offensivePlaybook == "option" or offensivePlaybook == "west coast" or offensivePlaybook == "pro")
       and (defensivePlaybook == "5-2" or defensivePlaybook == "4-3" or defensivePlaybook == "3-3-5")
       and playType == "pass"):
        return 0
    elif((offensivePlaybook == "option" or offensivePlaybook == "west coast")
       and (defensivePlaybook == "4-4" or defensivePlaybook == "3-4")
       and playType == "pass"):
        return 4
    elif((offensivePlaybook == "option" or offensivePlaybook == "west coast")
       and (defensivePlaybook == "4-3" or defensivePlaybook == "3-3-5")
       and playType == "pass"):
        return 8
    elif((offensivePlaybook == "option")
       and (defensivePlaybook == "3-4")
       and playType == "pass"):
        return 12
    elif((offensivePlaybook == "option")
       and (defensivePlaybook == "3-3-5")
       and playType == "pass"):
        return 16
    elif((offensivePlaybook == "west coast" or offensivePlaybook == "pro" or offensivePlaybook == "spread")
       and (defensivePlaybook == "5-2" or defensivePlaybook == "4-3" or defensivePlaybook == "3-3-5")
       and playType == "pass"):
        return 20
    elif((offensivePlaybook == "west coast" or offensivePlaybook == "pro")
       and (defensivePlaybook == "4-4" or defensivePlaybook == "3-4")
       and playType == "pass"):
        return 24
    elif((offensivePlaybook == "pro" or offensivePlaybook == "spread" or offensivePlaybook == "air raid")
       and (defensivePlaybook == "5-2" or defensivePlaybook == "4-3" or defensivePlaybook == "3-3-5")
       and playType == "pass"):
        return 28
    elif((offensivePlaybook == "pro" or offensivePlaybook == "spread")
       and (defensivePlaybook == "4-4" or defensivePlaybook == "3-4")
       and playType == "pass"):
        return 32
    elif((offensivePlaybook == "spread" or offensivePlaybook == "air raid")
       and (defensivePlaybook == "5-2" or defensivePlaybook == "4-3")
       and playType == "pass"):
        return 40
    elif((offensivePlaybook == "spread" or offensivePlaybook == "air raid")
       and (defensivePlaybook == "4-4" or defensivePlaybook == "3-4")
       and playType == "pass"):
        return 44
    elif((offensivePlaybook == "air raid") 
       and (defensivePlaybook == "5-2")
       and playType == "pass"):
        return 48
    elif((offensivePlaybook == "air raid") 
       and (defensivePlaybook == "4-4")
       and playType == "pass"):
        return 52
    
    #Rushing Values
    if((offensivePlaybook == "option" or offensivePlaybook == "west coast" or offensivePlaybook == "pro")
       and (defensivePlaybook == "5-2" or defensivePlaybook == "4-3" or defensivePlaybook == "3-3-5")
       and playType == "run"):
        return 56
    elif((offensivePlaybook == "option" or offensivePlaybook == "west coast")
       and (defensivePlaybook == "4-4" or defensivePlaybook == "3-4")
       and playType == "run"):
        return 60
    elif((offensivePlaybook == "option" or offensivePlaybook == "west coast")
       and (defensivePlaybook == "4-3" or defensivePlaybook == "3-3-5")
       and playType == "run"):
        return 64
    elif((offensivePlaybook == "option")
       and (defensivePlaybook == "3-4")
       and playType == "run"):
        return 68
    elif((offensivePlaybook == "option")
       and (defensivePlaybook == "3-3-5")
       and playType == "run"):
        return 72
    elif((offensivePlaybook == "west coast" or offensivePlaybook == "pro" or offensivePlaybook == "spread")
       and (defensivePlaybook == "5-2" or defensivePlaybook == "4-3" or defensivePlaybook == "3-3-5")
       and playType == "run"):
        return 76
    elif((offensivePlaybook == "west coast" or offensivePlaybook == "pro")
       and (defensivePlaybook == "4-4" or defensivePlaybook == "3-4")
       and playType == "run"):
        return 80
    elif((offensivePlaybook == "pro" or offensivePlaybook == "spread" or offensivePlaybook == "air raid")
       and (defensivePlaybook == "5-2" or defensivePlaybook == "4-3" or defensivePlaybook == "3-3-5")
       and playType == "run"):
        return 84
    elif((offensivePlaybook == "pro" or offensivePlaybook == "spread")
       and (defensivePlaybook == "4-4" or defensivePlaybook == "3-4")
       and playType == "run"):
        return 88
    elif((offensivePlaybook == "spread" or offensivePlaybook == "air raid")
       and (defensivePlaybook == "5-2" or defensivePlaybook == "4-3")
       and playType == "run"):
        return 96
    elif((offensivePlaybook == "spread" or offensivePlaybook == "air raid")
       and (defensivePlaybook == "4-4" or defensivePlaybook == "3-4")
       and playType == "run"):
        return 100
    elif((offensivePlaybook == "air raid") 
       and (defensivePlaybook == "5-2")
       and playType == "run"):
        return 104
    elif((offensivePlaybook == "air raid") 
       and (defensivePlaybook == "4-4")
       and playType == "run"):
        return 108
    else:
        return -69

    
"""
Get the matchup's play result and time

"""
def getPlayResult(resultColumn, timeColumn, minColumn, maxColumn, difference):  
    for i in range(len(minColumn)):
        if(representsInt(minColumn[i]) == True and representsInt(maxColumn[i]) == True 
           and int(minColumn[i]) <= int(difference) and int(maxColumn[i]) >= int(difference)):
            return {0: resultColumn[i], 1: int(timeColumn[i])}
    return {0: "DID NOT FIND PLAY", 1: "DID NOT FIND TIME"}        
  
"""
Get the final result to send to discord

"""            
def getFinalResult(offensivePlaybook, defensivePlaybook, playType, difference):
    colNumber = getColNum(offensivePlaybook.lower(), defensivePlaybook.lower(), playType.lower())
    if(colNumber != -69):
        resultColumn = getResultColumn(colNumber)
        timeColumn = getTimeColumn(colNumber)
        minColumn = getMinRangeColumn(colNumber)
        maxColumn = getMaxRangeColumn(colNumber)
        result = getPlayResult(resultColumn, timeColumn, minColumn, maxColumn, difference)
        return result
    else:
        return {0: "DID NOT FIND PLAY", 1: "DID NOT FIND TIME"} 
