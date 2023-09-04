from flask import *
import sqlite3
import compress
import random
import datetime
import random, string
import os
import genCodes
from werkzeug.security import generate_password_hash, check_password_hash



Flask.secret_key = '......P.o.l.i.s.h.I.s.N.o.t.m.y.N.a.t.i.o.n.a.l.i.t.y.....'
database = 'database.db'


def initDB():
    with open('.sql', 'r') as sql_file:
        sql_statements = sql_file.read()

    # Split SQL statements based on the semicolon delimiter
    statements = sql_statements.split(';')

    # Establish a connection to the SQLite database
    conn = sqlite3.connect(database)
    db = conn.cursor()

    # Iterate through and execute each SQL statement
    for statement in statements:
        statement = statement.strip()  # Remove leading/trailing whitespace
        if statement:  # Skip empty statements
            try:
                db.execute(statement)
            except sqlite3.Error as e:
                print(f"Error executing statement: {statement}")
                print(e)

    # Commit changes and close the connection
    conn.commit()
    conn.close()
def generateID(length):
    letters = string.ascii_letters+string.digits
    return ''.join(random.choice(letters) for i in range(length))
def _post(id,pizza,body,rating,paths,date,updated):
    conn = sqlite3.connect(database)
    db = conn.cursor()
    db.execute('INSERT INTO PIZZAS VALUES (?,?,?,?,?,?,?,?,?)',(id,pizza,body,rating,date or datetime.date.today().strftime('%Y-%m-%d'),session['uid'],paths,0,updated or datetime.date.today().strftime('%Y-%m-%d')))
    conn.commit()
    conn.close()
def getPost(id):
    conn = sqlite3.connect(database)
    db = conn.cursor()
    r = db.execute(f'SELECT * FROM PIZZAS WHERE REVIEW_ID="{id}"').fetchone()
    conn.close()
    return r
def execute(sql):
    conn = sqlite3.connect(database)
    db = conn.cursor()
    r = db.execute(sql).fetchall()
    conn.commit()
    conn.close()
    return r
def generateInviteCode():
    return generateID(random.randint(8,16))
def dateToTextDate(date):
    print(date)
    date = date.split('-')
    year = date[0]
    m={
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December"
}
    month = m[int(date[1])]
    day = date[2]
    return f"{month} {day}, {year}"
initDB()
if len(execute('SELECT * FROM INVITATIONS')) < 1:
    genCodes.generateCodes(128)
print(execute('SELECT * FROM INVITATIONS'))
app = Flask(__name__)

@app.route('/')
def index():
    latest = execute('SELECT REVIEW_ID,MENU_ITEM,RATING,DATE_REVIEWED,PATHS FROM PIZZAS WHERE POSTING_STATUS != 0 ORDER BY DATE_REVIEWED DESC LIMIT 10;')
    best  =  execute('SELECT REVIEW_ID,MENU_ITEM,RATING,DATE_REVIEWED,PATHS FROM PIZZAS WHERE POSTING_STATUS != 0 ORDER BY RATING DESC LIMIT 10;')
    lt=[] #latest thumbs
    bt=[] #best thumbs
    for i in latest:
        print(i)
        lt.append(json.loads(f'''{{"a":{i[4].replace("'",'"')}}}''')['a'][0])
    for i in best:
        bt.append(json.loads(f'''{{"a":{i[4].replace("'",'"')}}}''')['a'][0])
    return render_template('index.html',latest=latest,best=best,bt=bt,lt=lt,date=dateToTextDate,enumerate=enumerate)

@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        f = request.form
        name = f.get('username')
        if not name:
            return render_template('signup.html',e='Please provide a username.')
        if execute(f'SELECT * FROM USERS WHERE USERNAME = "{name}"'):
            return render_template('signup.html',e='That user already exists.')
        pw = f.get('pw')
        if not pw:
            return render_template('signup.html',e='Please provide a password.')
        invitation = f.get('ic')
        if not invitation:
            return render_template('signup.html',e='Please provide an invitation code.')
        if (invitation,) not in execute('SELECT * FROM INVITATIONS'):
            return render_template('signup.html',e='Invalid invitation code.')
        execute(f'DELETE FROM INVITATIONS WHERE CODE="{invitation}"')
        uid = random.randint(100000,9999999)
        joined = datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S.%f')
        conn = sqlite3.connect('database.db')
        db = conn.cursor()
        db.execute('INSERT INTO USERS VALUES (?,?,?,?,?)',(uid,name,generate_password_hash(pw),joined,'[]'))
        conn.commit()
        conn.close()
        session['logged_in'] = True
        session['uid'] = uid
        session['username'] = name
        return redirect('/')
    if session.get('logged_in'):
        return redirect('/')
    return render_template('signup.html')
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        f = request.form
        name = f.get('username')
        pw = f.get('pw')
        p = execute(F'SELECT PW FROM USERS WHERE USERNAME="{name}"')[0][0]
        if not p:
            return render_template('login.html',e='User does not exist.')
        if not check_password_hash(p,pw):
            return render_template('login.html',e='Invalid password.')
        session['logged_in'] = True
        session['uid'] = execute(f'SELECT ID FROM USERS WHERE USERNAME="{name}"')[0][0]
        session['username'] = name
        return redirect('/')
    if session.get('logged_in'):
        return redirect('/')
    return render_template('login.html')
@app.route('/logout')
def logout():
    session.pop('logged_in')
    session.pop('uid')
    session.pop('username')
    return redirect('/')


@app.route('/post',methods=['GET','POST'])
def post():
    if request.method == 'POST':
        if not session.get('logged_in'):
            return render_template('post.html',e='You must be logged in to review a pizza.')
        print('POST MADE')
        # if session.get('validated') or True:
        f = request.form
        _f = request.files.getlist('pizza_pic')
        for file in _f: #check if any file is invalid
            _f_ext = file.filename.split('.')[-1] #get file extension
            if _f_ext.lower() not in ['png','jpg','jpeg','webp','jfif','tiff','heic']: # check if is an image
                return render_template('post.html',e=f'File: {file.filename}, is not an image file.')
        paths = []
        for file in _f: # after check, now go through files to compress and save them
            filen = generateID(12) # file name
            p = 'static/uploads/'+filen+'.'+_f_ext # path
            ep = 'static/uploads/'+filen+'.webp' # end path
            paths.append(ep)
            file.save(p) # save temp file
            compress.compress_image(p,ep) #compress image
            os.remove(p)
        id = generateID(10)
        # img_posted_time = compress.convertDate(compress.getImageDATETIME(paths[0]))
        img_posted_time = f.get('date_reviewed')
        if not img_posted_time:
            return render_template('post.html',e='Please provide a valid date.')
        print('reviewed on: '+img_posted_time)
        _post(
            id,
            f.get('pizza'),
            f.get('body'),
            min(int(f.get('rating')),5),
            str(paths),
            img_posted_time,
            None
            ) # save to db
        return redirect(f'/review/{id}/{f.get("pizza").replace(" ","_")}')
    return render_template('post.html')

@app.route('/review/<id>')
@app.route('/review/<id>/<path:remainder>')
def review(id,remainder=None):
    data = getPost(id)
    print(data)
    if data == None or len(data) < 1:
        # print(data +'is invalid')
        return render_template('null_review.html')
    pizza = data[1]
    body = data[2]
    rating = data[3]
    post_time = dateToTextDate(str(data[4]))
    img_paths = data[6]
    id = data[0]
    reviewer = execute(
        f'''SELECT USERNAME FROM USERS WHERE ID={
                                                execute(f"SELECT REVIEWER_ID FROM PIZZAS WHERE REVIEW_ID='{id}'")[0][0]
                                                }''')[0][0]
    updated = dateToTextDate(str(data[8]))
    o = session.get('uid') == data[5]
    if data[7] == 0: # if not posted to internet
        print('Creator',data[5],"You",session.get('uid'))
        if o: #check if user is the poster, if so, they can view it
            return render_template('review.html',
                                   id=id,
                                   pizza=pizza,
                                   body=body,
                                   rating=rating,
                                   post_time=post_time,
                                   paths=img_paths,
                                   o=o,
                                   published=data[7],
                                   reviewer=reviewer,
                                   updated=updated
                                   )
        else: # no you cant
            return render_template('null_review.html')
    if data[7] == 1: # posted to internet. anyone can view
        return render_template('review.html',
                               id=id,
                               pizza=pizza,
                               body=body,
                               rating=rating,
                               post_time=post_time,
                               paths=img_paths,
                               published=data[7],
                               o=o,
                               reviewer=reviewer,
                               updated=updated
                               )
    if data[7] == 2: # archive - item is removed from menu or restaurant (sadly) closes
        return render_template('review.html',
                               id=id,
                               pizza=pizza,
                               body=body,
                               rating=rating,
                               post_time=post_time,
                               paths=img_paths,
                               published=data[7],
                               reviewer=reviewer,
                               updated=updated,
                               archive='yes'
                               )
    return render_template('null_review.html') # if pending deletion or deleted

@app.route('/edit/<id>',methods=['GET','POST'])
def edit(id):
    if request.method == 'POST':
        if not session.get('logged_in'):
            return redirect('/')
        id = request.referrer.split('/')[4]
        FF = request.form.get
        paths = execute(f'SELECT PATHS FROM PIZZAS WHERE REVIEW_ID="{id}"')[0][0].replace("'",'"')
        print(paths)
        paths = '{"a":'+paths+"}"
        print(paths)
        paths = json.loads(paths)['a']
        _f = request.files.getlist('pizza_pic')
        f_ = True
        for __f in _f: #check if there is an empty file
            if __f.filename == '':
                f_ = False
                break
        if f_:
            for path in paths:
                try:
                    os.remove(path)
                except:
                    print('hmm...')
            for file in _f: #check if any file is invalid
                _f_ext = file.filename.split('.')[-1] #get file extension
                if _f_ext.lower() not in ['png','jpg','jpeg','webp','jfif','tiff','heic']: # check if is an image
                    return render_template('edit.html',e=f'File: {file.filename}, is not an image file.')
            paths = []
            for file in _f: # after check, now go through files to compress and save them
                filen = generateID(12) # file name
                p = 'static/uploads/'+filen+'.'+_f_ext # path
                ep = 'static/uploads/'+filen+'.webp' # end path
                paths.append(ep)
                file.save(p) # save temp file
                compress.compress_image(p,ep) #compress image
                os.remove(p)
        print('|%!%|%!%| TODAY:',datetime.date.today())
        s_q_l = F'''UPDATE PIZZAS SET MENU_ITEM="{FF('pizza')}", BODY="{FF('body')}",RATING={FF('rating')},DATE_REVIEWED="{FF('date_reviewed')}",PATHS="{paths}",DATE_UPDATED="{datetime.date.today()}" WHERE REVIEW_ID='{id}';'''
        print(s_q_l)
        execute(s_q_l)
        return redirect(f'/review/{id}/{FF("pizza")}')
    uid = session.get('uid')
    rid = execute(f'SELECT REVIEWER_ID FROM PIZZAS WHERE REVIEW_ID="{id}"')[0][0] # reviewer-i-d
    print('UID',uid,'REVIEWER',rid)
    if uid == rid:
        data = execute(F'SELECT * FROM PIZZAS WHERE REVIEW_ID="{id}"')[0]
        pizza = data[1]
        body = data[2]
        rating = data[3]
        date = data[4]
        paths = data[6]
        return render_template('edit.html',id=id,pizza=pizza,body=body,date=date,paths=paths,rating=rating)
    return redirect('/review/'+id+'/🪬🛑🐙🛑🪬--;)')

@app.route('/publish',methods=['POST'])
def publish():
    if not session.get('logged_in'):
            return redirect('/')
    id = request.referrer.split('/')[4]
    if session.get('uid') == execute(f'SELECT REVIEWER_ID FROM PIZZAS WHERE REVIEW_ID="{id}"')[0][0]:
        execute(f'UPDATE PIZZAS SET POSTING_STATUS=1 WHERE REVIEW_ID="{id}"')
    return redirect(request.referrer)
@app.route('/unpublish',methods=['POST'])
def unpublish():
    if not session.get('logged_in'):
            return render_template('/')
    id = request.referrer.split('/')[4]
    if session.get('uid') == execute(f'SELECT REVIEWER_ID FROM PIZZAS WHERE REVIEW_ID="{id}"')[0][0]:
        execute(f'UPDATE PIZZAS SET POSTING_STATUS=0 WHERE REVIEW_ID="{id}"')
    print('UNPUBLISHED:',execute(f'SELECT * FROM PIZZAS WHERE REVIEW_ID="{id}"'))
    return redirect(request.referrer)

@app.route('/all')
def allReviews():
    reviews = execute('SELECT * FROM PIZZAS WHERE POSTING_STATUS != 0') #all+r = all+reviews; NOT MISPELLING OF ALLER (to go:french)
    thumbs = []
    for r in reviews:
        print(json.loads('{"a":'+r[6].replace("'",'"')+'}')['a'][0])
        thumbs.append(json.loads('{"a":'+r[6].replace("'",'"')+'}')['a'][0])
    return render_template('all.html',reviews=reviews,thumbs=thumbs,enumerate=enumerate,date=dateToTextDate)
@app.route('/my_reviews')
def myrevs():
    if not session.get('logged_in'):
        return redirect('/')
    reviews = execute(f'SELECT * FROM PIZZAS WHERE REVIEWER_ID={session.get("uid")}')
    thumbs = []
    for r in reviews:
        print(json.loads('{"a":'+r[6].replace("'",'"')+'}')['a'][0])
        thumbs.append(json.loads('{"a":'+r[6].replace("'",'"')+'}')['a'][0])
    unpublished = execute(f'SELECT * FROM PIZZAS WHERE REVIEWER_ID={session.get("uid")} AND POSTING_STATUS=0')
    published = execute(f'SELECT * FROM PIZZAS WHERE REVIEWER_ID={session.get("uid")} AND POSTING_STATUS=1')
    print(unpublished,published)
    return render_template('my_revs.html',reviews=reviews,unpublished=unpublished,published=published,thumbs=thumbs,enumerate=enumerate)

@app.route('/users/<path:remainder>')
def u():
    return redirect('/')
@app.errorhandler(404)
@app.route('/stars')
def stars():
    return render_template('stars.html')
app.run(port=4576)