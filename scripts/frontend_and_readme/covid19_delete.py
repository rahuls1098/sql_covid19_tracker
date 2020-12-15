from collections import defaultdict
import pymysql
from array import array
from tabulate import tabulate
import sys
import os

def return_table(cur):
	rows = cur.fetchall();
	columns = []
	for cd in cur.description:
		columns.append(cd[0])
	print(tabulate(rows, headers="keys", tablefmt='psql'))	


def getNum(dct):
	num = ""
	count = 0;
	for c in dct:
		if(not c.isalpha() and (c in '0123456789')):
			if(')' not in dct[count:len(dct)]):
				num += c;
		count += 1;
	return int(num);

def delete_region():
	import covid19_tracker_interface
	global cur;
	global cnx;
	cur = covid19_tracker_interface.cur;
	cnx = covid19_tracker_interface.cnx;
	confirmValidated = False;
	nameValidated = False;
	nameValidated2 = False;
	regionName = '';

	print("\n" + covid19_tracker_interface.line_separator(".", 65) + "\nDELETE FROM REGION" + 
		"\nSpecify region name to delete\n\nEnter field\n-----------");

	while(not nameValidated):
		regionName = input("regionName: ")
		if(not regionName.replace(" ", "").isalpha()):
			print("Please enter a string")
		else:
			try:	
				cur.callproc('verify_regionName', [regionName])
				print("\nRegion verified!\n")
				try:
					query = 'SELECT getRegionId(%s)'

					tempRegion = cur.execute(query, regionName)
					tempRegion2 = cur.fetchall()[0]
					tempRegion = getNum("%s" % str(tempRegion2))
					regionName = tempRegion
					nameValidated = True;
				except pymysql.Error as e:
					print("\n" + e.args[1] + "\n")
					nameValidated = True;
			except pymysql.Error as e:
				err = e.args[1]
				print("\n" + e.args[1] + "\n")
				if('Multiple instance' in err):
					print("Please enter the unique id of the desired region.\nRefer to the table below:")
					try:
						query = 'SELECT id, regionName, country, latitude, longitude FROM region WHERE regionName = %s';
						cur.execute(query, (regionName))
						return_table(cur)
					except pymysql.Error as e:
						print(e.args[1])
					while(not nameValidated2):
						try:
							regionName = int(input("Region ID: "));						
							try:
								cur.callproc('does_regionId_exist', [regionName])
								nameValidated2 = True;
							except pymysql.Error as e:
								print("\n" + e.args[1] + "\n")
						except Exception as e:
							print("Please enter a number")
					nameValidated = True;
				elif('not exist' in err):
					print("Refer to the following table below")
					try:
						query = 'SELECT DISTINCT(regionName) FROM region';
						cur.execute(query)
						return_table(cur)
					except pymysql.Error as e:
						print(e.args[1])
	while(not confirmValidated):
		print("\nAre you sure you want to delete from region?\n(1) Yes\n(2) No")
		try:
			confirm = int(input("Enter a number (1-2): "))
			if(not isinstance(confirm, int)):
				print("Please enter a number")
		except:
			print("Please enter a number")

		if(confirm == 1):
			
			try:
				cur.callproc('delete_region', [regionName])
				cnx.commit();
				print("\nSuccessfully deleted!\n")
				confirmValidated = True;
				covid19_tracker_interface.delete();

			except pymysql.Error as e:
				print("\n" + e.args[1] + "\n")
				confirmValidated = True;
				covid19_tracker_interface.delete();
	
		elif(confirm == 2):
			print("Deletion of region aborted.")
			confirmValidated = True;
			covid19_tracker_interface.delete();
		else:
			print("\nPlease enter a number 1-2")


def delete_hospital():
	import covid19_tracker_interface
	global cur;
	global cnx;
	cur = covid19_tracker_interface.cur;
	cnx = covid19_tracker_interface.cnx;
	confirmValidated = False;
	nameValidated = False;
	nameValidated2 = False;
	hospitalName = '';

	print("\n" + covid19_tracker_interface.line_separator(".", 65) + "\nDELETE FROM HOSPITAL" + 
		"\nSpecify hospital to delete\n\nEnter field\n-----------");

	while(not nameValidated):
		hospitalName = input("name: ")
		if(not hospitalName.replace(" ", "").isalpha()):
			print("Please enter a string")
		else:
			try:
				cur.callproc('does_hospital_exist', [hospitalName])
				print("\nHospital verified!\n")
				try:
					query = 'SELECT getHospitalId(%s)'

					tempHospital = cur.execute(query, hospitalName)
					tempHospital2 = cur.fetchall()[0]
					tempHospital = getNum("%s" % str(tempHospital2))
					hospitalName = tempHospital
					nameValidated = True;
				except pymysql.Error as e:
					print("\n" + e.args[1] + "\n")
					regionValidated = True;
			except pymysql.Error as e:
				err = e.args[1] 
				print("\n" + err + "\n")
				if('Multiple instance' in err):
					print("Please enter the unique id of the desired region.\nRefer to the table below:")
					try:
						query = 'SELECT t.id AS id, name AS %s, regionName AS %s FROM (SELECT id, name, regionId FROM hospital WHERE name = %s) t JOIN region WHERE region.id = t.regionId';
						cur.execute(query, ("Hospital Name", "Region Name",str(hospitalName)))
						return_table(cur)
					except pymysql.Error as e:
						print(e.args[1])
					while(not nameValidated2):
						try:
							hospitalName = int(input("Hospital ID: "));						
							try:
								cur.callproc('does_hospitalId_exist', [hospitalName])
								nameValidated2 = True;
							except pymysql.Error as e:
								print("\n" + e.args[1] + "\n")
						except Exception as e:
							print("Please enter a number")
					nameValidated = True;

				elif('not exist' in err):
					print("Refer to the following table below")
					try:
						query = 'SELECT DISTINCT(name) FROM hospital';
						cur.execute(query)
						return_table(cur)
					except pymysql.Error as e:
						print(e.args[1])
	while(not confirmValidated):
		print("\nAre you sure you want to delete from hospital?\n(1) Yes\n(2) No")
		try:
			confirm = int(input("Enter a number (1-2): "))
			if(not isinstance(confirm, int)):
				print("Please enter a number")
		except:
			print("Please enter a number")

		if(confirm == 1):
			
			try:
				cur.callproc('delete_hospital', [hospitalName])
				cnx.commit();
				print("\nSuccessfully deleted!\n")
				confirmValidated = True;
				covid19_tracker_interface.delete();

			except pymysql.Error as e:
				print("\n" + e.args[1] + "\n")
				confirmValidated = True;
				covid19_tracker_interface.delete();
	
		elif(confirm == 2):
			print("Deletion of hospital aborted.")
			confirmValidated = True;
			covid19_tracker_interface.delete();
		else:
			print("\nPlease enter a number 1-2")



def delete_person():
	import covid19_tracker_interface
	global cur;
	global cnx;
	cur = covid19_tracker_interface.cur;
	cnx = covid19_tracker_interface.cnx;
	fNameValidated = False;
	lNameValidated = False;
	firstAndLastValidated = False;
	personIdValidated = False;
	confirmValidated1 = False;
	confirmValidated2 = False;
	personIdValidated = False;
	personId = 0;
	firstName = '';
	lastName = '';

	print("\n" + covid19_tracker_interface.line_separator(".", 65) + "\nDELETE FROM PERSON" + 
		"\nSpecify person to delete\n\nEnter fields\n------------");
	while(not firstAndLastValidated):
		while(not fNameValidated):
			firstName = input("First name: ")
			if(not firstName.replace(" ", "").isalpha()):
				print("Please enter a string")
			else:
				fNameValidated = True;

		while(not lNameValidated):
			lastName = input("Last name: ")
			if(not lastName.replace(" ", "").isalpha()):
				print("Please enter a string")
			else:
				lNameValidated = True;

		try:
			query = 'SELECT * FROM person WHERE firstName = %s AND lastName = %s';
			cur.execute(query, (firstName, lastName));
			if(cur.rowcount == 1):
				while(not confirmValidated1):
					print("\nAre you sure you want to delete from person?\n(1) Yes\n(2) No")
					try:
						confirm = int(input("Enter a number (1-2): "))
						if(not isinstance(confirm, int)):
							print("Please enter a number")
					except:
						print("Please enter a number")

					if(confirm == 1):
						try:
							query = 'SELECT getPersonId(%s, %s)';
							tempPerson = cur.execute(query, (firstName, lastName))
							tempPerson2 = cur.fetchall()[0]
							tempPerson = getNum("%s" % str(tempPerson2))
							personId = tempPerson

							try:
								cur.callproc('delete_person', [personId])
								cnx.commit();
								print("\nSuccessfully deleted!\n")
								confirmValidated1 = True;
								firstAndLastValidated = True;
								covid19_tracker_interface.delete();

							except pymysql.Error as e:
								print("\n" + e.args[1] + "\n")
								confirmValidated1 = True;
								firstAndLastValidated = True;
								covid19_tracker_interface.delete();
						except Exception as e:
							print(e)	
							confirmValidated1 = True;
							firstAndLastValidated = True;
							covid19_tracker_interface.delete();
					elif(confirm == 2):
						print("Deletion of " + str(firstName) + " " + str(lastName) + " aborted.")
						confirmValidated = True;
						covid19_tracker_interface.delete();
					else:
						print("\nPlease enter a number 1-2")

			elif(cur.rowcount == 0):
				print("\nNo person found with name " + str(firstName) + " " + str(lastName) + "\n")
				print("Refer to the following table below:")
				try:
					f = 'First Name'
					l = 'Last Name'
					query = 'SELECT firstName AS %s, lastName AS %s FROM person';
					cur.execute(query, (f,l))
					return_table(cur)
					fNameValidated = False;
					lNameValidated = False;
				except pymysql.Error as e:
					print("\n" + e.args[1] + "\n")


			elif(cur.rowcount > 1):
				print("\nMultiple instances of " + str(firstName) + " " + str(lastName) + "exist.")
				print("Please enter a unique id.\nRefer to the table below:")

				try: 
					query = 'SELECT id, firstName, lastName FROM person WHERE firstName = %s AND lastName = %s';
					cur.execute(query, (str(firstName), str(lastName)))
					return_table(cur)
				except Exception as e:
					print(e)
				while(not personIdValidated):
					try:
						personId = int(input("Person ID: "));
						cur.callproc('does_personId_exist', [personId])
						personIdValidated = True;
						while(not confirmValidated2):
							print("\nAre you sure you want to delete " + str(firstName) + " " + str(lastName) + "?\n(1) Yes\n(2) No")
							try:
								confirm = int(input("Enter a number (1-2): "))
								if(not isinstance(confirm, int)):
									print("Please enter a number")
							except:
								print("Please enter a number")
							if(confirm == 1):
								try:
									cur.callproc('delete_person', [personId])
									cnx.commit();
									print("\nSuccessfully deleted!\n")
									confirmValidated2 = True;
									firstAndLastValidated = True;
									covid19_tracker_interface.delete();
								except pymysql.Error as e:
									print("\n" + e.args[1] + "\n")
									confirmValidated1 = True;
									firstAndLastValidated = True;
									covid19_tracker_interface.delete();
							elif(confirm == 2):
								print("Deletion of " + str(firstName) + " " + str(lastName) + " aborted.")
								confirmValidated2 = True;
								covid19_tracker_interface.delete();
							else:
								print("Please enter a number 1-2")
					except pymysql.Error as e:
						print(e.args[1] + "\n")

		except pymysql.Error as e:
			print("\n" + e.args[1] + "\n")
