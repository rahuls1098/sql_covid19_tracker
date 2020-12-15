from collections import defaultdict
import pymysql
from array import array
from tabulate import tabulate
import datetime
import sys
import os

exitMsg = "\nRemember to wash your hands and stay at home. Stay safe out there!\n"

def drawTable(query, table):
	try:
		cur.execute(query)
		if(cur.rowcount > 0):
			rows = cur.fetchall();
			columns = []
			for cd in cur.description:
				columns.append(cd[0])
			print("\nTable: " + table + "\n" + tabulate(rows, headers="keys", tablefmt='psql'))	
		else:
			print("\n                              No records found in " + table + "!")
	except:
		print("\n" + table + " does not exist in the database.")


# View all people
def viewAllPerson():
	table = "person"
	query = "SELECT * FROM " + table
	drawTable(query, table)
	

# View all infected
def viewAllInfected():
	table = "infected"
	query = "SELECT * FROM infected NATURAL JOIN person"
	print("\nNote: only id and infectionDate are a part of the infected table.\n" +
		"the other fields are from the parent table (person), displayed for reference.")
	drawTable(query, table)

# View all recovered
def viewAllRecovered():
	table = "recovered"
	query = "SELECT * FROM recovered NATURAL JOIN person"
	print("\nNote: only id and recoveryDate are a part of the recovery table.\n" +
		"the other fields are from the parent table (person), displayed for reference.")
	drawTable(query, table)


# View all dead
def viewAllDead():
	table = "dead"
	query = "SELECT * FROM dead NATURAL JOIN person"
	print("\nNote: only id and deathDate are a part of the dead table.\n" +
		"the other fields are from the parent table (person), displayed for reference.")
	drawTable(query, table)

# View all regions
def viewAllRegion():
	table = "region"
	query = "SELECT * FROM " + table
	drawTable(query, table)


# View all hospitals
def viewAllHospital():
	table = "hospital"
	query = "SELECT * FROM " + table
	drawTable(query, table)

# View all hospital visits
def viewAllHospitalVisit():
	table = "hospital_visit"
	query = "SELECT * FROM " + table
	drawTable(query, table)

# View all tests
def viewAllTest():
	table = "test"
	query = "SELECT * FROM " + table
	drawTable(query, table)



# Display available tables
def displayTables():
	import covid19_tracker_interface
	global cur;
	global cnx;
	cur = covid19_tracker_interface.cur;
	cnx = covid19_tracker_interface.cnx;
	print("\n" + covid19_tracker_interface.line_separator(".", 65))
	tables = ["Person", "Infected", "Recovered", "Dead",  "Region", "Hospital", "Hospital_visit", "Test"];
	rowCount = 2;
	count = 0;
	lineBreak = "\n";
	actionValidated = False;
	print("(0) Exit application\n(1) Go back\n\nTables:\n-------")
	for x in tables:
		print("(" + str(rowCount) + ") " + x)
		rowCount += 1;
	while(not actionValidated):
		if(count > 0):
			lineBreak = "";
		try:
			numAction = int(input(lineBreak + "Enter a number (0-9): "));
		
			if(numAction == 0):
				cnx.close();
				actionValidated = True;
				print(exitMsg);
				os._exit(0);
			elif(numAction == 1):
				covid19_tracker_interface.view()
				actionValidated = True;
			elif(numAction == 2):
				viewAllPerson();
				actionValidated = True;
			elif(numAction == 3):
				viewAllInfected();
				actionValidated = True;
			elif(numAction == 4):
				viewAllRecovered();
				actionValidated = True;
			elif(numAction == 5):
				viewAllDead();
				actionValidated = True;
			elif(numAction == 6):
				viewAllRegion();
				actionValidated = True;
			elif(numAction == 7):
				viewAllHospital();
				actionValidated = True;
			elif(numAction == 8):
				viewAllHospitalVisit();
				actionValidated = True;
			elif(numAction == 9):
				viewAllTest();
				actionValidated = True;
			count += 1;
		except ValueError:
			count += 1;

		print("\n")
		displayTables();

def top5InfectedRegions():
	import covid19_tracker_interface
	global cur;
	global cnx;
	cur = covid19_tracker_interface.cur;
	cnx = covid19_tracker_interface.cnx;
	print("\n" + covid19_tracker_interface.line_separator(".", 65))
	try:
		cur.callproc('top5_most_infected_regions')
		rows = cur.fetchall();
		columns = []
		for cd in cur.description:
			columns.append(cd[0])
		print("\nTop 5 most infected regions:\n" + tabulate(rows, headers="keys", tablefmt='psql'))	
	except:
		print("Cannot view top 5 infected regions at this time.")


# Draw region tables with specified risk level
def drawRegionRisk(level):
	import covid19_tracker_interface
	global cur;
	global cnx;
	cur = covid19_tracker_interface.cur;
	cnx = covid19_tracker_interface.cnx;
	try:
		cur.callproc('regions_of_riskLevel', [level])
		if(cur.rowcount > 0):
			rows = cur.fetchall();
			columns = []
			for cd in cur.description:
				columns.append(cd[0])
			print("Regions of risk level " + str(level) + ":" "\n" + tabulate(rows, headers="keys", tablefmt='psql')
				+ "\nTuple count: " + str(cur.rowcount))	
		else:
			print("\n                              No records found for regions of level " + str(level) + "!")
	except Exception as e:
		print(e)
		print("Cannot retrieve regions at this time.")


# Specify risk level of regions to view
def regionsOfRiskLevel():
	import covid19_tracker_interface
	global cur;
	global cnx;
	cur = covid19_tracker_interface.cur;
	cnx = covid19_tracker_interface.cnx;
	print("\n" + covid19_tracker_interface.line_separator(".", 65))
	count = 0;
	lineBreak = "\n";
	actionValidated = False;
	while(not actionValidated):
		if(count > 0):
			lineBreak = "";
		try:
			level = int(input("Choose a risk level (0-3): "))
			
			drawRegionRisk(level)
			actionValidated = True;
			count += 1;
		except:
			count += 1;

		print("\n")

# Display people who are actively infected before or after a certain date
def viewActivelyInfectedBeforeAfter():
	import covid19_tracker_interface
	global cur;
	global cnx;
	cur = covid19_tracker_interface.cur;
	cnx = covid19_tracker_interface.cnx;
	print("\n" + covid19_tracker_interface.line_separator(".", 65))
	print("View actively infected people before (2) or after (3) a specified date")
	count = 0;
	lineBreak = "\n";
	actionValidated = False;
	tArr = ["before", "after"]
	while(not actionValidated):
		if(count > 0):
			lineBreak = ""
		try:
			beforeOrAfter = int(input("\n(0) Exit Application\n(1) Go back\n\nEnter a number (0-3): "));

			if(beforeOrAfter == 0):
				cnx.close();
				actionValidated = True;
				print(exitMsg);
				os._exit(0);
			elif(beforeOrAfter == 1):
				displayStatistics();
			elif(beforeOrAfter == 2 or beforeOrAfter == 3):

				year = int(input("Enter a year [YYYY]: "));
				month = int(input("Enter a month [M]: "))
				day = int(input("Enter a day [D]: "))
				date = datetime.date(year, month, day)
				try:
					cur.callproc('infected_before_afterDate', [beforeOrAfter, date])
					if(cur.rowcount > 0):
						rows = cur.fetchall();
						columns = []
						for cd in cur.description:
							columns.append(cd[0])

						print("\nActively infected people (" + tArr[beforeOrAfter - 2] + " " + str(year) +
						 "-" + str(month) + "-" + str(day) + "):\n" + tabulate(rows, headers="keys", tablefmt='psql')
						 + "\nTuple count: " + str(cur.rowcount))	
						actionValidated = True;
					else:
						print("\n                              No records found for your specifications. Try a different date!")
				except Exception as e:
					count += 1;
					print(e)
					print("Cannot retrieve people infected at this time")
		except:
			count += 1;

# Display statistics options
def displayStatistics():
	import covid19_tracker_interface
	global cur;
	global cnx;
	cur = covid19_tracker_interface.cur;
	cnx = covid19_tracker_interface.cnx;
	print("\n" + covid19_tracker_interface.line_separator(".", 65))
	print("(0) Exit application\n(1) Go back\n\nStatistics:\n-----------\n(2) Top 5 most infected regions\n(3) Regions with specific risk levels\n(4) Actively infected people before or after date");
	count = 0;
	lineBreak = "\n";
	actionValidated = False;
	while(not actionValidated):
		if(count > 0):
			lineBreak = "";
		try:
			numAction = int(input(lineBreak + "Enter a number (0-4): "));
			if(numAction == 0):
				cnx.close();
				actionValidated = True;
				print(exitMsg);
				os._exit(0);
			elif(numAction == 1):
				covid19_tracker_interface.view()
				actionValidated = True;
			elif(numAction == 2):
				top5InfectedRegions()
				actionValidated = True;
			elif(numAction == 3):
				regionsOfRiskLevel()
				actionValidated = True;
			elif(numAction == 4):
				viewActivelyInfectedBeforeAfter();
				actionValidated = True;
			count += 1;
		except Exception as e:
			count += 1;

		print("\n")
		displayStatistics();


