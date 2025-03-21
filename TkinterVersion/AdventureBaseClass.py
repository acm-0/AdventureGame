
import json
import copy
import sys
from os import system
from os.path import exists
from click import getchar

class AdventureBaseClass :

    useSound = False
    soundsDir = "./sounds/"
    if sys.argv[0].rfind("/") != -1 :
        soundsDir = sys.argv[0][0:sys.argv[0].rfind("/")]+"/sounds/"
    print(f'soundsDir={soundsDir}')

    jsonFile = "adventure.json"
    if len(sys.argv) > 1 :
        jsonFile = sys.argv[1]

    if exists(jsonFile) :
        with open(jsonFile, 'r') as openfile:
            # Reading from json file
            adventureDict = json.load(openfile)
    else :
        print(f'Adventure file "{jsonFile}" does not exist.  Make sure adventure.json is in the current directory')
        print("or specify the path to the adventure file on the command line")
        exit()
                  
    @classmethod
    def UseSound(cls,tf) :
        if tf :
            cls.useSound = True
            from playsound import playsound
        else :
            cls.useSound = False
        
    @classmethod
    def Quit(cls):
        quitStr = input("Type 'q' again if you really want to quit: ")
        if quitStr.lower() == "q":
            print("Goodbye")
            exit()
        print()

    @classmethod
    def Look(cls):
        return True

    @classmethod
    def UpdateNumber(cls,alpha,increment):
        return str(int(alpha)+increment)

    @classmethod
    def Help(cls):
        print("In general commands are of three forms:")
        print("  1. movement")
        print("  2. <action> <object>, for example 'take sword'")
        print("  3. use <object> on <another object>, for example 'use key on door'")
        print("For actions for which there is no specific command in the list below, try the 'use' option")
        print()
        print("Inventory shows you what you are carrying")
        print("Look gives you a description of the room")
        print()
        print("Here is a list of all possible commands:")
        commandsDict = cls.getCommandsDict()
        for command in commandsDict.keys() :
            if type(commandsDict[command]) is not list :
                print(f', shortcut: {command}',end="")
            else :
                print()
                print(command,end="")
        print("\n")
        print("Hit any key to continue ",end="",flush=True)
        getchar()
        return True

    @classmethod
    def GetAllItems(cls):
        itemList = list()
        for item in cls.adventureDict['objects'].keys() :
            itemList.append(item)
        return itemList

    @classmethod
    def FindItemsInLocation(cls,location):
        itemList = list()
        for item in cls.adventureDict['objects'].keys() :
            if cls.adventureDict['objects'][item]['location'] == location :
                itemList.append(item)
        return itemList

    @classmethod
    def GetParticle(cls,item) :
        if cls.GetPlurality(item) == "are" :
            return ""
        elif item[0] in "aeiou" :
            particle = "an "
        else :
            particle = "a "
        return particle

    @classmethod
    def GetPlurality(cls,item) :
        if item[-1] == "s" and item[-2] != "s" :
            return "are"
        else :
            return "is"
        

    @classmethod
    def ShowItemsHere(cls,mylocation) :
        itemsHere = cls.FindItemsInLocation(mylocation)
        for item in itemsHere :
            skip = False
            if "visibility" in cls.adventureDict['objects'][item].keys() :
                if cls.adventureDict['objects'][item]['visibility'] == "hidden" :
                    skip = True
            if not skip : 
                print(f'There {cls.GetPlurality(item)} {cls.GetParticle(item)}{item} here',end=".")
                if "state" in cls.adventureDict['objects'][item].keys() :
                    print(f"  The {item} {cls.GetPlurality(item)} {cls.adventureDict['objects'][item]['state']}")
                else :
                    print()

    @classmethod
    def GetItemsHere(cls,mylocation) :
        itemsHere = cls.FindItemsInLocation(mylocation)
        itemlist = []
        for item in itemsHere :
            skip = False
            if "visibility" in cls.adventureDict['objects'][item].keys() :
                if cls.adventureDict['objects'][item]['visibility'] == "hidden" :
                    skip = True
            if not skip : 
                mystr = f"There {cls.GetPlurality(item)} {cls.GetParticle(item)}{item} here."
                if "state" in cls.adventureDict['objects'][item].keys() :
                    mystr += f"  The {item} {cls.GetPlurality(item)} {cls.adventureDict['objects'][item]['state']}"
                itemlist.append(mystr)
        return itemlist

    @classmethod
    def GetInventory(cls) :
        inventory = cls.FindItemsInLocation("inventory")
        itemlist = []
        if inventory == []:
            itemlist.append("<you are not carrying any items>")
        else:
            mystr = item
            if "state" in cls.adventureDict['objects'][item].keys() :
                mystr += f" - the {item} {cls.GetPlurality(item)} {cls.adventureDict['objects'][item]['state']}"
            itemlist.append(mystr)
        return itemlist

    @classmethod
    def Inventory(cls) :
        itemsInInventory = cls.FindItemsInLocation("inventory")
        if len(itemsInInventory) == 0 :
            print("You are not carrying anything")
        else :
            print("You are carrying:")
            for item in itemsInInventory :
                print(f'{cls.GetParticle(item)}{item}')

# This is a recursive function to find and replace all the instances of 'arg1', 'arg2', etc in the condition tree of the
# function with specific words from the calling location, e.g. 'take,key' will replace all values of 'arg1'. whether they be
# keys or in a value text string, with 'key'
    @classmethod
    def SubSubArgs(cls,subroutineDict,substitutionArgs) :
        argCount = 1
        argLiterals = list()
# Create a list containging text: "arg1", "arg2" ... for as many args are provided in the calling location
        for item in substitutionArgs :
            argLiterals.append("arg"+str(argCount))
            argCount = argCount + 1
# If we are not down to a simple text string, search the keys for any occurrences of 'arg1', 'arg2', etc. and replace
# them with the arguments the function was called with.  Since you can't just rename a key, remove the existing key and
# add a new one with the proper name to the dictionary
        if type(subroutineDict) is dict :
            for arg in argLiterals :
                if arg in subroutineDict.keys() :
                    subroutineDict[substitutionArgs[argLiterals.index(arg)]] = subroutineDict.pop(arg)
# Here's where the recursiveness happens.  If the values at the current level of the dictionary are themselves
# dictionaries, perform this same function on the sub-dictionaries
        for val in subroutineDict.keys() :
            if type(subroutineDict[val]) is dict :
                subroutineDict[val] = cls.SubSubArgs(subroutineDict[val],substitutionArgs)
# Eventually we will get to a point where the value will be a simple text string.  In this case just replace any
# occurrences of 'arg1, 'arg2', etc with the appropriate text from the function call
            else :
                for arg in argLiterals :
                    subroutineDict[val] = subroutineDict[val].replace(arg,substitutionArgs[argLiterals.index(arg)])
        return subroutineDict

# This function walks down a tree of conditions and attributes that are specified in the adventure dictionary
# to find the outcome that matches the current state of these conditions and attributes
    @classmethod
    def ParseConditionTree(cls,conditionSubDict) :
        if type(conditionSubDict) is dict :
            while conditionSubDict.get('attributes') or conditionSubDict.get('conditions') or conditionSubDict.get('subroutine') : 
                if conditionSubDict.get('subroutine') :
                    subArgs = conditionSubDict['subroutine'].split(",")
                    subName = subArgs.pop(0)
# Below we are redirected to a subroutine in the adventure file.  The subroutine contains both keys and values that must be
# replaced with arguments from the calling location.  We don't want to update the master adventure dictionary, so we
# work on a copy of the subroutine
                    conditionSubDict = cls.SubSubArgs(copy.deepcopy(cls.adventureDict['subroutines'][subName]),subArgs)
                elif conditionSubDict.get('attributes') :
                    attribute = list(conditionSubDict['attributes'].keys())[0] # list() is needed to get the keys in the form of a list of words
                    state = cls.adventureDict['attributes'][attribute]['state']
                    if conditionSubDict['attributes'][attribute].get(state) :
                        conditionSubDict = conditionSubDict['attributes'][attribute][state]
                    elif conditionSubDict['attributes'][attribute].get('default') :
                        conditionSubDict = conditionSubDict['attributes'][attribute]['default']
                    else :
                        print(conditionSubDict)
                        print(f'Error - the state of attribute {attribute} is {state} but no action for this state is defined and there is no default')
                        exit()
                else :
                    object = list(conditionSubDict['conditions'].keys())[0]
                    property = list(conditionSubDict['conditions'][object].keys())[0]
                    value = cls.adventureDict['objects'][object][property]
                    if conditionSubDict['conditions'][object][property].get(value) :
                        conditionSubDict = conditionSubDict['conditions'][object][property][value]
                    elif conditionSubDict['conditions'][object][property].get('default') :
                        conditionSubDict = conditionSubDict['conditions'][object][property]['default']
                    else :
                        print(conditionSubDict)
                        print(f'Error - the {property} of {object} is {value} but no action for this value is defined and there is no default')
                        exit()
        return conditionSubDict

    @classmethod
    def UpdateAttributes(cls,attributeDict) :
        for attribute in attributeDict.keys() :
            possibleAttributeStates = cls.adventureDict['attributes'][attribute]['possible states'].split(",")
            if attributeDict[attribute] in possibleAttributeStates :
                cls.adventureDict['attributes'][attribute]['state'] = attributeDict[attribute]
            elif attributeDict[attribute] in cls.adventureDict['attributes'].keys():
                cls.adventureDict['attributes'][attribute]['state'] = cls.adventureDict['attributes'][attributeDict[attribute]]['state']
            else :
                print(f'Error, no such state as {attributeDict[attribute]} defined for {attribute}')
                exit()

    @classmethod
    def UpdateObjects(cls,objectDict) :
    #    print(objectDict)
        for object in objectDict.keys() :
    #        print(object)
            if object in cls.adventureDict['objects'].keys() :
                for objectProperty in objectDict[object].keys() :
    #                print(objectProperty)
                    if objectProperty in cls.adventureDict['objects'][object].keys() :
    # First check if the new value for the property is actually an attribute.  If it is, use the value of the attribute
    # as the new value of the propery.  Otherwise use the new value of the property directly                    
                        if cls.adventureDict['attributes'].get(objectDict[object][objectProperty]) :
                            cls.adventureDict['objects'][object][objectProperty] = cls.adventureDict['attributes'][objectDict[object][objectProperty]]['state']
                        else :
                            cls.adventureDict['objects'][object][objectProperty] = objectDict[object][objectProperty]
                    else :
                        print(f'Error, no such object property as {objectProperty} in object {object}')
                        exit()
            else :
                print(f'Error, no such object as {object}')
                exit()

    @classmethod
    def UseObjectOnObject(cls,action,object1,object2) :
        mylocation = cls.adventureDict['attributes']['mylocation']['state']
        if (cls.adventureDict['objects'][object1]['location'] != mylocation) and (cls.adventureDict['objects'][object1]['location'] != "inventory") :
            print(f'There {cls.GetPlurality(object1)} no {object1} here') # If there is such an object but it is not here nor in the inventory
            return False
        if (cls.adventureDict['objects'][object2]['location'] != mylocation) and (cls.adventureDict['objects'][object2]['location'] != "inventory") :
            print(f'There {cls.GetPlurality(object2)} no {object2} here') # If there is such an object but it is not here nor in the inventory
            return False
        if object1 not in cls.adventureDict['objects'][object2]['actions'] :
            print(f'You cannot use the {object1} on the {object2}')
            return False
        else :
            return cls.ActionOnObject(object1,object2)

    @classmethod
    def MoveCommand(cls,direction) :
        mylocation = cls.adventureDict['attributes']['mylocation']['state']
#        direction = cls.directionDict[commandStr.split()[0]]
        # Check that the desired direction is allowable from this room
        if direction in cls.adventureDict['rooms'][mylocation]['directions']:
            # Check if there are any conditions on the movement
            movementSubDict = cls.ParseConditionTree(cls.adventureDict['rooms'][mylocation]['directions'][direction])
            if cls.useSound and movementSubDict.get('transition sound'):
                playsound(cls.soundsDir+movementSubDict['transition sound']+".mp3",False)
            if movementSubDict.get('attribute change') :
                cls.UpdateAttributes(movementSubDict['attribute change'])
            if movementSubDict.get('object change') :
                cls.UpdateObjects(movementSubDict['object change'])
            if movementSubDict.get('custom function') :
                cls.CustomFuncDispatch(movementSubDict['custom function']['name'])
            if mylocation != cls.adventureDict['attributes']['mylocation']['state'] :
                system('clear')
                if movementSubDict.get('transition text') :
                    print(movementSubDict['transition text'])
                elif movementSubDict.get('transition textstring') :
                    print(cls.adventureDict["textstrings"][movementSubDict['transition textstring']])
                mylocation = cls.adventureDict['attributes']['mylocation']['state']
                if "number of visits" in cls.adventureDict['rooms'][mylocation] :
                    cls.adventureDict['rooms'][mylocation]['number of visits'] = cls.UpdateNumber(cls.adventureDict['rooms'][mylocation]['number of visits'],1)
#                    print(f"number of visits = {cls.adventureDict['rooms'][mylocation]['number of visits']}")
                return True # If as a result of the action we have moved to a different room, show the room description
            else :
                if movementSubDict.get('transition text'):
                    print(movementSubDict['transition text'])
                elif movementSubDict.get('transition textstring') :
                    print(cls.adventureDict["textstrings"][movementSubDict['transition textstring']])
                return False
        else: # The desired direction is not allowed from this room
            print("You can't go in that direction")
            return False

    @classmethod
    def ActionOnObject(cls,action,object):
        mylocation = cls.adventureDict['attributes']['mylocation']['state']
        if not cls.adventureDict['objects'].get(object) : # Check that there is such an object
            if action == "drop" :
                print(f'You are not carrying {cls.GetParticle(object)}{object}')
            else :
                print(f'There {cls.GetPlurality(object)} no {object} here')
        elif (cls.adventureDict['objects'][object]['location'] != mylocation) and (cls.adventureDict['objects'][object]['location'] != "inventory") :
            if action == "drop" :
                print(f'You are not carrying {cls.GetParticle(object)}{object}') # If there is such an object but it is not here nor in the inventory
            else:
                print(f'There {cls.GetPlurality(object)} no {object} here') # If there is such an object but it is not here nor in the inventory
        elif not cls.adventureDict['objects'][object]['actions'].get(action) :
            print(f'You cannot {action} the {object}') # If the requested action is not defined for this object
        else: # Valid action on valid object in valid location
            actionSubDict = cls.ParseConditionTree(cls.adventureDict['objects'][object]['actions'][action])
            if cls.useSound and actionSubDict.get('transition sound'):
                playsound(cls.soundsDir+actionSubDict['transition sound']+".mp3",False)
            if actionSubDict.get('transition text') :
                print(actionSubDict['transition text'])
            elif actionSubDict.get('transition textstring') :
                print(cls.adventureDict["textstrings"][actionSubDict['transition textstring']])
            if actionSubDict.get('attribute change') :
                cls.UpdateAttributes(actionSubDict['attribute change'])
            if actionSubDict.get('object change') :
                cls.UpdateObjects(actionSubDict['object change'])
            if actionSubDict.get('custom function') :
                cls.CustomFuncDispatch(actionSubDict['custom function']['name'])
        if mylocation != cls.adventureDict['attributes']['mylocation']['state'] :
            return True # If as a result of the action we have moved to a different room, show the room description
        else :
            return False

    @classmethod
    def getCommandsDict(cls) :
        commandsDict = {
            'north' : [cls.MoveCommand,1],
            'n' : 'north',
            'south' : [cls.MoveCommand,1],
            's' : 'south',
            'east' : [cls.MoveCommand,1],
            'e' : 'east',
            'west' : [cls.MoveCommand,1],
            'w' : 'west',
            'up' : [cls.MoveCommand,1],
            'u' : 'up',
            'down' : [cls.MoveCommand,1],
            'd' : 'down',
            'northeast' : [cls.MoveCommand,1],
            'ne' : 'northeast',
            'northwest' : [cls.MoveCommand,1],
            'nw' : 'northwest',
            'southeast' : [cls.MoveCommand,1],
            'se' : 'southeast',
            'southwest' : [cls.MoveCommand,1],
            'sw' : 'southwest',
            'use' : [cls.UseObjectOnObject,3],
            'read' : [cls.ActionOnObject,2],
            'wear' : [cls.ActionOnObject,2],
            'remove' : [cls.ActionOnObject,2],
            'take' : [cls.ActionOnObject,2],
            'drop' : [cls.ActionOnObject,2],
            'open' : [cls.ActionOnObject,2],
            'close' : [cls.ActionOnObject,2],
            'drink' : [cls.ActionOnObject,2],
            'eat' : [cls.ActionOnObject,2],
            'turn on' : [cls.ActionOnObject,2],
            'turn off' : [cls.ActionOnObject,2],
            'quit' : [cls.Quit,0],
            'q' : 'quit',
            'inventory' : [cls.Inventory,0],
            'i' : 'inventory',
            'look' : [cls.Look,0],
            'l' : 'look',
            'help' : [cls.Help,0],
            'h' : 'help'
        }
        return commandsDict

# This function checks whether the action specified on the command line matches an action in the commandsDict
# dictionary, and if it doesn't, tries to guess what action may have been meant.
    @classmethod
    def CheckAndCorrectAction(cls,actionWord) :
        commandsDict = cls.getCommandsDict()
        commandOK = False
        commandMaybeOK = False
        if actionWord in commandsDict : # If the action word is in the commands dictionary then we are done
            commandOK = True
            commandMaybeOK = True
        else : # Otherwise try to guess what action was meant
            if len(actionWord) == 1 : # A one-letter command, too short to guess
                return actionWord,None,0,False,False
            else :
                for guess in commandsDict :
                    if actionWord in guess : # if the command letters were a subset of the actual command
                        actionWord = guess   # then this is our guess
                        commandMaybeOK = True
                        break
                if not commandMaybeOK : # If a guess was not found in loop above
                    bestScore = 0
                    for guess in commandsDict : # check for matching letters, see equivalent comment text
                        score = 0               # in CheckAndCorrectObject below
                        if abs(len(guess) - len(actionWord)) <= 2 :
                            for letter in actionWord :
                                if letter in guess :
                                    score = score + 1
                                    if guess.index(letter) == actionWord.index(letter) :
                                        score = score + 1
                            if score > bestScore :
                                bestScore = score
                                bestGuess = guess
                    if bestScore > 0 :
                        actionWord = bestGuess
                        commandMaybeOK = True
        if commandOK or commandMaybeOK :
            while type(commandsDict[actionWord]) is not list : # This loop walks through commnad aliases until
                actionWord = commandsDict[actionWord]          # it gets to the base command
        return actionWord,commandsDict[actionWord][0],commandsDict[actionWord][1],commandOK,commandMaybeOK

# This function checks whether the object specified on the command line matches an object in the adventure
# dictionary, and if it doesn't, tries to guess what object may have been meant.
    @classmethod
    def CheckAndCorrectObject(cls,object) :
        objects = list(cls.adventureDict['objects'].keys())
        if object in objects : # If the object is in the adventure dictionary, there is no typo, the task is done
            return object,True,True
        elif object == "" : # If no object was specified, cannot make a guess
            return object,False,False
        else : # Try to guess what object was meant
            for guess in objects :
                if object in guess : # If the letters typed are a subset of an actual object, guess that object
                    return guess,False,True
            bestScore = 0
            for guess in objects :
                score = 0
                if abs(len(guess) - len(object)) <= 2 : # Otherwise, for all objects that have approximately 
                    for letter in object :              # the same number of letters as what was typed,
                        if letter in guess :            # create a scoreboard based on the number of matching
                            score = score + 1           # letters between what was typed and an actual object
                            if guess.index(letter) == object.index(letter) :
                                score = score + 1
                    if score > bestScore :              # in the game.  Return the best guess
                        bestScore = score
                        bestGuess = guess
            if bestScore > 0 :
                return bestGuess,False,True
            else :
                return object,False,False
        
# A command string has been typed.  It has the following possible forms:
# 1. command (with no arguments), i.e. a movement command or 'inventory' or 'look'
# 2. command with one argument, i.e. take sword, read scroll
# 3. command with two arguments, i.e. use key on chest
# This routine extracts the command word, object1, and potential object 2 from the command
# It returns the extracted words, and whether the command line is valid to execute
    @classmethod
    def ParseCommand(cls,commandStr) : # Attempt to recognize and correct typos in the command string
        commandWords = commandStr.split()
        actionWord = commandWords.pop(0)
        object1 = ""
        object2 = ""
        if actionWord == "turn" : # Special case for the 'turn on' and 'turn off' action words which are really two words
            if len(commandWords) > 0 :
                actionWord = actionWord + ' ' + commandWords.pop(0)
        actionWord,actionFunc,actionWordCount,commandOK,commandMaybeOK = cls.CheckAndCorrectAction(actionWord) 
        if commandOK or commandMaybeOK :
            if actionWordCount == 3 :
                if "on" in commandWords : # The only 3 arg command is 'use <something> on <something else>
                    index = commandWords.index("on")
                    object1 = ("".join((commandWords[i]+' ') for i in range(0,index))).strip()
                    object1,object1OK,object1MaybeOK = cls.CheckAndCorrectObject(object1)
                    object2 = ("".join((commandWords[i]+' ') for i in range(index+1,len(commandWords)))).strip()
                    object2,object2OK,object2MaybeOK = cls.CheckAndCorrectObject(object2)
                else : # No 'on' found
                    object1OK = False
                    object1MaybeOK = False
                    object2OK = False
                    object2MaybeOK = False
                    print("Expecting command line of the form: use <something> on <something else>")
            elif actionWordCount == 2:
                object1 = ("".join((word+' ') for word in commandWords)).strip()
                object1,object1OK,object1MaybeOK = cls.CheckAndCorrectObject(object1)
                object2OK = True
                if object1 == "" :
                    print(f'Expecting command line of the form: {actionWord} <something>')
            else :
                object1OK = True
                object2OK = True
        if commandOK and object1OK and object2OK :
            return (True,actionWord,actionFunc,actionWordCount,object1,object2)
# We have called routines to try and guess the intent of the command line if there are typos, i.e. the action, object1
# and potential object2 don't match keywords in the game.  Below, if we have come up with possible guesses for all
# actions and objects, present the guess to the user for confirmation
        elif (commandOK or commandMaybeOK) and (object1OK or object1MaybeOK) and (object2OK or object2MaybeOK) :
            yesno = ""
            while yesno == "" :
                if actionWordCount < 2 :
                    print(f'Did you mean: {actionWord}? (y/n):',end="")
                elif actionWordCount == 2 :
                    print(f'Did you mean: {actionWord} {object1}? (y/n):',end="")
                else :
                    print(f'Did you mean: {actionWord} {object1} on {object2}? (y/n):',end="")
                yesno = input(" ").lower()
            if yesno[0] == "y" :
                return (True,actionWord,actionFunc,actionWordCount,object1,object2)
            else : # The guess was wrong, we don't know what the dyslexic user actually meant to type
                return (False,actionWord,actionFunc,actionWordCount,object1,object2)
        else : # We were unable to come up with even a guess as to what the user meant
            return (False,actionWord,actionFunc,actionWordCount,object1,object2)            

# The action passed to to this function is actually a list of two elements.  The first is a pointer to which
# function to be called for this particular game command, and the second is a number indicating how many
# arguments are needed.  The options are indicated below
    @classmethod
    def ExecuteCommand(cls,action,actionFunc,actionWordCount,object1,object2):
        if actionWordCount == 0 : # No arguments needed, e.g. 'help' or 'quit'
            repeatLocationDescription = actionFunc()
        elif actionWordCount == 1 : # 1 argument needed, which is the command itself, e.g. 'north', 'south'
            repeatLocationDescription = actionFunc(action)
        elif actionWordCount == 2 : # 2 arguments needed, the command and one object, e.g. 'take sword'
            repeatLocationDescription = actionFunc(action,object1)
        elif actionWordCount == 3 : # 3 arguments needed, the command and two objects, e.g. 'use key on chest'
            repeatLocationDescription = actionFunc(action,object1,object2)
        else :
            print(f'Invalid action list {action}')
            exit()
        return repeatLocationDescription

# Function to get the current location
    @classmethod
    def GetLocation(cls) :
        return cls.adventureDict['attributes']['mylocation']['state']

# Function to get the current location description
    @classmethod
    def GetLocationDescription(cls) :
        mylocation = cls.adventureDict['attributes']['mylocation']['state']
        descriptionDict = cls.ParseConditionTree(cls.adventureDict['rooms'][mylocation]['description'])
        if descriptionDict.get("text") :
            return descriptionDict["text"]
        elif descriptionDict.get("textstring") :
            return cls.adventureDict["textstrings"][descriptionDict["textstring"]]
        else :
            return "Error - missing description"

# Function to get the current location image
    @classmethod
    def GetLocationImage(cls) :
        mylocation = cls.adventureDict['attributes']['mylocation']['state']        
        return cls.adventureDict['rooms'][mylocation]['image']
        
# Function to get possible commands with item
# This is a bit of a pain, because of the 'use <object1> on <object2>' command format.  For two word commands such as
# 'drink elixir of life' or 'take sword' the allowable actions can be found under the 'objects' section of the dictionary.
# But for 'use', you have to look under object2 to see if object1 has an entry, that is, object1 is treated as an action
# that can be taken on object2.  So to see if 'use' is a possible command for an <objectx>, you have to check all objects
# to see if <objectx> is listed.
    @classmethod
    def GetPossibleCommands(cls,item) :
        allItems = cls.GetAllItems()
        actions = []
# The simple actions
        for action in cls.adventureDict['objects'][item]['actions'].keys() :
            if action == "drop":
                if cls.adventureDict['objects'][item]['location'] == "inventory":
                    actions.append(action)
            elif action == "take":
                if cls.adventureDict['objects'][item]['location'] == cls.GetLocation():
                    actions.append(action)
            else: actions.append(action)
# The use-<object>-on-<object>
        for checkItem in allItems:
            if item in cls.adventureDict['objects'][checkItem]['actions'].keys() :
                actions.append("use")
        return actions

# How to tell when the game is over
    @classmethod
    def SuccessCondition(cls) :
#Note : This has to be overridden by the method in the custom class
        return False

# What to print when the game is over
    @classmethod
    def SuccessMessage(cls) :
#Note : This has to be overridden by the method in the custom class
        pass
    
# Main Loop
    @classmethod
    def RunTheGame(cls) :
        system('clear')
        if cls.useSound :
            playsound(cls.soundsDir+"intro.mp3",False)
        print("\n\n    Welcome to the game!\n\nType 'help' to see list of possible actions\n\n")
        repeatLocationDescription = True
        mylocation = cls.adventureDict['attributes']['mylocation']['state'] # Where we are in the adventure world
        while not cls.SuccessCondition() : # While the quest is not over
# Print a description of where we are now.  This will be triggered if we have moved to a new room, or on the 'look' command
            if repeatLocationDescription : 
                print()
                print("**************************************************")
                descriptionDict = cls.ParseConditionTree(cls.adventureDict['rooms'][mylocation]['description'])
                if descriptionDict.get("text") :
                    print(descriptionDict["text"])
                elif descriptionDict.get("textstring") :
                    print(cls.adventureDict["textstrings"][descriptionDict["textstring"]])
                else :
                    printt("Error - missing description")
                    exit()
                print("**************************************************")
                cls.ShowItemsHere(mylocation)
            else :
                print()
            parseOK = False
            while not parseOK : # Keep getting command lines until it can be parsed into valid actions and objects
                commandStr = ""
                while commandStr == "":
                    commandStr = input("Command: ").lower()
                parseOK,action,actionFunc,actionWordCount,object1,object2 = cls.ParseCommand(commandStr)
# Execute the action
            repeatLocationDescription = cls.ExecuteCommand(action,actionFunc,actionWordCount,object1,object2)
            mylocation = cls.adventureDict['attributes']['mylocation']['state'] # update to new location
        cls.SuccessMessage()
