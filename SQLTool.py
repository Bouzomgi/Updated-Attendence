import sqlite3 as sql
import datetime
import pandas as pd
import csv
import re

database = "attendDB.db"
today = datetime.datetime.today().date()

def initTables():
	connection = sql.connect(database)
	startDate = today
	dates = pd.date_range(start = startDate, periods = 4, freq = 'W-SUN') #CHANGE THIS DATE
	dateformat = ', '.join([f'"{i.date()}" INT' for i in dates])

	connection.execute('CREATE TABLE IF NOT EXISTS Members(email TEXT PRIMARY KEY, firstName TEXT, lastName TEXT, needsCredit TEXT, ID TEXT);')

	connection.execute(f'CREATE TABLE IF NOT EXISTS AttendanceDates(email TEXT PRIMARY KEY, totalAttendance INT, {dateformat}, \
				FOREIGN KEY (email) REFERENCES Members(email) ON DELETE CASCADE);')

	connection.commit()


def pullNameList(filename):
	fieldnames = ['Timestamp', 'firstName', 'lastName', 'email', 'needsCredit']
	with open(filename, newline='') as csvfile:
		content = csv.DictReader(csvfile, fieldnames=fieldnames)
		return list(content)

def markAttendanceEmail(email):
	connection = sql.connect(database)
	value = connection.execute(f'SELECT * FROM Members WHERE email = "{email}"').fetchone()
	if value:
		previouslyMarked = connection.execute(f'SELECT "{today}" FROM AttendanceDates WHERE email = "{email}"').fetchone()
		if not previouslyMarked[0]:
			connection.execute(f'UPDATE AttendanceDates SET "{today}" = 1, totalAttendance = totalAttendance + 1 WHERE email = "{email}"')
			connection.commit()
			return (email, 0)
		return (email, 1)
	return None

def markAttendanceCard(ID):
	connection = sql.connect(database)
	email = connection.execute(f'SELECT email FROM Members WHERE ID = "{ID}"').fetchone()
	if email:
		email = email[0]
		previouslyMarked = connection.execute(f'SELECT "{today}" FROM AttendanceDates WHERE email = "{email}"').fetchone()
		if not previouslyMarked[0]:
			connection.execute(f'UPDATE AttendanceDates SET "{today}" = 1 WHERE email = "{email}"')
			connection.commit()
			return (email, 0)
		return (email, 1)
	return None

def pullName(email):
	connection = sql.connect(database)
	connection.row_factory = sql.Row
	value = connection.execute(f'SELECT firstName, lastName FROM Members WHERE email = "{email}"')
	return value.fetchone()

def checkDate():
	connection = sql.connect(database)
	connection.row_factory = sql.Row
	value = connection.execute('SELECT * from AttendanceDates')
	valueDict = dict(value.fetchall()[0])
	return str(today) in valueDict

def resetTables():
	initTables()
	addMembers(pullNameList('input.csv')[1:])

def bindCard(email, ID):
	connection = sql.connect(database)
	value = connection.execute(f'SELECT * FROM Members WHERE email = "{email}"').fetchone()
	if value:
		connection.execute(f'UPDATE Members SET ID = "{ID}" WHERE email = "{email}"')
		connection.commit()		
		return email
	return None

def addMembers(content, single = 0):
	connection = sql.connect(database)
	for member in content:
		info = member['email'], member['firstName'], member['lastName'], member['needsCredit']

		val = connection.execute(f'SELECT * FROM Members WHERE email = "{info[0]}"').fetchone()
		if single and val:
			return None

		connection.execute(f'INSERT OR REPLACE INTO Members (email, firstName, lastName, needsCredit) VALUES ("{info[0]}", \
			"{info[1]}", "{info[2]}", "{info[3]}");')

		connection.execute(f'INSERT OR REPLACE INTO AttendanceDates (email, totalAttendance) VALUES ("{info[0]}", 0);')

	connection.commit()
	if single: return info[1], info[2]


def removeMember(email):
	connection = sql.connect(database)
	connection.row_factory = sql.Row
	value = connection.execute(f'SELECT * FROM Members WHERE email = "{email}"').fetchone()
	if value:
		value = dict(value)
		cur = connection.cursor()
		cur.executescript(f'PRAGMA foreign_keys = ON; \
			DELETE FROM Members WHERE email = "{email}"')
		connection.commit()		
		return value['firstName'], value['lastName']
	return None


resetTables()
