#helper functions
def list_subjects(string_list):
    """turns 'CS, MATH, ECON' into ['CS', 'MATH', 'ECON']"""
    return [subject for subject in string_list.split(', ').strip()]

import csv
import io

#load students
def load_students():
    with open('student_list.csv', 'r') as infile1:
        dictReader1 = csv.DictReader(infile1)
        student_list = [row for row in dictReader1] # Read the CSV file into a list of dictionaries
        print(student_list)

#load teachers
def load_teachers():
    with open('teacher_list.csv', 'r') as infile2:
        dictReader2 = csv.DictReader(infile2)
        teacher_list = [row for row in dictReader2] # Read the CSV file into a list of dictionaries
        print(teacher_list)

#sample output
students = load_students()
teachers = load_teachers()

#print(students)
#print(teachers)

#parsing availability
from datetime import datetime

def parse_time(time):
    """converts '13:00' or '7:00' into a datetime object"""
    for fmt in ("%H:%M", "%I:%M%p", "%I%p"):
        try:
            return datetime.strptime(time, fmt)
        except ValueError:
            pass

def parse_block(timeblock):
    """"converts 'Monday 13:00-15:00' into ('Monday', datetime(13:00), datetime(15:00))"""
    timeblock = timeblock.strip()
    day, time = timeblock.split(None, 1)
    start_time, end_time = [t.strip() for t in time.split('-')]
    return (day, parse_time(start_time), parse_time(end_time))

def parse_availability(availability):
    """convert ccs string into a list of blocks"""
    return [parse_block(block) for block in availability.split(',')]

def parse_csv(source, kind="student"):
    # If given a string, open it as a file
    if isinstance(source, str):
        f = open(source, newline="")
        close_when_done = True
    else:
        # assume it's already a file-like object (StringIO, open file, etc.)
        f = source
        close_when_done = False

    reader = csv.DictReader(f)
    rows = []
    for row in reader:
        if kind == "student":
            row["s_available"] = parse_availability(row["s_available"])
        else:
            row["t_available"] = parse_availability(row["t_available"])
        rows.append(row)

    if close_when_done:
        f.close()
    return rows

# --- sample data as if from CSV files ---
student_csv = io.StringIO("""student_name,major(s),class_year,group_preferred,subjects_preferred,s_available,assigned_teachers,current_hours
Calvin M.,"6.3, 14",senior,middle,"CS, MATH, ECON, FL","Monday 13:00-15:00, Tuesday 7:00 - 9:00",,0
""")

teacher_csv = io.StringIO("""teacher_name,school,group_taught,subjects_taught,t_available,max_students,num_current_students
Sarah Wharton,PHA,middle,CS,"Monday 8:35 - 9:15, Tuesday 11:22 - 12:37",2,0
""")
# --- run parsing ---
students = parse_csv(student_csv, kind="student")
teachers = parse_csv(teacher_csv, kind="teacher")
# --- print results ---
#print("Student:", students[0]["student_name"])
#print("Availability:", students[0]["s_available"])
#print()
#print("Teacher:", teachers[0]["teacher_name"])
#print("Availability:", teachers[0]["t_available"])


###matching algorithm###
#turns the lists into sets
def set_subjects(raw):
    if isinstance(raw, set):
        return {s.strip() for s in raw}
    return {s.strip() for s in raw.split(',')}

#matches subjects
def subject_match(student, teacher):
    s_subjects = set_subjects(student["subjects_preferred"])
    t_subjects = set_subjects(teacher["subjects_taught"])
    return len(s_subjects & t_subjects) > 0   # True if any overlap

#matches age group
def group_match(student, teacher):
    return student["group_preferred"].strip() == teacher["group_taught"].strip()

#--test cases--
#student = students[0]
#teacher = teachers[0]
#print("Subject overlap:", subject_match(student, teacher))
#print("Group match:", group_match(student, teacher))

#time matching
from datetime import datetime, timedelta

def adjust_time(t, minutes):
    """Takes a 'HH:MM' string or datetime/time and shifts by minutes. 
       Returns a datetime object (with dummy date).
    """
    if isinstance(t, str):
        dt = datetime.strptime(t, "%H:%M")
    elif isinstance(t, datetime):
        dt = t
    elif hasattr(t, "hour") and hasattr(t, "minute"):  # datetime.time
        dt = datetime.combine(datetime.today(), t)
    else:
        raise TypeError(f"Unsupported type: {type(t)}")

    return dt + timedelta(minutes=minutes)

def blocks_overlap(block1, block2, buffer_minutes=30, min_overlap_minutes=30):
    day1, start1, end1 = block1  # student
    day2, start2, end2 = block2  # teacher
    # Different days → no overlap
    if day1 != day2:
        return False
    # Convert to datetime consistently
    start1 = adjust_time(start1, -buffer_minutes)
    end1   = adjust_time(end1, buffer_minutes)
    start2 = adjust_time(start2, 0)
    end2   = adjust_time(end2, 0)
    # Calculate overlap
    overlap_start = max(start1, start2)
    overlap_end   = min(end1, end2)
    overlap_minutes = (overlap_end - overlap_start).total_seconds() / 60
    return overlap_minutes >= min_overlap_minutes

def overlap_hours(block1, block2):
    day1, start1, end1 = block1
    day2, start2, end2 = block2
    if day1 != day2:
        return 0
    start1 = adjust_time(start1, 0)
    end1   = adjust_time(end1, 0)
    start2 = adjust_time(start2, 0)
    end2   = adjust_time(end2, 0)
    overlap_start = max(start1, start2)
    overlap_end   = min(end1, end2)
    
    if overlap_start >= overlap_end:
        return 0
    return (overlap_end - overlap_start).total_seconds() / 3600


#match availability blocks
def availability_match(student, teacher):
    for s_block in student["s_available"]:
        for t_block in teacher["t_available"]:
            if blocks_overlap(s_block, t_block):
                return True
    return False

##full matching according to all criteria for a single student
def is_match(student, teacher):
    return (
        subject_match(student, teacher) and
        group_match(student, teacher) and
        availability_match(student, teacher) and
        teacher["num_current_students"] < teacher["max_students"]
    )
#print(is_match(students[0], teachers[0]))

##all student and teacher matches
def find_all_matches(students, teachers):
    matches = []
    for student in students:
        for teacher in teachers:
            if is_match(student, teacher):
                matches.append((student["student_name"], teacher["teacher_name"]))
    return matches

def assign_students(students, teachers):
    assignments = []
    for student in students:
        if "assigned_teachers" not in student or not student["assigned_teachers"]:
            student["assigned_teachers"] = []
        
        if student.get("current_hours") is None:
            student["current_hours"] = 0

        for teacher in teachers:
            if is_match(student, teacher) and teacher["num_current_students"] < teacher["max_students"]:
                
                # Calculate overlap hours + store block
                added_hours = 0
                assigned_block = None
                subject_matched = None

                for s_block in student["s_available"]:
                    for t_block in teacher["t_available"]:
                        hours = overlap_hours(s_block, t_block)
                        if hours > 0:
                            added_hours = hours
                            assigned_block = (
                                s_block[0],   # Day
                                max(s_block[1], t_block[1]),  # Start
                                min(s_block[2], t_block[2])   # End
                            )
                            # Pick a subject both share
                            subject_matched = next(iter(student["subjects_preferred"] & teacher["subjects_taught"]), None)
                            break
                    if added_hours > 0:
                        break

                if assigned_block:
                    # Don’t exceed student’s 3-hour cap
                    if student["current_hours"] + added_hours <= 3:
                        # Save assignment with details
                        assignments.append({
                            "student": student["student_name"],
                            "teacher": teacher["teacher_name"],
                            "group": teacher["group_taught"],
                            "subject": subject_matched,
                            "block": assigned_block
                        })

                        # Update teacher + student records
                        teacher["num_current_students"] += 1
                        student["assigned_teachers"].append(teacher["teacher_name"])
                        student["current_hours"] += added_hours
                        
    return assignments


# Sample data (normally you'd load from CSVs)
students = [
    {
        "student_name": "Calvin M.",
        "group_preferred": "middle",
        "subjects_preferred": {"CS", "MATH"},
        "s_available": [
            ("Monday", "13:00", "15:00"),   # 2 hr block
            ("Tuesday", "07:00", "09:00")   # 2 hr block
        ],
        "assigned_teachers": [],
        "current_hours": 0
    },

    {
        "student_name": "Srithi S.",
        "group_preferred": "middle",
        "subjects_preferred": {"CS", "MATH"},
        "s_available": [
            ("Monday", "13:00", "15:00"),   # 2 hr block
            ("Tuesday", "07:00", "09:00")   # 2 hr block
        ],
        "assigned_teachers": [],
        "current_hours": 0
    },
]

teachers = [
    {
        "teacher_name": "Sarah Wharton",
        "group_taught": "middle",
        "subjects_taught": {"CS"},
        "t_available": [
            ("Monday", "13:30", "14:30")   # 1 hr overlap with student
        ],
        "max_students": 2,
        "num_current_students": 0
    },
    {
        "teacher_name": "Mr. Smith",
        "group_taught": "middle",
        "subjects_taught": {"MATH"},
        "t_available": [
            ("Tuesday", "07:30", "08:30")   # 1 hr overlap
        ],
        "max_students": 1,
        "num_current_students": 0
    }
]

# Run matching
results = assign_students(students, teachers)

# Print results
print("Assignments:")
for r in results:
    print(r)

print("\nUpdated student record:")
print(students[0])

print("\nUpdated teacher records:")
for t in teachers:
    print(t)

import pandas as pd
def format_schedule(assignments):
    rows = []
    for a in assignments:
        day, start, end = a["block"]  # store the actual block when you assign
        rows.append({
            "Day": day,
            "Time": f"{start} - {end}",
            "Subject": a["subject"],
            "Teacher": a["teacher"],
            "Group": a.get("group", ""),
            "Student": a["student"]
        })

    # Convert to DataFrame
    df = pd.DataFrame(rows)

    # Pivot so each student becomes its own column
    pivot = df.pivot_table(
        index=["Day", "Time", "Subject", "Teacher", "Group"],
        values="Student",
        aggfunc=lambda x: ", ".join(x),  # if multiple students in same slot
    ).reset_index()

    return pivot
print(f"\nFormatted Schedule:\n {format_schedule(results)}")