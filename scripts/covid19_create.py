from collections import defaultdict
import pymysql
from array import array
from tabulate import tabulate
import datetime
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

def insert_hospital():
	import covid19_tracker_interface
	global cur;
	global cnx;
	cur = covid19_tracker_interface.cur;
	cnx = covid19_tracker_interface.cnx;
	nameValidated = False;
	regionValidated = False;
	regionValidated2 = False;
	confirmValidated = False;
	hospitalName = '';
	region = '';

	print("\n" + covid19_tracker_interface.line_separator(".", 65) + "\nINSERT ON HOSPITAL" + 
		"\nFields: [id, name, regionId]\n\nEnter fields\n------------");
	
	while(not regionValidated):
		region = str(input("Hospital region: "));
		if(not region.replace(" ", "").isalpha()):
			print("Please enter a string")
		else:
			try:
				cur.callproc('verify_hospital_regionName', [region])
				print("\nRegion verified!\n")
				try:
					query = 'SELECT getRegionId(%s)'

					tempReg = cur.execute(query, region)
					tempReg2 = cur.fetchall()[0]
					tempReg = getNum("%s" % str(tempReg2))
					region = tempReg
					regionValidated = True;
				except pymysql.Error as e:
					print("\n" + e.args[1] + "\n")
					regionValidated = True;
			except pymysql.Error as e:
				err = e.args[1]
				print("\n" + err + "\n")
				if('not exist' in err):
					print("Refer to the following table below")
					try:
						query = 'SELECT DISTINCT(regionName) FROM region';
						cur.execute(query)
						return_table(cur)
					except pymysql.Error as e:
						print(e.args[1])
				elif('Multiple instances'):
					print("Please enter the unique id of the desired region.\nRefer to the table below:")
					try: 
						query = 'SELECT id, regionName, country, latitude, longitude FROM region WHERE regionName = %s';
						cur.execute(query, (region))
						return_table(cur)
					except Exception as e:
						print(e)
					while(not regionValidated2):
						try:
							region = int(input("Region ID: "));
							try:
								cur.callproc('does_regionId_exist', [region])
								regionValidated2 = True;
							except pymysql.Error as e:

								print(e.args[1] + "\n")
						except Exception as e:
							print("Please enter a number")
					regionValidated = True;

	while(not nameValidated):
		hospitalName = str(input("Hospital name: "));
		if(not hospitalName.replace(" ", "").isalpha()):
			print("Please enter a string")
		else:
			try:
				cur.callproc('verify_hospital', [hospitalName, region])
				print("\nHospital name verified!\n")
				nameValidated = True;
			except pymysql.Error as e:
				err = e.args[1]
				print("\n" + err)
				print("Use another name for hospital.\n")

	while(not confirmValidated):
		print("\nAre you sure you want to insert into hospital?\n(1) Yes\n(2) No")
		confirm = int(input("\nEnter a number (1-2): "))
		if(confirm == 1):
			try:
				cur.callproc('insert_in_hospital', [hospitalName, int(region)])
				cnx.commit();
				print("\nSuccessfully inserted!\n")
				confirmValidated = True;
				covid19_tracker_interface.create();
			except pymysql.Error as e:
				print("\n" + e.args[1])
		elif(confirm == 2):
			print("Insert of " + hospitalName + " aborted.")
			confirmValidated = True;
			covid19_tracker_interface.create();
		else:
			print("\nPlease enter a number 1-2")


def insert_region():
	import covid19_tracker_interface
	global cur;
	global cnx;
	cur = covid19_tracker_interface.cur;
	cnx = covid19_tracker_interface.cnx;
	nameValidated = False;
	countryValidated = False;
	latValidated = False;
	longValidated = False;
	totalPopValidated = False;
	lockdownValidated = False;
	confirmValidated = False;
	region = '';
	country = '';
	lat = 0;
	lon = 0;
	totalPop = 0;
	lockdown = False;

	print("\n" + covid19_tracker_interface.line_separator(".", 65) + "\nINSERT ON REGION" + 
	"\nFields: [id, regionName, country, latitude, longitude, totalPop, riskLevel, percentInfected]\n\nEnter fields\n------------");

	while(not nameValidated):
		print("Region name can be anywhere an outbreak has occured\n" +
			"including a city, country, cruise ship, etc.\n")
		region = str(input("Region name: "))
		if(not region.replace(" ", "").isalpha()):
			print("Please enter a string")
		else:
			nameValidated = True;
	while(not countryValidated):
		country = str(input("Country name: "))
		if(not country.replace(" ", "").isalpha()):
			print("Please enter a string")
		else:
			countryValidated = True;
	while(not latValidated):
		try:
			lat = float(input("Latitude: "))
			if(not isinstance(lat, float) and not isinstance(lat, int)):
				print("Please enter a number")
			else:
				latValidated = True;
		except:
			print("Please enter a number")
	while(not longValidated):
		try:
			lon = float(input("Longitude: "))
			if(not isinstance(lon, float) and not isinstance(lon, int)):
				print("Please enter a number")
			else:
				longValidated = True;
		except:
			print("Please enter a number")
	while(not totalPopValidated):
		try:
			totalPop = int(input("Total Population: "))
			if(not isinstance(totalPop, int)):
				print("Please enter a number")
			else:
				totalPopValidated = True;
		except: 
			print("Please enter a number")
	while(not lockdownValidated):
		lockdown = input(region + " on lockdown? (y/n): ")
		if((lockdown is not 'y') and (lockdown is not 'n')):
			print("Please enter y or n")
		else:
			if(lockdown == 'y'):
				lockdown = True;
			elif(lockdown == 'n'):
				lockdown = False;
			lockdownValidated = True;
	try:
		cur.callproc('verify_uniqueRegion', [region, country, lat, lon])
		print("Region fields validated!")
	except pymysql.Error as e:
		print("\n" + e.args[1] + "\n");
		print("Try again?\n(1) Yes\n(2) Abort insert region")
		tryAgain = int(input("Enter a number (1-2)"))
		if(tryAgain == 1):
			insert_region();
		elif(tryAgain == 2):
			create();
		else:
			print("Please enter a number 1-2")

	while(not confirmValidated):
		print("\nAre you sure you want to insert into region?\n(1) Yes\n(2) No")
		confirm = int(input("\nEnter a number (1-2): "))
		if(confirm == 1):
			try:
				cur.callproc('insert_region', [region, country, lat, lon, totalPop, lockdown])
				cnx.commit();
				print("\nSuccessfully inserted!\n")
				confirmValidated = True;
				covid19_tracker_interface.create();
			except pymysql.Error as e:
				print("\n" + e.args[1])
		elif(confirm == 2):
			print("Insert of " + region +" aborted.")
			confirmValidated = True;
			covid19_tracker_interface.create();
		else:
			print("\nPlease enter a number 1-2")




def insert_person():
	import covid19_tracker_interface
	global cur;
	global cnx;
	cur = covid19_tracker_interface.cur;
	cnx = covid19_tracker_interface.cnx;
	fNameValidated = False;
	lNameValidated = False;
	sexValidated = False;
	dobValidated = False;
	regionValidated = False;
	regionValidated2 = False;
	infectDateValidated = False;
	admitHospitalValidated = False;
	admitHospitalValidated2 = False;
	hospitalValidated = False;
	confirmValidated = False;
	firstName = '';
	lastName = '';
	sex = '';
	dob = 'YYYY-MM-DD';
	homeRegion = 0;
	currentRegion = 0;
	hospital = 0;
	count = 0;
	lineBreak = "\n";

	print("\n" + covid19_tracker_interface.line_separator(".", 65) + "\nINSERT ON PERSON" + 
		"\nFields: [id, firstName, lastName, dob, sex, homeRegion, currentRegion]\n\nEnter fields\n------------");
	while(not fNameValidated):
		firstName = str(input("First name: "));
		if(not firstName.replace(" ", "").isalpha()):
			print("Please enter a string")
		else:
			fNameValidated = True;

	while(not lNameValidated):
		lastName = str(input("Last name: "));
		if(not lastName.replace(" ", "").isalpha()):
			print("Please enter a string")
		else:
			lNameValidated = True;

	while(not sexValidated):
		sex = str(input("Sex: ")).lower()
		if(sex == 'male' or sex == 'female' or sex == 'other'):
			sexValidated = True;
		else:
			print("Please enter string: male, female, or other")

	while(not dobValidated):
		try:
			print("Date of Birth")
			year = int(input("YYYY: "));
			month = int(input("MM: "));
			day = int(input("DD: "));
			dob = datetime.date(year, month, day);
			try: 
				cur.callproc('validate_dateOfBirth', [dob])
				dobValidated = True;
			except pymysql.Error as e:
				print(e.args[1] + "\n")
		except Exception as e:
			print("Please enter using the specified date format\n")

	while(not regionValidated):
		homeRegion = str(input("Home Region: "));
		currentRegion = str(input("Current Region: "));
		if((not homeRegion.replace(" ", "").isalpha()) or (not currentRegion.replace(" ", "").isalpha())):
			print("Please enter a string")
		else:
			try:
				cur.callproc('verify_person_regionName', [homeRegion, currentRegion])
				print("\nRegions successfully validated!")
				try:
					query = 'SELECT getRegionId(%s)';
					
					tempHome = cur.execute(query, homeRegion)
					tempHome2 = cur.fetchall()[0]
					tempHome = getNum("%s" % str(tempHome2))
					homeRegion = tempHome

					tempCurrent = cur.execute(query, currentRegion)
					tempCurrent2 = cur.fetchall()[0]
					tempCurrent = getNum("%s" % str(tempCurrent2))
					currentRegion = tempCurrent
					regionValidated = True;
				except pymysql.Error as e:
					print("\n" + err + "\n")
					regionValidated = true;

			except pymysql.Error as e:
				err = e.args[1]
				print("\n" + err + "\n")
				if('not exist' in err):
					print("Refer to the following table below:")
					try:
						query = 'SELECT DISTINCT(regionName) FROM region';
						cur.execute(query)
						return_table(cur)
					except pymysql.Error as e:
						print(e.args[1])
				elif('Multiple instances' in err):
					print("Please enter the unique id of the desired region.\nRefer to the table below:")
					try:
						query = 'SELECT id, regionName, country, latitude, longitude FROM region WHERE regionName = %s or regionName = %s';
						cur.execute(query, (homeRegion, currentRegion))
						return_table(cur)
					except pymysql.Error as e:
						print(e.args[1])
					while(not regionValidated2):
						try:
							homeRegion = int(input("Home Region ID: "));
							currentRegion = int(input("Current Region ID: "))
						
							try:
								cur.callproc('does_regionId_exist', [homeRegion])
								cur.callproc('does_regionId_exist', [currentRegion])
								regionValidated2 = True;
							except pymysql.Error as e:
								print("\n" + e.args[1] + "\n")
						except Exception as e:
							print("Please enter a number")
					regionValidated = True;

						
	print("\n" + firstName + " " + lastName + " will be added to the list of infected people.\n" +
		"Please provide a few more details:\n");

	while(not infectDateValidated):
		try:
			print("Infection Date")
			iyear = int(input("YYYY: "));
			imonth = int(input("MM: "));
			iday = int(input("DD: "));
			infectDate = datetime.date(iyear, imonth, iday);
			try:
				cur.callproc('validate_infectionDate', [infectDate, dob])
				infectDateValidated = True;
			except pymysql.Error as e:
				print(e.args[1] + "\n")
		except Exception as e:
			print("Please enter using the specified date format\n")

	try:
		cur.callproc('check_hospital_in_region', [int(currentRegion)]);
		while(not admitHospitalValidated):
			print("\n\nAdmit " + firstName + " " + lastName + " to a hospital?\n(1) Yes\n(2) No")
			try:
				admitToHospital = int(input("\nEnter a number (1-2): "));
				if(admitToHospital == 1):
					admitHospitalValidated = True;
					while(not hospitalValidated):
						hospital = str(input("Enter hospital name: "))
						for x in hospital:
							if(x.isalpha() or x == ' '):
								continue;
							else:
								print("Please enter a string")
								break;	
						try:
							cur.callproc('hospital_exists_in_region', [hospital, int(currentRegion)])
							print("Hospital successfully validated!")
							try:
								query = 'SELECT getHospId(%s, %s)';
								tempHospital = cur.execute(query, (hospital, currentRegion))
								tempHospital2 = cur.fetchall()[0]
								tempHospital = getNum("%s" % str(tempHospital2))
								hospital = tempHospital


								hospitalValidated = True;
								admitHospitalValidated = True;
							except pymysql.Error as e:
								print("\n" + e.args[1] + "\n")

						except pymysql.Error as e:
							err = e.args[1]
							print("\n" + err + "\n")
							if('does not exist' in err):
								print("Refer to the following table below:")
								try:
									query = 'SELECT DISTINCT(name) FROM hospital where regionId = %s';
									cur.execute(query, (int(currentRegion)))
									return_table(cur)
								except pymysql.Error as e:
									print(e.args[1])
				elif(admitToHospital == 2): 
					admitHospitalValidated = True;
			except:
				print("\nPlease enter a number 1-2")
	except pymysql.Error as e:
		admitToHospital = 0;
		print("\n" + e.args[1])
		print(firstName + " " + lastName + " will not be admitted to a hospital at this time.\n")

	while(not confirmValidated):
		print("\nAre you sure you want to insert into person?\n(1) Yes\n(2) No")
		confirm = int(input("\nEnter a number (1-2): "))
		if(confirm == 1):
			try:
				cur.callproc('insert_person', [firstName, lastName, dob, sex, homeRegion, currentRegion, infectDate, admitToHospital, hospital])
				cnx.commit();
				print("\nSuccessfully inserted!\n")
				confirmValidated = True;
				covid19_tracker_interface.create();
			except pymysql.Error as e:
				print("\n" + e.args[1])
		elif(confirm == 2):
			print("Insert of " + firstName + " " + lastName + " aborted.")
			confirmValidated = True;
			covid19_tracker_interface.create();
		else:
			print("\nPlease enter a number 1-2")




	
			
		






	


	

