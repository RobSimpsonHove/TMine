#!/usr/bin/python3

title = 'TMine v.40'

import codecs
import io
import os
import random
import shutil
import time

from collections import OrderedDict
#import tkinter.messagebox
from tkinter.filedialog import askopenfilename
from tkinter.messagebox import showwarning
from tkinter.filedialog import asksaveasfilename
from tkinter.scrolledtext import *
from tkinter import *
import configparser

tmp='temp/'
if not os.path.exists(tmp):
    os.makedirs(tmp)
config = configparser.ConfigParser()

if not os.path.isfile("directories.ini"):
    config.add_section('Directories')
    config.set('Directories', 'lastdir', tmp)

    with open("directories.ini", 'w',encoding="utf-8") as cfgfile:
        config.write(cfgfile)

config.read('directories.ini')

FILETYPES = [    ("Text files", "*.txt"), ("All files", "*")    ]

dotdotdot='([^ .,]*[ ,]+){0,4}'
amper='.*?'

class Cancel(Exception):
    pass

class myText(ScrolledText, object):
    windowcounter = 0
    def __init__(self, master, **options):
        ScrolledText.__init__(self, master, **options)
        self.config(
            font="{Courier New} 8",
            foreground="black",
            background="white",
            insertbackground="black", # cursor
            selectforeground="black", # selection
            selectbackground="grey",
            wrap=WORD, # use word wrapping
            undo=True
            )
        self.filename = None # current document
        self.bind_class("Text","<Control-a>", self.selectall)

    def selectall(self, event):
        event.widget.tag_add("sel","1.0","end")

    def _getfilename(self):
        return self._filename

    def _setfilename(self, filename):
        self._filename = filename
#        title = os.path.basename(filename or "(new document)")
#        title = title + " - " + TITLE
#        self.winfo_toplevel().title(title)

    filename = property(_getfilename, _setfilename)

    def edit_modified(self, value=None):
        # Python 2.5's implementation is broken
        return self.tk.call(self, "edit", "modified", value)

    def load(self, filename):
        text = open(filename,mode="r", encoding="utf-8").read()
        self.delete(1.0, END)
        self.insert(END, text)
        self.mark_set(INSERT, 1.0)
        self.modified = False
        self.filename = filename

    def save(self, filename=None):
        if filename is None:
            filename = self.filename
        f = open(filename, mode="w", encoding="utf-8")
        s = self.get(1.0, END)
        s=s.replace('\n', '\n')
        try:
            f.write(s.rstrip())
            f.write("\n")
        finally:
            f.close()
        self.modified = False
        self.filename = filename

def rightclick(x):
    #  Add selected text to bottoms of patterns file/window
    selection=root.selection_get()
    text3.save(tmp+"patterns.txt")
    with open(tmp+"patterns.txt", "a") as myfile:
        myfile.write(selection)
    text3.load(tmp+"patterns.txt")



def find():
    # Find and highlight selected test in all windows
    selection=root.selection_get()
    selection=re.sub('&',amper,selection,1)
    selection=re.sub('\.\.\.',dotdotdot,selection,1)

    text1.save(tmp + "text1.txt")
    f1 = open(tmp+"text1.txt", mode="r", encoding="utf-8")
    f2 = open(tmp+"found.txt", mode="w", encoding="utf-8")

    n=0
    linecount=0
    for line in f1:
        linecount += 1
        if re.search(selection, line,re.IGNORECASE):
            f2.write(line)
            n += 1
    f1.close()
    f2.close()

    with open(tmp+"found.txt", mode="r+", encoding="utf-8") as f:
        content = f.read()
        f.seek(0, 0)
        f.write('Found pattern %s in  %d out of %d lines' % (selection,n,linecount) + '\n' + content)

    popup.lift()
    popup.title('Found pattern %s in  %d out of %d lines' % (selection, n, linecount))

    text5.load(tmp + "found.txt")

    text1.tag_delete('found')
    text2.tag_delete('found')
    text3.tag_delete('found')
    text4.tag_delete('found')
    text5.tag_delete('found')
    text1.tag_config('found', background='yellow')
    text2.tag_config('found', background='yellow')
    text3.tag_config('found', background='yellow')
    text4.tag_config('found', background='yellow')
    text5.tag_config('found', background='yellow')
    search(text1, selection, 'found')
    search(text2, selection, 'found')
    search(text3, selection, 'found')
    search(text5, selection, 'found')



def open_Verbatims():

    lastdir=config.get('Directories', 'lastdir')
    f = askopenfilename(parent=root, initialdir = lastdir, filetypes=FILETYPES)
    if not f:
        raise Cancel
    try:
        text1.load(f)
        updatelastdir(f)
    except IOError:
        from tkinter.messagebox import showwarning
        showwarning("Open", "Cannot open the file.")
        raise Cancel


def clearVerbatims():
    if messagebox.askokcancel("Clear verbatims", "Do you really want to clear the verbatims?"):
        text1.delete(1.0, END)


def open_Patterns():

    lastdir=config.get('Directories', 'lastdir')
    f = askopenfilename(parent=root, initialdir = lastdir, filetypes=FILETYPES)
    if not f:
        raise Cancel
    try:
        text3.load(f)
        updatelastdir(f)
    except IOError:
        showwarning("Open", "Cannot open the file.")
        raise Cancel


def save_Patterns():
    f = asksaveasfilename(parent=root)
    fstem=re.sub('\..*','',f)

    if not f:
        raise Cancel
    try:
        text3.save(fstem+'.patterns.txt')
    except IOError:
        showwarning("Save As", "Cannot save the file.")
        raise Cancel

    updatelastdir(f)



def open_project():
    lastdir=config.get('Directories', 'lastdir')
    f = askopenfilename(parent=root, initialdir = lastdir, filetypes=FILETYPES)
    fstem=re.sub('\..*','',f)
    #print 'FSTEM: %s'+fstem
    if not f:
        raise Cancel
    try:
        text1.load(fstem + '.txt')
        root.wm_title('TMiner - '+fstem+'.txt')
        text3.load(fstem+'.patterns.txt')
    except IOError:
        showwarning("Open Project", "Cannot open all files.")
        raise Cancel
    updatelastdir(f)


def save_project():
    f = asksaveasfilename(parent=root)
    fstem=re.sub('\..*','',f)
    gen_fdl()
    if not f:
        raise Cancel
    try:
        text1.save(fstem + '.txt')
        text3.save(fstem+'.patterns.txt')
        text2.save(fstem+'.unflagged.txt')
        text4.save(fstem+'.counts.txt')
        shutil.copy(tmp+'uniqwords.txt', fstem+'.words.txt')
        shutil.copy(tmp+'patterns.fdl', fstem+'.fdl')
    except IOError:
        showwarning("Save As", "Cannot save the file.")
        raise Cancel

    updatelastdir(f)



def updatelastdir(f):
    print('Updating directories',f)
    head, tail = os.path.split(f)
    config.set('Directories', 'lastdir', head)
    with open("directories.ini", 'w',encoding="utf-8") as cfgfile:
        config.write(cfgfile)


def gen_fdl():
    build_patterns()
    clean_text()
    marked = open(tmp+'marked.txt', 'r',encoding="utf-8").read()
    field={}
    pos={}
    neg={}
    with open(tmp+'patterns1.txt', 'r',encoding="utf-8") as patterns:
        for pattern in patterns:
            pattern=re.sub(r"\?\\","\\?",pattern)
            list=re.split('([>!])',pattern.rstrip())
            field[list[2]]=  list[2]
            if list[1]=='>':
                try:
                    x= pos[list[2]]
                except:
                    pos[list[2]]='match(tolower(\"'+list[0]+'\"),tminelower)'
                    neg[list[2]]='false'
                else:
                    pos[list[2]]=pos[list[2]]+' or match(tolower(\"'+list[0]+'\"),tminelower)'
            else:
                try:
                    x= neg[list[2]]
                except:
                    neg[list[2]]='match(tolower(\"'+list[0]+'\"),tminelower)'
                    pos[list[2]]='true'
                else:
                    neg[list[2]]=neg[list[2]]+' or match(tolower(\"'+list[0]+'\"),tminelower)'



        f=io.open(tmp+'patterns.fdl', mode='w',encoding="utf-8")
        f.write('create tminelower := tolower(text);\n')
        for x in field:
            fdl='create '+re.sub('[^äa-zA-ZöüßÄÖÜẞ0-9]','_',''+field[x])+' := ('+pos[x]+') and not('+neg[x]+');\n'
            fdl=re.sub(' and not\(false\)','',fdl)
            fdl=re.sub('false or','',fdl)
            fdl=re.sub('true or','',fdl)
            fdl=re.sub('\(true\) and','',fdl)
            f.write(fdl)

        f.close()



def exit_command():
        #if tkMessageBox.askokcancel("Quit", "Do you really want to quit?"):
        root.destroy()

def about_command():
    text="""TMiner RS 2017
# All patterns are case-insensitive
# Hashes start a comment!!

spring                  ## Single pattern maps to its own flag

cat,dog,fish>animal     ## List of patterns map to the same flag

fishing,fishers!animal  ## ! (NOT) negates previous patterns

m[ae]n>male             ## [xyz] Alternative characters - Man or Men

dress-?maker>dressmaker ## ? means optional character - here

sl..p                   ## . means any single character - matches sleep, slipp

wives...girls           ## Three dots (ellipsis) ... means 'near'
                        ## (up to 4 words apart)

$cheese                 ## Looks for 'cheese' flags, rather than the word itself

 """

    label = messagebox.showinfo("About", text)

def dummy():
    print("I am a Dummy Command.")

def tryint(s):
    try:
        return int(s)
    except:
        return s

def alphanum_key(s):
    """ Turn a string into a list of string and number chunks.
        "z23a" -> ["z", 23, "a"]
    """
    return [ tryint(c) for c in re.split('([0-9]+)', s) ]

def sort_nicely(l):
    """ Sort the given list in the way that humans expect.
    """
    l.sort(key=alphanum_key)


def flag():
    flag_button.config(relief=SUNKEN)
    build_patterns()
    flag_patterns()
    show_unmarked()
    show_flags()
    flag_button.config(relief=RAISED)


def build_patterns():
    text3.save(tmp+"patterns.txt")
    f=open(tmp+'patterns1.txt', 'w',encoding="utf-8")
    with open(tmp+'patterns.txt','r',encoding="utf-8") as patterns:
        for pattern in patterns:
            pattern = pattern.rstrip()
            pattern=re.sub('#.*','',pattern)                         ##  Delete comments

            if pattern.strip() and re.search('^([^,>!]+)$',pattern):## Single word: "goat"  -> "goat>goat" ## Why \\1 not \1 ??
                thispattern=(re.sub('^([^,>]+)$','\\1>\\1',pattern)+'\n')
                thispattern=re.sub('\.\.\.',dotdotdot,thispattern,1) # 0-3 words accepted between, for 'near'
                thispattern=re.sub('&',amper,thispattern,1) # 0-3 words accepted between, for 'near'
                f.write(thispattern)
            elif re.search('[>!]',pattern):      ## lists : "apple,pear>fruit" -> "apple>fruit \n  pear>fruit"
                lhs = re.sub('[>!].*','',pattern)
                mid = re.sub('.*([>!]).*','\\1',pattern)
                rhs = re.sub('.*[>!]','',pattern)
                for lhs_item in lhs.split(","):
                    if len(lhs_item)>0:
                        thispattern=lhs_item+mid+rhs+'\n'
                        thispattern=re.sub('\.\.\.',dotdotdot,thispattern,1) ##  Implement 'near' (four words or less)
                        thispattern=re.sub('&',amper,thispattern,1) ##  Implement 'near' (four words or less)
                        f.write(thispattern)
    f.close()
    patterns.close()

    allpatterns=[]
    with open(tmp+'patterns1.txt','r',encoding="utf-8") as patterns:
        for pattern in patterns:
            allpatterns.append(pattern)
    #print(allpatterns)
    #Collect all patterns for each flag
    flags=OrderedDict()
    for p, pattern in enumerate(allpatterns):
        ps=re.split('([>!])',pattern.rstrip())
        #print('ps',ps)
        if len(ps)>1:
            if ps[1]=='>':
                #Ordered dict is [('spring', ['spring']), ('animal', ['cat', 'dog', 'fish']), ('_neg_animal', ['fishing']),
                # Negations shown with leading '!'
                if ps[2] in flags:
                    flags[ps[2]].append(ps[0])
                else:
                    flags[ps[2]]=[ps[0]]
            elif ps[1]=='!':
                if '_neg_'+ps[2] in flags:
                    flags['_neg_'+ps[2]].append(ps[0])
                else:
                    flags['_neg_'+ps[2]]=[ps[0]]

    #Write out collected flags
    #print(flags)
    f2=open(tmp+'patterns2.txt', 'w',encoding="utf-8")
    for f in flags:
        flag=''
        if '_neg_' in f:
            ff=re.sub('_neg_','',f)
            for i in flags[f]:
                flag=flag+'(?:'+i+')|'
            flag=flag.rstrip('|')+'!'+ff
        else:
            for i in flags[f]:
                flag=flag+'(?:'+i+')|'
            flag=flag.rstrip('|')+'>'+f
        #print flag
        f2.write(flag+'\n')
    f2.close()




def clean_text():
    # Removes all patterns from main text and saves as marked.txt
    text1.save(tmp + "marked.txt")  # Saves to marked.txt
    f=open(tmp+'marked2.txt', 'w',encoding="utf-8")
    with open(tmp+'marked.txt', 'r',encoding="utf-8") as inputfile:
        for line in inputfile:
            line = re.sub('.*## ?','', line.rstrip())
            line = re.sub('^','## ', line.rstrip())
            f.write(line + '\n')
    f.close()
    inputfile.close()
    os.remove(tmp+"marked.txt")
    os.rename(tmp+"marked2.txt",tmp+"marked.txt")


def flag_patterns():
    ## Applies one regex per pattern, to the whole file, for performance reasons (at least in Python2)
    clean_text()
    text1.load(tmp + "marked.txt")
    global marked_line_count
    with open(tmp+'marked.txt', 'r',encoding="utf-8") as markedx:
        marked_line_count= sum(1 for line in markedx)
    markedx.close()

    badpatterns = open(tmp+"badpatterns.txt", mode="w", encoding="utf-8")
    marked = open(tmp+'marked.txt', 'r',encoding="utf-8").read()
    with open(tmp+'patterns2.txt', 'r',encoding="utf-8") as patterns:
        for pattern in patterns:
            if '>' in pattern: # POSITIVE PATTERN
                p=pattern.rstrip().split(">") # eg. cheese>dairy
                mypattern, myflag = p[0], p[1]
                if mypattern.startswith('(?:$'): # pattern is $flagname, so only search LHS
                    mypattern=re.sub('\$','',mypattern) # Drop the dollar sign
                    try:
                        lhs_flag=re.compile('(\n|^)(((?:[^#]*),)*'+mypattern+',((?:[^#]*),)*##)',re.IGNORECASE)
                        marked = re.sub(lhs_flag,'\\1'+myflag+','+'\\2', marked)
                    except:
                        print('BAD PATTERN in positive label flagging: '+ pattern)
                        badpatterns.write('BAD PATTERN in positive label flagging: '+  pattern)
                else:  # Not a label, search RHS only
                    try:
                        rhs_pattern=re.compile('(## [^\n]*('+mypattern+')[^\n]*\n)',re.IGNORECASE)
                        marked = re.sub(rhs_pattern, myflag + ',\\1', marked)
                    except:
                        print('BAD PATTERN in positive flagging: '+  pattern)
                        badpatterns.write('BAD PATTERN in positive label flagging: '+  pattern)

            elif '!' in pattern:  # NEGATIVES
                p=pattern.rstrip().split("!")   #cheese>dairy
                mypattern, myflag = p[0], p[1]

                if mypattern.startswith('(?:$'): # pattern is $flagname, so only search LHS
                    mypattern=re.sub('\$','',mypattern) # Drop the dollar sign

                    anylabels='(?:[^#]+,)*?' # unspecified number of labels (each followed by a comma)

                    try:
                        # A before B ...
                        lhs_flag=re.compile('(\n'+anylabels+mypattern+','+anylabels+')'+myflag+','+'('+anylabels+'##)'
                                            ,re.IGNORECASE)
                        marked = re.sub(lhs_flag,'\\1\\2', marked)

                        # ... or B before A
                        lhs_flag=re.compile('(\n'+anylabels+')'+myflag+',('+anylabels+mypattern+','+anylabels+'##)'
                                            ,re.IGNORECASE)
                        marked = re.sub(lhs_flag,'\\1\\2', marked)
                    except:
                        print('BAD PATTERN in negative label flagging: '+  pattern)
                        badpatterns.write('BAD PATTERN in positive label flagging: '+  pattern)

                else:   # pattern is not flagname, just text, so search RHS
                    try:
                        negative_pattern=re.compile('(\n(?:(?:[^#,])+,)*)'+myflag+',((?:(?:[^#,])+,)*##[^\n]+('+mypattern+')[^\n]*)',re.IGNORECASE)
                        marked = re.sub(negative_pattern , '\\1\\2', marked)
                    except:
                        print('BAD PATTERN in negative label flagging: '+  pattern)
                        badpatterns.write('BAD PATTERN in positive label flagging: '+  pattern)

        patterns.close()
        badpatterns.close()

    # Dedup flags
    f2=open(tmp+'marked2.txt', 'w',encoding="utf-8")
    for line in marked.split("\n"):
        l=line.split("##")
        if len(l)>1:
            deduptags = ''
            if  ',' in l[0]:
                deduptags=','.join(OrderedDict.fromkeys(l[0].split(',')))
            f2.write(deduptags+'##'+l[1]+'\n')

    f2.close()

    os.remove(tmp+"marked.txt")
    os.rename(tmp+"marked2.txt",tmp+"marked.txt")
    text1.load(tmp + "marked.txt")



def show_unmarked():
    f=open(tmp+'marked.txt', 'r',encoding="utf-8")
    f2=open(tmp+'unmarked.txt', 'w',encoding="utf-8")
    n=0
    for line in f:
        if re.search('^ *##',line):
            f2.write(re.sub('^ *## ','',line))
            n += 1

    f.close()
    f2.close()

    f2=open(tmp+'unmarked.txt', 'r',encoding="utf-8")

    if shuf.get()==1:
        with f2 as source:
            data = [ (random.random(), line) for line in source ]
        data.sort()
        with open(tmp+'shuff_unmarked.txt', 'w',encoding="utf-8") as target:
            for _, line in data:
                target.write( line )
        f2.close()
        unmarked = open(tmp+'shuff_unmarked.txt', 'r',encoding="utf-8").read()
    else:
        unmarked = open(tmp+'unmarked.txt', 'r',encoding="utf-8").read()

    text2.delete(0.0,END)
    text2.insert(END, 'Unflagged lines: %d out of %d \n\n' % (n,marked_line_count))
    text2.insert(END, unmarked)


def explore09_text():
    clean_text() # write  window 1 to marked.txt

    #Load kill list in to regex expesssion (^| )(aaa|bbb|ccc)($| )

    if not os.path.isfile('utils\\kill_list.txt'):
        f=io.open('utils\\kill_list.txt', mode='w',encoding="utf-8")
        f.write('the')
        f.close()

    f=io.open('utils\\kill_list.txt', mode='r',encoding="utf-8")
    kill_list='zz'
    for line in f:
        kill_list=kill_list+'|'+line.rstrip()
    f.close()
    kill='(^| )('+kill_list+')($| )'


    if not os.path.isfile('utils\\save_list.txt'):
        f=io.open('utils\\save_list.txt', mode='w',encoding="utf-8")
        f.write('tma')
        f.close()

    #Load save list into regex expesssion
    f=io.open('utils\\save_list.txt', mode='r',encoding="utf-8")
    save_list='zz'
    for line in f:
        save_list=save_list+'|'+line.rstrip()
    f.close()
    save='^('+save_list+')$'

    #Split Marked text into word file
    f=open(tmp+'marked.txt', 'r',encoding="utf-8")
    f2=io.open(tmp+'words.txt', mode='w',encoding="utf-8")
    for line in f:
        #split on non-word characters
        line = re.sub('[^a-zA-ZäöüßÄÖÜẞ0-9-:?;)(S~_]',' ',''+line.lower())
        line = re.sub('\s+','~',''+line)
        for item in line.split("~"):
            if not re.search(save,item):
                item = re.sub(kill,'',item)  # kill kill-list items
                item = re.sub('^[0-9]{5,}$','',item) # delete number 5 digits or longer
                item = re.sub('^.{1,2}$','',item) # delete words of 1 or 2 characters

            if  len(item)>0:
                f2.write(item+'\n')
    f.close()
    f2.close()
    #f3.close()
    ##call(["./utils/sort.exe ","words.txt | utils/uniq.exe -c | ./utils/sort.exe -rn > uniqwords.txt"])
    os.system("utils\\sort.exe "+tmp+"words.txt | utils\\uniq.exe -c | utils\\sort.exe -rn > "+tmp+"uniqwords.txt")

    popup.lift()
    popup.title('Unique words in order frequency')
    text5.load(tmp+"uniqwords.txt")


def exploreAZ_text():
    clean_text() # write  window 1 to marked.txt

    #Load kill list in to regex expesssion (^| )(aaa|bbb|ccc)($| )

    if not os.path.isfile('utils\\kill_list.txt'):
        f=io.open('utils\\kill_list.txt', mode='w',encoding="utf-8")
        f.write('the')
        f.close()

    f=io.open('utils\\kill_list.txt', mode='r',encoding="utf-8")

    kill_list='zz'
    for line in f:
        kill_list=kill_list+'|'+line.rstrip()
    f.close()
    kill='(^| )('+kill_list+')($| )'

    if not os.path.isfile('utils\\save_list.txt'):
        f=io.open('utils\\save_list.txt', mode='w',encoding="utf-8")
        f.write('tma')
        f.close()

    #Load save list into regex expesssion
    f=io.open('utils\\save_list.txt', mode='r',encoding="utf-8")
    save_list='zz'
    for line in f:
        save_list=save_list+'|'+line.rstrip()
    f.close()
    save='^('+save_list+')$'

    #Split Marked text into word file
    f=open(tmp+'marked.txt', 'r',encoding="utf-8")
    f2=io.open(tmp+'words.txt', mode='w',encoding="utf-8")
    for line in f:
        #split on non-word characters
        line = re.sub('[^a-zA-ZäöüßÄÖÜẞ0-9-:?;)(S~_]',' ',''+line.lower())
        line = re.sub('\s+','~',''+line)
        for item in line.split("~"):
            if not re.search(save,item):
                item = re.sub(kill,'',item)  # kill kill-list items
                item = re.sub('^[0-9]{5,}$','',item) # delete number 5 digits or longer
                item = re.sub('^.{1,2}$','',item) # delete words 1 or 2 characters

            if  len(item)>0:
                f2.write(item+'\n')
    f.close()
    f2.close()
    #f3.close()
    ##call(["./utils/sort.exe ","words.txt | utils/uniq.exe -c | ./utils/sort.exe -rn > uniqwords.txt"])
    os.system("utils\\sort.exe "+tmp+"words.txt | utils\\uniq.exe -c  > "+tmp+"uniqwords.txt")

    popup.lift()
    popup.title('Unique words in alphabetical order')
    text5.load(tmp+"uniqwords.txt")


def show_flags():
    f=open(tmp+'marked.txt', 'r',encoding="utf-8")
    f2=open(tmp+'flags.txt', 'w',encoding="utf-8")

    ####
    for line in f:
        if re.search('^[^#]',line):
            line = re.sub('##.*','',line.rstrip())
            line = re.sub(',','\n',line.rstrip())
            f2.write(line+'\n')
    f.close()
    f2.close()

    f=open(tmp+'flags.txt', 'r',encoding="utf-8").readlines()
    f.sort()
    f2=open(tmp+'sortflags.txt', 'w',encoding="utf-8")
    f2.writelines(f)
    f2.close()

    f=open(tmp+'sortflags.txt', 'r',encoding="utf-8")
    f2=open(tmp+'countflags.txt', 'w',encoding="utf-8")
    n=0; l=''
    for line in f:
        if l != line.rstrip():
            if n!=0:
                f2.write("%d %s\n" % (n,l))
            n =0
            l = line.rstrip()
        n += 1
    f2.write("%d %s\n" % (n,l))
    f.close()
    f2.close()

    f=open(tmp+'countflags.txt', 'r',encoding="utf-8").read()

##    numPattern = re.compile('(\d*)\.', re.IGNORECASE)
##    f.sort()(cmp, key=lambda tFile:
##                   int(numPattern.search(tFile).group(1)))
##    f.sort

    counts=[]
    #print f
    #print f.split("\n")
    for z in f.split("\n"):
        counts.append([tryint(re.sub("([0-9]+) (.*)","\\1",z)),re.sub("([0-9]+) (.*)","\\2",z)])
    counts.pop(len(counts)-1)
    counts.sort(key=lambda x: (x[0]))

    f2=open(tmp+'sortcountflags.txt', 'w',encoding="utf-8")
    for i in range(0,len(counts)):
        if not counts[i][1]=='':
            f2.write(str(counts[i][0])+': '+counts[i][1]+'\n')
    f2.close()

    f2=open(tmp+'revsortcountflags.txt', 'w',encoding="utf-8")
    f=reversed(open(tmp+'sortcountflags.txt', 'r',encoding="utf-8").readlines())
    f2.writelines(f)
    f2.close()
    text4.load(tmp+"revsortcountflags.txt") # put up two lines??


def search(text_widget, keyword, tag):
    pos = '1.0'
    count  = IntVar()

    badpatterns = open(tmp+"badpatterns.txt", mode="w", encoding="utf-8")
    while True:
        try:
            idx = text_widget.search(keyword, pos, END, count=count , nocase=1,regexp=True)
        except:
            print('BAD pattern in Find:',keyword)
            badpatterns.write('BAD pattern in Find: '+ keyword)
            idx=False
        if not idx:
            break
        pos = '{}+{}c'.format(idx, count.get())
        text_widget.tag_add(tag, idx, pos)
    badpatterns.close()



def colourall():
    global colourflag
    color_range = ['#1F77B4', '#AEC7E8', '#FF7F0E', '#FFBB78', '#2CA02C', '#98DF8A', '#D62728', '#FF9896', '#9467BD',
              '#C5B0D5', '#8C564B', '#C49C94', '#E377C2', '#F7B6D2', '#7F7F7F', '#C7C7C7', '#BCBD22', '#DBDB8D',
              '#17BECF', '#9EDAE5']
    color_range = ['#336699', '#99CCFF', '#999933', '#666699', '#CC9933', '#006666', '#3399FF', '#993300', '#CCCC99', '#666666', '#FFCC66', '#6699CC', '#663366', '#9999CC', '#CCCCCC', '#669999', '#CCCC66', '#CC6600', '#9999FF', '#0066CC', '#99CCCC', '#999999', '#FFCC00', '#009999', '#99CC33', '#FF9900', '#999966', '#66CCCC', '#339966', '#CCCC33'] ## 30
    color_range_len=len(color_range)
    if colourflag==1:
        for pnum in range(0,999):
            text1.tag_delete('regex_tag'+ str(pnum))
            text3.tag_delete('regex_tag'+ str(pnum))
        colourflag=0
        showall_button.config(relief=RAISED)
    else:
        build_patterns()
        with open(tmp+'patterns2.txt', 'r',encoding="utf-8") as patterns:
            for pnum, pattern in enumerate(patterns):#
                #print(pattern)
                if '>' in pattern:
                    text1.tag_delete('regex_tag' + str(pnum))
                    colour=color_range[pnum % color_range_len]
                    text1.tag_config('regex_tag' + str(pnum), background=colour)
                    p = pattern.split('>')[0]
                    search(text1, p, 'regex_tag'+str(pnum))

        with open(tmp+'patterns2.txt', 'r',encoding="utf-8") as patterns:  #Using unoptimised regex instead of a or b or c...
            for pnum, pattern in enumerate(patterns):
                if '>' in pattern:
                    text3.tag_delete('regex_tag' + str(pnum))
                    colour=color_range[pnum % color_range_len]
                    text3.tag_config('regex_tag' + str(pnum), background=colour)
                    p=pattern.rstrip().split('>')[1]
                    search(text3, p, 'regex_tag'+str(pnum)) # why doesn't False work here?
        colourflag=1
        showall_button.config(relief=SUNKEN)

def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        root.destroy()

def ctrl_s(event):
    save_Patterns()


def hidepopup():
    popup.lower()



##########################################

popup=None
root = Tk(className="T-Miner root")

menu = Menu(root)
root.config(menu=menu)
root.iconbitmap(default='icon.ico')

root.protocol("WM_DELETE_WINDOW", exit_command)
filemenu = Menu(menu)
menu.add_cascade(label="File", menu=filemenu)
filemenu.add_command(label="Load Patterns", command=open_Patterns)
filemenu.add_command(label="Save Patterns", command=save_Patterns)
filemenu.add_separator()
filemenu.add_command(label="Load Project", command=open_project)
filemenu.add_command(label="Save Project", command=save_project)
filemenu.add_separator()
filemenu.add_command(label="Load Verbatims", command=open_Verbatims)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=exit_command)
helpmenu = Menu(menu)
menu.add_cascade(label="Help", menu=helpmenu)
helpmenu.add_command(label="About...", command=about_command)

content = Frame(root)
text1 = myText(content)
text2 = myText(content)
text3 = myText(content)
text4 = myText(content)
exploreAZ_button = Button(content, text="Explore A-Z", command=exploreAZ_text)
explore09_button = Button(content, text="Explore 0-9", command=explore09_text)
flag_button = Button(content, text=" Flag ", command=flag)
showall_button = Button(content, text=" Show all ", command=colourall)
find_button = Button(content, text=" Find ", command=find)
clear_verbatims = Button(content, text=" Clear text ", command=clearVerbatims)
projectname = None # current unsaved project
#root.bind("<Control-f>", DoubleClickText4c)
global marked_line_count

root.bind("<Button-3>", rightclick)
root.bind('<Control-s>', ctrl_s)
root.bind('<Control-S>', ctrl_s)

shuf = IntVar()
shuf.set(1)
shuffle = Checkbutton(content, text="Shuffle", variable=shuf)

global colourflag
colourflag=0

content.grid(column=0, row=0, sticky=(N, S, E, W))
text1.grid(column=0, row=0, columnspan=1, rowspan=20, sticky=(N, S, E, W))
text2.grid(column=0, row=20, columnspan=1, rowspan=20, sticky=(N, S, E, W))
text3.grid(column=1, row=0, columnspan=1, rowspan=20, sticky=(N, S, E, W))
text4.grid(column=1, row=20, columnspan=1, rowspan=20, sticky=(N, S, E, W))


exploreAZ_button.grid(column=3, row=31)
explore09_button.grid(column=3, row=30)
clear_verbatims.grid(column=3, row=3)
find_button.grid(column=3, row=5)
flag_button.grid(column=3, row=0)
showall_button.grid(column=3, row=1)
shuffle.grid(column=3, row=2)


#cancel.grid(column=2, row=4)

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
content.columnconfigure(0, weight=1)
content.columnconfigure(1, weight=1)
content.columnconfigure(2, weight=0)

content.rowconfigure(0, weight=1)
content.rowconfigure(1, weight=1)
content.rowconfigure(2, weight=1)
content.rowconfigure(3, weight=1)
content.rowconfigure(4, weight=1)
content.rowconfigure(5, weight=1)


popup= Toplevel()
some_frame = Frame(popup)
text5 = myText(some_frame)
some_frame.grid(column=0, row=0, sticky=(N, S, E, W))
text5.grid(column=0, row=0, columnspan=1, rowspan=20, sticky=(N, S, E, W))
popup.protocol("WM_DELETE_WINDOW", hidepopup)


quote1 = """To begin at the beginning:
:-)
It is spring, moonless night in the small town, starless
and bible-black, the cobblestreets silent and the hunched,
courters'-and-rabbits' wood limping invisible down to the
sloeblack, slow, black, crowblack, fishingboatbobbing sea.
The houses are blind as moles (though moles see fine to-night
in the snouting, velvet dingles) or blind as Captain Cat
there in the muffled middle by the pump and the town clock,
the shops in mourning, the Welfare Hall in widows' weeds.
And all the people of the lulled and dumbfound town are
sleeping now.

Hush, the babies are sleeping, the farmers, the fishers,
the tradesmen and pensioners, cobbler, schoolteacher,
postman and publican, the undertaker and the fancy woman,
drunkard, dressmaker, preacher, policeman, the webfoot
cocklewomen and the tidy wives. Young girls lie bedded soft
or glide in their dreams, with rings and trousseaux,
bridesmaided by glowworms down the aisles of the
organplaying wood. The boys are dreaming wicked or of the
bucking ranches of the night and the jollyrodgered sea. And
the anthracite statues of the horses sleep in the fields,
and the cows in the byres, and the dogs in the wetnosed
yards; and the cats nap in the slant corners or lope sly,
streaking and needling, on the one cloud of the roofs.

You can hear the dew falling, and the hushed town breathing.
Only _your_ eyes are unclosed to see the black and folded
town fast, and slow, asleep. And you alone can hear the
invisible starfall, the darkest-beforedawn minutely dewgrazed
stir of the black, dab-filled sea where the _Arethusa_, the
_Curlew_ and the _Skylark_, _Zanzibar_, _Rhiannon_, the _Rover_,
the _Cormorant_, and the _Star of Wales_ tilt and ride.

Listen. It is night moving in the streets, the processional
salt slow musical wind in Coronation Street and Cockle Row,
it is the grass growing on Llaregyb Hill, dewfall, starfall,
the sleep of birds in Milk Wood.

Listen. It is night in the chill, squat chapel, hymning in
bonnet and brooch and bombazine black, butterfly choker and
bootlace bow, coughing like nannygoats, sucking mintoes,
fortywinking hallelujah; night in the four-ale, quiet as a
domino; in Ocky Milkman's lofts like a mouse with gloves;
in Dai Bread's bakery flying like black flour. It is to-night
in Donkey Street, trotting silent, With seaweed on its
hooves, along the cockled cobbles, past curtained fernpot,
text and trinket, harmonium, holy dresser, watercolours
done by hand, china dog and rosy tin teacaddy. It is night
neddying among the snuggeries of babies.

Look. It is night, dumbly, royally winding through the
Coronation cherry trees; going through the graveyard of
Bethesda with winds gloved and folded, and dew doffed;
tumbling by the Sailors Arms.

Time passes. Listen. Time passes.

Come closer now.

Only you can hear the houses sleeping in the streets in the
slow deep salt and silent black, bandaged night. Only you
can see, in the blinded bedrooms, the combs and petticoats
over the chairs, the jugs and basins, the glasses of teeth,
Thou Shalt Not on the wall, and the yellowing dickybird-watching
pictures of the dead. Only you can hear and see, behind the
eyes of the sleepers, the movements and countries and mazes
and colours and dismays and rainbows and tunes and wishes
and flight and fall and despairs and big seas of their dreams.

From where you are, you can hear their dreams.

"""

quote3="""## A single pattern maps to its own flag
spring

## A list of patterns map to the same flag
cat,dog,fish>animal

## ! (NOT) negates previous patterns
fishing,fishers!animal

## [xyz] Alternative characters - Man or Men
m[ae]n>male

## ? means optional character
dress-?maker>dressmaker

## . means any single character - matches sleep, slipp
sl..p

## Three dots (ellipsis) ... means 'near' (up to 4 words apart)
wives...girls

##Emoticons
[:;]-?[\)D\]]>smile
:-?[\(\[|\/]>frown

## Excluding something from a flag
$Seasons>Cold  ##  A new flag ‘Cold’ is defined as all things with a ‘Seasons’ flag ($Seasons means Seasons flag)…
Sommer!Cold   ## but now we exclude ‘sommer’ from ‘Cold’



"""


## ISOBELLE issue 1
xquote1="""It is spring, moonless night in the small town, starless
and bible-black, the cobblestreets silent and the hunched,
courters'-and-rabbits' wood limping invisible down to the
"""
xquote3="""spring

## A list of patterns map to the same flag
cat,dog,fish>animal

## ! (NOT) negates previous patterns
fishing,fishers!animal

## [xyz] Alternative characters - Man or Men
m[ae]n>male"""

# For testing
xquote1=quote1 * 10
xquote3=quote3 * 1
xquote3='''
m[ae]n>male
dress-?maker>dressmaker
$dress!male
'''
text1.insert(END, quote1)

root.wm_title(title)

text2.insert(END, "unflagged")
text3.insert(END, quote3)
text4.insert(END, "counts")
f=open(tmp+'uniqwords.txt', 'w',encoding="utf-8")
f.write("\n")
f.close()

root.mainloop()
