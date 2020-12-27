import xlrd
from util import representsInt
from util import convertYardLine
from game_database_functions import getGameInfo
from game_database_functions import updateClockStopped

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

#########################
#      NORMAL PLAY      #
#########################

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
Get the final play result to send to discord

"""            
def getFinalPlayResult(message, offensivePlaybook, defensivePlaybook, playType, difference, clockRunoffType, clockStopped):
    clockRunoff = 0
    
    # Add clock runoff
    if clockStopped == "NO":
        if clockRunoffType == "normal":
            if offensivePlaybook == "flexbone":
                clockRunoff = 20
            if offensivePlaybook == "west coast":
                clockRunoff = 17
            if offensivePlaybook == "pro":
                clockRunoff = 15
            if offensivePlaybook == "spread":
                clockRunoff = 13
            if offensivePlaybook == "air raid":
                clockRunoff = 10
        elif clockRunoffType == "chew":
            clockRunoff = 30
        elif clockRunoffType == "hurry":
            clockRunoff = 7
            
    if playType == "run" or playType == "pass":
        matchupColumnNum = getMatchupColumnNum(offensivePlaybook.lower(), defensivePlaybook.lower(), playType.lower())
        if(matchupColumnNum != -69):
            resultRow = getPlayResultRow(matchupColumnNum, difference)
            result = getResult(resultRow)

            if(representsInt(result) == False):
                if str(result) == "Incompletion":
                    updateClockStopped(message.channel, "YES")

            time = getTime(resultRow)
            return {0: result, 1: int(time) + clockRunoff} 
        else:
            return {0: "DID NOT FIND PLAY", 1: "DID NOT FIND TIME"} 
        
    elif playType == "field goal":
        result = getFGResult(message, difference)
        
        if(str(result) != "Kick 6"):
            time = 5
        else:
            time = 13
            
        updateClockStopped(message.channel, "YES")
        return {0: result, 1: int(time) + clockRunoff} 
    
    elif playType == "punt":
        resultRow = getPuntResultRow(message, difference)
        result = getPuntResult(resultRow)
        
        time = 15
        updateClockStopped(message.channel, "YES")
        return {0: result, 1: int(time) + clockRunoff}  
        
    elif playType == "spike":
        result = "Incompletion"
        time = 3
        updateClockStopped(message.channel, "YES")
        return {0: result, 1: time}  
        
    elif playType == "kneel":
        result = "-2"
        time = 40
        updateClockStopped(message.channel, "NO")
        return {0: result, 1: time}  
    
#########################
#       FIELD GOAL      #
#########################

def getFGResult(message, difference):  
    distanceColumn = []
    madeColumn = []
    missColumn = []
    blockedColumn = []
    kickSixColumn = []
    
    gameInfo = getGameInfo(message.channel)
    yardLine = convertYardLine(gameInfo)

    for i in range(fieldgoalRanges.nrows):
        distanceColumn.append(ranges.cell_value(i, 0))
        madeColumn.append(ranges.cell_value(i, 1))
        missColumn.append(ranges.cell_value(i, 2))
        blockedColumn.append(ranges.cell_value(i, 3))
        kickSixColumn.append(ranges.cell_value(i, 4))
        
    fieldGoalDistance = int(yardLine) + 17
    
    # Iterate through each row in the column and fine what bucket the distance falls into
    for i in range(4, len(distanceColumn)):
        if fieldGoalDistance == distanceColumn[i]:
            minNum = int(madeColumn[i].split("-")[0])
            maxNum = int(madeColumn[i].split("-")[1])
            if difference >= minNum and difference <= maxNum:
                return "Made"
                break
            if "-" in str(missColumn[i]):
                minNum = int(madeColumn[i].split("-")[0])
                maxNum = int(madeColumn[i].split("-")[1])
                if difference >= minNum and difference <= maxNum:
                    return "Miss"
            if "-" in str(blockedColumn[i]):
                minNum = int(blockedColumn[i].split("-")[0])
                maxNum = int(blockedColumn[i].split("-")[1])
                if difference >= minNum and difference <= maxNum:
                    return "Blocked"
            if "-" in str(kickSixColumn[i]):
                minNum = int(kickSixColumn[i].split("-")[0])
                maxNum = int(kickSixColumn[i].split("-")[1])
                if difference >= minNum and difference <= maxNum:
                    return "Kick 6"
        else:
            return "Miss"
        
    

#########################
#        PUNTS          #
#########################

"""
Iterate through the rows and get the result

"""
def getPuntResult(row):
    resultColumn = []
    for i in range(puntRanges.nrows):
        resultColumn.append(puntRanges.cell_value(i, 0))
    return resultColumn[row]

"""
Get the bucket that the field position is in

"""
def getFieldPositionColumnNum(yardLine):
    if yardLine <= 100 and yardLine >= 66:
        return 1
    elif yardLine <= 65 and yardLine >= 61:
        return 2
    elif yardLine <= 60 and yardLine >= 56:
        return 3
    elif yardLine <= 55 and yardLine >= 51:
        return 4
    elif yardLine <= 50 and yardLine >= 46:
        return 5
    elif yardLine <= 45 and yardLine >= 41:
        return 6
    elif yardLine <= 40 and yardLine >= 36:
        return 7
    elif yardLine <= 35 and yardLine >= 31:
        return 8
    elif yardLine <= 30 and yardLine >= 26:
        return 9
    elif yardLine <= 25 and yardLine >= 21:
        return 10
    elif yardLine <= 20 and yardLine >= 15:
        return 11
    elif yardLine <= 15 and yardLine >= 11:
        return 12
    elif yardLine <= 10 and yardLine >= 6:
        return 13
    elif yardLine <= 5 and yardLine >= 1:
        return 14
    else:
        return -1

"""
Get the row that the result is in the spreadsheet

"""
def getPuntResultRow(message, difference): 
    gameInfo = getGameInfo(message.channel)
    yardLine = convertYardLine(gameInfo)
    
    fieldPositionColumnNum = getFieldPositionColumnNum(yardLine)

    fieldPositionColumn = []
    resultsColumn = []
    resultRow = 0

    for i in range(puntRanges.nrows):
        fieldPositionColumn.append(puntRanges.cell_value(i, fieldPositionColumnNum))
        resultsColumn.append(puntRanges.cell_value(i, 0))
        
    # Iterate through each row in the column and fine what bucket the difference falls into
    for i in range(4, len(fieldPositionColumn)):
        if "-" in str(fieldPositionColumn[i]):
            minNum = int(fieldPositionColumn[i].split("-")[0])
            maxNum = int(fieldPositionColumn[i].split("-")[1])
            if difference >= minNum and difference <= maxNum:
                resultRow = i
                break
        elif "-" not in str(fieldPositionColumn[i]) and "N/A" not in str(fieldPositionColumn[i]):
            if fieldPositionColumn[i] == difference:
                resultRow = i
                break
                
    return resultRow       
    

#########################
#        KICKOFFS       #
#########################

    
"""
Get the matchup's normal kickoff result and time

"""
def getNormalKickoffResultRow(difference):  
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
Get the normal kickoff time 

"""   
def getNormalKickoffTime(row):
    timeColumn = []
    for i in range(kickoffPATRanges.nrows):
        timeColumn.append(kickoffPATRanges.cell_value(i, 3))
    return timeColumn[row]

"""
Get the normal kickoff result

"""
def getNormalKickoffResult(row):
    resultColumn = []
    for i in range(kickoffPATRanges.nrows):
        resultColumn.append(kickoffPATRanges.cell_value(i, 0))
    return resultColumn[row]

"""
Get the matchup's squib kickoff result and time

"""
def getSquibKickoffResultRow(difference):  
    differencesColumn = []
    resultsColumn = []
    resultRow = 0

    for i in range(kickoffPATRanges.nrows):
        differencesColumn.append(kickoffPATRanges.cell_value(i, 4))
        resultsColumn.append(kickoffPATRanges.cell_value(i, 3))
        
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
Get the squib kickoff time 

"""   
def getSquibKickoffTime(row):
    timeColumn = []
    for i in range(kickoffPATRanges.nrows):
        timeColumn.append(kickoffPATRanges.cell_value(i, 5))
    return timeColumn[row]

"""
Get the squib kickoff result

"""
def getSquibKickoffResult(row):
    resultColumn = []
    for i in range(kickoffPATRanges.nrows):
        resultColumn.append(kickoffPATRanges.cell_value(i, 3))
    return resultColumn[row]

"""
Get the matchup's onside kickoff result and time

"""
def getOnsideKickoffResultRow(difference):  
    differencesColumn = []
    resultsColumn = []
    resultRow = 0

    for i in range(kickoffPATRanges.nrows):
        differencesColumn.append(kickoffPATRanges.cell_value(i, 7))
        resultsColumn.append(kickoffPATRanges.cell_value(i, 6))
        
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
Get the onside kickoff time 

"""   
def getOnsideKickoffTime(row):
    timeColumn = []
    for i in range(kickoffPATRanges.nrows):
        timeColumn.append(kickoffPATRanges.cell_value(i, 8))
    return timeColumn[row]

"""
Get the onside kickoff result

"""
def getOnsideKickoffResult(row):
    resultColumn = []
    for i in range(kickoffPATRanges.nrows):
        resultColumn.append(kickoffPATRanges.cell_value(i, 6))
    return resultColumn[row]
   
"""
Get and return the kickoff result

"""
def getFinalKickoffResult(playType, difference):
    if(playType.lower() == "normal"):
        resultRow = getNormalKickoffResultRow(difference)
        result = getNormalKickoffResult(resultRow)
        time = getNormalKickoffTime(resultRow)
    elif(playType.lower() == "squib"):
        resultRow = getSquibKickoffResultRow(difference)
        result = getSquibKickoffResult(resultRow)
        time = getSquibKickoffTime(resultRow)
    elif(playType.lower() == "onside"):
        resultRow = getOnsideKickoffResultRow(difference)
        result = getOnsideKickoffResult(resultRow)
        time = getOnsideKickoffTime(resultRow)
    if representsInt(result):
        result = int(result)
    return {0: result, 1: time} 
