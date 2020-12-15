from collections import defaultdict
import pymysql
from array import array
from tabulate import tabulate
import datetime
import sys
import os

exitMsg = "\nRemember to wash your hands and stay at home. Stay safe out there!\n"


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

def updateToInfected(personId):
	import covid19_tracker_interface
	global cur;
	global cnx;
	cur = covid19_tracker_interface.cur;
	cnx = covid19_tracker_interface.cnx;
	infectDateValidated = False;
	infectDate = 'YYYY-MM-DD';
	confirmValidated = False;
	admitHospitalValidated = False;
	admitToHospital = 0;
	considerHospital = False;
	hospitalValidated = False;
	currentRegion = 0;
	confirm = 0;


	try:
		curRegQuery = 'SELECT getCurrentRegion(%s)';
		tempReg = cur.execute(curRegQuery, (personId))
		tempReg2 = cur.fetchall()[0]
		tempReg = getNum("%s" % str(tempReg2))
		currentRegion = tempReg
		considerHospital = True;
	except pymysql.Error as e:
		print("\n" + e.args[1] + "\n")

	print("\n" + covid19_tracker_interface.line_separator(".", 90) + "\nUPDATE TO INFECTED\n\nEnter infection date:")
	while(not infectDateValidated):
		try:
			print("\nInfection Date\n----------------")
			year = int(input("YYYY: "));
			month = int(input("MM: "));
			day = int(input("DD: "));
			infectDate = datetime.date(year, month, day);
			try: 
				cur.callproc('validate_InfectDate', [personId, infectDate])
				infectDateValidated = True;
			except pymysql.Error as e:
				print(e.args[1] + "\n")
		except Exception as e:
			print("Please enter using the specified date format\n")


	while(not confirmValidated):
		print("\nAre you sure you want to update person?\n(1) Yes\n(2) No")
		confirm = int(input("\nEnter a number (1-2): "))
		if(confirm is not 1 and confirm is not 2):
			print("\nPlease enter a number 1-2")
		else:
			confirmValidated = True;

	if(confirm == 1):
		try:
			cur.callproc('recovered_to_infected', [personId, infectDate])
			print("Successfully inserted in dead and deleted from infected!")
			if(considerHospital):
				try:
					cur.callproc('check_hospital_in_region', [int(currentRegion)]);
					while(not admitHospitalValidated):
						print("\n\nAdmit to a hospital?\n(1) Yes\n(2) No")
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
											hospQuery = 'INSERT INTO hospital_visit() VALUES(DEFAULT, %s, %s, %s, DEFAULT, DEFAULT)'
											cur.execute(hospQuery, (int(personId), int(hospital), infectDate));
											print("Person admitted to hospital.\n")
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
					print("Person will not be admitted to a hospital at this time.\n")

			cnx.commit()
			covid19_tracker_interface.update()
		except pymysql.Error as e:
			print("\n" + e.args[1] + "\n")
			print("\nChange of status aborted")
			covid19_tracker_interface.update()
	elif(confirm == 2):
		print("\nChange of status aborted")
		update_status();



def updateToDead(personId):
	import covid19_tracker_interface
	global cur;
	global cnx;
	cur = covid19_tracker_interface.cur;
	cnx = covid19_tracker_interface.cnx;
	deathDateValidated = False;
	deathDate = 'YYYY-MM-DD';
	confirmValidated = False;
	confirm = 0;
	print("\n" + covid19_tracker_interface.line_separator(".", 90) + "\nUPDATE TO DEAD\n\nEnter death date:")
	while(not deathDateValidated):
		try:
			print("\nDeath Date\n------------")
			year = int(input("YYYY: "));
			month = int(input("MM: "));
			day = int(input("DD: "));
			deathDate = datetime.date(year, month, day);
			try: 
				cur.callproc('validate_deathDate1', [personId, deathDate])
				deathDateValidated = True;
			except pymysql.Error as e:
				print(e.args[1] + "\n")
		except Exception as e:
			print("Please enter using the specified date format\n")


	while(not confirmValidated):
		print("\nAre you sure you want to update person?\n(1) Yes\n(2) No")
		confirm = int(input("\nEnter a number (1-2): "))
		if(confirm is not 1 and confirm is not 2):
			print("\nPlease enter a number 1-2")
		else:
			confirmValidated = True;

	if(confirm == 1):
		try:
			cur.callproc('infect_to_dead', [personId, deathDate])
			cnx.commit()
			print("Successfully inserted in infected and deleted from recovered!")
			covid19_tracker_interface.update()
		except pymysql.Error as e:
			print("\n" + e.args[1] + "\n")
			print("\nChange of status aborted")
			covid19_tracker_interface.update()
	elif(confirm == 2):
		print("\nChange of status aborted")
		update_status();

def updateToRecovered(personId):
	import covid19_tracker_interface
	global cur;
	global cnx;
	cur = covid19_tracker_interface.cur;
	cnx = covid19_tracker_interface.cnx;
	recoverDateValidated = False;
	recoverDate = 'YYYY-MM-DD';
	confirmValidated = False;
	confirm = 0;
	print("\n" + covid19_tracker_interface.line_separator(".", 90) + "\nUPDATE TO RECOVERED\n\nEnter recovery date:")
	while(not recoverDateValidated):
		try:
			print("\nRecovery Date\n--------------")
			year = int(input("YYYY: "));
			month = int(input("MM: "));
			day = int(input("DD: "));
			recoverDate = datetime.date(year, month, day);
			try: 
				cur.callproc('validate_recoveryDate', [personId, recoverDate])
				recoverDateValidated = True;
			except pymysql.Error as e:
				print(e.args[1] + "\n")
		except Exception as e:
			print("Please enter using the specified date format\n")


	while(not confirmValidated):
		print("\nAre you sure you want to update person?\n(1) Yes\n(2) No")
		confirm = int(input("\nEnter a number (1-2): "))
		if(confirm is not 1 and confirm is not 2):
			print("\nPlease enter a number 1-2")
		else:
			confirmValidated = True;

	if(confirm == 1):
		try:
			cur.callproc('infected_to_recovered_', [personId, recoverDate])
			cnx.commit()
			print("Successfully inserted in recovered and deleted from infected!")
			covid19_tracker_interface.update()
		except pymysql.Error as e:
			print("\n" + e.args[1] + "\n")
			print("\nChange of status aborted")
			covid19_tracker_interface.update()
	elif(confirm == 2):
		print("\nChange of status aborted")
		update_status();



def update_status():
	import covid19_tracker_interface
	global cur;
	global cnx;
	cur = covid19_tracker_interface.cur;
	cnx = covid19_tracker_interface.cnx;
	personTable = 'SELECT * FROM person';
	count = 0;
	personId = 0;
	numAction = 0;
	actionValidated = False;
	validateId = False;
	lineBreak = "\n";

	print("\n" + covid19_tracker_interface.line_separator(".", 90) + "\n(0) Exit Application\n(1) Go back");
	print("\nSelect id of person to change status for from the table below: ");
	cur.execute(personTable)
	return_table(cur);

	while(not validateId):
		try:
			personId = int(input("Person ID: "))
			if(not isinstance(personId, int)):
				print("Please enter a number")
			else:
				try:
					cur.callproc('does_personId_exist', [int(personId)])
					print("ID validated!\n")
					validateId = True;
				except pymysql.Error as e:
					err = e.args[1]
					print(err + "\n")
		except:
			print("Please enter a number")

	while(not actionValidated):
		print("\nSelect a Status Change:\n-----------------------" + 
			"\n(2) Update to infected\n(3) Update to recovered\n(4) Update to dead");

		if(count > 0):
			lineBreak = "";
		try:
			numAction = int(input(lineBreak + "Enter a number (0-4): "));
			if(not isinstance(numAction, int)):
				print("\nPlease enter a number");
			else:
				if(numAction > 5 or numAction < 0):
					print("\nPlease enter a number 0-4")
				elif(numAction == 0):
					print(exitMsg);
					actionValidated = True;
					os._exit(0);
					cnx.close();
				elif(numAction == 1):
					covid19_tracker_interface.update()
					actionValidated = True;
				elif(numAction == 2):
					updateToInfected(personId);
					actionValidated = True;
				elif(numAction == 3):
					updateToRecovered(personId)
					actionValidated = True;
				elif(numAction == 4):
					updateToDead(personId)
					actionValidated = True;
				else:
					print("\nPlease enter a number 0-4")
					count += 1;
					actionValidated = True;
		except Exception as e:
			print("\nPlease enter a number 0-4")	




def update_region():
	import covid19_tracker_interface
	global cur;
	global cnx;
	cur = covid19_tracker_interface.cur;
	cnx = covid19_tracker_interface.cnx;
	regionTable = 'SELECT * FROM region';
	updatableFields = ["regionName", "country", "latitude", "longitude", "totalPop", "lockdown"]
	updateRegionName = 'UPDATE region SET regionName = %s WHERE id = %s';
	updateCountry = 'UPDATE region SET country = %s WHERE id = %s';
	updateLatitude = 'UPDATE region SET latitude = %s WHERE id = %s';
	updateLongitude = 'UPDATE region SET longitude = %s WHERE id = %s';
	updateTotalPop = 'UPDATE region SET totalPop = %s WHERE id = %s';
	updateLockdown = 'UPDATE region SET lockdown = %s WHERE id = %s';
	nameValidated = False;
	countryValidated = False;
	latValidated = False;
	longValidated = False;
	totalPopValidated = False;
	lockDownValidated = False;
	validateId = False;
	confirmValidated = False;
	name = '';
	country = '';
	lat = 0;
	lon = 0;
	totalPop = 0;
	lockdown = False;
	regionId = 0;

	print("\nSelect id of region to update from table below: ");
	cur.execute(regionTable)
	return_table(cur);

	while(not validateId):
		try:
			regionId = int(input("Region ID: "))
			if(not isinstance(regionId, int)):
				print("Please enter a number")
			else:
				try:
					cur.callproc('does_regionId_exist', [int(regionId)])
					print("ID validated!\n")
					validateId = True;
				except pymysql.Error as e:
					err = e.args[1]
					print(err + "\n")
		except:
			print("Please enter a number")

	print("\nEnter new fields (put in old value for fields you do not wish to update):")
	while(not nameValidated):
		name = str(input("Region name: "))
		if(not name.replace(" ", "").isalpha()):
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
	while(not lockDownValidated):
		lockdown = input(name + " on lockdown? (y/n): ")
		if((lockdown is not 'y') and (lockdown is not 'n')):
			print("Please enter y or n")
		else:
			if(lockdown == 'y'):
				lockdown = True;
			elif(lockdown == 'n'):
				lockdown = False;
			lockDownValidated = True;

	try:
		cur.callproc('verify_uniqueRegion', [name, country, lat, lon])
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
		print("\nAre you sure you want to update region?\n(1) Yes\n(2) No")
		confirm = int(input("\nEnter a number (1-2): "))
		if(confirm is not 1 and confirm is not 2):
			print("\nPlease enter a number 1-2")
		else:
			confirmValidated = True;


	if(confirm == 1):
		try:
			print("Fields updated: ")
			try:
				cur.execute(updateRegionName, (str(name), regionId))
				cnx.commit();	
				print("name, ")
			except pymysql.Error as e:
				print(e.args[1] + "\n")
			try:
				cur.execute(updateCountry, (str(country), regionId))
				cnx.commit();
				print("country, ")

			except pymysql.Error as e:
				print(e.args[1] + "\n")
			try:
				cur.execute(updateLatitude, (float(lat), regionId))
				cnx.commit();
				print("longitude, ")

			except pymysql.Error as e:
					print(e.args[1] + "\n")
			try:
				cur.execute(updateLongitude, (float(lon), regionId))
				cnx.commit();
				print("latitude, ")

			except pymysql.Error as e:
					print(e.args[1] + "\n")
			try:
				cur.execute(updateTotalPop, (int(totalPopValidated), regionId))
				cnx.commit();
				print("totalPop, ")
			except pymysql.Error as e:
					print(e.args[1] + "\n")
			try:
				cur.execute(updateLockdown, (lockdown, regionId))
				cnx.commit();
				print("lockdown, - all fields successfully updated!")
				print("\n\nSuccessfully updated!\n")
				covid19_tracker_interface.update();
			except pymysql.Error as e:
				print(e.args[1] + "\n")
		except pymysql.Error as e:
			print("\n" + e.args[1] + "\n")
			cnx.rollback();
			covid19_tracker_interface.update()

	elif(confirm == 2):
		print("Update of " + name + " aborted.")
		covid19_tracker_interface.update();






def update_hospital():
	import covid19_tracker_interface
	global cur;
	global cnx;
	cur = covid19_tracker_interface.cur;
	cnx = covid19_tracker_interface.cnx;
	hospitalTable = 'SELECT * FROM hospital';
	updatableFields = ["name", "regionId"]
	updateName = 'UPDATE hospital SET name = %s WHERE id = %s';
	updateRegion = 'UPDATE hospital SET regionId = %s WHERE id = %s';
	hospitalName = '';
	regionValidated = False;
	regionValidated2 = False;
	validateId = False;
	nameAndRegionValidated = False;
	nameValidated = False;
	confirmValidated = False;
	confirm = 0;
	nameValidated = False;
	hospitalId = 0;
	region = 0;

	print("\nSelect id of hospital to update from table below: ");
	cur.execute(hospitalTable)
	return_table(cur);

	while(not validateId):
		try:
			hospitalId = int(input("Hospital ID: "))
			if(not isinstance(hospitalId, int)):
				print("Please enter an ID number")
			else:
				try:
					cur.callproc('does_hospitalId_exist', [int(hospitalId)])
					print("ID validated!\n")
					validateId = True;
				except pymysql.Error as e:
					err = e.args[1]
					print(err + "\n")
		except Exception as e:
			print("Please enter an ID number")

	print("\nEnter new fields (put in old value for fields you do not wish to update):")

	while(not nameAndRegionValidated):
		while(not nameValidated):
			hospitalName = str(input("Hospital name: "));
			if(not hospitalName.replace(" ", "").isalpha()):
				print("Please enter a string")
			else:
				nameValidated = True;

		while(not regionValidated):
			region = str(input("Region: "));
			if((not region.replace(" ", "").isalpha())):
				print("Please enter a string")
			else:
				try:
					cur.callproc('verify_hospital_regionName', [region])
					print("\nRegion successfully validated!")
					try:
						query = 'SELECT getRegionId(%s)';
						tempHome = cur.execute(query, region)
						tempHome2 = cur.fetchall()[0]
						tempHome = getNum("%s" % str(tempHome2))
						region = tempHome

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
							query = 'SELECT id, regionName, country, latitude, longitude FROM region WHERE regionName = %s';
							cur.execute(query, (region))
							return_table(cur)
						except pymysql.Error as e:
							print(e.args[1])
						while(not regionValidated2):
							try:
								region = int(input("Region ID: "));
							
								try:
									cur.callproc('does_regionId_exist', [region])
									regionValidated2 = True;
									print("\nRegion successfully validated!")
								except pymysql.Error as e:
									print("\n" + e.args[1] + "\n")
							except Exception as e:
								print("Please enter a number")
						regionValidated = True;
		try:
			cur.callproc('verify_hospital', [hospitalName, region])
			print("Successfully validated new fields!")
			nameAndRegionValidated = True;
			regionValidated = True;
			nameValidated = True;
		except pymysql.Error as e:
			print("\n" + e.args[1])
			print("You cannot have more than one hospital with the same name of the same region.")
			print("\n" + "Aborting update of hospital" + "\n")
			regionValidated = False;
			nameValidated = False;
			covid19_tracker_interface.update()

		while(not confirmValidated):
			print("\nAre you sure you want to update hospital?\n(1) Yes\n(2) No")
			confirm = int(input("\nEnter a number (1-2): "))
			if(confirm is not 1 and confirm is not 2):
				print("\nPlease enter a number 1-2")
			else:
				confirmValidated = True;

		updateName = 'UPDATE hospital SET name = %s WHERE id = %s';
		updateRegion = 'UPDATE hospital SET regionId = %s WHERE id = %s';

		if(confirm == 1):
			try:
				print("Fields updated: ")
				try:
					cur.execute(updateName, (str(hospitalName), hospitalId))
					cnx.commit();
					print("name, ")
				except pymysql.Error as e:
					print(e.args[1] + "\n")

				try:
					cur.execute(updateRegion, (int(region), hospitalId))

					cnx.commit();
					print("region - all fields successfully updated! ")
				except pymysql.Error as e:
					print(e.args[1] + "\n")


				print("\n\nSuccessfully updated!\n")
				covid19_tracker_interface.update();
			except pymysql.Error as e:
				print("\n" + e.args[1] + "\n")
				covid19_tracker_interface.update()

		elif(confirm == 2):
				print("Update of " + hospitalName + " aborted.")
				covid19_tracker_interface.update();






def update_person():
	import covid19_tracker_interface
	global cur;
	global cnx;
	cur = covid19_tracker_interface.cur;
	cnx = covid19_tracker_interface.cnx;
	personTable = 'SELECT * FROM person';
	updatableFields = ["firstName", "lastName", "dob", "sex", "homeRegion", "currentRegion"]
	updateFirstName = 'UPDATE person SET firstName = %s WHERE id = %s';
	updateLastName = 'UPDATE person SET lastName = %s WHERE id = %s';
	updateDob = 'UPDATE person SET dob = %s WHERE id = %s';
	updateSex = 'UPDATE person SET sex = %s WHERE id = %s';
	updateCurrentRegion = 'UPDATE person SET currentRegion = %s WHERE id = %s';
	updateHomeRegion = 'UPDATE person SET homeRegion = %s WHERE id = %s';
	regionValidated2 = False;
	validateId = False;
	fNameValidated = False;
	lNameValidated = False;
	sexValidated = False;
	dobValidated = False;
	regionValidated = False;
	confirmValidated = False;
	confirm = 0;

	isInfected = False;
	personId = 0;
	firstName = '';
	lastName = '';
	sex = '';
	dob = 'YYYY-MM-DD';
	homeRegion = 0;
	currentRegion = 0;

	print("\nSelect id of person to update from table below: ");
	cur.execute(personTable)
	return_table(cur);

	while(not validateId):
		try:
			personId = int(input("Person ID: "))
			if(not isinstance(personId, int)):
				print("Please enter a number")
			else:
				try:
					cur.callproc('does_personId_exist', [int(personId)])
					print("ID validated!\n")
					validateId = True;
				except pymysql.Error as e:
					err = e.args[1]
					print(err + "\n")
		except:
			print("Please enter a number")

	print("\nEnter new fields (put in old value for fields you do not wish to update):")


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
				cur.callproc('validate_dob_infectDate', [dob, personId])
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
	
					
	updateFirstName = 'UPDATE person SET firstName = %s WHERE id = %s';
	updateLastName = 'UPDATE person SET lastName = %s WHERE id = %s';
	updateDob = 'UPDATE person SET dob = %s WHERE id = %s';
	updateSex = 'UPDATE person SET sex = %s WHERE id = %s';
	updateCurrentRegion = 'UPDATE person SET currentRegion = %s WHERE id = %s';
	updateHomeRegion = 'UPDATE person SET homeRegion = %s WHERE id = %s';

	while(not confirmValidated):
		print("\nAre you sure you want to update person?\n(1) Yes\n(2) No")
		confirm = int(input("\nEnter a number (1-2): "))
		if(confirm is not 1 and confirm is not 2):
			print("\nPlease enter a number 1-2")
		else:
			confirmValidated = True;

	if(confirm == 1):
		print("\nFields updated: ")
		try:
			cur.execute(updateFirstName, (str(firstName), personId))
			cnx.commit();
			print("firstName, ")
		except pymysql.Error as e:
			print(e.args[1] + "\n")

		try:
			cur.execute(updateLastName, (str(lastName), personId))
			cnx.commit();
			print("lastName, ")

		except pymysql.Error as e:
			print(e.args[1] + "\n")

		try:
			cur.execute(updateDob, (dob, personId))
			cnx.commit();
			print("dob, ")

		except pymysql.Error as e:
			print(e.args[1] + "\n")

		try:
			cur.execute(updateSex, (str(sex), personId))
			cnx.commit();
			print("sex, ")

		except pymysql.Error as e:
			print(e.args[1] + "\n")

		try:
			cur.execute(updateHomeRegion, (int(homeRegion), personId))
			cnx.commit();
			print("homeRegion, ")

		except pymysql.Error as e:
			print(e.args[1] + "\n")	

		try:

			cur.callproc('isInfected', [int(personId)])

			cur.execute(updateCurrentRegion, (int(currentRegion), personId))
			cnx.commit();
			print("currentRegion - all fields successfully updated! ")

		except pymysql.Error as e:
			print("\n" + e.args[1] + "\n")

		print("\n\nSuccessfully updated!\n")
		covid19_tracker_interface.update();

	elif(confirm == 2):
			print("Insert of " + firstName + " " + lastName + " aborted.")
			covid19_tracker_interface.update();



