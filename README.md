Installation Instructions for Running this Project (MacOS)

I.
For backend verification from the Database:
	- MySQL workbench latest version 8.0.19 
		- Download: https://dev.mysql.com/downloads/workbench/ 
	- MySQL community server latest version 8.0.19
		- Download: https://dev.mysql.com/downloads/mysql/ 
	- Download and establish a connection to server
		- Keep track of username and password
	- Open on MySQL workbench: covid19_tracker_dump
		- Run the dump file
		- Refresh your schema
		- Open a new query tab and type: USE `covid19_tracker` 
			- Commands to view tables 
				- SELECT * FROM person;
				- SELECT * FROM hospital;
				- SELECT * FROM infected;
				- SELECT * FROM recovered;
				- SELECT * FROM dead;
				- SELECT * FROM region;
				- SELECT * FROM hospital_visit
				- SELECT * FROM test

II.
For running the client interface application:
	- Open Mac Terminal application
	- Download Python latest version (Python3). Two methods:
		- (1) Download
			- Download latest version from: https://www.python.org/downloads/ 
			- Run the python installer to install Python on your Mac
			- Can find python in the Applications directory of your Mac
		- (2) Homebrew (longer method)
			- Open Mac terminal
			- Enter in terminal: xcode-select --install
			- Enter in terminal: /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
			- Enter in terminal: brew install python3
		- Type the following in the Mac Terminal verify version: python --version (should be 3.X.X)
	- Donwload the following by entering in your Mac terminal (may need to enter your password to allow)
	  These enable the application to run and includes libraries used in the application.
		- sudo easy_install pip
		- PyMySQL: pip install PyMySQL
		- Tabulate: pip install tabulate
	- In Mac terminal, navigate to the folder containing the python files 
	- To begin application, type: python run.py
	- Login with MySQL username and password