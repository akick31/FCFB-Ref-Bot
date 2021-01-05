import jsonfrom datetime import datetimefrom github import Githubfrom game_database_functions import updateGistwith open('FCFB-Ref-Bot/config.json') as f:    data = json.load(f)githubToken = json.loads(data)["githubToken"]githubLogRepo = json.loads(data)["logRepository"]g = Github(githubToken)repo = g.get_repo(githubLogRepo)async def createLogFile(channel, homeTeam, awayTeam):    """    Create the log file and push it to GitHub    """        content = (homeTeam + " vs " + awayTeam + " on " + datetime.today().strftime('%Y-%m-%d') + " || GAME STARTED\n"            + "============================================================\n"            + "============================================================\n"            + "Home score|Away score|Quarter|Clock|Ball Location|Possession|Down|Yards to go|Defensive Submitter|Offensive Submitter|Defensive number|Offensive number|Play|Result|Yards|Play time\n")    year = datetime.today().strftime('%Y-%m-%d').split("-")[0]    month = datetime.today().strftime('%Y-%m-%d').split("-")[1]    day = datetime.today().strftime('%Y-%m-%d').split("-")[2]    fileName = str(year) + "/" + str(month) + "/" + str(day) + "/" + str(homeTeam) + "-vs-" + str(awayTeam) + "-" + str(channel.id)    updateGist(channel, fileName)    repo.create_file(fileName, "Create game " + str(channel.id), content)    def getLogFile(fileName):    """    Get the log file from GitHub    """        logFile = repo.get_contents(fileName)    return logFiledef getLogFileURL(fileName):    """    Get the raw url from GitHub    """        logFile = repo.get_contents(fileName)    return logFile.download_urlasync def updateLogFile(message, logFile, gameInfo, play, result, yards, playTime):    """    Update the log file on GitHub    """        homeScore = str(gameInfo["home score"])    awayScore = str(gameInfo["away score"])    quarter = str(gameInfo["quarter"])    clock = str(gameInfo["time"])    ballLocation = str(gameInfo["yard line"])    possession = str(gameInfo["possession"])    down = str(gameInfo["down"])    yardsToGo = str(gameInfo["distance"])    if gameInfo["possession"] == gameInfo["home name"]:        defensiveSubmitter = str(gameInfo["away name"])        offensiveSubmitter = str(gameInfo["home name"])    elif gameInfo["possession"] == gameInfo["away name"]:        defensiveSubmitter = str(gameInfo["home name"])        offensiveSubmitter = str(gameInfo["away name"])    else:        return    defensiveNumber = str(gameInfo["defensive number"])    offensiveNumber = str(gameInfo["offensive number"])        infoString = (homeScore + "|" + awayScore + "|" + quarter + "|" + clock + "|" + ballLocation + "|" +                  possession + "|" + down + "|" + yardsToGo + "|" + defensiveSubmitter + "|" + offensiveSubmitter + "|" +                   defensiveNumber + "|" + offensiveNumber + "|" + play + "|" + str(result) + "|" + str(yards) + "|" + str(playTime) + "\n")        oldContent = str(logFile.decoded_content, 'utf-8')    updatedContents = str(oldContent) + infoString    repo.update_file(logFile.path, "Update game " + str(message.channel.id), updatedContents, logFile.sha)