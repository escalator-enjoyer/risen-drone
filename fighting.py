#                            ▒▒████                              
#                            ████████                            
#                          ██████████                            
#                          ████▒▒██████                          
#                        ██████    ████▒▒                        
#                        ████      ▒▒████                        
#                      ██████        ██████                      
#                    ▒▒████    ████    ████                      
#                    ████▒▒  ████████  ██████                    
#                  ██████    ████████    ████                    
#                  ████░░    ████████    ██████                  
#                ██████      ████████      ████▒▒                
#              ░░████        ████████      ▒▒████                
#              ██████        ████████        ██████              
#            ▒▒████          ████████          ████              
#            ████▒▒          ██████▒▒          ██████            
#          ██████              ████              ████            
#          ████                ████              ██████          
#        ██████                ████                ████▒▒        
#      ░░████                                      ▒▒████        
#      ████▓▓                                        ██████      
#    ▒▒████                    ████                    ████      
#    ████▒▒                  ████████                  ██████    
#  ██████                      ▒▒▒▒                      ████░░  
#  ████          work in progress                          ████░░
#██████  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  ░░░░░░░░░░░░░░░░▒▒██████
#████████████████████████████████████████████████████████████████
#▓▓████████████████████████████████████████████████████████████▓▓

import random
import time
import asyncio

from globals import *
from rated import *

#gets the dictionary but this one will change
CURRENT_CLASSES = FG_CLASSES

#default stats
NEW_PLAYER = {
    "class": None,
    "hp": 200,
    "dmg": 100,
    "charges": None
}

#pre-attack checks
TICK = ["poison", "h. poison"]
AVOID = ["dodge"]

#players with modified stats
GOOD_STATUSES = {}   #usr:             [0]status,    [1]stat,     [2]buff/debuff,  [3]damage/amount,  [4]turns
BAD_STATUSES = {}    #usr:             [0]status,    [1]stat,     [2]buff/debuff,  [3]damage/amount,  [4]turns
STATUSES_EXAMPLES = {"roibrari#2287": ["poison",     None,        None,            15,                2],
                    "sleazel#0820":   ["h. poison",  "accuracy",  "debuff",        15,                2],
                    "frfr#0431":      ["shield",     None,        None,            50,                3],
                    "cashier#6099":   [None,         "damage",    "buff",          30,                2],
                    }

def FG_RESET():
    FG_PLAYERS.clear()
    FG_QUEUE.clear()
    FG['status'] = "off"
    FG['currentPlayer'] = 0
    FG['tick'] = 0
    FG["class-picked"] = 0
    FG["channel"] = None

def FG_NEXT_PLAYER():
    FG['currentPlayer'] += 1
    if FG['currentPlayer'] > len(FG_QUEUE) - 1:
        FG['currentPlayer'] = 0
        

async def FG_LOOP(toSend):
    FG['tick'] = time.time()
    ourTick = FG['tick']
    
    while True:   
        toSend = "It's **" + FG_QUEUE[FG['currentPlayer']].name + "**'s time to shine! Select a skill to use against your opponent."
        await SEND(FG['channel'], toSend)
        
        await asyncio.sleep(60)
        
        if FG['tick'] != ourTick:
            return
        
        cp = MG_QUEUE[FG['currentPlayer']]
        return
    

async def FightingProcessClass(usr, msg):
    lmsg = msg.lower()
        
    if FG['status'] == "class-picking":

        print(FG_PLAYERS)

        if lmsg in SANCTUARY.keys() and lmsg not in FG_CLASSES.keys():
            await SEND(FG["channel"], "The selected Alignment has not made it into the fighting scene yet, sadly.") 
            return

        if lmsg not in SANCTUARY.keys() and lmsg not in FG_CLASSES.keys():
            await SEND(FG["channel"], "I gave you a list. Read it and answer accordingly!") 
            return

        if FG_PLAYERS[usr]["class"] != None:
            await SEND(FG["channel"], "No takes-back.") 
            return

        FG_PLAYERS[usr]["class"] = lmsg
        print(FG_PLAYERS[usr]["class"])
        await SEND(FG["channel"], f"{usr.mention} is playing as {lmsg.capitalize()}.")

        FG["class-picked"] += 1

        if FG["class-picked"] == 2:
            await asyncio.sleep(2)
            FG['status'] = "battling"
            toSend = "Everyone is now ready. Here are your picks:\n\n"

            for user in FG_PLAYERS:
                toSend += f"{user.name} will be playing as {str(FG_PLAYERS[user][0]).capitalize()}.\n"
            
            toSend += "\nLet's begin."

            await SEND(FG["channel"], toSend)

            ShowSkills()

        return
    
    elif LADDERS['status'] == "battling" and lmsg in MG_SPELLS and MG_QUEUE[FG['currentPlayer']] == usr:
        spell = lmsg
        while spell == "chameleon":
            spell = random.choice(MG_SPELLS)
        FG_NEXT_PLAYER()
        await FG_LOOP(FG_ACTION(usr,spell))


async def PlayFightingGame(usr, ch):
    if FG['status'] != "off":
        await SEND(ch, "A match is already in progress.")
        return
    else:
        FG['channel'] = ch
        FG['status'] = "second-player"
        FG_PLAYERS[usr] = NEW_PLAYER
        FG_QUEUE.append(usr)
        FG['currentPlayer'] = 0
        FG['tick'] = time.time()
        ourTick = FG['tick']

        await SEND(ch, f"{usr.mention} has decided they do not like guns anymore and wants to start a fight! Type 'join fight' to battle! (BETA)")
        await asyncio.sleep(60)

        if FG['status'] == "second-player" and ourTick == FG['tick']:
            await SEND(ch, "Nobody will fight for now.")
            FG_RESET()
        return


async def JoinFightingGame(usr):
    if usr in FG_PLAYERS:
        await SEND(FG['channel'], "Wait for someone else.")
        return
    else:
        FG_PLAYERS[usr] = NEW_PLAYER
        FG_QUEUE.append(usr)
        await SEND(FG["channel"], f"{usr.mention} is eager to fight too.\n")

        await asyncio.sleep(2)
        await SEND(FG["channel"], ClassShowcase())
        FG['status'] = "class-picking"

        await asyncio.sleep(30)

        for user in FG_PLAYERS:
            if FG_PLAYERS[user]["class"] == None:
                await SEND(FG["channel"], "One or more users have not selected an Alignment in the given time. Fight is cancelled.")
                FG_RESET()
                break
        return


def ClassShowcase():
    toSend = "You may now pick your Alignment. Select between:\n\n"

    for alignment in FG_CLASSES.keys():
        toSend += f"`{str(alignment.capitalize())}`\n" 
        
    return toSend

def ShowSkills():
    usr = MG_QUEUE[LADDERS['currentPlayer']]
    usrClass = FG_PLAYERS[usr][0]

