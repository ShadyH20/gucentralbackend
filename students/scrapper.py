import requests
from requests_ntlm import HttpNtlmAuth
from bs4 import BeautifulSoup, NavigableString
import re
from enum import Enum
import mechanicalsoup

schedule_url = 'https://student.guc.edu.eg/Web/Student/Schedule/GroupSchedule.aspx'
courses_url = 'https://cms.guc.edu.eg/apps/student/HomePageStn.aspx'
transcriptUrl = "https://student.guc.edu.eg/external/student/grade/Transcript.aspx"


class Scrapper:
    def __init__(self, username, password):

        self.username = username+"@student.guc.edu.eg"
        self.password = password

    # only login
    def login(self):
        r = requests.get(courses_url, auth=HttpNtlmAuth(
            self.username, self.password))
        if r.status_code != 200:
            # Wrong Credentials
            print("An Error Occurred. Check Credentials And Try Again.")
            return [], False
        else:
            # Correct Credentials

            # Get Cumilatuve GPA
            gpa, successGPA = self.get_gpa_please("2022-2023")

            # Get Courses
            courses, successCourses = self.get_courses_data()

            # Get Schedule
            schedule, successSch = self

    # converts(returns) the index of the day given the day's name

    def get_day_index(self, day_name: str):
        day_name = day_name.lower()
        index = -1
        if day_name == 'saturday':
            index = 0
        elif day_name == 'sunday':
            index = 1
        elif day_name == 'monday':
            index = 2
        elif day_name == 'tuesday':
            index = 3
        elif day_name == 'wednesday':
            index = 4
        elif day_name == 'thursday':
            index = 5
        return index

    # scrappes the website for the day's schedule
    def get_day_schedule_data(self, day_index: int):
        day_schedule = []
        r = requests.get(schedule_url, auth=HttpNtlmAuth(
            self.username, self.password))
        if r.status_code != 200:
            print("An Error Occurred. Check Credentials And Try Again.")
            return
        else:
            soup = BeautifulSoup(r.content, 'html.parser')
            table: NavigableString = soup.find("table", id="scdTbl")
            children = table.findChildren("tr", recursive=False)
            children.pop(0)
            day = children[day_index]
            day_sessions = day.findChildren("td", recursive=False)
            for slot in day_sessions:
                tables = slot.findChildren("table", recursive=False)
                if len(tables) == 0:
                    continue
                elif len(tables) == 1:  # its a tutorial
                    tut_infos = tables[0].findChildren("td", recursive=True)
                    day_schedule.append(
                        tut_infos[2].text + " " + tut_infos[1].text)
                elif len(tables) > 1:
                    table = tables[1]
                    data = table.find("span")
                    day_schedule.append(data.text)
            return day_schedule

    # Get ID and Full name
    def get_idname(self):
        r = requests.get(schedule_url, auth=HttpNtlmAuth(
            self.username, self.password))
        if r.status_code != 200:
            print("An Error Occurred. Check Credentials And Try Again.")
            return ["", ""], False
        else:
            soup = BeautifulSoup(r.content, 'html.parser')
            span = soup.find("span", id="scdTpLbl")
            result = span.text.split(" - ")

            # Returns ID and Full Name
            return result, True

    # Get ID and Full name
    def get_gpa_please(self, year):
        # Create a browser object with MechanicalSoup
        browser = mechanicalsoup.StatefulBrowser()

        # Set the authentication credentials
        browser.session.auth = HttpNtlmAuth(self.username, self.password)

        # Navigate to the web page
        res = browser.open(transcriptUrl)
        if res.status_code != 200:
            print("An Error Occurred. Check Credentials And Try Again.")
            return "", False
        else:
            # Get the option value from its text
            option_value = browser.page.find("option", string=year)['value']

            # Submit the form
            form = browser.select_form('form')
            form.set_select({'stdYrLst': option_value})
            res = browser.submit_selected()
            if res.status_code != 200:
                print(
                    "An Error Occurred. Check Credentials And Try Again. SC: ", res.status_code)
                return "", False
            else:
                # Extract the information you need from the resulting page
                return browser.page.find("span", id="cmGpaLbl").text, True

    # prints the week's schedule as a 2d array with the index being the day, with starting index 0 for saturday

    def get_week_schedule_printer(self):
        week_schedule = []
        for i in range(0, 6):
            week_schedule.append(self.get_day_schedule_formatted_data(i))
        print(week_schedule)

    # returns the week schedule data
    def get_week_schedule_data(self):
        week_schedule = []
        for i in range(0, 6):
            week_schedule.append(self.get_day_schedule_formatted_data(i))
        return week_schedule

    # returns a list representing the day's schedule

    def get_day_schedule_formatted_data(self, day_index: int):
        schedule = self.get_day_schedule_data(day_index)
        formatted_schedule = []
        for item in schedule:
            formatted_schedule.append(item.replace("\r\n\t\t\t\t\t\t\t\t\t\t\t\tTut\r\n\t\t\t\t\t\t\t\t\t\t\t\n", " Tut").replace(
                "\r\n\t\t\t\t\t\t\t\t\t\t\t\tLab\r\n\t\t\t\t\t\t\t\t\t\t\t\n", " Lab"))
        return formatted_schedule

    # prints a list representing the day's schedule
    def get_day_schedule_formatted_printer(self, day_index: int):
        schedule = self.get_day_schedule_data(day_index)
        formatted_schedule = []
        for item in schedule:
            formatted_schedule.append(item.replace("\r\n\t\t\t\t\t\t\t\t\t\t\t\tTut\r\n\t\t\t\t\t\t\t\t\t\t\t\n", " Tut").replace(
                "\r\n\t\t\t\t\t\t\t\t\t\t\t\tLab\r\n\t\t\t\t\t\t\t\t\t\t\t\n", " Lab"))
        print(formatted_schedule)

    # returns the courses as a list
    def get_courses_data(self):
        courses = []
        r = requests.get(courses_url, auth=HttpNtlmAuth(
            self.username, self.password))
        if r.status_code != 200:
            print("An Error Occurred. Check Credentials And Try Again.")
            return [], False
        else:
            soup = BeautifulSoup(r.content, 'html.parser')
            table = soup.find(
                'table', id='ContentPlaceHolderright_ContentPlaceHoldercontent_GridViewcourses')
            course_rows = table.findChildren('tr', recursive=False)
            course_rows.pop(0)
            for course in course_rows:
                course_name = course.findChildren(
                    'td', recursive=False)[1].text
                courses.append(course_name)
            return courses, True




class ClassType(Enum):
    Lecture = 1
    Lab = 2
    Tutorial = 3

# class Class:
#     def __init__(self, type: ClassType, location, course, groupNum):
#         self.type = type
#         self.course = course
#         self.groupNum = groupNum

    # GET WHOLE SCHEDULE #
    def get_schedule_whole(self):

        schedResp = requests.get(schedule_url,
                                 auth=HttpNtlmAuth(self.username, self.password))
        if schedResp.status_code != 200:
            print("An Error Occurred. Check Credentials And Try Again.")
            return [], False
        else:
            schedSoup = BeautifulSoup(schedResp.text, 'html.parser')

            def removeBlanks(string):
                return string != ''

            def removeUnwanted(string):
                return string.replace("\t", "").replace("\r", "")

            ########################### EXTRACTING ROW DATA (EACH DAY) ###########################
            sched = schedSoup.find_all(id='scdTbl')
            schedArrayTemp = []

            for i in sched[0].find_all('tr', {"id": re.compile('^Xrw')}):
                dayTemp = list(filter(removeBlanks, i.text.split('\n')))
                dayTemp2 = list(map(removeUnwanted, dayTemp))
                day = list(filter(removeBlanks, dayTemp2))
                schedArrayTemp.append(day)

            ########################### GROUPING TUTS/LABS AS ONE SLOT ###########################
            schedArray = []
            for day in schedArrayTemp:
                current = []
                counter = 0
                while counter < len(day):
                    myString = day[counter]
                    if myString[0].isnumeric():
                        current.append([day[counter], day[counter+1],
                                        day[counter+2], day[counter+3]])
                        counter += 4
                    else:
                        current.append(myString)
                        counter += 1
                schedArray.append(current)

            ## shady ## NORMALIZING THE CLASSES ###########
            for day in schedArray:
                for i in range(len(day)):
                    slot = day[i]
                    if not isinstance(slot, list):
                        words: str = slot.split()

                        if len(words) <= 1:
                            continue

                        temp = [0] * 4
                        temp[2] = words[0] + " " + words[1]
                        temp[3] = words[2]
                        temp[0] = words[3][1:] + " " + words[4][:4]
                        temp[1] = words[4][5:]
                        # print(temp, end="", sep=" ")

                        day[i] = temp

            return schedArray, True
