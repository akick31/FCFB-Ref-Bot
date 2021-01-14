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


"""
Functions that handle getting and updating information in the ranges database

@author: apkick
"""

#########################
#      NORMAL PLAY      #
#########################
def getResult(row):
    """
    Get the normal play result from the ranges sheet
    
    """
    
    resultColumn = []
    for i in range(ranges.nrows):
        resultColumn.append(ranges.cell_value(i, 0))
    return resultColumn[row]


def getTime(row):
    """
    Get the normal play time from the ranges sheet
    
    """
    
    timeColumn = []
    for i in range(ranges.nrows):
        timeColumn.append(ranges.cell_value(i, 26))
    return timeColumn[row]


def getMatchupColumnNum(offensivePlaybook, defensivePlaybook, playType):
    """
    Go through all the possible playbook matchups and return the column that the matchup 
    is in on the ranges spreadsheet
    
    """

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
    

def getPlayResultRow(matchupColumnNum, difference):  
    """
    Get the row that the normal play result is on in the ranges sheet
    
    """
    
    matchupColumn = []
    resultsColumn = []
    resultRow = 0

    for i in range(ranges.nrows):
        matchupColumn.append(ranges.cell_value(i, matchupColumnNum))
        resultsColumn.append(ranges.cell_value(i, 0))
        
    # Iterate through each row in the column and find what bucket the difference falls into
    for i in range(4, len(matchupColumn)):
        if "-" in str(matchupColumn[i]):
            minNum = int(matchupColumn[i].split("-")[0])
            maxNum = int(matchupColumn[i].split("-")[1])
            if minNum <= difference <= maxNum:
                resultRow = i
                break
        elif "-" not in str(matchupColumn[i]) and "N/A" not in str(matchupColumn[i]):
            if matchupColumn[i] == difference:
                resultRow = i
                break
    if resultRow == 0:
        print("Could not find the row in the range sheet that the result was")
    return resultRow          
  
           
def getFinalPlayResult(message, offensivePlaybook, defensivePlaybook, playType, difference, clockRunoffType, clockStopped):
    """
    Get a normal play's result and return it
    
    """
    
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
        if matchupColumnNum != -69:
            resultRow = getPlayResultRow(matchupColumnNum, difference)
            result = getResult(resultRow)

            if representsInt(result) is False:
                if str(result) == "Incompletion":
                    updateClockStopped(message.channel, "YES")

            time = getTime(resultRow)
            return {0: result, 1: int(time) + clockRunoff} 
        else:
            return {0: "DID NOT FIND PLAY", 1: "DID NOT FIND TIME"} 
        
    elif playType == "field goal":
        result = getFGResult(message, difference)
        
        if str(result) != "Kick 6":
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
    """
    Get the field goal result from the ranges sheet and return it
    
    """
    
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
    
    # Iterate through each row in the column and find what bucket the distance falls into
    for i in range(4, len(distanceColumn)):
        if fieldGoalDistance == distanceColumn[i]:
            minNum = int(madeColumn[i].split("-")[0])
            maxNum = int(madeColumn[i].split("-")[1])
            if minNum <= difference <= maxNum:
                return "Made"
            if "-" in str(missColumn[i]):
                minNum = int(madeColumn[i].split("-")[0])
                maxNum = int(madeColumn[i].split("-")[1])
                if minNum <= difference <= maxNum:
                    return "Miss"
            if "-" in str(blockedColumn[i]):
                minNum = int(blockedColumn[i].split("-")[0])
                maxNum = int(blockedColumn[i].split("-")[1])
                if minNum <= difference <= maxNum:
                    return "Blocked"
            if "-" in str(kickSixColumn[i]):
                minNum = int(kickSixColumn[i].split("-")[0])
                maxNum = int(kickSixColumn[i].split("-")[1])
                if minNum <= difference <= maxNum:
                    return "Kick 6"
        else:
            return "Miss"
        
    

#########################
#        PUNTS          #
#########################
def getPuntResult(row):
    """
    Get the punt result from the ranges sheet
    
    """
    
    resultColumn = []
    for i in range(puntRanges.nrows):
        resultColumn.append(puntRanges.cell_value(i, 0))
    return resultColumn[row]


def getFieldPositionColumnNum(yardLine):
    """
    Get the bucket that the field position is in
    
    """
    
    if 100 >= yardLine >= 71:
        return 1
    elif 70 >= yardLine >= 66:
        return 2
    elif 65 >= yardLine >= 61:
        return 3
    elif 60 >= yardLine >= 56:
        return 4
    elif 55 >= yardLine >= 51:
        return 5
    elif 50 >= yardLine >= 46:
        return 6
    elif 45 >= yardLine >= 41:
        return 7
    elif 40 >= yardLine >= 36:
        return 8
    elif 35 >= yardLine >= 31:
        return 9
    elif 30 >= yardLine >= 26:
        return 10
    elif 25 >= yardLine >= 21:
        return 11
    elif 20 >= yardLine >= 16:
        return 12
    elif 15 >= yardLine >= 11:
        return 13
    elif 10 >= yardLine >= 6:
        return 14
    elif 5 >= yardLine >= 1:
        return 14
    else:
        return -1


def getPuntResultRow(message, difference): 
    """
    Get the row that the punt result is on in the ranges sheet
    
    """
    
    gameInfo = getGameInfo(message.channel)
    yardLine = convertYardLine(gameInfo)
    
    fieldPositionColumnNum = getFieldPositionColumnNum(yardLine)

    fieldPositionColumn = []
    resultsColumn = []
    resultRow = 0

    for i in range(puntRanges.nrows):
        fieldPositionColumn.append(puntRanges.cell_value(i, fieldPositionColumnNum))
        resultsColumn.append(puntRanges.cell_value(i, 0))
        
    # Iterate through each row in the column and find what bucket the difference falls into
    for i in range(3, len(fieldPositionColumn)):
        if "-" in str(fieldPositionColumn[i]):
            minNum = int(fieldPositionColumn[i].split("-")[0])
            maxNum = int(fieldPositionColumn[i].split("-")[1])
            if minNum <= difference <= maxNum:
                resultRow = i
                break
        elif "-" not in str(fieldPositionColumn[i]) and "N/A" not in str(fieldPositionColumn[i]):
            if fieldPositionColumn[i] == difference:
                resultRow = i
                break
    if resultRow == 0:
        print("Could not find the row in the range sheet that the result was")
    return resultRow       
    

#########################
#        KICKOFFS       #
#########################
def getNormalKickoffResultRow(difference): 
    """
    Get the row that the normal kickoff result is on in the ranges sheet
    
    """
    
    differencesColumn = []
    resultsColumn = []
    resultRow = 0

    for i in range(kickoffPATRanges.nrows):
        differencesColumn.append(kickoffPATRanges.cell_value(i, 1))
        resultsColumn.append(kickoffPATRanges.cell_value(i, 0))
        
    # Iterate through each row in the column and find what bucket the difference falls into
    for i in range(7, len(differencesColumn)):
        if "-" in str(differencesColumn[i]):
            minNum = int(differencesColumn[i].split("-")[0])
            maxNum = int(differencesColumn[i].split("-")[1])
            if minNum <= difference <= maxNum:
                resultRow = i
                break
        elif "-" not in str(differencesColumn[i]) and "N/A" not in str(differencesColumn[i]):
            if differencesColumn[i] == difference:
                resultRow = i
                break

    if resultRow == 0:
        print("Could not find the row in the range sheet that the result was")
    return resultRow  
  

def getNormalKickoffTime(row):
    """
    Get the normal kickoff time from the ranges sheet
    
    """
    
    timeColumn = []
    for i in range(kickoffPATRanges.nrows):
        timeColumn.append(kickoffPATRanges.cell_value(i, 2))
    return timeColumn[row]


def getNormalKickoffResult(row):
    """
    Get the normal kickoff result from the ranges sheet
    
    """
    
    resultColumn = []
    for i in range(kickoffPATRanges.nrows):
        resultColumn.append(kickoffPATRanges.cell_value(i, 0))
    return resultColumn[row]


def getSquibKickoffResultRow(difference):
    """
    Get the row that the squib kickoff result is on in the ranges sheet
    
    """
    
    differencesColumn = []
    resultsColumn = []
    resultRow = 0

    for i in range(kickoffPATRanges.nrows):
        differencesColumn.append(kickoffPATRanges.cell_value(i, 4))
        resultsColumn.append(kickoffPATRanges.cell_value(i, 3))
        
    # Iterate through each row in the column and find what bucket the difference falls into
    for i in range(7, len(differencesColumn)):
        if "-" in str(differencesColumn[i]):
            minNum = int(differencesColumn[i].split("-")[0])
            maxNum = int(differencesColumn[i].split("-")[1])
            if minNum <= difference <= maxNum:
                resultRow = i
                break
        elif "-" not in str(differencesColumn[i]) and "N/A" not in str(differencesColumn[i]):
            if differencesColumn[i] == difference:
                resultRow = i
                break
                
    return resultRow  
  

def getSquibKickoffTime(row):
    """
    Get the squib kickoff time from the ranges sheet
    
    """
    
    timeColumn = []
    for i in range(kickoffPATRanges.nrows):
        timeColumn.append(kickoffPATRanges.cell_value(i, 5))
    return timeColumn[row]


def getSquibKickoffResult(row):
    """
    Get the squib kickoff result from the ranges sheet
    
    """
    
    resultColumn = []
    for i in range(kickoffPATRanges.nrows):
        resultColumn.append(kickoffPATRanges.cell_value(i, 3))
    return resultColumn[row]


def getOnsideKickoffResultRow(difference):  
    """
    Get the row that the onside kickoff result is on in the ranges sheet
    
    """
    
    differencesColumn = []
    resultsColumn = []
    resultRow = 0

    for i in range(kickoffPATRanges.nrows):
        differencesColumn.append(kickoffPATRanges.cell_value(i, 7))
        resultsColumn.append(kickoffPATRanges.cell_value(i, 6))
        
    # Iterate through each row in the column and find what bucket the difference falls into
    for i in range(7, len(differencesColumn)):
        if "-" in str(differencesColumn[i]):
            minNum = int(differencesColumn[i].split("-")[0])
            maxNum = int(differencesColumn[i].split("-")[1])
            if minNum <= difference <= maxNum:
                resultRow = i
                break
        elif "-" not in str(differencesColumn[i]) and "N/A" not in str(differencesColumn[i]):
            if differencesColumn[i] == difference:
                resultRow = i
                break
                
    return resultRow  
  

def getOnsideKickoffTime(row):
    """
    Get the onside kickoff time from the ranges sheet
    
    """
    
    timeColumn = []
    for i in range(kickoffPATRanges.nrows):
        timeColumn.append(kickoffPATRanges.cell_value(i, 8))
    return timeColumn[row]


def getOnsideKickoffResult(row):
    """
    Get the onside kickoff result from the ranges sheet
    
    """

    resultColumn = []
    for i in range(kickoffPATRanges.nrows):
        resultColumn.append(kickoffPATRanges.cell_value(i, 6))
    return resultColumn[row]
   

def getFinalKickoffResult(playType, difference):
    """
    Get and return the kickoff result
    
    """

    if playType.lower() == "normal":
        resultRow = getNormalKickoffResultRow(difference)
        result = getNormalKickoffResult(resultRow)
        time = getNormalKickoffTime(resultRow)
    elif playType.lower() == "squib":
        resultRow = getSquibKickoffResultRow(difference)
        result = getSquibKickoffResult(resultRow)
        time = getSquibKickoffTime(resultRow)
    elif playType.lower() == "onside":
        resultRow = getOnsideKickoffResultRow(difference)
        result = getOnsideKickoffResult(resultRow)
        time = getOnsideKickoffTime(resultRow)
    else:
        return
    if representsInt(result):
        result = int(result)
    return {0: result, 1: time} 


def getFinalPointAfterResult(playType, difference):
    """
    Get and return the point after attempt/two point result
    
    """

    if playType.lower() == "pat":
        if 0 <= difference <= 720:
            return {0: "Good", 1: 0}
        elif 721 <= difference <= 747:
            return {0: "No Good", 1: 0}
        elif 748 <= difference <= 750:
            return {0: "Defense 2PT", 1: 0}
    elif playType.lower() == "two point":
        if 0 <= difference <= 300:
            return {0: "Good", 1: 0}
        elif 301 <= difference <= 747:
            return {0: "No Good", 1: 0}
        elif 748 <= difference <= 750:
            return {0: "Defense 2PT", 1: 0}
