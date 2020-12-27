import xlrd

rangesWorkbook = xlrd.open_workbook(r'ranges.xlsx')
ranges = rangesWorkbook.sheet_by_index(0)
kickoffPATRanges = rangesWorkbook.sheet_by_index(1)
puntRanges = rangesWorkbook.sheet_by_index(2)
fieldgoalRanges = rangesWorkbook.sheet_by_index(3)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 18 23:59:04 2020

@author: apkick
"""

"""
Get the matchup's result column

"""
def getResult(row):
    resultColumn = []
    for i in range(ranges.nrows):
        resultColumn.append(ranges.cell_value(i, 0))
    return resultColumn[row]

"""
Get the matchup's time column

"""
def getTime(row):
    timeColumn = []
    for i in range(ranges.nrows):
        timeColumn.append(ranges.cell_value(i, 26))
    return timeColumn[row]

"""
Get the column number to find the result

"""
def getMatchupColumnNum(offensivePlaybook, defensivePlaybook, playType):
    column = 0
    
    if playType == "pass":
        if offensivePlaybook == "flexbone":
            if defensivePlaybook == "5-2": 
                column = 1
            elif defensivePlaybook == "4-4": 
                column = 2
            elif defensivePlaybook == "4-3": 
                column = 3
            elif defensivePlaybook == "3-4": 
                column = 4
            elif defensivePlaybook == "3-3": 
                column = 5
            else:
                column = -69
        elif offensivePlaybook == "west coast":
            if defensivePlaybook == "5-2": 
                column = 6
            elif defensivePlaybook == "4-4": 
                column = 7
            elif defensivePlaybook == "4-3": 
                column = 8
            elif defensivePlaybook == "3-4": 
                column = 9
            elif defensivePlaybook == "3-3": 
                column = 10
            else:
                column = -69
        elif offensivePlaybook == "pro":
            if defensivePlaybook == "5-2": 
                column = 11
            elif defensivePlaybook == "4-4": 
                column = 12
            elif defensivePlaybook == "4-3": 
                column = 13
            elif defensivePlaybook == "3-4": 
                column = 14
            elif defensivePlaybook == "3-3": 
                column = 15
            else:
                column = -69
        elif offensivePlaybook == "spread":
            if defensivePlaybook == "5-2": 
                column = 16
            elif defensivePlaybook == "4-4": 
                column = 17
            elif defensivePlaybook == "4-3": 
                column = 18
            elif defensivePlaybook == "3-4": 
                column = 19
            elif defensivePlaybook == "3-3": 
                column = 20
            else:
                column = -69
        elif offensivePlaybook == "air raid":
            if defensivePlaybook == "5-2": 
                column = 21
            elif defensivePlaybook == "4-4": 
                column = 22
            elif defensivePlaybook == "4-3": 
                column = 23
            elif defensivePlaybook == "3-4": 
                column = 24
            elif defensivePlaybook == "3-3": 
                column = 25
            else:
                column = -69
        else:
            column = -69
    elif playType == "run":
        if offensivePlaybook == "flexbone":
            if defensivePlaybook == "5-2": 
                column = 27
            elif defensivePlaybook == "4-4": 
                column = 28
            elif defensivePlaybook == "4-3": 
                column = 29
            elif defensivePlaybook == "3-4": 
                column = 30
            elif defensivePlaybook == "3-3": 
                column = 31
            else:
                column = -69
        elif offensivePlaybook == "west coast":
            if defensivePlaybook == "5-2": 
                column = 32
            elif defensivePlaybook == "4-4": 
                column = 33
            elif defensivePlaybook == "4-3": 
                column = 34
            elif defensivePlaybook == "3-4": 
                column = 35
            elif defensivePlaybook == "3-3": 
                column = 36
            else:
                column = -69
        elif offensivePlaybook == "pro":
            if defensivePlaybook == "5-2": 
                column = 37
            elif defensivePlaybook == "4-4": 
                column = 38
            elif defensivePlaybook == "4-3": 
                column = 39
            elif defensivePlaybook == "3-4": 
                column = 40
            elif defensivePlaybook == "3-3": 
                column = 41
            else:
                column = -69
        elif offensivePlaybook == "spread":
            if defensivePlaybook == "5-2": 
                column = 42
            elif defensivePlaybook == "4-4": 
                column = 43
            elif defensivePlaybook == "4-3": 
                column = 44
            elif defensivePlaybook == "3-4": 
                column = 45
            elif defensivePlaybook == "3-3": 
                column = 46
            else:
                column = -69
        elif offensivePlaybook == "air raid":
            if defensivePlaybook == "5-2": 
                column = 47
            elif defensivePlaybook == "4-4": 
                column = 48
            elif defensivePlaybook == "4-3": 
                column = 49
            elif defensivePlaybook == "3-4": 
                column = 50
            elif defensivePlaybook == "3-3": 
                column = 51
            else:
                column = -69
        else:
            column = -69
    else:
        column = -69
        
    return column
    
"""
Get the matchup's play result and time

"""
def getPlayResultRow(matchupColumnNum, difference):  
    matchupColumn = []
    resultsColumn = []
    resultRow = 0

    for i in range(ranges.nrows):
        matchupColumn.append(ranges.cell_value(i, matchupColumnNum))
        resultsColumn.append(ranges.cell_value(i, 0))
        
    # Iterate through each row in the column and fine what bucket the difference falls into
    for i in range(4, len(matchupColumn)):
        if "-" in str(matchupColumn[i]):
            minNum = int(matchupColumn[i].split("-")[0])
            maxNum = int(matchupColumn[i].split("-")[1])
            if difference >= minNum and difference <= maxNum:
                resultRow = i
                break
        elif "-" not in str(matchupColumn[i]) and "N/A" not in str(matchupColumn[i]):
            if matchupColumn[i] == difference:
                resultRow = i
                break
                
    return resultRow   

"""
Get the matchup's kickoff result and time

"""
def getKickoffResultRow(difference):  
    differencesColumn = []
    resultsColumn = []
    resultRow = 0

    for i in range(kickoffPATRanges.nrows):
        differencesColumn.append(kickoffPATRanges.cell_value(i, 1))
        resultsColumn.append(kickoffPATRanges.cell_value(i, 0))
        
    # Iterate through each row in the column and fine what bucket the difference falls into
    for i in range(7, len(differencesColumn)):
        if "-" in str(differencesColumn[i]):
            minNum = int(differencesColumn[i].split("-")[0])
            maxNum = int(differencesColumn[i].split("-")[1])
            if difference >= minNum and difference <= maxNum:
                resultRow = i
                break
        elif "-" not in str(differencesColumn[i]) and "N/A" not in str(differencesColumn[i]):
            if differencesColumn[i] == difference:
                resultRow = i
                break
                
    return resultRow         
  
"""
Get the final play result to send to discord

"""            
def getFinalPlayResult(offensivePlaybook, defensivePlaybook, playType, difference):
    matchupColumnNum = getMatchupColumnNum(offensivePlaybook.lower(), defensivePlaybook.lower(), playType.lower())
    if(matchupColumnNum != -69):
        resultRow = getPlayResultRow(matchupColumnNum, difference)
        result = getResult(resultRow)
        time = getTime(resultRow)
        return {0: result, 1: time} 
    else:
        return {0: "DID NOT FIND PLAY", 1: "DID NOT FIND TIME"} 
  
"""
Get the kickoff time 

"""   
def getKickoffTime(row):
    timeColumn = []
    for i in range(kickoffPATRanges.nrows):
        timeColumn.append(kickoffPATRanges.cell_value(i, 3))
    return timeColumn[row]

"""
Get the kickoff result

"""
def getKickoffResult(row):
    resultColumn = []
    for i in range(kickoffPATRanges.nrows):
        resultColumn.append(kickoffPATRanges.cell_value(i, 0))
    return resultColumn[row]
   

def getFinalKickoffResult(playType, difference):
    resultRow = getKickoffResultRow(difference)
    result = getKickoffResult(resultRow)
    time = getKickoffTime(resultRow)
    print(time)
    return {0: result, 1: time} 
