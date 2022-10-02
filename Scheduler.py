import numpy as np
import pandas as pd
import csv as csv
chjgvjvjjh
# Maps each day to a particular number
def getDayMap(s):
	if (s=="Sunday"):
		return 0
	if (s=="Monday"):
		return 1
	if (s=="Tuesday"):
		return 2
	if (s=="Wednesday"):
		return 3
	if (s=="Thursday"):
		return 4
	if (s=="Friday"):
		return 5
	if (s=="Saturday"):
		return 6
	return 7

# Reads EXISTING TIME TABLE from csv file and stores it as a matrix
def getTimeTable ():
	T = pd.read_csv("Time Table.csv",sep=",").fillna(0).as_matrix()[0:,1:]
	time_slots = T.shape[0]
	days = T.shape[1]
	return (T,time_slots,days)

# Reads QUIZ info from csv file and stores it in a matrix
def getQuizList():
	quizList = pd.read_csv("Quiz List.csv",sep=",").fillna(0).as_matrix()
	for i in range (0,quizList.shape[0]):
		quizList[i][2] = getDayMap(quizList[i][2])
	return quizList

# Reads COURSE info from csv file and stores it in a matrix
def getCourseList():
	return (pd.read_csv("Course List.csv",sep=",").as_matrix())

# Stores free time per day in an array
def getFreeTime (T):
	freetime = np.zeros(7) # stores number of hours free in a days
	hh = 0.0
	for j in range (0,days):
		for i in range (0,time_slots):
			if (T[i][j]!=0):
				continue
			hh = hh + 1
		freetime[j] = float(hh/2)
		hh=0.0
	return freetime

# Allots time to be devoted to each course on each day on the basis of credits, confidence, free time, and presence of quiz
def studyTimePerDay (courseList, quizList, freetime):
	M = courseList.shape[0] # number of courses
	p = np.zeros((M,7)) # study time of each course on each day
	p_orig = np.zeros((M,7))
	qt = np.zeros(M) # extra time to be studied for quiz 
	F = np.zeros(M) # free time till that quiz day (incl.)
	R = np.zeros(M) # remaining number of days after quiz
	for i in range (0,M):
		for j in range (0,7):
			p_orig[i][j] = float(courseList[i][1])/courseList[i][2]*freetime[j]/np.sum(freetime)
			p[i][j] = p_orig[i][j]
	# calculate net extra time to be studied for quiz per course
	for i in range (0,M):
		qt[i] = 4/float(courseList[i][2])*quizList[i][1]*courseList[i][1]/100
	# calculate remaining number of days after a quiz, remaining days include the day of the quiz as well
	for i in range (0,M):
		if (quizList[i][2] < 7):
			R[i] = 7 - quizList[i][2]
		else:
			R[i] = 7
	# net free time (on all days) TILL each quiz
	for i in range (0,M):
		F[i] = np.sum(freetime[0:quizList[i][2]])
	# do the job:
	for i in range (0,M):
		if (quizList[i][2] != 7):
			for j in range (0,quizList[i][2]):
				p[i][j] = p[i][j] + freetime[j]*qt[i]/F[i]
			for j in range (quizList[i][2],7):
				p[i][j] = p_orig[i][j] - qt[i]/R[i]
	for i in range (0,M):
		for j in range (0,7):
			if (p[i][j] < 0):
				p[i][j] = 0
	return p

# Ranks courses to be studied in each day in order of the number of hours devoted to it using bubble sort
def returnCourseOrder (p,courseList):
	M = courseList.shape[0]
	p_mat = p
	courses = courseList[:,0]
	course_mat = np.empty((M,7),dtype='a7')
	for j in range (0,7):
		course_mat[:,j] = courses
	for i in range (0,7):
		for j in range (0,M):
			for k in range (0,M-j-1):
				if (p_mat[k][i]>p_mat[k+1][i]):
					p_mat[k][i],p_mat[k+1][i] = p_mat[k+1][i],p_mat[k][i]
					course_mat[k][i],course_mat[k+1][i] = course_mat[k+1][i],course_mat[k][i]
	return course_mat,p_mat

# Fit time to be studied in empty slots in the EXISTING TIME TABLE
def makeDay (T, course_mat, p_mat):
	T_copy = np.copy(T)
	T = np.vstack([T,[0,0,0,0,0,0,0]]) # add dummy row for calculation purpose
	T_text = np.copy(T)
	slot_count = T.shape[0] # number of slots on a day
	course_count = course_mat.shape[0] # number of courses
	current_course = 0 
	for j in range (0,7):
		day = T[:,j] # slots
		ttt = T_text[:,j]
		for k in range (0,slot_count):
			if (ttt[k]==0):
				ttt[k] = ""
		course_order = course_mat[:,j]
		p_order = p_mat[:,j]*60.0 # converting to minutes
		current_course = 0
		for i in range (0,slot_count):
			if (day[i] != 0): # if slot is not empty
				continue
			if (i+1 < slot_count):
				if (day[i+1] != 0): # if next slot is not empty
					# continue filling till slot is full
					while (current_course < course_count and p_order[current_course]<=20-day[i]):
						day[i] = day[i] + p_order[current_course]
						x = int(round(p_order[current_course],0))
						if (x>0):
							ttt[i] = ttt[i] + str(course_order[current_course]) + ":" + str(x) + " "
						current_course = current_course + 1
					# if course study time takes up entire time of the slot
					if (current_course < course_count and p_order[current_course] > 20-day[i]):
						p_order[current_course] = p_order[current_course] - (20-day[i])
						x = int(round(20-day[i],0))
						day[i] = 20
						if (x>0):
							ttt[i] = ttt[i] + str(course_order[current_course]) + ":" +  str(x) + " "
				else: # if next slot is empty
					# continue filling till slot is full
					while (current_course < course_count and p_order[current_course] <= 25-day[i]):
						day[i] = day[i] + p_order[current_course]
						x = int(round(p_order[current_course],0))
						if (x>0):
							ttt[i] = str(course_order[current_course]) + ":" +  str(x) + " "
						current_course = current_course + 1
					# if course study time takes up entire time of the slot
					if (current_course < course_count and p_order[current_course] > 25-day[i]):
						p_order[current_course] = p_order[current_course] - (25-day[i])
						x = int(round(25-day[i],0))
						day[i] = 25
						if (x>0):
							ttt[i] = ttt[i] + str(course_order[current_course])  + ":" +  str(x) + " "
		T_text[:,j] = ttt
	# formatting
	T_text = np.delete(T_text,slot_count-1,0)
	for j in range (0,7):
		for i in range (0,slot_count-1):
			if (T_text[i][j] == 0):
				T_text[i][j] = ''
	return T_text

# Formats the output
def outputTimeTable (T_text):
	T_temp = pd.read_csv("Time Table.csv",sep=",",header=None).fillna(0).as_matrix()
	T_temp[1:T_text.shape[0]+1,1:8] = T_text
	T_temp[0,0] = ''
	with open('Proposed Time Table.csv', 'wb') as f:
	 	csv.writer(f).writerows(T_temp)

# Run code:
T, time_slots, days = getTimeTable()
freetime = getFreeTime(T)
courseList = getCourseList()
quizList = getQuizList()
p = studyTimePerDay(courseList,quizList,freetime)
course_mat, p_mat = returnCourseOrder(p,courseList)
T_text = makeDay(T,course_mat,p_mat)
outputTimeTable(T_text)
