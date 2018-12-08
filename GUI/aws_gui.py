#!/usr/bin/python3

#-----------------------------------------------------------
# Name: Access_control_system_based_on_image_recognition
# Authors: Kamil Kryczka, Damian Osinka
# Thesis supervisor: dr hab. inz. Mikołaj Leszczuk
# Purpose: Engineering Thesis
# Created: 13-10-2018
#-----------------------------------------------------------
import sys
sys.path.append("../")

import PIL.Image
import tkinter.messagebox
import tkinter as tk
from tkinter import *
from PIL import ImageTk
from tkinter.filedialog import askopenfilename
from Access_control_system_based_on_image_recognition.Database.Database import *
from Access_control_system_based_on_image_recognition.Raspberry_face.face_recognition import *
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
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.aws_communication_obj = FaceRecognition()

    def create_label(self, text, x_position, y_position, size):
        text_field = Label(self, text=text, font=("Helvetica bold", size), anchor= CENTER)
        text_field.place(x=x_position, y=y_position)

    def create_img(self, image_name, x_position, y_position):
        load = PIL.Image.open(image_name)
        render = ImageTk.PhotoImage(load)
        img = Label(self, image=render)
        img.Image = render
        img.place(x=x_position, y=y_position)

    def create_label_in_new_window(self, new_window_object, text, x_position=0, y_position=0):
        label = Label(new_window_object, text=text, font=("Helvetica bold", 10), bg ="grey", anchor= CENTER)
        label.pack()
        if x_position != 0 or y_position != 0:
            label.place(x=x_position, y=y_position)

    def create_user_input_in_new_window(self, new_window_object, password=None, x_position=0, y_position=0):
        if not password:
            user_input = Entry(new_window_object)
        else:
            user_input = Entry(new_window_object, show = "*")
        user_input.pack()
        if x_position != 0 or y_position != 0:
            user_input.place(x=x_position, y=y_position)
        return user_input

########################################################################################################################
#----------------------------------------------- GuiManager class -----------------------------------------------------#
########################################################################################################################

class GuiManager(tk.Tk, Utilities):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        Utilities.__init__(self)
        container = Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight =1)
        container.grid_columnconfigure(0, weight=1)

        self.title("Access control system")
        self.frames = {}

        for page in (LoginPage, MainMenuPage):
            frame = page(container, self)
            self.frames[page]= frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(LoginPage)

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
        Utilities.__init__(self)
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

        username = self.name_entry.get()
        password = create_hash(self.password_entry.get())

        if self.db_manager.check_login_and_password_hash("users", username, password):
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
        Utilities.__init__(self)
        self.controller = controller
        self.initialize_toolbar()
        self.path_to_file = ""

    def on_enter_add_new_user(self, event):
        self.l2.configure(text="Add new person in charge")

    def on_enter_del_new_user(self, event):
        self.l2.configure(text="Delete new person in charge")

    def on_enter_exit(self, event):
        self.l2.configure(text="Exit")

    def on_enter_start_system(self, event):
        self.l2.configure(text="Start Access control system")

    def on_enter_stop_system(self, event):
        self.l2.configure(text="Stop Access control system")

    def on_enter_check_system(self, event):
        self.l2.configure(text="Check Access control system status")

    def on_enter_add_new_data(self, event):
        self.l2.configure(text="Insert new face picture, plate number or relation")

    def on_enter_del_data(self, event):
        self.l2.configure(text="Delete face picture, plate number or relation")

    def on_enter_search_data(self, event):
        self.l2.configure(text="Search face picture, plate number or relation")

    def on_leave(self, enter):
        self.l2.configure(text="Access control system")

    def initialize_toolbar(self):
        self.l2 = tk.Label(self, text="",height=1, width=50)
        self.l2.place(x=0, y=0)

        self.add_user_img = tk.PhotoImage(file="add_user.png")
        self.add_user_button = Button(self, image=self.add_user_img, width="120", height="120", command=self.add_new_user)
        self.add_user_button.place(x=0, y=17)

        self.add_user_button.bind("<Enter>", self.on_enter_add_new_user)
        self.add_user_button.bind("<Leave>", self.on_leave)

        self.del_user_img = tk.PhotoImage(file="delete_user.png")
        self.del_user_button = Button(self, image=self.del_user_img, width="120", height="120", command=self.delete_user)
        self.del_user_button.place(x=125, y=17)

        self.del_user_button.bind("<Enter>", self.on_enter_del_new_user)
        self.del_user_button.bind("<Leave>", self.on_leave)

        self.exit_img = tk.PhotoImage(file="exit.png")
        self.exit_button = Button(self, image=self.exit_img, width="120", height="120", command=self.exit)
        self.exit_button.place(x=250, y=17)

        self.exit_button.bind("<Enter>", self.on_enter_exit)
        self.exit_button.bind("<Leave>", self.on_leave)

        self.start_system_img = tk.PhotoImage(file="start_system.png")
        self.start_system_button = Button(self, image=self.start_system_img, width="120", height="120", command=self.start_system_window)
        self.start_system_button.place(x=0, y=142)

        self.start_system_button.bind("<Enter>", self.on_enter_start_system)
        self.start_system_button.bind("<Leave>", self.on_leave)

        self.stop_system_img = tk.PhotoImage(file="stop_system.png")
        self.stop_system_button = Button(self, image=self.stop_system_img, width="120", height="120", command=self.stop_system_window)
        self.stop_system_button.place(x=125, y=142)

        self.stop_system_button.bind("<Enter>", self.on_enter_stop_system)
        self.stop_system_button.bind("<Leave>", self.on_leave)

        self.info_img = tk.PhotoImage(file="info.png")
        self.info_button = Button(self, image=self.info_img, width="120", height="120", command=self.check_system_window)
        self.info_button.place(x=250, y=142)

        self.info_button.bind("<Enter>", self.on_enter_check_system)
        self.info_button.bind("<Leave>", self.on_leave)

        self.upload_img = tk.PhotoImage(file="upload.png")
        self.upload_button = Button(self, image=self.upload_img, highlightcolor="red", command=self.upload_window)
        self.upload_button.place(x=0, y=267)

        self.upload_button.bind("<Enter>", self.on_enter_add_new_data)
        self.upload_button.bind("<Leave>", self.on_leave)

        self.delete_img = tk.PhotoImage(file="delete.png")
        self.delete_button = Button(self, image=self.delete_img, highlightcolor="red", command=self.delete_window)
        self.delete_button.place(x=125, y=267)

        self.delete_button.bind("<Enter>", self.on_enter_del_data)
        self.delete_button.bind("<Leave>", self.on_leave)

        self.search_img = tk.PhotoImage(file="search.png")
        self.search_button = Button(self, image=self.search_img, highlightcolor="red", command=self.search_window)
        self.search_button.place(x=250, y=267)

        self.search_button.bind("<Enter>", self.on_enter_search_data)
        self.search_button.bind("<Leave>", self.on_leave)

        self.back_home_img = tk.PhotoImage(file="logout2.png")
        self.back_home_button = Button(self, image=self.back_home_img, width="375", height="80", command=self.back_login_page)
        self.back_home_button.place(x=0, y=392)

    def upload_window(self):
        self.create_new_window("", size_x=280, size_y=370)

        self.create_label_in_new_window(self.new_window, text="Upload face picture:", x_position=72, y_position=5)

        self.upload2_img = tk.PhotoImage(file="upload2.png")
        self.upload2_button = Button(self.new_window, image=self.upload2_img, command=self.type_photo_path)
        self.upload2_button.pack()
        self.upload2_button.place(x=95, y=25)

        self.file_path_label_info = Label(self.new_window, text="selected file:", background="grey")
        self.file_path_label_info.pack()
        self.file_path_label_info.place(x=55, y=140)

        self.create_label_in_new_window(self.new_window, text="Type name and surname:\n for instance John_Smith:", x_position=55, y_position=165)

        self.file_plate_input = self.create_user_input_in_new_window(self.new_window, x_position=56, y_position=200)

        self.file_plate_button = Button(self.new_window, text="Confirm", command=self.send_photo_to_aws)
        self.file_plate_button.pack()
        self.file_plate_button.place(x=100, y=220)

        self.create_label_in_new_window(self.new_window, text="Add relation to db\nphoto face - plate number:", x_position=48, y_position=280)

        self.add_photo_face_input = Entry(self.new_window, width=10)
        self.add_photo_face_input.pack()
        self.add_photo_face_input.place(x=48, y=315)

        self.add_plate_number_input = Entry(self.new_window, width=10)
        self.add_plate_number_input.pack()
        self.add_plate_number_input.place(x=139, y=315)

        self.add_relation_button = Button(self.new_window, text="Confirm", command=self.add_relation_photo_plate)
        self.add_relation_button.pack()
        self.add_relation_button.place(x=100, y=335)

    def delete_window(self):

        self.create_new_window("", size_x=220, size_y=240)

        self.create_label_in_new_window(self.new_window, text="Delete template photo face:", x_position=13, y_position=5)
        self.del_face_photo_input = self.create_user_input_in_new_window(self.new_window, x_position=23, y_position=25)

        self.del_face_photo_button = Button(self.new_window, text="Confirm", command=self.del_face_photo_from_aws)
        self.del_face_photo_button.pack()
        self.del_face_photo_button.place(x=62, y=45)


        self.create_label_in_new_window(self.new_window, text="Delete owner from db:", x_position=35, y_position=80)
        self.del_owner_input = self.create_user_input_in_new_window(self.new_window, x_position=23, y_position=105)

        self.del_owner_button = Button(self.new_window, text="Confirm", command=self.del_owner_from_db)
        self.del_owner_button.pack()
        self.del_owner_button.place(x=62, y=126)

        self.create_label_in_new_window(self.new_window, text="Delete number plate from db:", x_position=10, y_position=162)
        self.del_plate_input = self.create_user_input_in_new_window(self.new_window, x_position=23, y_position=185)

        self.del_plate_button = Button(self.new_window, text="Confirm", command=self.del_plate_from_db)
        self.del_plate_button.pack()
        self.del_plate_button.place(x=62, y=206)


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

        self.create_label_in_new_window(self.new_window, text="Enter your username")
        self.username_input = self.create_user_input_in_new_window(self.new_window)

        self.create_label_in_new_window(self.new_window, text="Enter your Password")
        self.password_input = self.create_user_input_in_new_window(self.new_window, password=True)

        self.create_label_in_new_window(self.new_window, text="Confirm your Password")
        self.password_confirm_input = self.create_user_input_in_new_window(self.new_window, password=True)

        self.add_user_button = Button(self.new_window, text="Confirm", command=self.add_user_to_db)
        self.add_user_button.pack()

    def delete_user(self):
        self.create_new_window("Delete user", size_x=180, size_y=70)

        self.create_label_in_new_window(self.new_window, text="Enter username to delete")
        self.username_to_delete = self.create_user_input_in_new_window(self.new_window)

        self.del_user_button = Button(self.new_window, text="Confirm", command=self.del_user_from_db)
        self.del_user_button.pack()

    def start_system_window(self):
        self.create_new_window("Start system", size_x=180, size_y=110)

        self.create_label_in_new_window(self.new_window, text="Raspberry_face_ip")
        self.rasp_1_start_input = self.create_user_input_in_new_window(self.new_window)
        self.rasp_1_start_input.insert(0, "192.168.2.100")

        self.create_label_in_new_window(self.new_window, text="Raspberry_plate_ip")
        self.rasp_2_start_input = self.create_user_input_in_new_window(self.new_window)

        self.start_system_button = Button(self.new_window, text="Start", command=self.start_system_from_gui)
        self.start_system_button.pack()

    def stop_system_window(self):
        self.create_new_window("Stop system", size_x=180, size_y=70)

        self.create_label_in_new_window(self.new_window, text="Raspberry_face_ip")
        self.rasp_1_stop_input = self.create_user_input_in_new_window(self.new_window)
        self.rasp_1_stop_input.insert(0, "192.168.2.100")

        self.stop_system_button = Button(self.new_window, text="Start", command=self.stop_system_from_gui)
        self.stop_system_button.pack()

    def check_system_window(self):
        self.create_new_window("Check system", size_x=180, size_y=70)

        self.create_label_in_new_window(self.new_window, text="Raspberry_face_ip")
        self.rasp_1_check_input = self.create_user_input_in_new_window(self.new_window)
        self.rasp_1_check_input.insert(0, "192.168.2.100")

        self.start_system_button = Button(self.new_window, text="Start", command=self.check_status_from_gui)
        self.start_system_button.pack()

# I RZĄD
# _____________________________________________________________________________________

    def add_user_to_db(self):
        username = self.username_input.get()
        password_hash = create_hash(self.password_input.get())
        password_confirm_hash = create_hash(self.password_confirm_input.get())

        if username == "" or password_hash == "" or password_confirm_hash == "":
            tkinter.messagebox.showerror('Error', 'Please, fill all fields')

        elif password_hash != password_confirm_hash:
            tkinter.messagebox.showerror('Error', 'Password does not match the confirm password')

        elif self.db_manager.check_if_user_in_database(username):
            tkinter.messagebox.showerror("Error", "User already exists!")

        elif self.db_manager.add_user_to_db(username, password_hash):
            tkinter.messagebox.showinfo("Error", "User has been added!")

        else:
            tkinter.messagebox.showerror("Error", "There is a problem with the database connection")

    def del_user_from_db(self):
        username = self.username_to_delete.get()

        if self.db_manager.check_if_user_in_database(username):
            if self.db_manager.del_user_from_db(username):
                tkinter.messagebox.showinfo('Information', 'User has been deleted!')
            else:
                tkinter.messagebox.showinfo('There is a problem with the database connection')
        else:
            tkinter.messagebox.showwarning('Warming', "user doesn't exist\nPlease try again!")
# _____________________________________________________________________________________

# II RZĄD
#_____________________________________________________________________________________
    def start_system_from_gui(self):
        result = start_system(self.rasp_1_start_input , self.rasp_2_start_input)
        if result == "ON":
            tkinter.messagebox.showinfo('Information', 'System has been started')
        elif result == "ALREADY_RUNNING":
            tkinter.messagebox.showinfo('Information', 'System is already running')
        else:
            tkinter.messagebox.showerror('Error', 'Check your connectivity')
        self.new_window.destroy()

    def check_status_from_gui(self):
        result = check_system_status(self.rasp_1_check_input)
        if result == "ON":
            tkinter.messagebox.showinfo('Information', 'System is on')
        elif result == "OFF":
            tkinter.messagebox.showinfo('Information', 'System is off')
        else:
            tkinter.messagebox.showerror('Check your connectivity', 'Check your connectivity')
        self.new_window.destroy()

    def stop_system_from_gui(self):
        if stop_system(self.rasp_1_stop_input):
            tkinter.messagebox.showinfo('Information', 'System has been stopped')
        else:
            tkinter.messagebox.showerror('Error', 'Check your connectivity')
        self.new_window.destroy()

#_____________________________________________________________________________________

# III RZĄD
# _____________________________________________________________________________________

    def type_photo_path(self):

        try:
            self.file_path_label.destroy()
        except:
            pass

        self.path_to_file = str(askopenfilename())
        split_list = self.path_to_file.split('/')
        file_name = split_list[(len(split_list) - 1)]

        if self.path_to_file != "":
            self.sel_img = Label(self.new_window, text = "Selected image:", background="grey")

            self.file_path_label = Label(self.new_window, text = file_name, background="grey")
            self.file_path_label.pack()
            self.file_path_label.place(x=138, y=140)


    def send_photo_to_aws(self):
        name_surname = self.file_plate_input.get()
        if name_surname == "" or self.path_to_file == "":
            tkinter.messagebox.showerror('Name, surname and photo', 'Please, type picture and name')
        else:
            if self.aws_communication_obj.add_face_to_collection(self.path_to_file, name_surname):
                tkinter.messagebox.showinfo('Name, surname and photo', 'The picture has been added to aws collection')
            else:
                tkinter.messagebox.showerror('An error occured. Face has not been added to collection!')

    def add_relation_photo_plate(self):
        owner = self.add_photo_face_input.get()
        plate_number = self.add_plate_number_input.get()
        if owner == "" or plate_number == "":
            tkinter.messagebox.showerror("Error", "Please, fill both fields")
        else:
            if self.db_manager.add_licence_plate_and_owner_to_db(plate_number, owner):
                tkinter.messagebox.showinfo("Info", "Relation has been added to db")
            else:
                tkinter.messagebox.showerror("Error", "Error")

    def del_face_photo_from_aws(self):
        face_photo_name = self.del_face_photo_input.get()
        if not face_photo_name == "":
            if self.aws_communication_obj.remove_face_from_collection(face_photo_name):
                tkinter.messagebox.showinfo("Info", "Photo has been deleted")
            else:
                tkinter.messagebox.showerror("Error", "Face does not exist in collection!")
        else:
            tkinter.messagebox.showinfo("Error", "Please type photo name")

    def del_owner_from_db(self):
        owner_to_delete = self.del_owner_input.get()
        if not owner_to_delete == "":
            self.db_manager.del_owner_from_database(owner_to_delete)
            tkinter.messagebox.showinfo("Info", "info")
        else:
            tkinter.messagebox.showerror("Error", "Please, type user")

    def del_plate_from_db(self):
        plate_to_delete = self.del_plate_input.get()
        if not plate_to_delete == "":
            self.db_manager.del_licence_plate_from_database(plate_to_delete)
            tkinter.messagebox.showinfo("Info", "Plate number has been deleted")
        else:
            tkinter.messagebox.showerror("Error", "Please, type plate number")

    def search_window(self):
        self.create_new_window("", size_x=190, size_y=370)

        self.create_label_in_new_window(self.new_window, text="Face patterns from AWS:")

        listFrame = Frame(self.new_window)
        listFrame.pack(side=TOP, padx=5, pady=5)

        scrollBar = Scrollbar(listFrame)
        scrollBar.pack(side=RIGHT, fill=Y)
        self.listBox = Listbox(listFrame, selectmode=SINGLE)
        self.listBox.pack(side=LEFT, fill=Y)
        scrollBar.config(command=self.listBox.yview)
        self.listBox.config(yscrollcommand=scrollBar.set)

        aws_faces_collection = self.aws_communication_obj.list_faces_in_collection()
        for item in aws_faces_collection:
            self.listBox.insert(END, item)

        self.create_label_in_new_window(self.new_window, text="Owner and plate number:")

        listFrame2 = Frame(self.new_window)
        listFrame2.pack(side=TOP, padx=5, pady=5)

        scrollBar2 = Scrollbar(listFrame2)
        scrollBar2.pack(side=RIGHT, fill=Y)
        self.listBox2 = Listbox(listFrame2, selectmode=SINGLE)
        self.listBox2.pack(side=LEFT, fill=Y)
        scrollBar2.config(command=self.listBox2.yview)
        self.listBox2.config(yscrollcommand=scrollBar2.set)


        output = self.db_manager.fetch_licence_plates_and_owners()
        for owner in output:
            self.listBox2.insert(END, owner)
            for plate_n in output[owner]:
                self.listBox2.insert(END, "--- " + plate_n)


    def back_login_page(self):
        self.controller.show_frame(LoginPage)

    def exit(self):
        sys.exit(0)


if __name__ == "__main__":
    app = GuiManager()
    app.geometry("%dx%d%+d%+d" % (375, 479, 400, 125))
    app.resizable(False, False)
    app.mainloop()
