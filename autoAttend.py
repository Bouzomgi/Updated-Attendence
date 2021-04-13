from flask import Flask, render_template, request
import re
from SQLTool import *

app = Flask(__name__)
host = 'http://127.0.0.1:5000/'
content = []

@app.route('/', methods=['POST', 'GET']) #remove, clear
def index():
	if request.method == 'POST':
		if request.form['mode'] == 'query':
			text = request.form['text']
			if text == 'clear': 
				content.clear()
			elif text.find('remove') != -1 and len(text) > 7:
				content.append(memberRemoval(text[7:]))
			else:
				content.append(markAttendance(text))

		elif request.form['mode'] == 'bind':
			email, card = request.form['email'], request.form['card']
			content.append(bindResult(email, card))

		elif request.form['mode'] == 'register':
			info = request.form['email'], request.form['firstName'], \
			request.form['lastName']
			creditInfo = 'Yes' if 'needsCredit' in request.form else 'No'
			content.append(memberRegistration(info, creditInfo))

	return render_template('base.html', content=content[::-1])


def markAttendance(user):
	if not checkDate():
		return 'Accessing on invalid date!'

	elif re.match(r'^%A[0-9]{9}=[0-9]{15}\?$', user):
		return('Swipe did not go through. Please reswipe.')

	elif re.match(r'^%A[0-9]{9}=[0-9]{15}\?;[0-9]{16}=[0-9]{12}\?$', user):
		if (result := markAttendanceCard(hash(user))):
			nameDict = dict(pullName(result[0]))
			if result[1] == 0:
				return f'Attendance has been recorded for {nameDict["firstName"]} {nameDict["lastName"]}.'
			elif result[1] == 1:
				return f'You\'ve already filled attendance for this week, {nameDict["firstName"]} {nameDict["lastName"]}.'
			
		return f'That card is not recognized. Please register your card with the Bind ID button above.'
		
	else:
		user = adjustEmail(user)
		if (result := markAttendanceEmail(user)):
			nameDict = dict(pullName(result[0]))
			if result[1] == 0:
				return f'Attendance has been recorded for {nameDict["firstName"]} {nameDict["lastName"]}.'
			elif result[1] == 1:
				return f'You\'ve already filled attendance for this week, {nameDict["firstName"]} {nameDict["lastName"]}.'
			
		return f'That email is not recognized. Please register your email with the Register button above.'

def adjustEmail(email):
	email = email.strip().lower()
	if not re.match(r'^[a-z0-9]+@psu\.edu$', email):
		email = email + '@psu.edu'
	return email

def bindResult(email, ID):
	email = adjustEmail(email)
	ID = ID.strip()
	if re.match(r'^%A[0-9]{9}=[0-9]{15}\?$', ID):
		return 'Swipe did not go through. Please try to bind again.'

	elif re.match(r'^%A[0-9]{9}=[0-9]{15}\?;[0-9]{16}=[0-9]{12}\?$', ID): 

		if (bindCard(email, hash(ID))):
			nameDict = dict(pullName(email))
			return f'{nameDict["firstName"]} {nameDict["lastName"]} has successfully binded their card.'

		return 'That email is not recognized. Please register your email with the Register button above.'

	return 'Invalid card value. Please try to bind again.'


def memberRegistration(info, creditInfo):
	info = [i.strip().lower() for i in info]
	info[0] = adjustEmail(info[0])
	info[1] = adjustText(info[1])
	info[2] = adjustText(info[2])
	infoDict = {'email': info[0], 'firstName': info[1], 'lastName': info[2], 'needsCredit': creditInfo}
	if (name := addMembers([infoDict], 1)):
		return f'{name[0]} {name[1]} has been formally registered for PyLO.'
	return 'The inputted email is already registered. Leave the line and ask Brian for assistance.'

def adjustText(txt):
	if txt.isspace() or not txt: return txt
	txt = list(txt)
	txt[0] = txt[0].upper()
	for index in range(len(txt)-1):
		if txt[index] in ("-", " "):
			txt[index + 1] = txt[index + 1].upper()
	return ''.join(txt)

def memberRemoval(email):
	email = adjustEmail(email)
	if (info := removeMember(email)):
		return f'{info[0]} {info[1]} has been removed from the PyLO Registration.'
	return f'Removal failed: The email {email} is not registered.'







