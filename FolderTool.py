import os
import re
import time
import sqlite3
from tkinter import DISABLED, NORMAL, Tk, VERTICAL, HORIZONTAL, W, E, IntVar, StringVar
from sqlite3 import Error
from tkinter.messagebox import showinfo, askokcancel
from tkinter.ttk import Separator, Entry, Progressbar, Button, Checkbutton, Radiobutton, Label

dbpath = r"C:\sqlite\db"
dbfilename = "pythonsqlite"

"""
Program made by Maarten Meijer

This was made for easily extracting a folder structure, storing all folders with a code like 'EU123456'.
After scanning, the tool makes it easy to open their file explorer at a desired path.

Made for Windows, but may also work on Linux or MacOS (never tested)

20/04/2020
"""


def main():
    dblocation = dbpath + "\\" + dbfilename + ".db"
    def create_connection(db_file):
        conn = None
        try:
            conn = sqlite3.connect(db_file)
            return conn
        except Error as e:
            # Just hope this doesn't happen
            pass

        return conn

    def execute_sql(conn, sql):
        try:
            c = conn.cursor()
            c.execute(sql)
        except Error as e:
            #Just hope this doesn't happen
            pass

    def insert_sql(conn, path):
        try:
            sql = ''' INSERT OR REPLACE INTO paths (id, path)
                          VALUES(?,?) '''
            c = conn.cursor()
            c.execute(sql, path)
        except Error as e:
            # Just hope this doesn't happen
            pass

    def delete_entries():
        conn = create_connection(dblocation)
        if conn is not None:
            c = conn.cursor()
            c.execute("DELETE FROM paths WHERE id > 0")
            conn.commit()
            conn.close()

    def search(id):
        conn = create_connection(dblocation)
        if conn is not None:
            c = conn.cursor()
            c.execute("SELECT path FROM paths WHERE id={}".format(id))
            var = c.fetchone()[0]
            conn.commit()
            conn.close()
            return var

    def delete_ranged_entries(min, max):
        conn = create_connection(dblocation)
        if conn is not None:
            c = conn.cursor()
            c.execute("DELETE FROM paths WHERE id BETWEEN {} AND {}".format(min, max))
            conn.commit()
            conn.close()

    def delete_one_entry(id):
        conn = create_connection(dblocation)
        if conn is not None:
            c = conn.cursor()
            c.execute("DELETE FROM paths WHERE id = {}".format(id))
            conn.commit()
            conn.close()

    def initialize():
        if not os.path.exists(dblocation):
            os.makedirs(dbpath)
        conn = create_connection(dblocation)
        sql_table = """ CREATE TABLE IF NOT EXISTS paths (
                            id integer PRIMARY KEY,
                            path text
                            );"""
        if conn is not None:
            execute_sql(conn, sql_table)

    def get_rows():
        conn = create_connection(dblocation)
        if conn is not None:
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM paths")
            var = c.fetchone()[0]
            conn.commit()
            conn.close()
            return var

    def scan_folder(folder):
        pb["value"] = 0
        conn = create_connection(dblocation)
        if conn is not None:
            counter = 0
            toplevel = [f for f in os.listdir(folder) if os.path.isdir(os.path.join(folder, f))]
            startime = time.time()
            progress = -1
            for root, dirs, files in os.walk(folder):
                for top in toplevel:
                    if root == folder + "\\" + top:
                        progress += 1
                        pbtext1["text"] = "Scanning..."
                        pbtext2["text"] = "Looking inside folder: {}".format(top)
                        pb["value"] = round((progress / len(toplevel)) * 100)
                        window.update_idletasks()
                counter += 1
                regex = re.search("(EU|ME|US|FR|CN|EA)[0-9]{6}", root)
                if regex:
                    if conn is not None:
                        insert_sql(conn, (regex.group()[2::], root))
                    dirs[:] = []
                    files[:] = []
            endtime = time.time()
            pbtext1["text"] = "Scan completed!"
            pbtext2["text"] = "Scanned {} folders in {} seconds\n".format(counter, round(endtime - startime))
            pb["value"] = 100
            conn.commit()
            conn.close()

    def scan_folder_exclude(folder, exclude):
        pb["value"] = 0
        conn = create_connection(dblocation)
        if conn is not None:
            counter = 0
            toplevel = [f for f in os.listdir(folder) if os.path.isdir(os.path.join(folder, f))]
            startime = time.time()
            progress = 0
            for root, dirs, files in os.walk(folder):
                dirs[:] = [d for d in dirs if d != exclude]
                for top in toplevel:
                    if root == folder + "\\" + top:
                        progress += 1
                        pbtext1["text"] = "Scanning..."
                        pbtext2["text"] = "Looking inside folder: {}".format(top)
                        pb["value"] = round((progress / len(toplevel)) * 100)
                        window.update_idletasks()
                if root.startswith(exclude):
                    dirs[:] = []
                    files[:] = []
                    continue
                counter += 1
                regex = re.search("(EU|ME|US|FR|CN|EA)[0-9]{6}", root)
                if regex:
                    if conn is not None:
                        insert_sql(conn, (regex.group()[2::], root))
                    dirs[:] = []
                    files[:] = []
            endtime = time.time()
            pbtext1["text"] = "Scan completed!"
            pbtext2["text"] = "Scanned {} folders in {} seconds\n".format(counter, round(endtime - startime))
            pb["value"] = 100
            conn.commit()
            conn.close()


    def scanbutton():
        if os.path.isdir(folder.get()):
            if vex.get() == 5:
                if os.path.isdir(exclude.get()):
                    scan_folder_exclude(folder.get(), exclude.get())
                else:
                    showinfo("Error", "Could not find folder: {}".format(exclude.get()))
            else:
                scan_folder(folder.get())
        else:
            showinfo("Error", "Could not find folder: {}".format(folder.get()))
        currententries["text"] = "Database currently has {} folder shortcuts".format(get_rows())

    def searchbutton():
        var = projectid.get()
        if len(var) >= 8:
            var = var[2:]
        try:
            os.startfile(search(var))
        except:
            showinfo("Error","Could not find a project with ID: {}".format(var))

    def deletebutton():
        if vdel.get() == 1:
            ok = askokcancel("Warning","You are about to delete ALL folder shortcuts in the database!\nThis means that you will have to scan all projects again to use this tool.\n\nPress ok to proceed or cancel to quit")
            if ok:
                pbtext1["text"] = "Deleting..."
                pbtext2["text"] = ""
                pb["value"] = 0
                delete_entries()
                pbtext1["text"] = "Deleted all folder shortcuts!"
                pbtext2["text"] = ""
                pb["value"] = 100

        elif vdel.get() == 2:
            varone = vone.get()
            if len(varone) >= 8:
                varone = varone[:8]
            try:
                int(varone)
                pbtext1["text"] = "Deleting..."
                pbtext2["text"] = ""
                pb["value"] = 0
                delete_one_entry(varone)
                pbtext1["text"] = "Deleted one folder shortcut (if it existed)!"
                pbtext2["text"] = ""
                pb["value"] = 100
            except:
                showinfo("Error",
                         "The project id: {} is not formatted correctly".format(varone))
        elif vdel.get() == 3:
            varmin = vmin.get()
            varmax = vmax.get()
            if len(varmin) >= 8:
                varmin = varmin[:8]
            if len(varmax) >= 8:
                varmax = varmax[:8]
            try:
                int(varmin)
                int(varmax)
                pbtext1["text"] = "Deleting..."
                pbtext2["text"] = ""
                pb["value"] = 0
                delete_ranged_entries(varmin, varmax)
                pbtext1["text"] = "Deleted all folder shortcuts in the range!"
                pbtext2["text"] = ""
                pb["value"] = 100
            except:
                showinfo("Error", "The variables:\n\tMin: {}\n\tMax: {}\nare not formatted correctly".format(varmin, varmax))
        currententries["text"] = "Database currently has {} folder shortcuts".format(get_rows())
    def clickall():
        one["state"] = DISABLED
        vone.set("EU123456")
        min["state"] = DISABLED
        vmin.set("min")
        max["state"] = DISABLED
        vmax.set("max")

    def clickone():
        one["state"] = NORMAL
        vone.set("")
        min["state"] = DISABLED
        vmin.set("min")
        max["state"] = DISABLED
        vmax.set("max")

    def clickminmax():
        one["state"] = DISABLED
        vone.set("EU123456")
        min["state"] = NORMAL
        vmin.set("")
        max["state"] = NORMAL
        vmax.set("")

    def clickexclude():
        if vex.get() == 5:
            exclude["state"] = NORMAL
        else:
            exclude["state"] = DISABLED

    def character_limit(entry_text):
        if len(entry_text.get()) > 8:
            entry_text.set(entry_text.get()[:8])

    window = Tk()
    window.geometry('800x300')
    window.title("FolderTool")

    separator = Separator(orient=VERTICAL)
    separator.grid(column=1,rowspan=13, sticky="ns")
    separator = Separator(orient=HORIZONTAL)
    separator.grid(columnspan=10, row=1, sticky="ew")
    separator = Separator(orient=HORIZONTAL)
    separator.grid(columnspan=10, row=5, sticky="ew")
    separator = Separator(orient=HORIZONTAL)
    separator.grid(columnspan=10, row=7, sticky="ew")

    title = Label(window, text="Open project", font=("", 20))
    title.grid(column=0, row=0, sticky=W)
    title = Label(window, text="Scan", font=("", 20))
    title.grid(column=2, row=0, sticky=W)
    title = Label(window, text="Delete", font=("", 20))
    title.grid(column=2, row=6, sticky=W)
    title = Label(window, text="Info", font=("", 20))
    title.grid(column=0, row=6, sticky=W)

    btn = Button(window, text="Open project", command=searchbutton)
    btn.grid(column=0, row=4, sticky=E, padx=10)
    btn = Button(window, text="Scan", command=scanbutton)
    btn.grid(column=2, row=4, sticky=E, padx=10)
    btn = Button(window, text="Delete", command=deletebutton)
    btn.grid(column=2, row=12, sticky=E, padx=10)

    text = Label(window, text="Scan folder: ")
    text.grid(column=2, row=2, sticky=W)
    #text = Label(window, text="Exclude folder: ")
    #text.grid(column=2, row=3, sticky=W)
    text = Label(window, text="Project ID: ")
    text.grid(column=0, row=2, sticky=W)

    vex = IntVar()
    excludebutton = Checkbutton(window, text="Exclude a folder from the scan", variable=vex, onvalue=5, offvalue=0, command=clickexclude)
    excludebutton.grid(column=2, row=3, sticky=W)

    vid = StringVar()
    vid.set("EU123456")
    vid.trace('w', lambda *args: character_limit(vid))
    projectid = Entry(window, width=9, textvariable=vid)
    projectid.grid(column=0,row=2, padx=10, sticky=E)

    folder = Entry(window, width=30)
    folder.grid(column=2, row=2, padx=10, sticky=E)

    exclude = Entry(window, width=30, state=DISABLED)
    exclude.grid(column=2, row=3, padx=10, sticky=E)

    vdel = IntVar()
    delall = Radiobutton(window, text="Delete all folder shortcuts", variable=vdel, value=1, command=clickall)
    delall.grid(column=2,row=8, sticky=W)
    delone = Radiobutton(window, text="Delete one folder shortcut", variable=vdel,value=2, command=clickone)
    delone.grid(column=2,row=9, sticky=W)
    delminmax = Radiobutton(window, text="Selective delete folder shortcuts", variable=vdel,value=3, command=clickminmax)
    delminmax.grid(column=2, row=10, sticky=W)

    vmin = StringVar()
    vmin.set("min")
    vmax = StringVar()
    vmax.set("max")
    vone = StringVar()
    vone.set("EU123456")
    vmin.trace('w', lambda *args: character_limit(vmin))
    vmax.trace('w', lambda *args: character_limit(vmax))
    vone.trace('w', lambda *args: character_limit(vone))
    one = Entry(window, width=9, textvariable=vone, state=DISABLED)
    one.grid(column=2, row=9, padx=10, sticky=E)
    min = Entry(window, width=9, textvariable=vmin, state=DISABLED)
    min.grid(column=2, row=10, padx=10, sticky=E)
    max = Entry(window, width=9, textvariable=vmax, state=DISABLED)
    max.grid(column=2, row=11, padx=10, sticky=E)

    currententries = Label(window,text="Database currently has {} folder shortcuts".format(get_rows()))
    currententries.grid(column=0,row=8,sticky=W)

    pbtext1 = Label(window)
    pbtext1.grid(column=0, row=10, sticky=W)
    pbtext2 = Label(window)
    pbtext2.grid(column=0, row=11, sticky=W)
    pb = Progressbar(window, orient=HORIZONTAL, length=200, mode="determinate", maximum=100)
    pb.grid(column=0, row=12)

    maartentext = Label(window, text="Made by Maarten Meijer")
    maartentext.grid(column=0,columnspan=3, row=13)

    window.grid_rowconfigure(0, weight=1)
    window.grid_rowconfigure(2, weight=1)
    window.grid_rowconfigure(3, weight=1)
    window.grid_rowconfigure(4, weight=1)
    window.grid_rowconfigure(6, weight=1)
    window.grid_rowconfigure(8, weight=1)
    window.grid_rowconfigure(9, weight=1)
    window.grid_rowconfigure(10, weight=1)
    window.grid_rowconfigure(11, weight=1)
    window.grid_rowconfigure(12, weight=1)
    window.grid_rowconfigure(13, weight=1)
    window.grid_columnconfigure(0, weight=1)
    window.grid_columnconfigure(2, weight=1)

    #window.wm_iconbitmap('MyIcon.ico')
    window.resizable(False,False)
    window.mainloop()


main()