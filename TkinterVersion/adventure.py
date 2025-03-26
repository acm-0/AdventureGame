import tkinter as tk
from tkinter import messagebox
import tkinter.scrolledtext as st
from PIL import Image, ImageTk
from AdventureCustomClass import AdventureCustomClass


#########                                                                           #########
######### Instantiate the Game, causes load of game json file. Start the Tk GUI     #########
#########                                                                           #########
game = AdventureCustomClass
# Whether to use sounds
game.UseSound(False)
# A null event for function calls where an event is required syntatically, but not needed
nullEvent = tk.Event()

# Create a Tkinter window
root = tk.Tk()
root.title("Adventure")
root.resizable(False, False)
#############################################################################################


#########                                                                           #########
######### This section is for displaying the help page if some hits the Help button #########
#########                                                                           #########
def ShowHelp():
   top=tk.Toplevel()
   top.title("Adventure Help")
   frame = tk.Frame(top,width=800,height=800,bg="white")
   frame.pack()
   img = Image.open("images/HelpImage.png").resize((400,400))
   photo_img = ImageTk.PhotoImage(img)
   label = tk.Label(frame,image=photo_img,bd=2,relief="solid")
   label.place(x=0,y=0,width=400,height=400)
   # For some reason, this line is required in order to get the image to display, as well
   # as defining it in the label call
   label.image=photo_img
   textbox1_text = tk.StringVar()
   textbox1_text.set(
'''
In this game you are an adventurer trying to fulfill a quest or mission.  You move from place to place, finding items that may be useful to you and putting them in your pack.  If you use these items the right way, in the right place, you will make progress.

You interact with the world through written commands.  In general commands are of three forms:
  1. movement
  2. <action> <object>, for example 'take sword'
  3. use <object> on <another object>, for example 'use key on door'

Movement commands are:
  n, s, e, w, ne, nw, se, sw, u (for up), d (for down)

'''
)
   textbox1 = tk.Text(frame,wrap="word",bg="white",takefocus=0,font=myfont)
   textbox1.place(x=400,y=0,width=400,height=400)
   textbox1.insert(tk.END,textbox1_text.get())
   textbox2_text = tk.StringVar()
   textbox2_text.set(
'''
The various windows of the Adventure GUI are described here.  Refer to the number in the image above.
  1.  This is where you enter commands.  Execute the command by hitting <Enter> or with the OK button
      You may abbreviate commands and the system will attempt to figure out what you mean.  For example,
      'wear sung' will be interpreted to 'wear sunglasses'.
  2.  This is the main dialog window.  The results of your actions will be displayed here.  If your
      action involves moving to a new location, the location ddescription shown in area 3 will also update.
  3.  Here you will see a description of your current location.  Generally this description will indicate
      the possible directions you can go from here, and may give hints to actions that should be performed.
  4.  This area shows a picture of your current location.  These pictures are AI generated and may not be
      totally accurate representations of the location.  Consider them entertainment value.
  5.  Any items to be found in your current location will be shown here.  Most of the time you can take
      items and put them in your pack.  If you highlight an item this command will be entered for you.
  6.  This list shows you the items you are currently carrying.  Highlighting an item will show the
      possible commands for this item in area 7.
  7.  This drop down menu shows the possible commands you can use associated with an item you highlight
      in area 6.  Choosing one of them will enter this command for you.
'''
)
   textbox2 = tk.Text(frame, wrap="word",bg="white",takefocus=0,font=myfont)
   textbox2.place(x=0,y=400,width=800,height=370)
   textbox2.insert(tk.END,textbox2_text.get())
   button = tk.Button(frame,image=photo_img2,command=top.destroy)
   button.place(x=700,y=770,width=50,height=25)
#############################################################################################

#########                                                                           #########
#########              Action when the Clear button is pressed                      #########
#########                                                                           #########
def ClearEntry():
    action_entrybox.delete(0,tk.END)
    action_entrybox.insert(tk.END,"Command: ")

#############################################################################################

#########                                                                           #########
#########               Action when the Quit button is pressed                      #########
#########                                                                           #########
def ConfirmQuit():
    if messagebox.askquestion("Quit Adventure", "Are you sure you want to quit?") == "yes":
        root.destroy()
#############################################################################################

#########                                                                           #########
#########   Action when a items here or items carrying listbox item is selected     #########
#########                                                                           #########
def item_selected(event):
    global possible_commands_item, possible_commands_item_save
    widget = event.widget
    selection = widget.curselection()
    if selection:
       selected_item = widget.get(selection[0])   
       item_found = ""
       for item in all_items:
          if item in selected_item:
             item_found = item
             break
       if item_found == "":
          possible_commands_item.set("Possible commands with...")
          possible_commands_item_save.set("Possible commands with...")
          possible_commands_optionmenu.config(textvariable=possible_commands_item)
          menu = possible_commands_optionmenu['menu']
          menu.delete(0, 'end')
       else:
          UpdatePossibleCommands(item_found)
    return

#############################################################################################

#########                                                                           #########
#########              Functions to update the location info in the GUI             #########
#########                                                                           #########
def UpdateLocationLabel():
    loc = game.GetLocation()
    location_description_label.config(text=loc)

def UpdateLocationText():
    loc = game.GetLocationDescription()
    location_textbox.config(state="normal")
    location_textbox.delete("1.0",tk.END)
    location_textbox.insert(tk.END,loc)
    location_textbox.config(state="disabled")
    
def UpdateLocationImage():
    imgfile = game.GetLocationImage()
    if imgfile == "none" or imgfile == "None":
        imgfile = "NoImg.png"
    imgfile = "images/"+imgfile
    img = Image.open(imgfile).resize((500,500))
    photo_img = ImageTk.PhotoImage(img)
    location_image.config(image=photo_img)
    location_image.image=photo_img
    
#############################################################################################

#########                                                                           #########
#########                Function to update the Command Result text box             #########
#########                                                                           #########

def UpdateCommandResultText(cmdresult):
    action_result_textbox.config(state="normal")
    action_result_textbox.delete("1.0",tk.END)
    action_result_textbox.insert(tk.END,cmdresult)
    action_result_textbox.config(state="disabled")

#############################################################################################

#########                                                                           #########
######### Functions to update the list of items at current location or in inventory #########
#########                                                                           #########
def UpdateItemsHere():
    items = game.GetItemsHere(game.GetLocation())
    items_here_listbox.delete(0,tk.END)
    for item in items:
        items_here_listbox.insert(tk.END,item)
    
def UpdateInventory():
   items = game.GetInventory()
   inventory_listbox.delete(0,tk.END)
   for item in items:
      inventory_listbox.insert(tk.END,item)

#############################################################################################

#########                                                                           #########
#########  Functions to update or clear the list of possible commands on an item    #########
#########                                                                           #########
def UpdatePossibleCommands(item):
    global possible_commands_item, possible_commands_item_save

    possible_commands_item.set("Possible commands with " + item + "...")
    possible_commands_item_save.set("Possible commands with " + item + "...")
    possible_actions = game.GetPossibleCommands(item)
    for i in range(len(possible_actions)):
       if possible_actions[i] == "use":
          possible_actions[i] += " " + item + " on "
       else:
          possible_actions[i] += " " + item
    menu = possible_commands_optionmenu['menu']
    menu.delete(0, 'end')
    for option in possible_actions:
        menu.add_command(label=option, command=tk._setit(possible_commands_item, option, CommandSelected))

def ClearPossibleCommands():
    global possible_commands_item, possible_commands_item_save

    possible_commands_item.set("Possible commands with...")
    possible_commands_item_save.set("Possible commands with...")
    menu = possible_commands_optionmenu['menu']
    menu.delete(0, 'end')
    menu.add_command(label="", command=tk._setit(possible_commands_item, "", CommandSelected))
   

#############################################################################################

#########                                                                           #########
#########        Function to enter a selected command on the command line           #########
#########                                                                           #########
def CommandSelected(command):
    global possible_commands_item

    action_entrybox.delete(0,tk.END)
    action_entrybox.insert(tk.END,"Command: ")
    action_entrybox.insert(tk.END,command)
    possible_commands_item.set(possible_commands_item_save.get())
    possible_commands_optionmenu.config(textvariable=possible_commands_item)

#############################################################################################

#########                                                                           #########
#########       Execute the Command in the Command Entry Window                     #########
#########                                                                           #########
def ExecuteCommand(event=nullEvent):
    command = commandstr.get()
    if command[0:9] == "Command: ":
       command = command[9:]
#   print(command)
    parseOK,action,actionFunc,actionWordCount,object1,object2 = game.ParseCommand(command)
    resultStr = game.ExecuteCommand(action,actionFunc,actionWordCount,object1,object2)
    if game.SuccessCondition():
        UpdateCommandResultText(game.SuccessMessage())
    else:    
        UpdateCommandResultText(resultStr)
        UpdateLocationLabel()
        UpdateLocationText()
        UpdateLocationImage()
        UpdateItemsHere()
        UpdateInventory()
        ClearPossibleCommands()
       
   
#############################################################################################

#########                                                                           #########
#########              Set up the layout of the GUI                                 #########
#########                                                                           #########
frame = tk.Frame(root,height=800,width=1000)
frame.pack()

# This is the blue color for the labels
mylabel_color = "#7adbff"
# THis is the font we will use
myfont=('Arial',14)

# Label for the Current Location textbox
location_description_label = tk.Label(frame,text="Current Location",bg=mylabel_color,bd=2,relief="solid",font=myfont)
location_description_label.place(x=5000,y=0,width=500,height=25)

# The Current Location textbox (upper left corner of the GUI)
location_textbox = tk.Text(frame, wrap="word",bg="white",takefocus=0,font=myfont)
location_textbox.place(x=500,y=25,width=500,height=225)
location_textbox.config(state="disabled")

# The Current Location Image (upper right corner of the GUI)
location_image = tk.Label(frame,text="Location Image")
location_image.place(x=0,y=0,width=500,height=500)

# Label for the Items Here listbox
items_here_label = tk.Label(frame,text="Items that are here",bg=mylabel_color,bd=2,relief="solid")
items_here_label.place(x=500,y=250,width=500,height=25)

# The Items Here listbox (lower left corner of the GUI)
items_here_listbox = tk.Listbox(frame,font=myfont) # ,listvariable=items)
items_here_listbox.bind('<<ListboxSelect>>', item_selected)
items_here_listbox.place(x=500,y=275,width=500,height=200)

# Label for the Inventory listbox
inventory_label = tk.Label(frame,text="Items you are carrying",bg=mylabel_color,bd=2,relief="solid")
inventory_label.place(x=500,y=475,width=500,height=25)

# The Inventory listbox (lower right corner of the GUI)
inventory_listbox = tk.Listbox(frame) # ,listvariable=items)
inventory_listbox.bind('<<ListboxSelect>>', item_selected)
inventory_listbox.place(x=500,y=500,width=500,height=240)

# Label for the Possible Commans optionmenu
possible_commands_label = tk.Label(frame,text="Possible commands with...",bg=mylabel_color,relief="solid")
possible_commands_label.place(x=500,y=740,width=500,height=30)

# The Possible Commands optionmenu, with initial blank options
possible_commands_item = tk.StringVar()
possible_commands_item.set("Possible commands with...")
possible_commands_item_save = tk.StringVar()
possible_commands_item_save.set("Possible commands with...")
possible_commands_options = [""]
possible_commands_optionmenu = tk.OptionMenu(frame, possible_commands_item, *possible_commands_options, command=CommandSelected)
possible_commands_optionmenu.place(x=500,y=770,width=500,height=30)

# Here we create a subframe to hold the command entry, command result, and buttons
# in the lower middle of the GUI
subframe = tk.Frame(frame,height=300,width=500,bg="white")
subframe.place(x=0,y=500,height=300,width=500)

# Label for the Action Result textbox
action_result_label = tk.Label(subframe,text="Command entry and result",bg=mylabel_color,bd=2,relief="solid")
action_result_label.place(x=0,y=0,width=500,height=25)

# The Action Result textbox (the lower middle of the GUI)
action_result_textbox = tk.Text(subframe, wrap="word",bd=3,relief="solid",bg="white",takefocus=0,font=myfont)
action_result_textbox.place(x=0,y=25,width=500,height=215)
action_result_textbox.config(state="disabled")

# The Entry widget for entering your command.  We will always have "Command: " as the prompt
commandstr = tk.StringVar()
action_entrybox = tk.Entry(subframe,textvariable=commandstr,font=myfont,bd=3,relief="solid")
action_entrybox.place(x=0,y=240,width=500,height=30)
action_entrybox.bind('<Return>', ExecuteCommand)
action_entrybox.insert(tk.END,"Command: ")

# Four buttons on the bottom middle of the GUI - Quit, Clear, Help, OK
# Each has an image as its display because the default text didn't look good
img = Image.open("images/QuitButton.png").resize((75,25))
photo_img = ImageTk.PhotoImage(img)
quit_button = tk.Button(subframe,image=photo_img,command=ConfirmQuit)
quit_button.place(x=25,y=270,width=50,height=30)

img1 = Image.open("images/ClearButton.png").resize((75,25))
photo_img1 = ImageTk.PhotoImage(img1)
clear_button = tk.Button(subframe,image=photo_img1,command=ClearEntry)
clear_button.place(x=150,y=270,width=50,height=30)

img3 = Image.open("images/HelpButton.png").resize((75,25))
photo_img3 = ImageTk.PhotoImage(img3)
help_button = tk.Button(subframe,image=photo_img3,command=ShowHelp)
help_button.place(x=275,y=270,width=50,height=30)

img2 = Image.open("images/OKButton.png").resize((75,25))
photo_img2 = ImageTk.PhotoImage(img2)
ok_button = tk.Button(subframe,image=photo_img2,command=ExecuteCommand)
ok_button.place(x=400,y=270,width=50,height=30)

#############################################################################################

#########                                                                           #########
#########               Initiaize the GUI with Starting Conditions                  #########
#########                                                                           #########
all_items = game.GetAllItems()
all_items.sort(key=len, reverse=True) # List of items MUST be sorted longest to shortest
UpdateLocationLabel()
UpdateLocationText()
UpdateLocationImage()
UpdateItemsHere()
UpdateInventory()

# Launch the main game loop
game.RunTheGame()


