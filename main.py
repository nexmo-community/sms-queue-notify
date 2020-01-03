import nexmo
import time, json, os
from flask import Flask, render_template, request, Response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


NEXMO_KEY = <Your Nexmo Key>
NEXMO_SECRET = <Your Nexmo Secret>
NEXMO_NUMBER = <Your Nexmo Number>


client = nexmo.Client(key=NEXMO_KEY, secret=NEXMO_SECRET)

db_path = "sqlite:///queue.db"

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = db_path

db = SQLAlchemy(app)

class User(db.Model):
    phone_number = db.Column(db.String, unique=True, nullable=False, primary_key=True)
    notified = db.Column(db.Integer)
    join_time = db.Column(db.DateTime)
    wait_time = db.Column(db.Integer)

@app.route('/')
def index():
    return render_template('index.html', length=query_length(), number=phone_format(NEXMO_NUMBER))

@app.route('/list', methods=('GET', 'POST'))
def list():
    if request.method == 'POST':
        if 'notify' in request.form:
            notify(request.form['notify'])
        elif 'remove' in request.form:
            remove(request.form['remove'])
        elif 'arrived' in request.form:
            remove(request.form['arrived'])
    users = query_users()
    return render_template('list.html', users=users)

@app.route('/webhooks/inbound-sms', methods=('GET', 'POST'))
def inbound_sms():
    if request.is_json:
        message = request.get(json())
    else:
        message = dict(request.form) or dict(request.args)
    num = message['msisdn']
    text = message['text'].lower()
    map = {
        "hi": add,
        "cancel": remove,
        "status": status,
        "help": help
    }
    action = map.get(text)
    if action:
        action(num)
    else:
        send(num, "Could not understand. Please try again")
    return ('', 204)

@app.route("/stream")
def stream():
    def eventStream():
        line_length = query_length()
        yield "data: {}\n\n".format(json.dumps(query_users()))
        while True:
            new_line_length = query_length()
            if new_line_length != line_length:
                line_length = new_line_length
                yield "data: {}\n\n".format(json.dumps(query_users()))
            time.sleep(1)
    return Response(eventStream(), mimetype="text/event-stream")

def phone_format(n):                                                                                                                                  
    return format(int(n[:-1]), ",").replace(",", "-") + n[-1]

def query_length():
    return User.query.filter(User.notified == 0).count()

def query_users():
    users_waiting = []
    users_notified = []
    for result in User.query.all():
        if result.notified == 0:
            time_diff = datetime.now() - result.join_time
            wait_time = divmod(time_diff.seconds, 60)[0]
            user = {"phone_number": str(result.phone_number), "wait_time": wait_time}
            users_waiting.append(user)
        else:
            wait_time = result.wait_time
            user = {"phone_number": str(result.phone_number), "wait_time": wait_time}
            users_notified.append(user)
    users = {"waiting": users_waiting, "notified": users_notified}
    return users

def send(num, text):    
    response = client.send_message({'from': NEXMO_NUMBER, 'to': num, 'text': text})
    response = response['messages'][0]
    if response['status'] == '0':
        print('Sent message', response['message-id'])
    else:
        print('Error:', response['error-text'])
    return

def add(num):
    if User.query.get(num):
        send(num, "Hello again!")
        status(num)
    else:
        user = User(phone_number=num, notified=0, join_time=datetime.now())
        db.session.add(user)
        db.session.commit()
        send(num, "You've been added to the list")
        help(num)
    return

def remove(num):
    user = User.query.get(num)
    if user:
        db.session.delete(user)
        db.session.commit()
        send(num, "You've been removed from the list")
    else:
        print("User not found")
    return

def notify(num):
    user = User.query.get(num)
    if user.notified == 0:
        send(num, "Your turn")
        user.notified = 1
        time_diff = datetime.now() - user.join_time
        user.wait_time = divmod(time_diff.seconds, 60)[0]
        db.session.commit()
    else:
        print("User already notified")
    return
    
def status(num):
    user = User.query.get(num)
    if not user:
        send(num, "Not in line")
    elif user.notified == 1:
        send(num, "Notified")
    else:
        users = query_users()
        users_sorted = sorted(users["waiting"], key = lambda i: i['wait_time'], reverse = True)   
        i = 0
        while i < len(users_sorted):
            if users_sorted[i]["phone_number"] == num:
                i += 1
                break
            i += 1
        send(num, "Number " + str(i) + " of " + str(len(users_sorted)) + " in line")
    return

def help(num):
    send(num, "For updates, text 'status'\nTo remove yourself from the list, text 'cancel'")
    return

if __name__ == '__main__':
    app.run(debug=True, threaded=True)


