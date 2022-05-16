
from flask import Flask
from flask import render_template, url_for, request, flash, redirect
import sqlite3, os
from werkzeug.utils import secure_filename
from sys import platform as _platform
import signal
import sys
import atexit

# SETTING UP DNS RECORD
##############################################################################################################################
def osFinder():
    if _platform == "linux":
        return "/etc/hosts"
    elif _platform == "darwin":
        return "/etc/hosts"
    elif _platform == "win32":
        return "C:\\Windows\\System32\\drivers\\etc\\hosts"

from python_hosts import Hosts, HostsEntry
hosts = Hosts(path=osFinder())
new_entry = HostsEntry(entry_type='ipv4', address='127.0.0.1', names=['www.pls-stock.com', 'pls-stock'])
hosts.add([new_entry])
hosts.write()

def signal_handler(sig, frame):
    hosts = Hosts(path=osFinder())
    hosts.remove_all_matching(name='www.pls-stock.com')
    hosts.write()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def exit_handler():
    hosts = Hosts(path=osFinder())
    hosts.remove_all_matching(name='www.pls-stock.com')
    hosts.write()

atexit.register(exit_handler)

##############################################################################################################################

UPLOAD_FOLDER = 'static/assets/css/images'
ALLOWED_EXTENSIONS = {'png'}

app = Flask(__name__)
app.secret_key = "plsstock"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                 endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def createTableData(): 

    items = []

    conn = sqlite3.connect('mangaStock.db')
    cur = conn.cursor()

    try:
        cur.execute('SELECT * FROM mangas')
        conn.commit()
    except:
        cur.execute("CREATE TABLE mangas(title TEXT, status TEXT, grade TEXT)")
        conn.commit()
        flash("Database has been created.")


    liste = cur.fetchall()

    for i in liste:
        templist = ['title', 'status', 'grade']
        tempdict = {}
        n=0
        cpt = 0
        for j in i:
            tempdict[templist[cpt]] = j
            cpt+=1

        items.append(tempdict)


    cur.close()
    conn.close()
            
        
    return items


@app.route("/backend/addData", methods=['POST'])
def addData(): 

    titlevar = request.form['title'] 
    statusvar = request.form['status']
    gradevar = request.form['grade']
    
    conn = sqlite3.connect('mangaStock.db')
    cur = conn.cursor()

    data = (titlevar, statusvar, gradevar)

    cur.execute("INSERT INTO mangas(title, status, grade) VALUES(?, ?, ?)", data)

    conn.commit()

    cur.close()
    conn.close()
    
    flash("Data has been successfully added.") 
    
    headers = ["Manga's title",'Status', 'Grade /10']
    
    return redirect(url_for('index'))
    return render_template('index.html', headers = headers, objects=createTableData()) 
    

@app.route("/backend/deleteData", methods=['POST']) 
def deleteData(): 

    titlevar = request.form['title']

    conn = sqlite3.connect('mangaStock.db')
    cur = conn.cursor()

    data = (titlevar,)

    cur.execute('SELECT * FROM mangas WHERE title = ?', data)
    conn.commit()

    liste = cur.fetchall()

    if len(liste)>0:

        cur.execute('DELETE FROM mangas WHERE title = ?', data)
        flash("Data has been removed.")
        conn.commit()

    else:
        flash("Error. Data must be wrong. Please retry.")

    headers = ["Manga's title",'Status', 'Grade /10']
    
    return redirect(url_for('index'))
    return render_template('index.html', headers = headers, objects=createTableData())


@app.route("/backend/updateData", methods=['POST']) 
def updateData(): 

    titlevar = request.form['ancienttitle']
    statusvar = request.form['ancientstatus']
    gradevar = request.form['ancientgrade']
    
    newtitlevar = request.form['newtitle']
    newstatusvar = request.form['newstatus']
    newgradevar = request.form['newgrade']

    conn = sqlite3.connect('mangaStock.db')
    cur = conn.cursor()

    data = (newtitlevar, newstatusvar, newgradevar, titlevar, statusvar, gradevar)
    
    data0 = (titlevar, statusvar, gradevar)

    cur.execute('SELECT * FROM mangas WHERE title = ? AND status = ? AND grade = ?', data0)
    conn.commit()

    liste = cur.fetchall()

    if len(liste)>0:

        cur.execute('UPDATE mangas SET title = ?, status = ?, grade = ? WHERE title = ? AND status = ? AND grade = ?', data)
        flash("Data has been successfully modified.")
        conn.commit()

    else:
        flash("Error. Data must be wrong. Please retry.")

    headers = ["Manga's title",'Status', 'Grade /10']
    
    return redirect(url_for('index'))
    return render_template('index.html', headers = headers, objects=createTableData())

@app.route('/backend/changeWallpp', methods=['POST'])
def changeWallpp():


    file = request.files['file']

    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], "wallpp.png"))
        return redirect(url_for('index'))

@app.route("/backend/resetdb", methods=['GET', 'POST']) 
def resetdb(): 

    conn = sqlite3.connect('mangaStock.db')
    cur = conn.cursor()


    cur.execute("DELETE FROM mangas")

    conn.commit()

    cur.close()
    conn.close()
    
    flash("Database has been successfully reseted.")
    
    headers = ["Manga's title",'Status', 'Grade /10']
    
    return redirect(url_for('index'))
    return render_template('index.html', headers = headers, objects=createTableData())


@app.route("/backend/search", methods=['POST']) 
def search(): 

    itemsearchlist = []

    conn = sqlite3.connect('mangaStock.db')
    cur = conn.cursor()

    key = request.form['keywords']
    keytuple = (key, key, key)

    cur.execute("SELECT * FROM mangas WHERE title LIKE ? OR status LIKE ? OR grade LIKE ?", keytuple)
    conn.commit()

    liste = cur.fetchall()

    for i in liste:
        templist = ['title', 'status', 'grade']
        tempdict = {}
        n=0
        cpt = 0
        for j in i:
            tempdict[templist[cpt]] = j
            cpt+=1

        itemsearchlist.append(tempdict)


    cur.close()
    conn.close()
    
    headers = ["Manga's title",'Status', 'Grade /10']
    
    return render_template('index.html', headers = headers, objects=createTableData(), itemsearch = itemsearchlist)


@app.route('/')
def index(): 

    headers = ["Manga's title",'Status', 'Grade /10']
    return render_template('index.html', headers = headers, objects=createTableData())

if __name__ == '__main__': 

    print("\n---------------------------------------------------------------------\n")
    print("plsStockMyScans now running on http://pls-stock.com\n")
    print("---------------------------------------------------------------------\n")

    app.run(host="127.0.0.1", port="80", debug=True)


    
