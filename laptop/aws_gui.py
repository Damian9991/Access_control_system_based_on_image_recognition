#!/usr/bin/python3

#-----------------------------------------------------------
# Name: Access_control_system_based_on_image_recognition
# Authors: Kamil Kryczka, Damian Osinka
# Thesis supervisor: dr hab. inz. Mikołaj Leszczuk
# Purpose: Engineering Thesis
# Created: 13-10-2018
#-----------------------------------------------------------

import PIL.Image
import tkinter.messagebox
import time
import tkinter as tk
import sqlite3
import sys
import os
from tkinter import *
from PIL import ImageTk

import logging
logger = logging.getLogger("gui.log")
hdlr = logging.FileHandler(os.popen("pwd").read().replace('\n', '').replace(' ', '') + "/gui.log")
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)

LARGE_FONT=("Verdana", 12)

########################################################################################################################
#------------------------------------------------ Mechanism class -----------------------------------------------------#
########################################################################################################################

class GuiManager(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        container = Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight =1)
        container.grid_columnconfigure(0, weight=1)

        self.label = tk.Label(text="", bg="yellow", font=("Helvetica ", 14))
        self.label.place(x=660, y =0)
        self.update_clock()

        self.frames = {}

        for F in (StartPage, MainMenu, TurnOffMenu):

            frame = F(container, self)
            self.frames[F]= frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

        self.title("Access control system based on image recognition")
        menu = Menu(self.master)    # creating a menu instance
        self.config(menu=menu)

        file = Menu(menu)       # create the file object)
        file.add_command(label="Exit", command=self.quit())  # adds a command to the menu option
        menu.add_cascade(label="File", menu=file)  # added "file" to the menu
        menu.add_cascade(label="About")            # added "About" to the menu

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

    def update_clock(self):
        now = time.strftime("%H:%M:%S")
        self.label.configure(text=now)
        self.after(1000, self.update_clock)

########################################################################################################################
#-------------------------------------------------StartPage class------------------------------------------------------#
########################################################################################################################

class StartPage(Frame):
    def __init__(self, parent, controller):
        self.controller = controller
        Frame.__init__(self, parent)

        self.tempLabel = Label(self, font=("Helvetica bold", 14))
        self.tempLabel.place(x=661, y=27)

        self.initWindow()
        self.showImg()
        self.showText()


    def end_program(self):
        sys.exit(0)

    def initWindow(self):
        nameLabel = Label(self, text = "Login")
        nameLabel.place(x = 280, y=150)

        passwordLabel = Label(self, text="Password")
        passwordLabel.place(x=280, y=170)

        self.nameEntry = Entry(self)
        self.nameEntry.place(x=350, y=150)

        self.passwordEntry = Entry(self, show = "*")
        self.passwordEntry.place(x=350, y=170)

        self.var = StringVar()
        self.var.set("default")
        checkButton = Checkbutton(self,text="Show password", variable=self.var, onvalue="show", offvalue="hide", command=self.checkCheckbutton)
        checkButton.place(x=350, y=200)

        loginButton = Button(self, text="Log in", command=self.checkUser)
        loginButton.place(x=400, y=220)

        quitButton = Button(self, text="Quit", command=self.end_program)
        quitButton.place(x=405, y=250)

    def checkCheckbutton(self):
        if self.var.get() == "show":
            self.passwordEntry.delete(0, END)
            self.passwordEntry = Entry(self)
            self.passwordEntry.place(x=350, y=170)
        else:
            self.passwordEntry.delete(0, END)
            self.passwordEntry = Entry(self, show = "*")
            self.passwordEntry.place(x=350, y=170)


    def showImg(self):
        load = PIL.Image.open("klodka.png")
        render = ImageTk.PhotoImage(load)

        img = Label(self, image=render)
        img.Image = render
        img.place(x=0, y=50)

    def showText(self):
        text = Label(self, text="Access control system", font=("Helvetica bold", 16), bg ="yellow", anchor= CENTER)
        text.place(x=310, y=30)
        text2 = Label(self, text="based on image recognition", font=("Helvetica bold", 16), bg ="yellow", anchor= CENTER)
        text2.place(x=280, y=60)

    def checkUser(self):
        username = self.nameEntry.get()
        password = self.passwordEntry.get()

#        with sqlite3.connect("Users.db") as db:
 #           cursor = db.cursor()
  #      find_user = ("SELECT * FROM user WHERE username = ? AND password =?")
#        cursor.execute(find_user, [(username), (password)])
  #      results = cursor.fetchall()

        if True:
            tkinter.messagebox.showinfo('Information', 'You have been logged in!')
            print("Login done")
            a = 1 # Depends which window we want
            if a == 1:
                OpenWindow(self.controller)
            else:
                OpenWindow1(self.controller)

            self.nameEntry.delete(0, 'end')
            self.passwordEntry.delete(0, 'end')

        else:
            tkinter.messagebox.showwarning('Warming', 'Username and password not recognized!')
            print("Login failed")


def OpenWindow(x):
    x.show_frame(MainMenu)

def OpenWindow1(x):
    x.show_frame(TurnOffMenu)

########################################################################################################################
#-------------------------------------------------MainMenu class-------------------------------------------------------#
########################################################################################################################

class MainMenu(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller

        button = Button(self, text="Back Home", command=self.Back_home_button)
        button.place(x=330, y=310)
        addUserButton = Button(self, text="Add user", command=self.showAddUserElements)
        addUserButton.place(x=600, y=50)

        delUserButton = Button(self, text="Delete user", command=self.showDelUserElements)
        delUserButton.place(x=594, y=80)

        self.End_programa()

    def Back_home_button(self):
        global x
        x = False
        self.controller.show_frame(StartPage)
    def showAddUserElements(self):
        self.addUserLabel = Label(self, text="Enter username to add")
        self.addUserLabel.place(x=570, y=110)

        self.addUserEntry = Entry(self)
        self.addUserEntry.place(x=565, y=130)

        self.addPINLabel = Label(self, text="Enter your PIN \n(must be a number)")
        self.addPINLabel.place(x=570, y=152)

        self.addPINEntry = Entry(self)
        self.addPINEntry.place(x=565, y=190)

        self.addPassLabel = Label(self, text="Enter your Password")
        self.addPassLabel.place(x=570, y=210)

        self.addPassEntry = Entry(self)
        self.addPassEntry.place(x=565, y=230)

        self.addUserOKButton = Button(self, text="Confirm", command=self.addUser)
        self.addUserOKButton.place(x=570, y=250)

        self.addUserCancelButton = Button(self, text="Cancel", command=self.cancelAdd)
        self.addUserCancelButton.place(x=655, y=250)

    def addUser(self):
        username = self.addUserEntry.get()
        PIN = self.addPINEntry.get()
        password = self.addPassEntry.get()

        found = 0
        while found == 0:
            #SQL
            with sqlite3.connect("Users.db") as db:
                cursor = db.cursor()
            find_user = ("SELECT * FROM user WHERE username = ? AND PIN =?")
            cursor.execute(find_user, [(username), (PIN)])

            if cursor.fetchall():

                self.addUserEntry.destroy()
                self.addUserEntry = Entry(self, bg='red')
                self.addUserEntry.place(x=565, y=130)
                tkinter.messagebox.showwarning('Warming', 'Username taken, please try again!')

                print(" Username Taken, please try again")
                break

            else:
                found = 1
                self.addUserLabel.destroy()
                self.addUserEntry.destroy()
                self.addPINLabel.destroy()
                self.addPINEntry.destroy()


                self.addPassLabel.destroy()
                self.addPassEntry.destroy()

                self.addUserOKButton.destroy()
                self.addUserCancelButton.destroy()

                insertData = '''INSERT INTO user(username, PIN, password)
                VALUES(?,?,?)'''
                cursor.execute(insertData, [(username), (PIN), (password)])
                tkinter.messagebox.showinfo('Add User', 'User has been added!')
                db.commit()

    def cancelAdd(self):
        self.addUserLabel.destroy()
        self.addUserEntry.destroy()
        self.addPINLabel.destroy()
        self.addPINEntry.destroy()
        self.addPassLabel.destroy()
        self.addPassEntry.destroy()
        self.addUserOKButton.destroy()
        self.addUserCancelButton.destroy()

    def showDelUserElements(self):
        self.delUserLabel = Label(self, text="Enter username to delete")
        self.delUserLabel.place(x=570, y=110)

        self.delUserEntry = Entry(self)
        self.delUserEntry.place(x=565, y=130)

        self.delUserOKButton = Button(self, text="Confirm", command=self.delUser)
        self.delUserOKButton.place(x=570, y=150)

        self.delUserCancelButton = Button(self, text="Cancel", command=self.cancelDel)
        self.delUserCancelButton.place(x=660, y=150)

    def delUser(self):
        username = self.delUserEntry.get()

        self.delUserLabel.destroy()
        self.delUserEntry.destroy()
        self.delUserOKButton.destroy()
        self.delUserCancelButton.destroy()

        #SQL
        with sqlite3.connect("Users.db") as db:
            cursor = db.cursor()
        find_user = ("SELECT * FROM user WHERE username = ? ")
        cursor.execute(find_user, [(username)])

        if cursor.fetchall():
            print(" User has been deleted")
            tkinter.messagebox.showinfo('Information', 'User has been deleted!')
            delrecord = ('''DELETE FROM user WHERE username=?''')
            cursor.execute(delrecord, [(username)])
            db.commit()
        else:
            print("Username has not exist")
            tkinter.messagebox.showwarning('Warming', 'Username has not exist! \nPlease try again!')

    def cancelDel(self):
        self.delUserLabel.destroy()
        self.delUserEntry.destroy()
        self.delUserOKButton.destroy()
        self.delUserCancelButton.destroy()

    def End_programa(self):
        try:
            global x
            if x == True:
                pass
            else:
                x = True
            self.controller.after(100, self.End_programa)
        except AttributeError:
            pass

########################################################################################################################
#----------------------------------------------- TurnOffMenu class ----------------------------------------------------#
########################################################################################################################
x = True

class TurnOffMenu(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller

        self.showText()
        self.addElementsOffMenu()

    def Back_home_button(self):
        self.entryPIN()
        global x
        x = False
        self.controller.show_frame(StartPage)


    def showText(self):
        text = Label(self, text="Access control system based on image recognition", font=("Helvetica bold", 16), bg="yellow",anchor=CENTER)
        text.place(x=300, y=10)

    def addElementsOffMenu(self):

        self.TurnOffLabel = Label(self, text="Click button below to turn off sensor")
        self.TurnOffLabel.place(x=260, y=150)

        self.button = Button(self, text="Back Home", command=lambda: self.entryPIN("back_home"))
        self.button.place(x=330, y=310)

    def entryPIN(self, action_type):

        self.action_type = action_type

        self.TurnOffButton.destroy()
        self.TurnOffLabel.destroy()
        self.button.destroy()

        self.userLabel = Label(self, text="Enter Username:")
        self.userLabel.place(x=320, y=160)

        self.UserEntry = Entry(self)
        self.UserEntry.place(x=300, y=180)

        self.PINLabel = Label(self, text="Enter PIN to confirm:")
        self.PINLabel.place(x=320, y=200)

        self.PINEntry = Entry(self, show="*")
        self.PINEntry.place(x=300, y=220)

        self.OKButton = Button(self, text="OK", command=self.checkPIN)
        self.OKButton.place(x=360, y=240)

    def checkPIN(self):
        username = self.UserEntry.get()
        PIN = str(self.PINEntry.get())
        print(PIN)
        print(type(PIN))

        with sqlite3.connect("Users.db") as db:
            cursor = db.cursor()
        find_user = ("SELECT * FROM user WHERE username = ? AND PIN =?")
        cursor.execute(find_user, [ (username), (PIN)])
        results = cursor.fetchall()

        if results:
            global x
            x=False

            tkinter.messagebox.showinfo('Information', 'You have turned off Sensor!')

            self.userLabel.destroy()
            self.UserEntry.destroy()
            self.PINEntry.delete(0, 'end')

            self.PINLabel.destroy()
            self.PINEntry.destroy()
            self.OKButton.destroy()

            if self.action_type == "back_home":
                self.controller.show_frame(StartPage)
                self.addElementsOffMenu()
            elif self.action_type == "turn_off":
                OpenWindow(self.controller)
                self.addElementsOffMenu()

        else:
            self.UserEntry.delete(0, 'end')
            self.PINEntry.delete(0, 'end')
            tkinter.messagebox.showwarning('Warming', 'You have to entry correct PIN!')

if __name__ == "__main__":
    app = GuiManager()
    app.geometry("%dx%d%+d%+d" % (750, 350, 400, 125))
    app.mainloop()
