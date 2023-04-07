import random
import time
import asyncio

from globals import *
from rated import *

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


async def FightingProcessClass(usr, msg):
    lmsg = msg.lower()
        
    if FG['status'] == "class-picking":

        if lmsg in SANCTUARY.keys() and lmsg not in FG_CLASSES.keys():
            await SEND(FG["channel"], "The selected Alignment has not made it into the fighting scene yet, sadly.") 
            return

        if lmsg not in SANCTUARY.keys() and lmsg not in FG_CLASSES.keys():
            await SEND(FG["channel"], "I gave you a list. Read it and answer accordingly!") 
            return

        if FG_PLAYERS[usr][0] != None:
            await SEND(FG["channel"], "No takes-back.") 
            return

        FG_PLAYERS[usr] = [lmsg, None, 70] # class, status, accuracy
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
        return


async def PlayFightingGame(usr, ch):
    if FG['status'] != "off":
        await SEND(ch, "A match is already in progress.")
        return
    else:
        FG['channel'] = ch
        FG['status'] = "second-player"
        FG_PLAYERS[usr] = [None, None, 70] #class, status, accuracy
        FG_QUEUE.append(usr)
        FG['currentPlayer'] = 0
        FG['tick'] = time.time()
        ourTick = FG['tick']
        await SEND(ch, f"{usr.mention} has decided they do not like guns anymore and wants to fight! Type 'join fight' to battle!")
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
        FG_PLAYERS[usr] = [None, None, 70] #class, status, accuracy
        FG_QUEUE.append(usr)
        await SEND(FG["channel"], f"{usr.mention} is eager to fight too.\n")
        await asyncio.sleep(2)
        await SEND(FG["channel"], ClassShowcase())
        FG['status'] = "class-picking"

        await asyncio.sleep(30)
        for user in FG_PLAYERS:
            if FG_PLAYERS[user][0] == None:
                await SEND(FG["channel"], "One or more users have not selected an Alignment in the given time. Fight is cancelled.")
                FG_RESET()
                break
        return


def ClassShowcase():
    toSend = "You may now pick your Alignment. Select between:\n\n"

    for alignment in FG_CLASSES.keys():
        toSend += f"`{str(alignment.capitalize())}`\n" 
        
    return toSend

