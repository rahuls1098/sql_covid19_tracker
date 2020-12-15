from collections import defaultdict
import pymysql
from array import array
from tabulate import tabulate
import covid19_view
import covid19_create
import covid19_update
import covid19_delete
import sys
import os
global cur;

################################################## \/ UTILITY FUNCTIONS/VARIABLES \/ ###############################################


exitMsg = "\nRemember to wash your hands and stay at home. Stay safe out there!\n"

def line_separator(mark, count):
	line = ""
	for x in range(count):
		line += mark
	return line;

# Login functionality
def login():
	validated = False;
	global cnx
	global cur
	while(not validated):
		try:
			username = input("Enter MySQL username: ");
			password = input("Enter MySQL password: ");
			cnx = pymysql.connect(host='localhost', user=username, password=password,
		                      db='covid19_tracker', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
			cur = cnx.cursor()
			validated = True;
		except:
			print('Incorrect username or password\n')


################################################## /\ UTILITY FUNCTIONS/VARIABLES /\ ##############################################





################################################## \/ CREATE CODE \/ #############################################################

def create():
	actionValidated = False;
	print("\n" + line_separator("*", 90) + "\n" + line_separator(" ", 42) + "CREATE" + "\n\nNOTE: Tables which you may directly add to here include:\n- person\n- region\n- hospital" +
		"\n\nAdding to the person table automatically adds them to infected, adds a test,\n" +
		"and provides the option of admitting them to a hospital (i.e. add to hospital_visit)." +
		"\nTo add to recovered, dead, or infected, the person must first be created here and then" +
		"\nyou can later choose to assign them to recovered, infected, or dead from the UPDATE "+ 
		"\nmenu option in the starting menu (equivalent to insert/create)." + 
		"\n" + line_separator("*", 90))
	print("\nChoose from the following tables to add an entry to:")
	print("(0) Exit application\n(1) Go back\n\nTables:\n-------")
	count = 0;
	lineBreak = "\n";
	tables = ["Person", "Region", "Hospital"];
	rowCount = 2
	for x in tables:
		print("(" + str(rowCount) + ") " + x)
		rowCount += 1;
	while(not actionValidated):
		if(count > 0):
			lineBreak = "";
		try:
			numTable = int(input(lineBreak + "Enter a number (0-4): "))

			if(numTable == 0):
				cnx.close();
				actionValidated = True;
				print(exitMsg);
				os._exit(0);
			elif(numTable == 1):
				main()
				actionValidated = True;
			elif(numTable == 2):
				covid19_create.insert_person()
				actionValidated = True;
			elif(numTable == 3):
				covid19_create.insert_region()
				actionValidated = True;
			elif(numTable == 4):
				covid19_create.insert_hospital()
				actionValidated = True;
			count += 1;
		except:
			count += 1;

################################################## /\ CREATE CODE /\ #############################################################





################################################## \/ UPDATE CODE \/ #############################################################

def update():
	actionValidated = False;
	print("\n" + line_separator("*", 90) + "\n" + line_separator(" ", 42) + "UPDATE" + "\n\nNOTE: "+
		"\nTables which you may directly update from here include:" +
		"\n- person\n- region\n- hospital\n\nHospital visit and test may not be modified" +
		" directly since they represent historical data\nthat document every instance of a person " +
		"getting infected, recovering, or dying. Indirect\nmodification of hospital visit and test may occur for " +
		"those that correspond to the current\nstatus of the person. Finally, update also " +
		"includes Update Status which entails\na CREATE (e.g. to recovered) and a DELETE (e.g. from infected).\n" +
		line_separator("*", 90))
	print("\nChoose from the following to update:")
	print("(0) Exit application\n(1) Go back\n\nTables:\n-------")
	count = 0;
	lineBreak = "\n";
	tables = ["Person", "Region", "Hospital", "^HEALTH STATUS"];
	rowCount = 2
	for x in tables:
		print("(" + str(rowCount) + ") " + x)
		rowCount += 1;
	print("\n^Change to infected, recovered, or dead\n")
	while(not actionValidated):
		if(count > 0):
			lineBreak = "";
		try:
			numTable = int(input(lineBreak + "Enter a number (0-5): "))

			if(numTable == 0):
				cnx.close();
				actionValidated = True;
				print(exitMsg);
				os._exit(0);
			elif(numTable == 1):
				main()
				actionValidated = True;
			elif(numTable == 2):
				covid19_update.update_person()
				actionValidated = True;
			elif(numTable == 3):
				covid19_update.update_region()
				actionValidated = True;
			elif(numTable == 4):
				covid19_update.update_hospital()
				actionValidated = True;
			elif(numTable == 5):
				covid19_update.update_status()
				actionValidated = True;
			count += 1;
		except:
			count += 1;


################################################## /\ UPDATE CODE /\ #############################################################


################################################## \/ DELETE CODE \/ #############################################################

def delete():
	actionValidated = False;
	print("\n" + line_separator("*", 90) + "\n" + line_separator(" ", 42) + "DELETE" + "\n\nNOTE: "+
		"Tables which you may directly delete from here include" +
		"\n- person\n- region\n- hospital\n\nDeleting from person automatically deletes" +
		" any associated hospital_visit and test tuples.\nDelete of infected, recovered," +
		"and dead are addressed in update. This is because changing\nthe status of a person" +
		" adds them to the new table (e.g. recovered) and deletes them\nfrom the old one (e.g. infected)." +
		"\n" + line_separator("*", 90))
	print("\nChoose from the following tables to delete an entry from:")
	print("(0) Exit application\n(1) Go back\n\nTables\n-------")
	count = 0;
	lineBreak = "\n";
	tables = ["Person", "Region", "Hospital"];
	rowCount = 2
	for x in tables:
		print("(" + str(rowCount) + ") " + x)
		rowCount += 1;
	while(not actionValidated):
		if(count > 0):
			lineBreak = "";
		try:
			numTable = int(input(lineBreak + "Enter a number (0-4): "))

			if(numTable == 0):
				cnx.close();
				actionValidated = True;
				print(exitMsg);
				os._exit(0);
			elif(numTable == 1):
				main()
				actionValidated = True;
			elif(numTable == 2):
				covid19_delete.delete_person()
				actionValidated = True;
			elif(numTable == 3):
				covid19_delete.delete_region()
				actionValidated = True;
			elif(numTable == 4):
				covid19_delete.delete_hospital()
				actionValidated = True;
			count += 1;
		except:

			count += 1;

################################################## /\ DELETE CODE /\ #############################################################



################################################## \/ VIEW CODE \/ #############################################################


def view():
	actionValidated = False;
	print("\n" + line_separator("*", 90) + "\n" + line_separator(" ", 42) + "VIEW" +  
	"\n" + line_separator("*", 90))
	print("\nChoose from the following viewable item:\n(0) Exit application\n(1) Go back\n\n(2) Tables\n(3) Statistics")
	count = 0;
	lineBreak = "\n";

	while(not actionValidated):
		if(count > 0):
			lineBreak = "";
		
		try:
			numAction = int(input(lineBreak + "Enter a number (0-3): "));
		
			if(numAction == 0):
				cnx.close();
				actionValidated = True;
				print(exitMsg);
				os._exit(0);
			elif(numAction == 1):
				main()
				actionValidated = True;
			elif(numAction == 2):
				covid19_view.displayTables();
				actionValidated = True;
			elif(numAction == 3):
				covid19_view.displayStatistics();
				actionValidated = True;
			count += 1;
		except:
			count += 1;


################################################## /\ VIEW CODE /\ #############################################################


################################################## \/ MAIN \/ ##################################################################


def main():
	cur = cnx.cursor();
	print("\n\n" + line_separator('~', 65) + "\n\nWelcome! Choose from the following list of actions: ");
	print("(0) Exit Application\n\n(1) CREATE\n(2) VIEW\n(3) UPDATE\n(4) DELETE");
	actionValidated = False;
	choiceValidated = False;
	count = 0;
	lineBreak = "\n";


	while(not actionValidated):
		if(count > 0):
			lineBreak = "";
		
		try:
			numAction = int(input(lineBreak + "Enter a number (0-4): "));
			if(not isinstance(numAction, int)):
				print("Please enter a number")
			else:
				if(numAction > 4 or numAction < 0):
					print("Please enter a number 1-4")
				elif(numAction == 0):
					print(exitMsg);
					actionValidated = True;
					os._exit(0);
					cnx.close();
				elif(numAction == 1):
					create()
					actionValidated = True;
				elif(numAction == 2):
					view()
					actionValidated = True;
				elif(numAction == 3):
					update()
					actionValidated = True;
				elif(numAction == 4):
					delete()
					actionValidated = True;
				else:
					print("Please enter a number 1-4")
					count += 1;
					actionValidated = True;
		except:
			print("Please enter a number 1-4")			


################################################## /\ MAIN /\ #################################################################


