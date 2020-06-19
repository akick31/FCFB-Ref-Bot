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


"""
Get the column number to find the result

"""
def getColNum(offensivePlaybook, defensivePlaybook, playType):
    # Passing values
    if((offensivePlaybook == "Option" or offensivePlaybook == "West Coast" or offensivePlaybook == "Pro")
       and (defensivePlaybook == "5-2" or defensivePlaybook == "4-3" or defensivePlaybook == "3-3-5")
       and playType == "Pass"):
        return 0
    elif((offensivePlaybook == "Option" or offensivePlaybook == "West Coast")
       and (defensivePlaybook == "4-4" or defensivePlaybook == "3-4")
       and playType == "Pass"):
        return 4
    elif((offensivePlaybook == "Option" or offensivePlaybook == "West Coast")
       and (defensivePlaybook == "4-3" or defensivePlaybook == "3-3-5")
       and playType == "Pass"):
        return 8
    elif((offensivePlaybook == "Option")
       and (defensivePlaybook == "3-4")
       and playType == "Pass"):
        return 12
    elif((offensivePlaybook == "Option")
       and (defensivePlaybook == "3-3-5")
       and playType == "Pass"):
        return 16
    elif((offensivePlaybook == "West Coast" or offensivePlaybook == "Pro" or offensivePlaybook == "Spread")
       and (defensivePlaybook == "5-2" or defensivePlaybook == "4-3" or defensivePlaybook == "3-3-5")
       and playType == "Pass"):
        return 20
    elif((offensivePlaybook == "West Coast" or offensivePlaybook == "Pro")
       and (defensivePlaybook == "4-4" or defensivePlaybook == "3-4")
       and playType == "Pass"):
        return 24
    elif((offensivePlaybook == "Pro" or offensivePlaybook == "Spread" or offensivePlaybook == "Air Raid")
       and (defensivePlaybook == "5-2" or defensivePlaybook == "4-3" or defensivePlaybook == "3-3-5")
       and playType == "Pass"):
        return 28
    elif((offensivePlaybook == "Pro" or offensivePlaybook == "Spread")
       and (defensivePlaybook == "4-4" or defensivePlaybook == "3-4")
       and playType == "Pass"):
        return 32
    elif((offensivePlaybook == "Spread" or offensivePlaybook == "Air Raid")
       and (defensivePlaybook == "5-2" or defensivePlaybook == "4-3")
       and playType == "Pass"):
        return 40
    elif((offensivePlaybook == "Spread" or offensivePlaybook == "Air Raid")
       and (defensivePlaybook == "4-4" or defensivePlaybook == "3-4")
       and playType == "Pass"):
        return 44
    elif((offensivePlaybook == "Air Raid") 
       and (defensivePlaybook == "5-2")
       and playType == "Pass"):
        return 48
    elif((offensivePlaybook == "Air Raid") 
       and (defensivePlaybook == "4-4")
       and playType == "Pass"):
        return 52
    
    #Rushing Values
    if((offensivePlaybook == "Option" or offensivePlaybook == "West Coast" or offensivePlaybook == "Pro")
       and (defensivePlaybook == "5-2" or defensivePlaybook == "4-3" or defensivePlaybook == "3-3-5")
       and playType == "Run"):
        return 56
    elif((offensivePlaybook == "Option" or offensivePlaybook == "West Coast")
       and (defensivePlaybook == "4-4" or defensivePlaybook == "3-4")
       and playType == "Run"):
        return 60
    elif((offensivePlaybook == "Option" or offensivePlaybook == "West Coast")
       and (defensivePlaybook == "4-3" or defensivePlaybook == "3-3-5")
       and playType == "Run"):
        return 64
    elif((offensivePlaybook == "Option")
       and (defensivePlaybook == "3-4")
       and playType == "Run"):
        return 68
    elif((offensivePlaybook == "Option")
       and (defensivePlaybook == "3-3-5")
       and playType == "Run"):
        return 72
    elif((offensivePlaybook == "West Coast" or offensivePlaybook == "Pro" or offensivePlaybook == "Spread")
       and (defensivePlaybook == "5-2" or defensivePlaybook == "4-3" or defensivePlaybook == "3-3-5")
       and playType == "Run"):
        return 76
    elif((offensivePlaybook == "West Coast" or offensivePlaybook == "Pro")
       and (defensivePlaybook == "4-4" or defensivePlaybook == "3-4")
       and playType == "Run"):
        return 80
    elif((offensivePlaybook == "Pro" or offensivePlaybook == "Spread" or offensivePlaybook == "Air Raid")
       and (defensivePlaybook == "5-2" or defensivePlaybook == "4-3" or defensivePlaybook == "3-3-5")
       and playType == "Run"):
        return 84
    elif((offensivePlaybook == "Pro" or offensivePlaybook == "Spread")
       and (defensivePlaybook == "4-4" or defensivePlaybook == "3-4")
       and playType == "Run"):
        return 88
    elif((offensivePlaybook == "Spread" or offensivePlaybook == "Air Raid")
       and (defensivePlaybook == "5-2" or defensivePlaybook == "4-3")
       and playType == "Run"):
        return 96
    elif((offensivePlaybook == "Spread" or offensivePlaybook == "Air Raid")
       and (defensivePlaybook == "4-4" or defensivePlaybook == "3-4")
       and playType == "Run"):
        return 100
    elif((offensivePlaybook == "Air Raid") 
       and (defensivePlaybook == "5-2")
       and playType == "Run"):
        return 104
    elif((offensivePlaybook == "Air Raid") 
       and (defensivePlaybook == "4-4")
       and playType == "Run"):
        return 108
    else:
        return -69
    
        
              
if __name__ == '__main__':
    colNumber = getColNum("West Coast", "4-4", "Pass")
    if(colNumber != -69):
        resultColumn = getResultColumn(colNumber)
        timeColumn = getTimeColumn(colNumber)
        minColumn = getMinRangeColumn(colNumber)
        maxColumn = getMaxRangeColumn(colNumber)
        difference = 286
        result = getPlayResult(resultColumn, timeColumn, minColumn, maxColumn, difference)
        print(result[0])
        print(result[1])
    else:
        print("ERROR IN GETTING PLAYBOOK MATCHUP")
