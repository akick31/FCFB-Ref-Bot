import discord
import random

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 26 19:35:49 2020

@author: apkick
"""

def coinToss(homeUser, awayUser, message):
    result = random.randint(1, 2)
    if("head" in message.content):
        if result == 1:
            return "heads, away wins"
        else:
            return "tails, home wins"
    else:
        if result == 1:
            return "heads, home wins"
        else:
            return "tails, away wins"
    return "Invalid"
