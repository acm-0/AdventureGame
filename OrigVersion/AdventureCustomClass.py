
from os import system
from AdventureBaseClass import AdventureBaseClass

class AdventureCustomClass(AdventureBaseClass) :

    customFuncList = ["DropInventoryItems"]

    @classmethod
    def CustomFuncDispatch(cls,str) :
        if str in cls.customFuncList :
# The following line returns the function in object cls with name str and executes it
            getattr(cls,str)()

    @classmethod
    def DropInventoryItems(cls) :
        mylocation = cls.adventureDict['attributes']['mylocation']['state']
        itemsInInventory = cls.FindItemsInLocation("inventory")
        for item in itemsInInventory :
            cls.adventureDict['objects'][item]['location'] = mylocation
            if item == "sunglasses" :
                cls.adventureDict['objects'][item]['state'] = "not being worn"
                
    @classmethod
    def SuccessCondition(cls) :
        if cls.adventureDict['attributes']['mylocation']['state'] == "start" and cls.adventureDict['objects']['orb of light']['location'] == "inventory" :
            return True
        else :
            return False

    @classmethod
    def SuccessMessage(cls) :
        system('clear')
        print("\n\n ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! !")
        print("\nCongratulations!  You have escaped with the Orb of Light!")
        print("\nYour quest is complete, mighty adventurer!")
        print("\n ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! !")
        print("\n\n\n\n\n\n\n")
