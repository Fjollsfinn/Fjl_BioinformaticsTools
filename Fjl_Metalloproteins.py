"""

Author:	  Bartlomiej Tuchowski 199341
Created:     02.06.2017

"""
# imports
import urllib.request
import pymysql as db
import re

#definitions
def MainMenu():

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
			
def AddEntries():
	connection= db.connect(host= "localhost", user = "user", passwd="okon", db="metaloproteins")
	cur = connection.cursor()
	def turned2():
		data1 = []
		data2 = []
		PDB = input("Please enter PDB code of molecule: ")
		result = cur.execute("SELECT 1 FROM proteins WHERE PDB_ID=%s;", (PDB,))
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
					atom_number = u[13:18]
					atom_number = atom_number.strip()
					for u in lines:
						if u[0:6] =="FORMUL":
							if u[13:15] == element_name:
								ox_state = re.search('(\d[(+*)])', u[22:26])
								ox_state = ox_state.group(0)
								data1.append([str(element_name), int(atom_number), str(ox_state)])
								for l in lines:
									if l[0:6] == "LINK  ":
										contact_atom = l[42:46]
										contact_atom = contact_atom.strip()
										residue = l[47:51]
										residue = residue.strip()
										distance = l[74:78]
										distance = distance.strip()
										atom_number2 = l[22:30]
										atom_number2 = atom_number2.strip()
										if atom_number == atom_number2:
											data2.append([str(element_name), str(ox_state), str(contact_atom),str(residue),float(distance)])

			query = "INSERT INTO proteins (PDB_ID, Metal, Ox, Residue, Atom, Distance) VALUE (%s, %s, %s, %s, %s, %s);"
			counter = 0
			for data in data2:
				cur.execute(query, (PDB_ID, data2[counter][0], data2[counter][1], data2[counter][3], data2[counter][2], data2[counter][4]))
				counter = counter + 1
			connection.commit()
			print ("Data about", PDB, "stored!")
			connection.close()
	turned2()

def Query():
	print ("\n#QUERY MENU")
	print ("Choices are: \n", "1. Show all data \n", "2. Querying by element and oxidation state \n", "3. Querying by residue and atom name \n", "4. Querying by metal and atom \n", "5. Back")
	connection= db.connect(host= "localhost", user = "user", passwd="okon", db="metaloproteins")
	cur = connection.cursor()
	choice3 = str(input("\nYour choice ? OPTIONS[1, 2, 3, 4, 5] "))

	if choice3 == "1":
		query = "DESCRIBE proteins;"
		cur.execute(query)
		columns = [c[0] for c in cur.fetchall()]
		print(' '.join([ "%-10s" % c for c in columns]))
		print('-' * (10*len(columns)))
		query = "SELECT * FROM proteins;"
		cur.execute(query)
		results = cur.fetchall()
		for row in results:
			print (" ".join([ "%-10s" % r for r in row]))
		connection.close()
	elif choice3 == "2":
		print ("In this mode program will display table with number of residues and atoms of each type, that form contact with the selected metal.")
		choice4 = str(input("Define PDB code: "))
		choice5 = str(input("Define HET atom: "))
		choice6 = str(input("Define oxidation state: "))
		print ("\nContacts with", choice5, choice6, "in", choice4, "molecule: ")
		columns = ["PDB_ID", "Residue", "Atom", "Count"]
		print(' '.join([ "%-10s" % c for c in columns]))
		print('-' * (10*len(columns)))
		query2 = "SELECT PDB_ID, Atom, Residue, COUNT(*) AS Count FROM proteins WHERE PDB_ID=%s AND Metal=%s AND Ox=%s GROUP BY Residue, Atom, PDB_ID HAVING COUNT(*) > 0;"
		result2 = cur.execute(query2, (choice4,choice5, choice6))
		results2 = cur.fetchall()
		for row in results2:
			print (" ".join([ "%-10s" % r for r in row]))
	elif choice3 == "3":
		print ("In this mode program will display table with number of metals and oxidation states that form contact with the given atom.")
		choice4 = str(input("Define PDB code: "))
		choice5 = str(input("Define residue: "))
		choice6 = str(input("Define atom: "))
		print ("\nContacts with", choice5, ",", choice6, "in", choice4, "molecule: ")
		columns = ["PDB_ID", "Metal", "Ox", "Count"]
		print(' '.join([ "%-10s" % c for c in columns]))
		print('-' * (10*len(columns)))
		query2 = "SELECT PDB_ID, Metal, Ox, COUNT(*) AS Count FROM proteins WHERE PDB_ID=%s AND Residue=%s AND Atom=%s GROUP BY Metal, Ox HAVING COUNT(*) > 0;"
		result2 = cur.execute(query2, (choice4, choice5,choice6,))
		results2 = cur.fetchall()
		for row in results2:
			print (" ".join([ "%-10s" % r for r in row]))
	elif choice3 == "4":
		distances = []
		print ("In this mode, when the contact type is specified precisely, the program will calculate and display the minimum, maximum and average value of the distance.")
		choice4 = str(input("Define PDB code: "))		
		choice5 = str(input("Define HET atom: "))
		choice6 = str(input("Define oxidation state: "))
		choice7 = str(input("Define atom: "))
		choice8 = str(input("Define residue: "))
		print ("\nContacts between", choice5, "(", choice6, ") and", choice7, "(", choice8, ") in", choice4, "molecele: ")
		query = "SELECT PDB_ID, Metal, Ox, Atom, Residue, Distance FROM proteins WHERE PDB_ID=%s AND Metal=%s AND Ox=%s AND Atom=%s AND Residue=%s;"
		result = cur.execute(query, (choice4, choice5,choice6,choice7, choice8,))
		results = cur.fetchall()
		columns = ["PDB_ID", "Metal", "Ox", "Atom", "Residue", "Distance"]
		print(' '.join([ "%-10s" % c for c in columns]))
		print('-' * (10*len(columns)))
		for row in results:
			print (" ".join([ "%-10s" % r for r in row]))
		for row in results:
			distances.append(float(row[5]))
		summation = 0
		counter = 0
		for distance in distances:
			summation = summation + distance
			counter = counter + 1
		average = (summation/counter)
		minimal = min(distances)
		maximal = max(distances)
		print ("Minimum distance:",minimal, "\nMaximum distance:", maximal, "\nAverage distance:", average)
	elif choice3 =="5":
		MainMenu()
		
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
				query = "CREATE TABLE proteins (PDB_ID VARCHAR(200), Metal VARCHAR(200), Ox VARCHAR(200), Residue VARCHAR(200), Atom VARCHAR(200), Distance CHAR(20), idx Serial);"
				cur.execute(query)
				print ("Table created!")
		elif choice2 == "2":
			if results < 1:
				print ("There is no tables in database!")
				turned()
			else:
				query = "drop table if exists proteins;"
				cur.execute(query)
				query = "CREATE TABLE proteins (PDB_ID VARCHAR(200), Metal VARCHAR(200), Ox VARCHAR(200), Residue VARCHAR(200), Atom VARCHAR(200), Distance CHAR(20), idx Serial);"
				cur.execute(query)
				print ("Table recreated!")
		elif choice2 == "3":
			MainMenu()
		else:
			print ("Wrong command. Use one of OPTIONS from Create/recreate table menu.")
			turned()
	turned()

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
		
#run
if __name__=="__main__":
	MainMenu()
	