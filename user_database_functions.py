import xlrd

userWorkbook = xlrd.open_workbook(r'user_database.xlsx')
userDB = userWorkbook.sheet_by_index(0)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 26 15:26:11 2020

@author: apkick
"""

def getNickname(team):
    for i in range(userDB.nrows):
        if userDB.cell_value(i, 0) == team:
            return userDB.cell_value(i, 1)
    return "COULD NOT FIND"

def getUser(team):
    for i in range(userDB.nrows):
        if userDB.cell_value(i, 0) == team:
            return userDB.cell_value(i, 3)
    return "COULD NOT FIND"

def getOffensivePlaybook(team):
    for i in range(userDB.nrows):
        if userDB.cell_value(i, 0) == team:
            return userDB.cell_value(i, 5)
    return "COULD NOT FIND"

def getDefensivePlaybook(team):
    for i in range(userDB.nrows):
        if userDB.cell_value(i, 0) == team:
            return userDB.cell_value(i, 6)
    return "COULD NOT FIND"

def getRecord(team):
    for i in range(userDB.nrows):
        if userDB.cell_value(i, 0) == team:
            return userDB.cell_value(i, 7)
    return "COULD NOT FIND"

