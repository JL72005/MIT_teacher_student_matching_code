import csv
#Grouping = [DayofWeek, Time, subject, Teacher, group, Student1, Student2] #0,1,2,3,4,5,6
Groups = [] # list of Groupings
teacher_list = [] #list of teacher dictionaries
student_list = [] #list of student dictionaries

#make the lists of dictionaries
with open('student_list.csv', 'r') as infile1:
    dictReader1 = csv.DictReader(infile1)
    student_list = [row for row in dictReader1] # Read the CSV file into a list of dictionaries
print(student_list)

with open('teacher_list.csv', 'r') as infile2:
    dictReader2 = csv.DictReader(infile2)
    teacher_list = [row for row in dictReader2] # Read the CSV file into a list of dictionaries
#print(teacher_list)

#matching algorithm
for teacher in teacher_list:
    
    t_available = teacher['t_available'].split(', ')
    print(t_available)
    max_students = int(teacher['max_students'])
    print(f"max_students:{max_students}")
    num_current_students = int(teacher['num_current_students'])
    print(f"num_current_students:{num_current_students}")
    subjects_taught = teacher['subjects_taught'].split(', ')
    print(subjects_taught)
    
    for student in student_list:
        if num_current_students >= max_students:
            break
        s_available = student['s_available'].split(', ')
        subjects_needed = student['subjects_preferred'].split(', ')
        for t in t_available:
            if num_current_students >= max_students:
                break
            if t in s_available:
                for subject in subjects_needed:
                    if subject in subjects_taught:
                        # Create a new grouping
                        grouping = [t, subject, teacher['teacher_name'], teacher['group_taught'], student['student_name']]
                        Groups.append(grouping)
                        num_current_students += 1
                        if len(assigned_teachers) == 0:
                            assigned_teachers=[teacher['teacher_name']]
                        else:
                            assigned_teachers.append(teacher['teacher_name'])
                        break  # Stop after finding the first matching subject
print(Groups)
for teacher in teacher_list:
	for student in student_list:
		if teacher[‘current_students’] < [‘max_students’] and student[“current_hours”] < 3: #teacher still has room and student has hit credit hour max yet 
			if teacher[‘group_taught’] in student[‘group_preferred]:
				common_topics =  set(teacher['subjects_taught']) & set(student['interested_subjects']
				if common_topics>=1):
					subject = common_topics
			Time situation dealt with 
		grouping[-1]!=””:
			grouping.append(DayofWeek, Time, subject, Teacher, group, Student1)
		grouping[-2]=””:
			grouping[-2] = student
