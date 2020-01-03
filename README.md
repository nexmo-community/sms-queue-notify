# sms-queue-notify
A basic application for managing queues via SMS

## Getting started:

Clone this repo and navigate to the main directory:
```
git clone https://github.com/nexmo-community/sms-queue-notify.git
cd sms-queue-notify
```
Create and activate a virtual environment:
```
python3 -m venv venv
source venv/bin/activate
```
Install dependencies:
```
pip install -r requirements.txt
```
Initialize database:
```
python
>>> from main import db
>>> db.create_all()
>>> quit()
```
Launch ngrok on port 500 in a seperate terminal:
```
ngrok http 5000
```
From the Nexmo Dashboard, copy Key and Secret and paste into `main.py`:
```
NEXMO_KEY = "<Your Nexmo Key>"
NEXMO_SECRET = "<Your Nexmo Secret>"
```
Go to *Numbers* -> *Your numbers* and hover over your number until you see the copy button. Copy the number and paste into `main.py`:
```
NEXMO_NUMBER = "<Your Nexmo Number>"
```
While you're here,  click on the gear icon under the *Manage* column. In the *Inbound Webhook URL* field, enter the following, using your ngrok URL:
```
<Your ngrok URL>/webhooks/inbound-sms
```
Save the setting.

Return to the terminal and launch the application:
```
python main.py
```
In a browser, navigate to your ngrok URL to see the status view, or go to `<ngrok url>/list` to see the management view. Then text 'Hi' to the number you've configured to add yourself to the list!




