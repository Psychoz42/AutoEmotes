import subprocess, keyboard, threading
from tkinter import *
from tkinter import ttk
from tkinter.messagebox import showerror, showwarning, showinfo
import os, time

class EmKeyboard:
    def __init__(self, keyboardName:str = '', emPreset:str = None):
        self.name = keyboardName
        self.emPresetName = emPreset
        if emPreset:
            self.emPresetDict = readEmotes(emPreset)

    def changePreset(self, newPreset):
        self.emPresetName = newPreset
        self.emPresetDict = readEmotes(newPreset)

proc = subprocess.Popen(
    ["main.exe"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1
)

def info(text):
    infoWin = Tk()
    infoWin.title('Add new Emote')
    infoWin.geometry('50x30+400+400')
    infoWin.attributes("-topmost", True)

    ttk.Label(infoWin, text=text).place(x=5, y=5)
    infoWin.after(400, infoWin.destroy)
    infoWin.mainloop()

def readEmotes(presetName):
    res = {}
    with open(f'presets/{presetName}.txt', 'r') as file:
        for s in file:
            sList = s.strip().split(' ')
            res[sList[0]] = sList[1]
    return res

def rewriteEmotes(emDictI, presetName):
    with open(f'presets/{presetName}.txt', 'w') as file:
        for i in emDictI.keys():
            file.write(f'{i} {emDictI[i]}\n')


curKeyboard = EmKeyboard()
curKeyboardVar = ''
deleteIgnoranceList = ['8', '13', '16', '17', '20', '39', '37', '38', '40']
doEnter = True
doSetNew = False
disable = False
doShowEm = False
presetVar = ''
emDict = {}
autoEnHot = '16'
onOffHot = '17'
disableCBtn = ''
disableEnterCBtn = ''

if not 'presets' in os.listdir():
    os.mkdir('presets')
if len(os.listdir('presets/')) > 0:
    presetsList = [i[:-4] for i in os.listdir('presets/')]
    emDict = readEmotes(presetsList[0])
else:
    with open('presets/emotes.txt', 'w') as file:
        presetsList = os.listdir('presets/')


def addEmote(key, emote, presetName):
    with open(f'presets/{presetName}.txt', 'a') as file:
        file.write('\n' + f'{str(key)} {emote}')
    global emDict
    emDict[str(key)] = emote

def keysProcessing():
    global curKeyboard
    global deleteIgnoranceList
    global emDict
    global curKeyboardVar
    global doSetNew
    global doShowEm
    global disable
    global doEnter
    for line in proc.stdout:
        print(line.strip())
        lineList = line.strip().split()
        if len(curKeyboard.name) == 0 and len(lineList) == 3:
            curKeyboard.name = lineList[0]
            curKeyboardVar.set('Keyboard: ' + curKeyboard.name)
        if not disable:
            if len(lineList) == 3 and lineList[2] == 'down' and lineList[0] == curKeyboard.name and not lineList[1] in deleteIgnoranceList:
                keyboard.send('backspace')
            if len(lineList) == 3 and lineList[2] == 'down' and lineList[0] == curKeyboard.name:
                if emDict.get(lineList[1]):
                    keyboard.write(emDict.get(lineList[1]))
                    if doEnter:
                        keyboard.send('enter')
        if len(lineList) == 3 and lineList[2] == 'down' and lineList[0] == curKeyboard.name:
            if doSetNew:
                doSetNew = False
                addNewEmote(lineList[1])
            if doShowEm:
                doShowEm = False
                if lineList[1] in emDict.keys():
                    showEmotesWindow(lineList[1])
                else:
                    global showEmoteAlertText
                    showEmoteAlertText.config(text='')
                    showinfo("Info", "This button is not assigned to any Emote")
            if lineList[1] == autoEnHot:
                doEnter = not doEnter
                disableEnterCBtn.select() if doEnter else disableEnterCBtn.deselect()
                info(f'Enter: {doEnter}')
            if lineList[1] == onOffHot:
                disable = not disable
                disableCBtn.select() if not disable else disableCBtn.deselect()
                info(f'Working: {not disable}')

def resetKeyboard():
    global curKeyboard
    global curKeyboardVar
    curKeyboard.name = ''
    curKeyboardVar.set('Press any key')

addNewEmoteAlertText = ''
showEmoteAlertText = ''

def addNewEmote(key:str):
    global addNewEmoteAlertText
    addNewEmoteAlertText.config(text='')

    addWin = Tk()
    addWin.title('Add new Emote')
    addWin.geometry('170x100+200+200')

    ttk.Label(addWin, text='Write emote:').place(x=5, y=5)
    entry = ttk.Entry(addWin)
    entry.place(x=5, y=30)

    def saveEm():
        addEmote(key, entry.get(), presetVar.get())
        addWin.destroy()

    saveBtn = ttk.Button(addWin, text='Save', command=saveEm)
    saveBtn.place(x=165, y=95, anchor='se')

    addWin.mainloop()

def showEmotesWindow(key):
    global showEmoteAlertText
    showEmoteAlertText.config(text='')
    showEmWin = Tk()
    showEmWin.title("Emotes")
    showEmWin.geometry("170x100+200+200")
    showEmWin.attributes("-topmost",True)

    ttk.Label(showEmWin, text='Write emote:').place(x=5, y=5)

    emEntry = ttk.Entry(showEmWin)
    emEntry.insert(0, emDict[key])
    emEntry.place(x=5, y=30)

    def saveEm():
        emDict[key] = emEntry.get()
        rewriteEmotes(emDict, presetVar.get())
        showEmWin.destroy()

    saveBtn = ttk.Button(showEmWin, text="Save", command=saveEm)
    saveBtn.place(x=165, y=95, anchor='se')

    showEmWin.mainloop()

def window():
    root = Tk()
    root.title("AutoEmotes")
    root.geometry("300x400")
    root.update_idletasks()

    global presetVar
    presetVar = StringVar(value=presetsList[0])
    #print(presetVar.get())

    def changePreset(event):
        global emDict
        emDict = readEmotes(presetVar.get())
        print(presetVar.get())

    ttk.Label(text='Preset:').place(x=5, y=5)
    presetsCB = ttk.Combobox(values=presetsList, textvariable=presetVar, state="readonly")
    presetsCB.bind("<<ComboboxSelected>>", changePreset)
    presetsCB.place(x=5, y=30)

    global addNewEmoteAlertText
    addNewEmoteAlertText = ttk.Label()
    addNewEmoteAlertText.place(x=root.winfo_width()-5, y=30, anchor="ne")

    global showEmoteAlertText
    showEmoteAlertText = ttk.Label()
    showEmoteAlertText.place(x=root.winfo_width()-5, y=85, anchor="ne")

    def addNewEmFlag():
        if len(curKeyboard.name) == 0:
            showerror(title="Error", message="Keyboard not selected")
            return
        global doSetNew
        doSetNew = True
        global addNewEmoteAlertText
        addNewEmoteAlertText.config(text='Press desired button')

    def showEmFlag():
        if len(curKeyboard.name) == 0:
            showerror(title="Error", message="Keyboard not selected")
            return
        global doShowEm
        doShowEm = True
        global showEmoteAlertText
        showEmoteAlertText.config(text='Press desired button')

    global curKeyboardVar

    curKeyboardVar = StringVar()
    curKeyboardVar.set('Press any key')

    resetBtn = ttk.Button(text='Reset Keyboard', command=resetKeyboard)
    resetBtn.place(x=5, y=60)

    keyboardName = ttk.Label(textvariable=curKeyboardVar)
    keyboardName.place(x=5, y=85)

    addNewBtn = ttk.Button(text='Add new Emote', command=addNewEmFlag)
    addNewBtn.place(x=root.winfo_width()-5, y=5, anchor="ne")

    showNewBtn = ttk.Button(text='Show Emote', command=showEmFlag)
    showNewBtn.place(x=root.winfo_width()-5, y=60, anchor="ne")

    def disableSwitch():
        global disable
        disable = not disable

    global disableCBtn
    disableCBtn = Checkbutton(text='On/Off', command=disableSwitch)
    disableCBtn.select()
    disableCBtn.place(x=5, y=115)

    def disableEnterSwitch():
        global doEnter
        doEnter = not doEnter

    global disableEnterCBtn
    disableEnterCBtn = Checkbutton(text='Auto-Enter On/Off', command=disableEnterSwitch)
    disableEnterCBtn.select()
    disableEnterCBtn.place(x=5, y=145)

    root.mainloop()

thr1 = threading.Thread(target=keysProcessing, daemon=True)
thr2 = threading.Thread(target=window)
thr1.start()
thr2.start()