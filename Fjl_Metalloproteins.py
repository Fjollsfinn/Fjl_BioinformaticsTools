"""

Author:	  Bartlomiej Tuchowski 199341
Created:     02.06.2017

"""
# imports
import urllib.request
import pymysql as db
import re

#definitions
def CreateReCreateTables():
	print ("\n#CREATE/RECREATE TABLE MENU")
	print ("Choices are: \n", "1. Create table \n", "2. Recreate table \n", "3. Back")
	connection= db.connect(host= "localhost", user = "user", passwd="okon", db="metaloproteins")
	cur = connection.cursor()
	query = "show tables;"
	results = cur.execute(query)
	print ("Tables in database:", results)

	def turned():
		choice2 = str(input("\nYour choice ? OPTIONS[1, 2, 3] "))
		if choice2 == "1":
			if results > 0:
				print ("Proteins database already exist!")
				turned()
			else:
				query = "create table proteins (PDB_ID VARCHAR(200), Metal VARCHAR(200), Ox VARCHAR(200), Residue VARCHAR(200), Atom VARCHAR(200), Distance CHAR(20), idx Serial);"
				cur.execute(query)
				print ("Table created!")
		elif choice2 == "2":
			if results < 1:
				print ("There is no tables in database!")
				turned()
			else:
				query = "drop table if exists proteins;"
				cur.execute(query)
				query = "create table proteins (PDB_ID VARCHAR(200), Metal VARCHAR(200), Ox VARCHAR(200), Residue VARCHAR(200), Atom VARCHAR(200), Distance CHAR(20), idx Serial);"
				cur.execute(query)
				print ("Table recreated!")
		elif choice2 == "3":
			MainMenu()
		else:
			print ("Wrong command. Use one of OPTIONS from Create/recreate table menu.")
			turned()
	turned()

def AddEntries():
	connection= db.connect(host= "localhost", user = "user", passwd="okon", db="metaloproteins")
	cur = connection.cursor()
	def turned2():
		data1 = []
		data2 = []
		PDB = input("Please enter PDB code of molecule: ")
		result = cur.execute("select 1 from proteins where PDB_ID=%s;", (PDB,))
		if result > 1:
			print ("That record already exist!")
			MainMenu()
		else:
			url_adress = "http://www.rcsb.org/pdb/files/" + PDB + ".pdb"
			x = urllib.request.urlopen(url_adress).read()
			lines = x.decode("ASCII").splitlines()
			for header in lines:
				if header[0:6] == "HEADER":
					PDB_ID = header[62:66]
			print (" \nYou can check the data about the", PDB_ID, "protein on that link:", url_adress, "\n" )

			for u in lines:
				if u[0:6] == "HET   ":
					element_name = u[7:10]
					element_name = element_name.strip()
					#print ("Element name is:", element_name)
					atom_number = u[13:18]
					atom_number = atom_number.strip()
					#print ("Atom number is:", atom_number)
					for u in lines:
						if u[0:6] =="FORMUL":
							if u[13:15] == element_name:
								ox_state = re.search('(\d[(+*)])', u[22:26])
								ox_state = ox_state.group(0)
								#print ("Oxidtadion state of", element_name, "is:", ox_state)
								data1.append([str(element_name), int(atom_number), str(ox_state)])
			#print (data1)
								#counter = 0
								for l in lines:
									if l[0:6] == "LINK  ":
										contact_atom = l[42:46]
										contact_atom = contact_atom.strip()
										#print ("Name of the atom that contat with", data1[counter][0], "is:", contact_atom)
										residue = l[47:51]
										residue = residue.strip()
										#print ("Name of ligand for", data1[counter][0], "is:", residue)
										distance = l[74:78]
										distance = distance.strip()
										#print ("Distance of", data1[counter][0], "-", contact_atom, "bond is:", distance)
										atom_number2 = l[22:30]
										atom_number2 = atom_number2.strip()
										#print ("Atom number is:", atom_number2)
										if atom_number == atom_number2:
											data2.append([str(element_name), str(ox_state), str(contact_atom),str(residue),float(distance)])
											#counter = counter + 1
			#print (data2)
								#print (PDB_ID, data2[0][0], data2[0][1], data2[0][2], data2[0][3], data2[0][4])

			query = "insert into proteins (PDB_ID, Metal, Ox, Residue, Atom, Distance) value (%s, %s, %s, %s, %s, %s);"
			counter = 0
			for data in data2:
				cur.execute(query, (PDB_ID, data2[counter][0], data2[counter][1], data2[counter][3], data2[counter][2], data2[counter][4]))
				counter = counter + 1
			connection.commit()
			print ("Data about", PDB, "stored!")
			connection.close()
	turned2()

def Continues():
	step = input ("Do you want to continue ? OPTIONS[y/n]: ")
	if step == "y":
		pass
	elif step == "n":
		print ("See you next time.")
		exit()
	else:
		print ("Wrong command. Use one of OPTIONS from menu.")
		Continues()

def Query():
	print ("\n#QUERY MENU")
	print ("Choices are: \n", "1. Show all data \n", "2. Querying by element and oxidation state \n", "3. Querying by residue and atom name \n", "4. Querying by metal and atom \n", "5. Back")
	connection= db.connect(host= "localhost", user = "user", passwd="okon", db="metaloproteins")
	cur = connection.cursor()
	choice3 = str(input("\nYour choice ? OPTIONS[1, 2, 3, 4, 5] "))

	if choice3 == "1":
		query = "describe proteins;"
		cur.execute(query)
		columns = [c[0] for c in cur.fetchall()]
		print(' '.join([ "%-10s" % c for c in columns]))
		print('-' * (10*len(columns)))
		query = "select * from proteins;"
		cur.execute(query)
		results = cur.fetchall()
		for row in results:
			print (" ".join([ "%-10s" % r for r in row]))
		connection.close()
	elif choice3 == "2":
		print ("In this mode program will display table with number of residues and atoms of each type, that form contact with the selected metal.")
		choice4 = str(input("Define HET atom: "))
		choice5 = str(input("Define oxidation state: "))
		print ("\nContacts with", choice4, choice5, ": ")
		columns = ["Residue", "Atom", "Count"]
		print(' '.join([ "%-10s" % c for c in columns]))
		print('-' * (10*len(columns)))
		query2 = "select Residue, Atom, count(*) as Count from proteins where Metal=%s and Ox=%s group by Residue, Atom having count(*) > 0;"
		result2 = cur.execute(query2, (choice4,choice5,))
		results2 = cur.fetchall()
		for row in results2:
			print (" ".join([ "%-10s" % r for r in row]))
	elif choice3 == "3":
		print ("In this mode program will display table with number of metals and oxidation states that form contact with the given atom.")
		choice6 = str(input("Define residue: "))
		choice7 = str(input("Define atom: "))
		print ("\nContacts with", choice6, ",", choice7, ": ")
		columns = ["Metal", "Ox", "Count"]
		print(' '.join([ "%-10s" % c for c in columns]))
		print('-' * (10*len(columns)))
		query2 = "select Metal, Ox, count(*) as Count from proteins where Residue=%s and Atom=%s group by Metal, Ox having count(*) > 0;"
		result2 = cur.execute(query2, (choice6,choice7,))
		results2 = cur.fetchall()
		for row in results2:
			print (" ".join([ "%-10s" % r for r in row]))
	elif choice3 == "4":
		distances = []
		print ("In this mode, when the contact type is specified precisely, the program will calculate and display the minimum, maximum and average value of the distance.")
		choice8 = str(input("Define HET atom: "))
		choice9 = str(input("Define oxidation state: "))
		choice10 = str(input("Define atom: "))
		choice11 = str(input("Define residue: "))
		print ("\nContacts between", choice8, "(", choice9, ") and", choice10, "(", choice11, "): ")
		query = "select Metal, Ox, Atom, Residue, Distance from proteins where Metal=%s and Ox=%s and Atom=%s and Residue=%s;"
		result = cur.execute(query, (choice8,choice9,choice10, choice11,))
		results = cur.fetchall()
		columns = ["Metal", "Ox", "Atom", "Residue", "Distance"]
		print(' '.join([ "%-10s" % c for c in columns]))
		print('-' * (10*len(columns)))
		for row in results:
			print (" ".join([ "%-10s" % r for r in row]))
		for row in results:
			distances.append(float(row[4]))
		#print (distances)
		summation = 0
		counter = 0
		for distance in distances:
			summation = summation + distance
			counter = counter + 1
		#print (summation, counter)
		average = (summation/counter)
		#print (average)
		minimal = min(distances)
		maximal = max(distances)
		print ("Minimum distance:",minimal, "\nMaximum distance:", maximal, "\nAverage distance:", average)
	elif choice3 =="5":
		MainMenu()

def MainMenu():
	#main menu

	MainLoop = True

	while MainLoop == True:
		print ("This program will help you with collecting data about metalloproteins. \n")
		print ("#MAIN MENU")
		print ("Choices are: \n", "(a) Add entries \n", "(q) Query \n", "(c) Create/recreate table \n", "(x) Quit \n")
		choice = input ("Your choice? OPTIONS[a, q, c, x] ")

		if choice == "a":
			AddEntries()
			Continues()

		elif choice == "q":
			Query()
			Continues()

		elif choice == "c":
			CreateReCreateTables()
			Continues()

		elif choice == "x":
			print ("See you next time.")
			exit()
		else:
			print ("Wrong command. Use one of OPTIONS from #MAIN MENU.")
			continue

MainMenu()