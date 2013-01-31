from __future__ import with_statement
from contextlib import closing
import sqlite3, datetime, random, string
from flask import Flask, request, g, redirect, url_for, render_template, flash, current_app

# configuration
DATABASE = 'url.db'
DEBUG = True
SECRET_KEY = 'development key'


app = Flask(__name__)
app.config.from_object(__name__)
today = datetime.date.today()

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def query_db(query, args=(), one=False):
    cur = g.db.execute(query, args)
    return cur

#function to generate and test new arbitrary length URL shortkeys.
def genkey(keylength):
    test = "0"
    while test == "0":
        #TO-DO
        #if no key after 5 times, increase the keyspace by one.
        chars = "".join( [random.choice(string.letters) for i in xrange(keylength)] )
        test = checkifused("key",chars)
    return chars

#tests to see if data is in the DB already. returns 0 if no, 1 if yes.
def checkifused(column, data):
    q = g.db.execute('SELECT dest FROM urls WHERE '+ column +' ="' + data + '"')
    checkval=q.fetchone()
    if checkval is None:
        return "1"
    else:
        return "0"

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    g.db.close()

def debug():
    assert current_app.debug == False

@app.route('/')
def main():
    return render_template('add.html')

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST' and request.form['dest_url']:
        #checking to see if the user entered a custom shortcode, test it and return error if it's already in use.
        if request.form['ccode']:
            newurlkey = request.form['ccode']
            if checkifused("key",newurlkey) == "1":
                return render_template("sorry.html") # need to create this page where it says the custom key is in use. display the code and URL.
        else:
            newurlkey = genkey(5)

        #Does the url include a protocol?
        foorl = request.form['dest_url']
        if foorl[0:8] != "https://" and foorl[0:7] != "http://":
            foorl = "http://" + foorl

        #test if the entered URL is already there. We don't want dupes!
        urltest = checkifused("dest",foorl)
        if urltest == "0":
            q = g.db.execute('SELECT key FROM urls WHERE dest = ?',(foorl, ))
            oldurlkey = q.fetchone()[0]
            return render_template("added.html",linkurl=oldurlkey) # mention URL is already in use. give the short code.
        else:
            g.db.execute('INSERT INTO urls (key, dest) values (?,?)',[newurlkey,foorl])
            g.db.commit()
            return render_template('added.html', linkurl=newurlkey)
    else:
        return redirect(url_for('main'))

@app.route('/<shortcode>')
def redirecturl(shortcode): 
	q = g.db.execute('SELECT dest FROM urls WHERE key ="' + shortcode + '"')
	redirect_url=q.fetchone()
        if redirect_url is None:
            return "404 Not Found", 404
	redirect_url=redirect_url[0]
	#debug()
    #do a thing here to increment the viewed number
	return render_template('redirect.html', redirect_url=redirect_url)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0')