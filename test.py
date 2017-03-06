import platform
import glob, os
import sys
import tkFont
import FileDialog
import tkFileDialog as filedialog
from Tkinter import *
import os.path
import tkMessageBox
from tkFileDialog import askopenfilename
from tkFileDialog import asksaveasfilename
import string as anotherstr
from sas7bdat import SAS7BDAT
import matplotlib as mpl
mpl.use("TkAgg")
import numpy as np
import pandas as pd
from collections import Counter
from matplotlib.widgets import Lasso
from matplotlib.colors import colorConverter
from matplotlib.collections import RegularPolyCollection
import matplotlib.pyplot as plt
from matplotlib import path
import ttk
import collections
from random import choice
import tkFont
import random

app = Tk()
app.withdraw()
default_font = tkFont.nametofont('TkDefaultFont')
default_font.configure(size=20)

def loadsas():
	global readsas
	global sasdata
	global variablelist
	global variabletype
	global cur_df
	global cur_df_naasNone
	global df
	global df_naasNone
	global variablelengths
	global Typedict
	filterinfo['text'] = ' '
	tkMessageBox.showinfo('Loading data',
						  'Choose SAS dataset you want to QC')
	readsas = askopenfilename()
	if str(readsas).find('.sas7bdat') == -1:
		tkMessageBox.showinfo('Error!', 'Not a SAS dataset')
		readsas = None
		return
	sasdata = SAS7BDAT(os.path.normcase(str(readsas)))

	win=Toplevel()
	win.title('Progress')
	progress = ttk.Progressbar(win, orient="horizontal",length=200, mode="determinate")
	info=ttk.Label(win,text='Loading data:')
	info.pack()
	progress.pack()

	count=sasdata.header.properties.row_count
	progress['maximum']=count
	variablelist = [item.encode('utf-8') for item in
					sasdata.column_names]
	variabletype = [item.encode('utf-8') for item in
					sasdata.column_types]
	Typedict = {}
	for i in range(len(variablelist)):
		Typedict[variablelist[i]] = variabletype[i]
	variablelengths = [float(x) / 8 + 0.55 for x in
					   sasdata.column_data_lengths]
	i=0
	listsasdata=[]
	for row in sasdata:
		listsasdata.append([(item.encode('utf-8') if isinstance(item,basestring) else item) for item in row])
		if i%100==0 or i==count:
			progress['value']=i
			progress.update()
			info['text']='Loading data:  %s %s'%(round(float(i)*100/count,1),'%')
		i+=1

	data = np.vstack(listsasdata)
	data = data[1:]
	df = pd.DataFrame(data, columns=variablelist)
	df_naasNone = df.copy()
	cur_df_naasNone = df.copy()
	df.fillna(value=np.nan, inplace=True)
	cur_df = df.copy()
	sasdata.close()
	win.destroy()
	win.mainloop()


def fillllllter():
	global cur_df
	global cur_df_naasNone
	Filterwin = Toplevel()
	Filterwin.geometry('600x160+200+200')
	Filterlabel1 = ttk.Label(Filterwin, text='Filter One')
	Filterlabel1.grid(row=0, column=1, padx=5, pady=5)
	Filterlabel2 = ttk.Label(Filterwin, text='Filter Two')
	Filterlabel2.grid(row=1, column=1, padx=5, pady=5)
	Filterlabel3 = ttk.Label(Filterwin, text='Filter Three')
	Filterlabel3.grid(row=2, column=1, padx=5, pady=5)
	# Why I have to write these function three times, someone please help me!

	# First filter
	def updatevaluelist1(self):
		global valuelist1
		valuelist1 = tuple([str(i) for i in set(df[filtervar1.get()])])
		value1['values'] = valuelist1
		if Typedict[filtervar1.get()] == 'string':
			signvar1.set('=')
			sign1.state(['disabled'])
		else:
			sign1.state(['!disabled'])


	filtervar1 = StringVar()
	filter1 = ttk.Combobox(Filterwin, textvariable=filtervar1)
	filter1['values'] = variablelist
	filter1.bind('<<ComboboxSelected>>', updatevaluelist1)
	filter1.grid(row=0, column=2, padx=5, pady=5)

	signvar1 = StringVar()
	sign1 = ttk.Combobox(Filterwin, textvariable=signvar1)
	sign1['values'] = ('=', '>', '<')
	sign1.grid(row=0, column=3, padx=5, pady=5)

	valuevar1 = StringVar()
	valuevar1.trace('w', lambda name, index, mode: update_list1())
	value1 = ttk.Combobox(Filterwin, textvariable=valuevar1)
	value1.grid(row=0, column=4, padx=5, pady=5)

	def update_list1():
		search_term = valuevar1.get()
		value1['values'] = tuple(i for i in valuelist1 if search_term
								in i)


	# Second Filter
	def updatevaluelist2(self):
		global valuelist2
		valuelist2 = tuple([str(i) for i in set(df[filtervar2.get()])])
		value2['values'] = valuelist2
		if Typedict[filtervar2.get()] == 'string':
			signvar2.set('=')
			sign2.state(['disabled'])
		else:
			sign2.state(['!disabled'])

	filtervar2 = StringVar()
	filter2 = ttk.Combobox(Filterwin, textvariable=filtervar2)
	filter2['values'] = variablelist
	filter2.bind('<<ComboboxSelected>>', updatevaluelist2)
	filter2.grid(row=1, column=2, padx=5, pady=5)

	signvar2 = StringVar()
	sign2 = ttk.Combobox(Filterwin, textvariable=signvar2)
	sign2['values'] = ('=', '>', '<')
	sign2.grid(row=1, column=3, padx=5, pady=5)

	valuevar2 = StringVar()
	valuevar2.trace('w', lambda name, index, mode: update_list2())
	value2 = ttk.Combobox(Filterwin, textvariable=valuevar2)
	value2.grid(row=1, column=4, padx=5, pady=5)

	def update_list2():
		search_term = valuevar2.get()
		value2['values'] = tuple(i for i in valuelist2 if search_term
								in i)

	# Third filter
	def updatevaluelist3(self):
		global valuelist3
		valuelist3 = tuple([str(i) for i in set(df[filtervar3.get()])])
		value3['values'] = valuelist3
		if Typedict[filtervar3.get()] == 'string':
			signvar3.set('=')
			sign3.state(['disabled'])
		else:
			sign3.state(['!disabled'])


	filtervar3 = StringVar()
	filter3 = ttk.Combobox(Filterwin, textvariable=filtervar3)
	filter3['values'] = variablelist
	filter3.bind('<<ComboboxSelected>>', updatevaluelist3)
	filter3.grid(row=2, column=2, padx=5, pady=5)

	signvar3 = StringVar()
	sign3 = ttk.Combobox(Filterwin, textvariable=signvar3)
	sign3['values'] = ('=', '>', '<')
	sign3.grid(row=2, column=3, padx=5, pady=5)

	valuevar3 = StringVar()
	valuevar3.trace('w', lambda name, index, mode: update_list3())
	value3 = ttk.Combobox(Filterwin, textvariable=valuevar3)
	value3.grid(row=2, column=4, padx=5, pady=5)

	def update_list3():
		search_term = valuevar3.get()
		value3['values'] = tuple(i for i in valuelist3 if search_term
								in i)

	def Apply():
		global cur_df
		global cur_df_naasNone
		print filtervar1.get(), signvar1.get(), valuevar1.get()
		print filtervar2.get(), signvar2.get(), valuevar2.get()
		print filtervar3.get(), signvar3.get(), valuevar3.get()
		filterinfo['text'] = 'Current filter: '
		if filtervar1.get()!='':
			filterinfo['text'] += filtervar1.get() + signvar1.get() + valuevar1.get() +' '
			if Typedict[filtervar1.get()] != 'string':
				t1 = float(valuevar1.get())
			else:
				t1 = valuevar1.get()

			if signvar1.get() == '=':
				sign1='=='
			else:
				sign1=signvar1.get()

			cur_df = eval('df[df[filtervar1.get()]'+sign1+'t1].reset_index(drop=True)')
			cur_df_naasNone = eval('df_naasNone[df_naasNone[filtervar1.get()]'+sign1+'t1].reset_index(drop=True)')
		if filtervar2.get()!='':
			filterinfo['text'] += filtervar2.get() + signvar2.get() + valuevar2.get() +' '
			if Typedict[filtervar2.get()] != 'string':
				t2 = float(valuevar2.get())
			else:
				t2 = valuevar2.get()

			if signvar2.get() == '=':
				sign2='=='
			else:
				sign2=signvar2.get()

			cur_df = eval('cur_df[cur_df[filtervar2.get()]'+sign2+'t2].reset_index(drop=True)')
			cur_df_naasNone = eval('cur_df_naasNone[cur_df_naasNone[filtervar2.get()]'+sign2+'t2].reset_index(drop=True)')

		if filtervar3.get()!='':
			filterinfo['text'] += filtervar3.get() + signvar3.get() + valuevar3.get()
			if Typedict[filtervar3.get()] != 'string':
				t3 = float(valuevar3.get())
			else:
				t3 = valuevar3.get()

			if signvar3.get() == '=':
				sign3='=='
			else:
				sign3=signvar3.get()

			cur_df = eval('cur_df[cur_df[filtervar3.get()]'+sign3+'t3].reset_index(drop=True)')
			cur_df_naasNone = eval('cur_df_naasNone[cur_df_naasNone[filtervar3.get()]'+sign3+'t3].reset_index(drop=True)')


		# 	if signvar1.get() == '=':
		# 		cur_df = df[df[filtervar1.get()] == t1].reset_index(drop=True)
		# 		cur_df_naasNone = df_naasNone[df[filtervar1.get()]== t1].reset_index(drop=True)
		# 	elif signvar1.get() == '>':
		# 	cur_df = df[df[filtervar1.get()] > t].reset_index(drop=True)
		# 	cur_df_naasNone = df_naasNone[df[filtervar1.get()]
		# 			> t].reset_index(drop=True)
		# elif signvar1.get() == '<':
		# 	cur_df = df[df[filtervar1.get()] < t].reset_index(drop=True)
		# 	cur_df_naasNone = df_naasNone[df[filtervar1.get()]
		# 			< t].reset_index(drop=True)

		
		
		Filterwin.destroy()

	def Remove():
		global cur_df
		global cur_df_naasNone
		cur_df = df.reset_index(drop=True)
		cur_df_naasNone = df_naasNone.reset_index(drop=True)
		filterinfo['text'] = ' '
		Filterwin.destroy()

	Applybut = ttk.Button(Filterwin, text='Apply Filter', command=Apply)
	Applybut.grid(row=3, column=2, padx=5, pady=5)
	Removebut = ttk.Button(Filterwin, text='Remove Filter',
						   command=Remove)
	Removebut.grid(row=3, column=3, padx=5, pady=5)

	Filterwin.mainloop()

def varfreq():
	if readsas is None:
		loaderror()
		return

	categorical_var = [variablelist[i] for i in
					   range(len(variablelist)) if variabletype[i]
					   == 'string']
	varfreqwin = Toplevel()
	varfreqwin.title('Variable Frequency')
	varfreqwin.geometry('800x600+200+200')
	treeScroll = ttk.Scrollbar(varfreqwin)
	treeScroll.pack(side=RIGHT, fill=Y)
	tree = ttk.Treeview(varfreqwin)
	ttk.Style().configure('.', font=('Helvetica', 20),
						  foreground='black')
	treeScroll.configure(command=tree.yview)
	tree.configure(yscrollcommand=treeScroll.set)
	tree['columns'] = ('value', 'n')
	tree.column('n', width=100)
	tree.column('value', width=100)
	tree.heading('n', text='n')
	tree.heading('value', text='category')
	nobs = len(cur_df_naasNone)
	m = 0

	for i in variablelist:
		cvar = Counter(cur_df_naasNone[i])
		distin = len(cvar)
		tree.insert('', m, i, text=i, tags=('title', ))
		m += 1
		cvar_order = collections.OrderedDict(sorted(cvar.items()))
		missing = 0
		if '' in cvar_order:
			missing+=cvar_order['']
			del cvar_order['']
		if None in cvar_order:
			missing+=cvar_order[None]
			del cvar_order[None]
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
	treeScroll.config(command=tree.yview)
	varfreqwin.mainloop()


def varstat():
	if readsas is None:
		loaderror()
		return

	continues_var = [variablelist[i] for i in range(len(variablelist)) if variabletype[i] == 'number']
	varstatwin = Toplevel()
	varstatwin.title('Variable Statistics')
	varstatwin.geometry('800x600+200+200')
	treeScroll_varstat = ttk.Scrollbar(varstatwin)
	treeScroll_varstat.pack(side=RIGHT, fill=Y)
	tree = ttk.Treeview(varstatwin)
	ttk.Style().configure('.', font=('Helvetica', 20),
						  foreground='black')
	treeScroll_varstat.configure(command=tree.yview)
	tree.configure(yscrollcommand=treeScroll_varstat.set)
	tree['columns'] = (
		'n',
		'max',
		'min',
		'mean',
		'median',
		'missing',
		)
	tree.column('n', width=80)
	tree.column('max', width=80)
	tree.column('min', width=80)
	tree.column('mean', width=80)
	tree.column('median', width=80)
	tree.column('missing', width=80)

	tree.heading('n', text='n')
	tree.heading('max', text='max')
	tree.heading('min', text='min')
	tree.heading('mean', text='mean')
	tree.heading('median', text='median')
	tree.heading('missing', text='missing')

	nobs = len(cur_df)
	m = 0
	for i in continues_var:

		cur_data = [float(x) for x in cur_df[i] if not np.isnan(float(x))]
		n = len(cur_data)
		if len(cur_data) == 0:
			continue
		tree.insert('', m, text=i, values=(
			n,
			max(cur_data),
			min(cur_data),
			round(np.mean(cur_data), 3),
			np.median(cur_data),
			nobs - n,
			), tags=(('oddrow' if m % 2 == 1 else 'evenrow'), ))
		m += 1
	tree.tag_configure('oddrow', background='white')
	tree.tag_configure('evenrow', background='lightgrey')
	tree.pack(expand=YES, fill=BOTH)
	treeScroll_varstat.config(command=tree.yview)
	varstatwin.mainloop()



def hist_plot():

	if readsas is None:
		loaderror()
		return
	print variabletype 
	numeric = []
	for i in range(len(variabletype)):
		if 'number' in variabletype[i]:
			numeric.append(variablelist[i])

	class App(object):

		def __init__(self,master):

			self.master = master
			self.variable_b = StringVar(self.master)
			self.optionmenu_b = OptionMenu(self.master,
					self.variable_b, *numeric)
			self.button = Button(self.master, text='  Plot  ',
								 command=self.select)
			self.label_b = Label(self.master, text='Variable Name')
			self.optionmenu_b.grid(row=1, column=1, padx=5, pady=5)
			self.button.grid(row=2, column=1, padx=5, pady=5)
			self.label_b.grid(row=1, column=0, padx=5, pady=5)

		def select(self, *args):
			curvar = self.variable_b.get()
			hist([float(i) for i in cur_df[curvar]], curvar)


	root = Tk()
	root.title('Hist Plot')
	root.geometry('%dx%d+%d+%d' % (300, 150, 50, 100))
	app = App(root)
	root.mainloop()

def bar_plot():
	global subjectlvlvar
	if readsas is None:
		loaderror()
		return
	variablelist_freq = [var for var in variablelist
						 if len(list(Counter(cur_df[var]))) < 30]
	if len(variablelist_freq)==0:
		tkMessageBox.showinfo('Warning!','None of the variables are categorical variable.')
		return
	class App(object):

		def __init__(self,master):


			self.master = master
			self.variable_b = StringVar(self.master)
			self.optionmenu_b = OptionMenu(self.master,
					self.variable_b, *variablelist_freq)
			self.button = Button(self.master, text='  Plot  ',command=self.select2)
			self.label_b = Label(self.master, text='Variable Name')
			self.optionmenu_b.grid(row=1, column=1, padx=5, pady=5)
			self.button.grid(row=2, column=1, padx=5, pady=5)
			self.label_b.grid(row=1, column=0, padx=5, pady=5)

		def select2(self, *args):
			curvar = self.variable_b.get()
			countvar = Counter(cur_df[curvar])
			n_groups = len(list(countvar))
			all_stat = [countvar[ele] for ele in list(countvar)]
			stat_max = max(all_stat)
			fig = plt.figure()
			ax1 = fig.add_axes((0.1, 0.40000000000000002, 0.8, .5))
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
	app = App(root)
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

	scatter_plot_data = [(float(cur_df[xvar.get()][i]), float(cur_df[yvar.get()][i]))
						 for i in range(len(cur_df))]

	if xvar.get() not in continues_var or yvar.get() \
		not in continues_var:
		tkMessageBox.showinfo('Error!',
							  'One or More variables you choose to plot are categorical variables.'
							  )
		return
	xmax = max(cur_df[xvar.get()])
	ymax = max(cur_df[yvar.get()])
	show_data = cur_df.ix[0:, variablelist_select].values.tolist()
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
			5,
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
								  bbox=[0.1, -0.6, 0.8, .5])
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

def loaderror():
	tkMessageBox.showinfo('Cauchy','No dataset loaded.')

def scatter_plot():
	if readsas is None:
		loaderror()
		return
	global checkbutdict, xvar, yvar, variablelist, variablelengths, \
		cur_df, continues_var

	continues_var = [variablelist[i] for i in range(len(variablelist))
					 if variabletype[i] == 'number']
	root = Toplevel()
	root.geometry('%dx%d+%d+%d' % (500, 525, 50, 100))
	root.title('Scatter Plot')
	xvar = StringVar(root)
	yvar = StringVar(root)

	# initial value

	choices = variablelist

	label_info = Label(root,
					   text='Select all variables you want to see\n for observations in plot'
					   , font=('Helvetica', 14))
	label_info.place(x=5, y=5)

	label_y = Label(root, text='Y-axis variable:')
	label_y.place(x=20, y=495)
	label_x = Label(root, text='X-axis variable:')
	label_x.place(x=20, y=465)
	optionx = OptionMenu(root, yvar, *choices)
	optionx.place(x=120, y=490)
	optiony = OptionMenu(root, xvar, *choices)
	optiony.place(x=120, y=460)

	Button(root, text="Let's plot!",
		   command=letsplot).place(x=250, y=475)
	numofcol = int(len(variablelist) / 15) + 1
	checkbutdict = {}
	for i in range(numofcol):
		curlist = variablelist[i * 15:min(i * 15 + 15,
				len(variablelist))]
		lng = Checkbar(root, curlist, side=TOP, anchor=W,
					   dict=checkbutdict)
		lng.pack(side=LEFT, fill=X)
	root.mainloop()


def hist(data, varname):
	r = lambda : random.randint(0, 255)
	print data
	# data = data[~np.isnan(data)]
	(m, bins, patches) = plt.hist(data, 50, normed=1, alpha=0.75)
	plt.xlabel(varname)
	plt.ylabel('Probability(%)')
	maxdata = max(data)
	mindata = min(data)
	meandata = round(np.mean(data), 3)
	mediandata = round(np.median(data), 3)
	plt.title('Histogram of ' + varname
			  + ': max=%s, min=%s,mean=%s,median=%s' % (maxdata,
			  mindata, meandata, mediandata))
	plt.axis([mindata - 0.1 * abs(maxdata), maxdata + 0.1
			 * abs(maxdata), 0, max(m) * 1.2])
	plt.grid(True)
	plt.show()


def hist_plot():

	if readsas is None:
		loaderror()
		return
	print variabletype 
	numeric = []
	for i in range(len(variabletype)):
		if 'number' in variabletype[i]:
			numeric.append(variablelist[i])

	class App(object):

		def __init__(self,master):

			self.master = master
			self.variable_b = StringVar(self.master)
			self.optionmenu_b = OptionMenu(self.master,
					self.variable_b, *numeric)
			self.button = Button(self.master, text='  Plot  ',
								 command=self.select)
			self.label_b = Label(self.master, text='Variable Name')
			self.optionmenu_b.grid(row=1, column=1, padx=5, pady=5)
			self.button.grid(row=2, column=1, padx=5, pady=5)
			self.label_b.grid(row=1, column=0, padx=5, pady=5)

		def select(self, *args):
			curvar = self.variable_b.get()
			hist([float(i) for i in cur_df[curvar]], curvar)


	root = Tk()
	root.title('Hist Plot')
	root.geometry('%dx%d+%d+%d' % (300, 150, 50, 100))
	app = App(root)
	root.mainloop()

readsas = None
diffvar = None


class ThemeDemo(ttk.Frame):

	def __init__(self, name='themesdemo'):
		global filterinfo
		ttk.Frame.__init__(self, name=name)
		self.pack(expand=Y, fill=BOTH)
		self.master.title('Cauchy')

		demoPanel = ttk.Frame(self)

		demoPanel.pack(side=TOP, fill=BOTH, expand=Y)
		
		themes = sorted(ttk.Style().theme_names())
		
		QC = ttk.Labelframe(demoPanel, text='')
		QC_text = Label(QC,
						text='''To use funtions, please load SAS dataset first'''
						)
		QC_text.grid(row=0,column=1,sticky=W + E + N + S,columnspan=2,padx=10,pady=5,)
		b = ttk.Button(QC, text='Load SAS Dataset', command=loadsas)
		b.grid(row=1, column=1, sticky=W + E + N + S, padx=10, pady=5)
		b = ttk.Button(QC, text='Frenquency Table', command=varfreq)
		b.grid(row=2, column=1, sticky=W + E + N + S, padx=10, pady=5)
		b = ttk.Button(QC, text='Summary Statistics', command=varstat)
		b.grid(row=3, column=1, sticky=W + E + N + S, padx=10, pady=5)
		b = ttk.Button(QC, text='Filter', command=fillllllter)
		b.grid(row=4, column=1, sticky=W + E + N + S, padx=10, pady=5)
		b = ttk.Button(QC, text='Bar Plot', command=bar_plot)
		b.grid(row=1, column=2, sticky=W + E + N + S, padx=10, pady=5)
		b = ttk.Button(QC, text='Scatter Plot', command=scatter_plot)
		b.grid(row=2, column=2, sticky=W + E + N + S, padx=10, pady=5)
		b = ttk.Button(QC, text='Histogram Plot', command=hist_plot)
		b.grid(row=3, column=2, sticky=W + E + N + S, padx=10, pady=5)

		filterinfo = ttk.Label(QC, text='')
		filterinfo.grid(row=7,column=1,sticky=W + E + N + S,columnspan=2,padx=10,pady=5)
		QC.pack(side=LEFT, expand=False, padx=20, pady=5, fill=BOTH)


app.deiconify()
ThemeDemo().mainloop()
