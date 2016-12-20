#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from Tkinter import *
import FileDialog
import tkFileDialog as filedialog
from tkFileDialog import askopenfilename
from tkFileDialog import asksaveasfilename
import win32com.client as win32
import matplotlib.backends.tkagg
import os.path
import tkMessageBox
import string as anotherstr
from sas7bdat import SAS7BDAT
import matplotlib as mpl
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
from collections import Counter
from matplotlib.widgets import Lasso
from matplotlib.colors import colorConverter
from matplotlib.collections import RegularPolyCollection
from matplotlib import path
from PIL import ImageTk, Image
import ttk
import collections

# Delete Default window

root = Tk()
root.withdraw()

# Generate a text message instruct how to use this program

tkMessageBox.showinfo('Simba 1.1',
                      'Choose the Data Specification Form for this study'
                      )

with open('initialpath.txt') as input_file:
    for i in input_file:
        initialpath = i
        break


def loaderror():

    window = Toplevel()
    window.title('Warning')
    window.configure(background='white')
    img = ImageTk.PhotoImage(Image.open('IMG_5029.jpg'))
    panel = Label(window, image=img)
    panel.pack(side='bottom', fill='both', expand='yes')
    window.mainloop()
    return


# Create buttons

def loadsas():
    global readsas
    global sasdata
    global variablelist
    global df
    global variablelengths
    tkMessageBox.showinfo('Loading data',
                          'Choose SAS dataset you want to QC')
    readsas = askopenfilename(initialdir=initialpath)
    if str(readsas).find('.sas7bdat') == -1:
        tkMessageBox.showinfo('Error!', 'Not a SAS dataset')
        readsas = None
        return
    sasdata = SAS7BDAT(os.path.normcase(str(readsas)))

    variablelist = [item.encode('utf-8') for item in
                    sasdata.column_names]

    variablelengths = [float(x) / 8 + 0.55 for x in
                       sasdata.column_data_lengths]

    data = np.vstack([[(item.encode('utf-8') if isinstance(item,
                     basestring) else item) for item in row] for row in
                     sasdata])

    data = data[1:]
    df = pd.DataFrame(data, columns=variablelist)

    sasdata.close()

    tkMessageBox.showinfo('Note', 'Finished!')


def varfreq():
    if readsas is None:
        loaderror()
        return
    list_name = [item.encode('utf-8') for item in sasdata.column_names]
    list_type = [item.encode('utf-8') for item in sasdata.column_types]
    categorical_var = [list_name[i] for i in range(len(list_type))
                       if list_type[i] == 'string']
    root2 = Toplevel()
    root2.title('Variable Frequency')
    root2.geometry('800x600+200+200')
    treeScroll = ttk.Scrollbar(root2)
    tree = ttk.Treeview(root2)
    ttk.Style().configure('.', font=('Helvetica', 10),
                          foreground='black')
    treeScroll.configure(command=tree.yview)
    tree.configure(yscrollcommand=treeScroll.set)
    tree['columns'] = ('value', 'n')
    tree.column('n', width=100)
    tree.column('value', width=100)
    tree.heading('n', text='n')
    tree.heading('value', text='category')
    nobs = len(df)
    m = 0

    for i in list_name:
        cvar = Counter([x for x in df[i] if x is not None])
        distin = len(cvar)
        tree.insert('', m, i, text=i, tags=('title', ))
        m += 1
        cvar_order = collections.OrderedDict(sorted(cvar.items()))
        missing = nobs - len([x for x in df[i] if x is not None and x
                             is not ''])
        if '' in cvar_order:
            del cvar_order['']
        if missing != 0:
            tree.insert(i, m, text='', values=('missing', missing),
                        tags=(('oddrow' if m % 2 == 1 else 'evenrow'),
                        ))
            m += 1
        distin = len(cvar_order)
        tree.insert(i, m, text='', values=('Unique Value', distin),
                    tags=(('oddrow' if m % 2 == 1 else 'evenrow'), ))
        m += 1
        for j in cvar_order:
            tree.insert(i, m, text='', values=(j, cvar_order[j]),
                        tags=(('oddrow' if m % 2 == 1 else 'evenrow'),
                        ))
            m += 1

    tree.tag_configure('title', background='white')
    tree.tag_configure('oddrow', background='lightskyblue')
    tree.tag_configure('evenrow', background='blanchedalmond')
    tree.pack(expand=YES, fill=BOTH)
    root2.mainloop()


def varstat():
    if readsas is None:
        loaderror()
        return
    list_type = [item.encode('utf-8') for item in sasdata.column_types]
    list_name = [item.encode('utf-8') for item in sasdata.column_names]
    continues_var = [list_name[i] for i in range(len(list_type))
                     if list_type[i] == 'number']
    root2 = Toplevel()
    root2.title('Variable Statistics')
    root2.geometry('800x600+200+200')
    tree = ttk.Treeview(root2)
    ttk.Style().configure('.', font=('Helvetica', 10),
                          foreground='black')
    tree['columns'] = ('n', 'max', 'min', 'missing')
    tree.column('n', width=100)
    tree.column('max', width=100)
    tree.column('min', width=100)
    tree.column('missing', width=100)

    tree.heading('n', text='n')
    tree.heading('max', text='max')
    tree.heading('min', text='min')
    tree.heading('missing', text='missing')

    nobs = len(df)
    m = 0
    for i in continues_var:
        if [x for x in df[i] if x is not None] == []:
            continue
        n = len([x for x in df[i] if x is not None])
        tree.insert('', m, text=i, values=(n, max([x for x in df[i]
                    if x is not None]), min([x for x in df[i] if x
                    is not None]), nobs - n), tags=(('oddrow' if m % 2
                    == 1 else 'evenrow'), ))
        m += 1
    tree.tag_configure('oddrow', background='white')
    tree.tag_configure('evenrow', background='lightgrey')
    tree.pack(expand=YES, fill=BOTH)
    root2.mainloop()


def bar_plot():
    global subjectlvlvar
    if readsas is None:
        loaderror()
        return

    class MyDialog:

        def __init__(self, parent):

            top = self.top = parent
            Label(top, text='Input ID variable').pack()
            self.e = Entry(top)
            self.e.pack(padx=5)
            b = Button(top, text='OK', command=self.ok)
            b.pack(pady=5)

        def ok(self):
            global ID_var
            if self.e.get() in sasdata.column_names:
                ID_var = self.e.get()
                self.top.destroy()
            else:
                tkMessageBox.showinfo('ID variable not found in dataset'
                        , 'Warning!')

    root = Toplevel()
    root.update()
    d = MyDialog(root)
    root.wait_window(d.top)
    print ID_var

    EVID = False

    ID_data = df[ID_var]
    subjectlvlvar = {}
    variablelist_freq = [var for var in variablelist
                         if len(list(Counter(df[var]))) < 30]
    for var in variablelist_freq:
        subjectlvlvar[var] = 1
    for var in variablelist_freq:
        detect_data = df[var]
        for i in range(len(detect_data)):
            curid = ID_data[i]
            curvalue = detect_data[i]
            if i > 0:
                if curid == lastid:
                    if curvalue != lastvalue:
                        subjectlvlvar[var] = 0
                        break
            lastid = curid
            lastvalue = curvalue

    sublvlist = []
    nonsublvlist = []
    for key in subjectlvlvar.keys():
        if subjectlvlvar[key] == 1:
            sublvlist.append(key)
        if subjectlvlvar[key] == 0:
            nonsublvlist.append(key)

    class App(object):

        def __init__(
            self,
            master,
            sublvlist,
            nonsublvlist,
            ):

            if nonsublvlist != []:
                self.dict = {'Subject level variable': sublvlist,
                             'Non-subject level variable': nonsublvlist}
            else:
                self.dict = {'Subject level variable': sublvlist}
            self.master = master
            self.variable_a = StringVar(self.master)
            self.variable_b = StringVar(self.master)

            self.variable_a.trace('w', self.update_options)

            self.optionmenu_a = OptionMenu(self.master,
                    self.variable_a, *self.dict.keys())
            self.optionmenu_b = OptionMenu(self.master,
                    self.variable_b, '')
            self.button = Button(self.master, text='  Plot  ',
                                 command=self.select2)
            self.label_a = Label(self.master, text='Variable Type')
            self.label_b = Label(self.master, text='Variable Name')

            self.variable_a.set('Subject level variable')

            self.optionmenu_a.grid(row=0, column=1, padx=5, pady=5)
            self.optionmenu_b.grid(row=1, column=1, padx=5, pady=5)
            self.button.grid(row=2, column=1, padx=5, pady=5)
            self.label_a.grid(row=0, column=0, padx=5, pady=5)
            self.label_b.grid(row=1, column=0, padx=5, pady=5)

        def update_options(self, *args):
            variablelist_subornot = self.dict[self.variable_a.get()]
            self.variable_b.set(variablelist_subornot[0])

            menu = self.optionmenu_b['menu']
            menu.delete(0, 'end')

            for var in variablelist_subornot:
                menu.add_command(label=var, command=lambda nation=var: \
                                 self.variable_b.set(nation))

        def select2(self, *args):
            if self.variable_a.get() == 'Non-subject level variable' \
                and EVID == True:
                curvar = self.variable_b.get()
                countvar = Counter(df[curvar])
                n_groups = len(list(countvar))
                countvar_dose = Counter(df_dose[curvar])
                dose_stat = [countvar_dose[ele] for ele in
                             list(countvar)]
                countvar_pk = Counter(df_pk[curvar])
                pk_stat = [countvar_pk[ele] for ele in list(countvar)]
                stat_max = max(dose_stat + pk_stat)
                fig = plt.figure()

                # ax1 = fig.add_axes((0.10000000000000001,
                # ................   0.40000000000000002, 0.8, .5))

                index = np.arange(n_groups)
                bar_width = 0.15
                opacity = 0.40000000000000002
                error_config = {'ecolor': '0.4'}
                rects1 = plt.bar(
                    index + 1.5 * bar_width,
                    dose_stat,
                    bar_width,
                    alpha=opacity,
                    color='b',
                    error_kw=error_config,
                    label='Dose data',
                    )
                rects2 = plt.bar(
                    index + .5 * bar_width,
                    pk_stat,
                    bar_width,
                    alpha=opacity,
                    color='c',
                    error_kw=error_config,
                    label='PK data',
                    )
                plt.ylim((0, stat_max * 1.25))
                plt.ylabel('Count')
                plt.title(curvar)
                plt.xticks(index + 1.5 * bar_width, list(countvar))
                for rect in rects1:
                    height = rect.get_height()
                    plt.text(rect.get_x() + rect.get_width() / 2., 1.05
                             * height, '%d' % int(height), ha='center',
                             va='bottom')
                for rect in rects2:
                    height = rect.get_height()
                    plt.text(rect.get_x() + rect.get_width() / 2., 1.05
                             * height, '%d' % int(height), ha='center',
                             va='bottom')
            else:
                curvar = self.variable_b.get()
                pairs = [(df[ID_var][i], df[curvar][i]) for i in
                         range(len(df))]
                unique_pairs = set(pairs)
                plot_data = [b for (a, b) in unique_pairs]
                countvar = Counter(plot_data)
                n_groups = len(list(countvar))
                all_stat = [countvar[ele] for ele in list(countvar)]
                stat_max = max(all_stat)
                fig = plt.figure()

                # ax1 = fig.add_axes((0.10000000000000001,
                # ................   0.40000000000000002, 0.8, .5))

                index = np.arange(n_groups)
                bar_width = 0.15
                opacity = 0.40000000000000002
                error_config = {'ecolor': '0.4'}
                rects1 = plt.bar(
                    index + 1 * bar_width,
                    all_stat,
                    bar_width,
                    alpha=opacity,
                    color='b',
                    error_kw=error_config,
                    )
                plt.ylim((0, stat_max * 1.25))
                plt.ylabel('Count')
                plt.title(curvar + ' (Subject-level)')
                plt.xticks(index + 1.5 * bar_width, list(countvar))
                for rect in rects1:
                    height = rect.get_height()
                    plt.text(rect.get_x() + rect.get_width() / 2., 1.05
                             * height, '%d' % int(height), ha='center',
                             va='bottom')
            plt.legend()
            plt.show()

    root = Tk()
    root.title('Bar Plot')
    root.geometry('%dx%d+%d+%d' % (300, 150, 50, 100))
    app = App(root, sublvlist, nonsublvlist)
    root.mainloop()


class Checkbar(Frame):

    def __init__(
        self,
        parent=None,
        picks=[],
        side=LEFT,
        anchor=W,
        dict=None,
        ):

        Frame.__init__(self, parent)
        for pick in picks:
            checkbutdict[pick] = IntVar()
            chk = Checkbutton(self, text=pick,
                              variable=checkbutdict[pick])
            chk.pack(side=side, anchor=anchor, expand=YES)


def letsplot():
    global click, scatter_plot_data, show_data, variablelength_select, \
        columns, columns_length
    checkbuttonvaluelist = []
    for var in variablelist:
        checkbuttonvaluelist.append(checkbutdict[var].get())
    variablelist_select = []
    variablelength_select = []
    for i in range(len(variablelist)):
        if checkbuttonvaluelist[i]:
            variablelist_select.append(variablelist[i])
            variablelength_select.append(variablelengths[i])
    if xvar.get() not in variablelist_select:
        variablelist_select.append(xvar.get())
        variablelength_select.append(1.3)
    if yvar.get() not in variablelist_select:
        variablelist_select.append(yvar.get())
        variablelength_select.append(1.3)

    scatter_plot_data = [(df[xvar.get()][i], df[yvar.get()][i])
                         for i in range(len(df))]

    if xvar.get() not in continues_var or yvar.get() \
        not in continues_var:
        tkMessageBox.showinfo('Error!',
                              'One or More variables you choose to plot are categorical variables.'
                              )
        return
    xmax = max(df[xvar.get()])
    ymax = max(df[yvar.get()])
    show_data = df.ix[0:, variablelist_select].values.tolist()
    print 'Finish loading data'

    data = [Datum(*xy) for xy in scatter_plot_data]
    click = 0

    columns = variablelist_select
    columns_length = variablelength_select
    ax = plt.axes(xlim=(0, 1.2 * float(xmax)), ylim=(0, 1.2
                  * float(ymax)), autoscale_on=False)
    lman = LassoManager(ax, data)
    plt.xlabel(xvar.get())
    plt.ylabel(yvar.get())
    plt.title('Scatter Plot of ' + xvar.get() + ' vs ' + yvar.get())
    plt.subplots_adjust(left=0.05, bottom=0.35)
    plt.show()


class Datum(object):

    colorin = colorConverter.to_rgba('red')
    colorout = colorConverter.to_rgba('dodgerblue')

    def __init__(
        self,
        x,
        y,
        include=False,
        ):

        self.x = x
        self.y = y
        if include:
            self.color = self.colorin
        else:
            self.color = self.colorout


class LassoManager(object):

    def __init__(self, ax, data):
        self.axes = ax
        self.canvas = ax.figure.canvas
        self.data = data

        self.Nxy = len(data)

        facecolors = [d.color for d in data]
        self.xys = [(d.x, d.y) for d in data]
        fig = ax.figure
        self.collection = RegularPolyCollection(
            fig.dpi,
            0,
            sizes=(30, ),
            facecolors=facecolors,
            edgecolor=facecolors,
            offsets=self.xys,
            transOffset=ax.transData,
            )

        ax.add_collection(self.collection)

        self.cid = self.canvas.mpl_connect('button_press_event',
                self.onpress)

    def callback(self, verts):
        global click
        global the_table
        global ind
        facecolors = self.collection.get_facecolors()
        p = path.Path(verts)
        ind = p.contains_points(self.xys)
        for i in range(len(self.xys)):
            if ind[i]:
                facecolors[i] = Datum.colorin
            else:
                facecolors[i] = Datum.colorout
        if sum(ind) > 0:
            if click > 0:
                the_table.remove()
            the_table = plt.table(cellText=[[str(c) for c in
                                  show_data[i]] for i in
                                  range(len(self.xys)) if ind[i]],
                                  colWidths=variablelength_select,
                                  colLabels=columns, loc='bottom',
                                  bbox=[0.10000000000000001, -0.6, 0.8,
                                  .5])
            click = 1
        else:
            if click > 0:
                the_table.remove()
            click = 0

        self.canvas.draw_idle()
        self.canvas.widgetlock.release(self.lasso)
        del self.lasso

    def onpress(self, event):
        if self.canvas.widgetlock.locked():
            return
        if event.inaxes is None:
            return
        self.lasso = Lasso(event.inaxes, (event.xdata, event.ydata),
                           self.callback)


        # acquire a lock on the widget drawing
        # self.canvas.widgetlock(self.lasso)

def scatter_plot():
    if readsas is None:
        loaderror()
        return
    global checkbutdict, xvar, yvar, variablelist, variablelengths, df, \
        continues_var
    list_type = [item.encode('utf-8') for item in sasdata.column_types]
    list_name = [item.encode('utf-8') for item in sasdata.column_names]
    continues_var = [list_name[i] for i in range(len(list_type))
                     if list_type[i] == 'number']
    root = Toplevel()
    root.geometry('%dx%d+%d+%d' % (500, 480, 50, 100))
    root.title('Scatter Plot')
    xvar = StringVar(root)
    yvar = StringVar(root)

    choices = variablelist

    label_info = Label(root,
                       text='Select all variables you want to see\n for observations in plot'
                       , font=('Helvetica', 14))
    label_info.place(x=5, y=5)

    label_y = Label(root, text='Y-axis variable:')
    label_y.place(x=20, y=455)
    label_x = Label(root, text='X-axis variable:')
    label_x.place(x=20, y=425)
    optionx = OptionMenu(root, yvar, *choices)
    optionx.place(x=100, y=450)
    optiony = OptionMenu(root, xvar, *choices)
    optiony.place(x=100, y=420)

    Button(root, text="Let's get this plot(party) started",
           command=letsplot).place(x=250, y=435)
    numofcol = int(len(variablelist) / 15) + 1
    checkbutdict = {}
    for i in range(numofcol):
        curlist = variablelist[i * 15:min(i * 15 + 15,
                len(variablelist))]
        lng = Checkbar(root, curlist, side=TOP, anchor=W,
                       dict=checkbutdict)
        lng.pack(side=LEFT, fill=X)
    root.mainloop()


readsas = None
diffvar = None

# Main Window

app = Tk()
app.title('Simba')
app.geometry('200x300+200+200')
Greet_text = Label(app, text='                   ')

QC_text = Label(app,
                text='''Quality Check:
 To use QC funtions, please click
 the button below to load dataset''')


def out():
    print 'Exit!'
    sys.exit()


# add these buttons

quit = Button(app, text='Quit', width=8, command=out)

button_loadsas = Button(app, text='Load SAS Dataset', width=20,
                        command=loadsas)
button_varstat = Button(app, text='Variable Statistics', width=20,
                        command=varstat)
button_varfreq = Button(app, text='Variable Frequency', width=20,
                        command=varfreq)
button_hist_plot = Button(app, text='Bar Plot', width=20,
                          command=bar_plot)
button_scatter_plot = Button(app, text='Scatter Plot', width=20,
                             command=scatter_plot)

QC_text.grid(row=1, column=1, rowspan=2, padx=5, pady=5)
button_loadsas.grid(row=3, column=1, padx=5, pady=5)
button_varfreq.grid(row=6, column=1, padx=5, pady=5)
button_varstat.grid(row=7, column=1, padx=5, pady=5)
button_hist_plot.grid(row=8, column=1, padx=5, pady=5)
button_scatter_plot.grid(row=9, column=1, padx=5, pady=5)
quit.grid(row=10, column=1, padx=5, pady=5)

app.mainloop()

# End of Program
# by Yiwen Luo
# 9/22/2016