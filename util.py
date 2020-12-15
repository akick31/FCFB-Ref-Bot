
"""
Created on Wed May 13 19:38:06 2020

@author: apkick
"""

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
Calculate the difference

"""     
def calculateDifference(offense, defense):
    if representsInt(str(offense)) and representsInt(str(defense)):
        offense = int(offense)
        defense = int(defense)
        difference = abs(offense-defense)
        if difference > 750:
            return 1500-difference
        else:
            return difference      
    else:
        return -1