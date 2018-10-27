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
from tkinter.filedialog import askopenfilename
from Access_control_system_based_on_image_recognition.GUI.gui_scripts import *
from Access_control_system_based_on_image_recognition.GUI.SQLiteManager import SQLiteManager
from Access_control_system_based_on_image_recognition.utils import *

import logging
logger = logging.getLogger("gui.log")
hdlr = logging.FileHandler(os.popen("pwd").read().replace('\n', '').replace(' ', '') + "/gui.log")
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)

LARGE_FONT=("Verdana", 12)

########################################################################################################################
#----------------------------------------------- Utilities class ------------------------------------------------------#
########################################################################################################################


class Utilities(object):

    def create_label(self, text, x_position, y_position, size):
        text_field = Label(self, text=text, font=("Helvetica bold", size), anchor= CENTER)
        text_field.place(x=x_position, y=y_position)

    def create_img(self, image_name, x_position, y_position):
        load = PIL.Image.open(image_name)
        render = ImageTk.PhotoImage(load)
        img = Label(self, image=render)
        img.Image = render
        img.place(x=x_position, y=y_position)

    def create_label_in_new_window(self, new_window_object, text, x_position, y_position):
        label = Label(new_window_object, text=text, font=("Helvetica bold", 10), bg ="grey", anchor= CENTER)
        label.pack()

    def create_user_input_in_new_window(self, new_window_object, x_position, y_position, password=None):
        if not password:
            user_input = Entry(new_window_object)
        else:
            user_input = Entry(new_window_object, show = "*")
        user_input.pack()
        return user_input

########################################################################################################################
#----------------------------------------------- GuiManager class -----------------------------------------------------#
########################################################################################################################

class GuiManager(tk.Tk, Utilities):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        container = Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight =1)
        container.grid_columnconfigure(0, weight=1)

        self.title("Access control system")

        #self.clock_label = tk.Label(text="", bg="grey", font=("Helvetica ", 14))
        #self.clock_label.place(x=660, y =0)

        self.frames = {}

        for page in (LoginPage, MainMenuPage):
            frame = page(container, self)
            self.frames[page]= frame
            frame.grid(row=0, column=0, sticky="nsew")

        #self.update_clock()
        self.show_frame(LoginPage)

    def update_clock(self):
        now = time.strftime("%H:%M:%S")
        self.clock_label.configure(text=now)
        self.clock_label.place(x=600, y=10)
        self.after(1000, self.update_clock)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

########################################################################################################################
#-------------------------------------------------LoginPage class------------------------------------------------------#
########################################################################################################################

class LoginPage(Frame, Utilities):
    def __init__(self, parent, controller):
        self.controller = controller
        Frame.__init__(self, parent)
        self.db_name = "aws_system.db"
        self.init_window()
        self.create_label("Access control system \n based on image recognition", x_position=30, y_position=0, size=16)

    def init_window(self):
        photo = PhotoImage(file="locker.png")
        background_label = Label(self, image=photo)
        background_label.place(x=0, y=0, relwidth=1, relheight=1)
        background_label.image = photo

        self.name_entry = Entry(self, width="13")
        self.name_entry.place(x=140, y=200)
        self.name_entry.insert(0,"login")

        self.password_entry = Entry(self, show = "*", width="13")
        self.password_entry.place(x=140, y=230)
        self.password_entry.insert(0, "password")

        login_button = Button(self, text="Log in", height="1", width="3", command=self.check_user_login_password)
        login_button.place(x=140, y=260)

        quit_button = Button(self, text="Quit", height="1", width="3", command=self.end_program)
        quit_button.place(x=200, y=260)

    def check_user_login_password(self):
        sqlite3_object = SQLiteManager(self.db_name)
        try:
            sqlite3_object.create_or_drop_table("CREATE TABLE users(id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
        except sqlite3.OperationalError:
            pass

        username = self.name_entry.get()
        password = sqlite3_object.create_hash_before_add_to_db(self.password_entry.get())

        if sqlite3_object.select_data("users", username, password):
            tkinter.messagebox.showinfo('Information', 'You have been logged in!')
            self.controller.show_frame(MainMenuPage)
            self.name_entry.delete(0, 'end')
            self.password_entry.delete(0, 'end')

        else:
            tkinter.messagebox.showwarning('Warming', 'Wrong username or password')

    def end_program(self):
        sys.exit(0)

########################################################################################################################
#-------------------------------------------------MainMenuPage class---------------------------------------------------#
########################################################################################################################

class MainMenuPage(Frame, Utilities):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        self.initialize_toolbar()

    def initialize_toolbar(self):
        self.add_user_img = tk.PhotoImage(file="add_user.png")
        self.add_user_button = Button(self, image=self.add_user_img, width="120", height="120", command=self.add_new_user)
        self.add_user_button.place(x=0, y=0)

        self.del_user_img = tk.PhotoImage(file="delete_user.png")
        self.del_user_button = Button(self, image=self.del_user_img, width="120", height="120", command=self.delete_user)
        self.del_user_button.place(x=125, y=0)

        self.start_system_img = tk.PhotoImage(file="start_system.png")
        self.start_system_button = Button(self, image=self.start_system_img, width="120", height="120", command=self.start_system_window)
        self.start_system_button.place(x=0, y=125)

        self.info_img = tk.PhotoImage(file="info.png")
        self.info_button = Button(self, image=self.info_img, width="120", height="120", command=self.check_system_window)
        self.info_button.place(x=250, y=125)

        self.stop_system_img = tk.PhotoImage(file="stop_system.png")
        self.stop_system_button = Button(self, image=self.stop_system_img, width="120", height="120", command=self.stop_system_window)
        self.stop_system_button.place(x=125, y=125)

        self.exit_img = tk.PhotoImage(file="exit.png")
        self.exit_button = Button(self, image=self.exit_img, width="120", height="120", command=self.exit)
        self.exit_button.place(x=250, y=0)

        self.back_home_img = tk.PhotoImage(file="arrow.png")
        self.back_home_button = Button(self, image=self.back_home_img, width="370", height="20", command=self.back_login_page)
        self.back_home_button.place(x=0, y=375)

        self.upload_img = tk.PhotoImage(file="upload.png")
        self.upload_button = Button(self, image=self.upload_img, highlightcolor="red", command=self.upload_window)
        self.upload_button.place(x=0, y=250)

        self.delete_img = tk.PhotoImage(file="delete.png")
        self.delete_button = Button(self, image=self.delete_img, highlightcolor="red", command=self.delete_window)
        self.delete_button.place(x=125, y=250)

        self.search_img = tk.PhotoImage(file="search.png")
        self.search_button = Button(self, image=self.search_img, highlightcolor="red", command=self.search_window)
        self.search_button.place(x=250, y=250)

    def upload_window(self):
        self.create_new_window("", size_x=280, size_y=370)

        self.file_face_label = Label(self.new_window, text="Upload face picture:", background="grey")
        self.file_face_label.pack()
        self.file_face_label.place(x=75, y=5)

        self.upload2_img = tk.PhotoImage(file="upload2.png")
        self.upload2_button = Button(self.new_window, image=self.upload2_img, command=self.Upload_file_path)
        self.upload2_button.pack()
        self.upload2_button.place(x=95, y=25)

        self.file_face_confirm_button = Button(self.new_window, text="Confirm")
        self.file_face_confirm_button.pack()
        self.file_face_confirm_button.place(x=100, y=160)

        self.file_plate_label = Label(self.new_window, text="Upload plate number:", background="grey")
        self.file_plate_label.pack()
        self.file_plate_label.place(x=70, y=200)

        self.file_plate_input = self.create_user_input_in_new_window(self.new_window, x_position=0, y_position=0)
        self.file_plate_input.place(x=53, y=220)

        self.file_plate_button = Button(self.new_window, text="Confirm")
        self.file_plate_button.pack()
        self.file_plate_button.place(x=100, y=240)

        self.add_relation_label = Label(self.new_window, text="Add relation to db\nphoto face <-> plate number:", background="grey")
        self.add_relation_label.pack()
        self.add_relation_label.place(x=45, y=280)

        self.add_relation_input = self.create_user_input_in_new_window(self.new_window, x_position=0, y_position=0)
        self.add_relation_input.place(x=53, y=315)

        self.add_relation_button = Button(self.new_window, text="Confirm")
        self.add_relation_button.pack()
        self.add_relation_button.place(x=100, y=335)

    def Upload_file_path(self):

        try:
            self.file_path_label.destroy()
        except:
            pass

        self.path_to_file = str(askopenfilename())
        split_list = self.path_to_file.split('/')
        file_name = split_list[(len(split_list) - 1)]

        self.sel_img = Label(self.new_window, text = "Selected image:", background="grey")
        #self.sel_img.place(x = 0, y=150)

        self.file_path_label = Label(self.new_window, text = file_name, background="grey")
        self.file_path_label.pack()
        self.file_path_label.place(x=95, y=140)
        print(self.path_to_file)

    def delete_window(self):

        self.create_new_window("", size_x=220, size_y=220)

        self.create_label_in_new_window(self.new_window, text="Delete plate number:", x_position=0, y_position=0)
        self.del_plate_number_input = self.create_user_input_in_new_window(self.new_window, x_position=0, y_position=0)
        self.del_plate_number_button = Button(self.new_window, text="Confirm", command=self.del_plate_number)
        self.del_plate_number_button.pack()

        self.create_label_in_new_window(self.new_window, text="Delete template photo face:", x_position=0, y_position=0)
        self.del_face_photo_input = self.create_user_input_in_new_window(self.new_window, x_position=0, y_position=0)
        self.del_face_photo_button = Button(self.new_window, text="Confirm", command=self.del_face_photo)
        self.del_face_photo_button.pack()

        self.create_label_in_new_window(self.new_window, text="Delete relation\n photo face <-> plate number:", x_position=0, y_position=0)
        self.del_relation_input = self.create_user_input_in_new_window(self.new_window, x_position=0, y_position=0)
        self.del_relation_button = Button(self.new_window, text="Confirm", command=self.del_relation)
        self.del_relation_button.pack()

    def del_plate_number(self):
        pass

    def del_face_photo(self):
        pass

    def del_relation(self):
        pass

    def search_window(self):
        self.create_new_window("", size_x=180, size_y=370)

        self.create_label_in_new_window(self.new_window, text="Face patterns from AWS:", x_position=0, y_position=0)

        listFrame = Frame(self.new_window)
        listFrame.pack(side=TOP, padx=5, pady=5)

        scrollBar = Scrollbar(listFrame)
        scrollBar.pack(side=RIGHT, fill=Y)
        self.listBox = Listbox(listFrame, selectmode=SINGLE)
        self.listBox.pack(side=LEFT, fill=Y)
        scrollBar.config(command=self.listBox.yview)
        self.listBox.config(yscrollcommand=scrollBar.set)
        for item in ['1','1','1']:
            self.listBox.insert(END, item)

        self.create_label_in_new_window(self.new_window, text="Plate numbers from db:", x_position=0, y_position=0)

        listFrame2 = Frame(self.new_window)
        listFrame2.pack(side=TOP, padx=5, pady=5)

        scrollBar2 = Scrollbar(listFrame2)
        scrollBar2.pack(side=RIGHT, fill=Y)
        self.listBox2 = Listbox(listFrame2, selectmode=SINGLE)
        self.listBox2.pack(side=LEFT, fill=Y)
        scrollBar2.config(command=self.listBox2.yview)
        self.listBox2.config(yscrollcommand=scrollBar2.set)
        for item in ['2','2','2']:
            self.listBox2.insert(END, item)

    def create_new_window(self, title, size_x, size_y):
        try:
            self.new_window.destroy()
        except AttributeError as err:
            pass
        self.new_window = tk.Toplevel(self.master)
        self.new_window.geometry("%dx%d%+d%+d" % (size_x, size_y, 400, 125))
        self.new_window.title(title)

    def add_new_user(self):
        self.create_new_window("Add user", size_x=180, size_y=150)

        self.create_label_in_new_window(self.new_window, text="Enter your username", x_position=0, y_position=0)
        self.username_input = self.create_user_input_in_new_window(self.new_window, x_position=0, y_position=0)

        self.create_label_in_new_window(self.new_window, text="Enter your Password", x_position=0, y_position=0)
        self.password_input = self.create_user_input_in_new_window(self.new_window, x_position=0, y_position=0, password=True)

        self.create_label_in_new_window(self.new_window, text="Confirm your Password", x_position=0, y_position=0)
        self.password_confirm_input = self.create_user_input_in_new_window(self.new_window, x_position=0, y_position=0, password=True)

        self.add_user_button = Button(self.new_window, text="Confirm", command=self.add_user_to_db)
        self.add_user_button.pack()

    def add_user_to_db(self):
        username = self.username_input.get()
        password_hash = create_hash(self.password_input.get())
        password_confirm_hash = create_hash(self.password_confirm_input.get())

        if username == "" or password_hash == "" or password_confirm_hash == "":
            tkinter.messagebox.showerror('Error', 'Please, fill all fields')

        elif password_hash != password_confirm_hash:
            tkinter.messagebox.showerror('Error', 'Password does not match the confirm password')

        else:
            with sqlite3.connect("aws_system.db") as db:
                cursor = db.cursor()
            find_user = "SELECT * FROM users WHERE username = ?"
            cursor.execute(find_user, [(username)])

            if cursor.fetchall():
                tkinter.messagebox.showwarning('Warming', 'Username taken, please try again!')

            else:
                insertData = "INSERT INTO users(username, password) VALUES(?,?)"
                cursor.execute(insertData, [(username), (password_hash)])
                tkinter.messagebox.showinfo('Add User', 'User has been added!')
                db.commit()

    def delete_user(self):
        self.create_new_window("Delete user", size_x=180, size_y=70)

        self.create_label_in_new_window(self.new_window, text="Enter username to delete", x_position=0, y_position=0)
        self.username_to_delete = self.create_user_input_in_new_window(self.new_window, x_position=0, y_position=0)

        self.del_user_button = Button(self.new_window, text="Confirm", command=self.del_user_from_db)
        self.del_user_button.pack()


    def del_user_from_db(self):
        username = self.username_to_delete.get()

        with sqlite3.connect("aws_system.db") as db:
            cursor = db.cursor()
            find_user = "SELECT * FROM users WHERE username = ? "
            cursor.execute(find_user, [(username)])

        if cursor.fetchall():
            delrecord = "DELETE FROM users WHERE username=?"
            cursor.execute(delrecord, [(username)])
            db.commit()
            tkinter.messagebox.showinfo('Information', 'User has been deleted!')

        else:
            tkinter.messagebox.showwarning('Warming', "user doesn't exist\nPlease try again!")

    def back_login_page(self):
        self.controller.show_frame(LoginPage)

    def start_system_window(self):
        self.create_new_window("Start system", size_x=180, size_y=110)

        self.create_label_in_new_window(self.new_window, text="Raspberry_face_ip", x_position=0, y_position=0)
        self.rasp_1_start_input = self.create_user_input_in_new_window(self.new_window, x_position=0, y_position=0)

        self.create_label_in_new_window(self.new_window, text="Raspberry_plate_ip", x_position=0, y_position=0)
        self.rasp_2_start_input = self.create_user_input_in_new_window(self.new_window, x_position=0, y_position=0)

        self.start_system_button = Button(self.new_window, text="Start", command=self.start_system_from_gui)
        self.start_system_button.pack()

    def stop_system_window(self):
        self.create_new_window("Stop system", size_x=180, size_y=110)

        self.create_label_in_new_window(self.new_window, text="Raspberry_face_ip", x_position=0, y_position=0)
        self.rasp_1_stop_input = self.create_user_input_in_new_window(self.new_window, x_position=0, y_position=0)

        self.stop_system_button = Button(self.new_window, text="Start", command=self.stop_system_from_gui)
        self.stop_system_button.pack()

    def check_system_window(self):
        self.create_new_window("Check system", size_x=180, size_y=110)

        self.create_label_in_new_window(self.new_window, text="Raspberry_face_ip", x_position=0, y_position=0)
        self.rasp_1_check_input = self.create_user_input_in_new_window(self.new_window, x_position=0, y_position=0)

        self.start_system_button = Button(self.new_window, text="Start", command=self.check_status_from_gui)
        self.start_system_button.pack()

    def start_system_from_gui(self):
        if start_system(self.rasp_1_start_input , self.rasp_2_start_input):
            tkinter.messagebox.showinfo('Information', 'System has been started')
        else:
            tkinter.messagebox.showerror('Error', 'Check your connectivity')

    def check_status_from_gui(self):
        if check_system_status(self.rasp_1_check_input):
            tkinter.messagebox.showinfo('System is on', 'System is on')
        else:
            tkinter.messagebox.showerror('System is off', 'Check your connectivity')

    def stop_system_from_gui(self):
        if stop_system(self.rasp_1_stop_input):
            tkinter.messagebox.showinfo('Information', 'System has been stopped')
        else:
            tkinter.messagebox.showerror('Error', 'Check your connectivity')

    def exit(self):
        sys.exit(0)


if __name__ == "__main__":
    app = GuiManager()
    app.geometry("%dx%d%+d%+d" % (375, 405, 400, 125))
    app.resizable(False, False)
    app.mainloop()
