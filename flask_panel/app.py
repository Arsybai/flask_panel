from base64 import decode
from flask import Flask, render_template, redirect, session, flash, request
import json, os, subprocess
import sql_control as db
from time import sleep

app = Flask(__name__)
app.secret_key = "FlaskPanelOIHSodiahsidnoIABDSIOandosdKONTOL"

with open('config.json', 'r') as cfg:
    config = json.load(cfg)

def execOS(cmd):
    tr_ = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = tr_.communicate()
    try:
        return str(decode(out))
    except:
        return str(out)

@app.route('/app/<port>/del')
def appDelApp(port):
    if not session.get('token'):
        flash("Session expired. Please relogin!", "warning")
        return redirect('/')
    data = db.fetchone("select * from sites where port='{}'".format(port))
    location_dir = "{port}{label}/*".format(**data)
    location_nginx = "/etc/nginx/sites-enabled/{port}{label}".format(**data)
    os.system("screen -X -S {port}{label} kill".format(**data))
    if os.path.isdir(location_dir):
        os.system("sudo rm -r {}".format(location_dir))
    if os.path.isfile(location_nginx):
        os.system("sudo rm -rf {}".format(location_nginx))
    db.delete("delete from sites where port='{port}'".format(**data))
    flash("App delete successfully", "success")
    return redirect('/app/my')


@app.route('/app/<port>/start')
def appStartApp(port):
    if not session.get('token'):
        flash("Session expired. Please relogin!", "warning")
        return redirect('/')
    data = db.fetchone("select * from sites where port='{}'".format(port))
    os.system("screen -dmS {port}{label}".format(**data))
    os.system("screen -S {port}{label} -X stuff 'cd /root/flask_panel/{port}{label} && python3 flask_panel_runner.py\n'".format(**data))
    db.update(["update sites set status='active' where port='{port}'".format(**data)])
    flash("App start successfully","success")
    return redirect('/app/my')

@app.route('/app/<port>/stop')
def appStopApp(port):
    if not session.get('token'):
        flash("Session expired. Please relogin!", "warning")
        return redirect('/')
    data = db.fetchone("select * from sites where port='{}'".format(port))
    if data == None:
        flash("App not found", "danger")
        return redirect('/app/my')
    os.system("screen -X -S {port}{label} kill".format(**data))
    db.update(["update sites set status='deactive' where port='{port}'".format(**data)])
    flash("App Shutdown successfully","success")
    return redirect('/app/my')

@app.route('/app/my')
def appMy():
    if not session.get('token'):
        flash("Session expired. Please relogin!", "warning")
        return redirect('/')
    datas = db.fetchall("select * from sites order by label asc")
    return render_template('myapp.html', datas=datas)
    

@app.route('/app/deploy', methods=['GET','POST'])
def appAppDeploy():
    if not session.get('token'):
        flash("Session expired. Please relogin!", "warning")
        return redirect('/')
    if request.method == 'GET':
        return render_template('deploy.html')
    elif request.method == 'POST':
        field = request.form
        site = db.fetchone("select * from sites where port='{}'".format(field['port']))
        if site != None:
            flash("App Deployed! access it from {}".format(field['server_name']), "success")
            return redirect('/app/deploy')
        db.insert(
                "insert into sites (label, port, server_name, location, status) values (%s,%s,%s,%s,%s)",
                (field['label'], field['port'], field['server_name'], 'r', 'active')
            )
        app_py = """from flask import Flask
app = Flask(__name__)
@app.route('/')
def hello():
    return 'Hello There :3'
if __name__ == "__main__":
    app.run()"""
        flask_panel_runner = """from app import app
from waitress import serve
if __name__ == "__main__":
    serve(app, host='0.0.0.0', port={})""".format(field['port'])
        nginx_se = """server {
            listen 80;
            server_name """+field['server_name']+""";
            location / {
                proxy_pass http://127.0.0.1:"""+field['port']+""";
                proxy_set_header Host $host;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            }
        }"""
        execOS(['mkdir','{port}{label}'.format(**field)])
        with open('{port}{label}/app.py'.format(**field), 'w') as ww:
            ww.write(app_py)
        with open('{port}{label}/flask_panel_runner.py'.format(**field), 'w') as ww:
            ww.write(flask_panel_runner)
        if not os.path.isfile('/etc/nginx/sites-enabled/{port}{label}'.format(**field)):
            with open('/etc/nginx/sites-enabled/{port}{label}'.format(**field), 'w') as ww:
                ww.write(nginx_se)
            execOS(['sudo','certbot','--nginx','-d',field['server_name']])
        execOS(['sudo','systemctl','restart','nginx'])
        sleep(3)
        os.system("screen -dmS {port}{label}".format(**field))
        os.system("screen -S {port}{label} -X stuff 'cd /root/flask_panel/{port}{label} && python3 flask_panel_runner.py\n'".format(**field))
        flash("Success deploy app. Please access it from your server name", "success")
        return redirect('/app/deploy')

@app.route('/app/ip')
def appThisIP():
    return execOS(['curl', '-4', 'icanhazip.com'])

@app.route('/databases/grant', methods=['POST'])
def appDatabaseGrant():
    if not session.get('token'):
        flash("Session expired. Please relogin!", "warning")
        return redirect('/')
    field = request.form
    db.update([
        "update user_db set privileges=concat(privileges, ', {database}') where username='{user}'".format(**field)
    ])
    os.system(
        "mysql -u root -e \"grant all privileges on {database}.* to '{user}'@'localhost'\"".format(**field)
    )
    flash("Grant privileges OK", "success")
    return redirect('/databases')


@app.route('/databases/user/create', methods=['POST'])
def appDatabasesCreateUser():
    if not session.get('token'):
        flash("Session expired. Please relogin!", "warning")
        return redirect('/')
    field = request.form
    db.insert(
        "insert into user_db (username,password) values (%s,%s)",
        (field['username'], field['password'])
    )
    os.system("mysql -u root -e \"create user '{username}'@'localhost' identified with mysql_native_password by '{password}'\"".format(**field))
    flash("Create user OK", "success")
    return redirect('/databases')

@app.route('/databases/create', methods=['POST'])
def appCreateDatabase():
    if not session.get('token'):
        flash("Session expired. Please relogin!", "warning")
        return redirect('/')
    field = request.form
    db.insert(
        "insert into db_list (db_name, user_db) values (%s,%s)",
        (field['data'], 'root')
    )
    try:
        os.system("mysql -u root -e \"create database {}\"".format(field['data']))
        flash("Create database OK", "success")
        return redirect('/databases')
    except Exception as e:
        flash(str(e), "danger")
        return redirect('/databases')


@app.route('/databases', methods=['GET','POST'])
def appDatabases():
    if not session.get('token'):
        flash("Session expired. Please relogin!", "warning")
        return redirect('/')
    if request.method == 'GET':
        users = db.fetchall("select * from user_db order by username asc")
        dbs = db.fetchall("select * from db_list")
        return render_template('databases.html', users=users, dbs=dbs)

@app.route('/', methods=['POST','GET'])
def hello():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        field = request.form
        if field['username'].lower() != config['admin']['username'].lower():
            flash("Wrong username!", "danger")
            return redirect('/')
        if field['password'] != config['admin']['password']:
            flash("Wrong password!", "danger")
            return redirect('/')
        session['token'] = field['username']
        return redirect('/panel')

@app.route('/logout')
def appLogout():
    session.clear()
    return redirect('/')

@app.route('/panel')
def appPanel():
    if not session.get('token'):
        flash("Session expired. Please relogin!", "warning")
        return redirect('/')
    return render_template('panel.html', phpmyadmin=config['server_name']['phpmyadmin'])

if __name__ == "__main__":
    app.run()