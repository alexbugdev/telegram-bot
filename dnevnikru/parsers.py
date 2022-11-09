from dnevnikru import settings
from dnevnikru.exceptions import DnevnikError

from bs4 import BeautifulSoup
from typing import Optional, Union
from datetime import date, timedelta, datetime


class Parser:
    basicTime = ["11:30", "12:20", "10:30", "10:30", "10:30", "10:30", "10:30"]
    @staticmethod
    def last_page(response: str) -> Optional[int]:
        """Функция для получения номера последней страницы (если она есть)"""
        try:
            soup = BeautifulSoup(response, 'lxml')
            all_pages = soup.find('div', {'class': 'pager'})
            pages = all_pages.find_all('li')
            last_page = pages[-1].text
            return last_page
        except AttributeError:
            return None

    @staticmethod
    def save_content(response: str, class2: str) -> tuple:
        """Функция парсинга и сохранения таблиц с сайта"""
        soup = BeautifulSoup(response, 'lxml')
        table = soup.find('table', {'class': class2})
        content = []
        all_rows = table.findAll('tr')
        for row in all_rows:
            content.append([])
            all_cols = row.findAll('td')
            for col in all_cols:
                the_strings = [str(s) for s in col.findAll(text=True)]
                the_text = ''.join(the_strings)
                content[-1].append(the_text)
        content = [a for a in content if a != []]
        return tuple(content)
    @staticmethod
    def isDefined(session) -> bool:

        link_1 = "https://xn--b1addnkoc.xn--p1ai/userfeed"

        week_response = session.get(link_1,
                                    headers={"Referer": link_1}).text
        soup = BeautifulSoup(week_response, 'lxml').text
        if("Object moved" in soup):
            return False
        else:
            return True
        #elems = soup.find_all("td", {"id": "d" + data + "_" + str(date1)})[0]

        return False
    @staticmethod
    def get_week_response(session, school: Union[int, str], _date: str, section: int = 0) -> str:
        """Функция для получения html страницы с результатами недели"""

        fs = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
        monday = {1:"9:00 - 9:45",2:"10:00 - 11:30", 3:"11:50 - 13:20", 4:"13:50 - 15:20", 5:"15:50 - 17:10", 6: "17:20 - 17:50"}

        all_days = {1:"9:00 - 10:30", 2:"10:50 - 12:20", 3:"12:50 - 14:20", 4: "14:40 - 16:10", 5: "16:20 - 17:50", 6: "18:00 - 19:30"}
        ss = ['Будни'] * 5 + ['Выходной'] * 2

        subjects = dict()


        #print(soup)

        userID = "1000021584849"
        scc = 1000018821170
        dd = datetime.strptime(_date, "%d.%m.%Y")
        if dd.month < 10:
            if dd.day < 10:
                data = "" + str(dd.year) + "0" + str(dd.month) + "0" + str(dd.day)
            else:
                data = "" + str(dd.year) + "0" + str(dd.month) + "" + str(dd.day)

        else:
            if dd.day < 10:
                data = "" + str(dd.year) + str(dd.month) + "0" + str(dd.day)
            else:
                data = "" + str(dd.year) + "" + str(dd.month) + "" + str(dd.day)
        formattedDate = FormattedDate(number=dd.day, name=fs[dd.weekday()], status=ss[dd.weekday()], formatted=_date)
        today = dd
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)
        week_d = today.weekday()
        dinnerTime = Parser.basicTime[week_d]

        link_1 = "https://schools.xn--b1addnkoc.xn--p1ai/schedules/view.aspx?school=1000018821170&group=1987125226191550537&period=1987862800925313819&year="+str(end.year)+"&month="+str(end.month)+"&day="+str(end.day)
        week_response = session.get(link_1,
                                    headers={"Referer": link_1}).text
        soup = BeautifulSoup(week_response, 'lxml')
        selects = 0
        group = section

        source = ""
        for date1 in range(1,7+1):
            try:
                elems = soup.find_all("td", {"id":"d" + data +"_"+str(date1)})[selects]
            except:
                return "error"
            currentTime = "";
            if (dd.day == start.day):

                currentTime = monday[date1]
            else:

                currentTime = all_days[date1]

            if len(elems) < 1:
                print("Нету пар")
                break

            try:
                h1 = elems.find_all("div", {"class": "dL"})
            except:
                break
            if len(h1) < 1:

                subjects[data+str(date1)] = None

                return "Занятий нет отдыхаем =)"
            round = 0
            for h in h1:
                subject = h.find("a", {"class": "aL"})
                subject_text = subject.select("a")
                subject_link = subject.get("href")

                ss = session.get(subject_link).text

                sup = BeautifulSoup(ss, 'lxml')

                teacher = h.find("p", {"data-test-id": "teacher"}).text

                room = h.find("p", {"data-test-id": "room"}).text

                if ('403' in sup.text and group == 1 and not('Группа 2' in sup.text)):

                    subj = Subject(subject=subject.get("title"), teacher=teacher, auditory=room, number=date1)

                    subjects[data+str(date1)] = DataOfState(subj,formattedDate)


                    source += str(date1)+"-я пара ->\n"+"📒   <b>Предмет:</b> "+subject.get("title") + "\n👨‍🏫   <b>Преподаватель:</b> "+teacher + "\n🗺️   <b>Аудитория:</b> "+room + "\n⏰   <b>Время: </b>"+ currentTime +"\n\n"
                    print("First INVOKE")
                    break
                # if group == 1 and not('Группа 2' in sup):
                #     subj = Subject(subject=subject.get("title"), teacher=teacher, auditory=room, number=date1)
                #
                #     subjects[data+str(date1)] = DataOfState(subj,formattedDate)
                #     source += str(date1)+"-я пара ->\n"+"<b>Предмет:</b> "+subject.get("title") + "\n<b>Преподаватель:</b> "+teacher + "\n<b>Аудитория:</b> "+room + "\n\n"
                #     print("Second INVOKE")
                #     break
                if group == 1 and ('Группа 2' in sup.text):
                    if (h1.index(h) == len(h1) - 1):
                        source += str(date1)+"-я пара ->\n Пары нет.\n\n"

                        print("THIRD INVOKE")
                        break
                if group == 0 and not('403' in sup.text):
                    source += str(date1) + "-я пара ->\n" + "📒  <b>Предмет:</b> " + subject.get(
                        "title") + "\n👨‍🏫   <b>Преподаватель:</b> " + teacher + "\n🗺️   <b>Аудитория:</b> " + room + "\n⏰   <b>Время: </b>" + currentTime + "\n\n"

                    print("FOUR INVOKE")
                    break
                if not('403' in sup.text) and not('Группа 2' in sup.text):

                    source += str(date1) + "-я пара ->\n" + "📒 <b>Предмет:</b> " + subject.get(
                        "title") + "\n👨‍🏫   <b>Преподаватель:</b> " + teacher + "\n🗺️   <b>Аудитория:</b> " + room + "\n⏰   <b>Время: </b>" + currentTime + "\n\n"

                    print("SIX INVOKE")
                    break
                else:
                    if(h1.index(h) == len(h1)-1):
                        source += str(date1)+"-я пара ->\n Пары нет.\n\n"
                        print("FIVE INVOKE")
        if week_d < 5:
            source += "\n<b>Обед: </b>" + dinnerTime
        #h = soup.find_all("div", {"class": head})[0]
        if(len(source) < 1):
            return "Нет пар, отдыхаем =)"
        return source

    @staticmethod
    def get_homework(self, link: str, last_page: Union[str, int], homework_response: str) -> dict:
        """Функция для получения домашних заданий"""
        if last_page is not None:
            subjects = []
            for page in range(1, int(last_page) + 1):
                homework_response = self._main_session.get(link, headers={"Referer": link}).text
                for i in Parser.save_content(homework_response, class2='grid gridLines vam hmw'):
                    subject = [i[2], i[0].strip(),
                               " ".join([_.strip() for _ in i[3].split()])]
                    subjects.append(tuple(subject))
            return {"homeworkCount": len(subjects), "homework": tuple(subjects)}
        if last_page is None:
            try:
                subjects = []
                for i in Parser.save_content(homework_response, class2='grid gridLines vam hmw'):
                    subject = [i[2], i[0].strip(),
                               " ".join([_.strip() for _ in i[3].split()])]
                    subjects.append(tuple(subject))
                return {"homeworkCount": len(subjects), "homework": tuple(subjects)}
            except Exception as e:
                raise DnevnikError(e, "DnevnikError")

    @staticmethod
    def get_marks(marks_response: str) -> tuple:
        """Функция для получения оценок"""
        try:
            marks = Parser.save_content(response=marks_response, class2='grid gridLines vam marks')
            for mark in marks:
                mark[2] = mark[2].replace(" ", "")
            return tuple(marks)
        except Exception as e:
            raise DnevnikError(e, "DnevnikError")

    @staticmethod
    def search_people(self, last_page: Union[int, str], link: str, searchpeople_response: str) -> dict:
        """Функция для поиска людей по школе"""
        if last_page is not None:
            members = []
            for page in range(1, int(last_page) + 1):
                members_response = self._main_session.get(link + f"&page={page}").text
                for content in Parser.save_content(members_response, class2='people grid'):
                    member = [content[1].split('\n')[1], content[1].split('\n')[2]]
                    members.append(tuple(member))
            return {"peopleCount": len(members), "people": tuple(members)}
        if last_page is None:
            members = []
            try:
                for content in Parser.save_content(searchpeople_response, class2='people grid'):
                    member = [content[1].split('\n')[1], content[1].split('\n')[2]]
                    members.append(tuple(member))
                return {"peopleCount": len(members), "people": tuple(members)}
            except Exception as e:
                raise DnevnikError(e, "DnevnikError")

    @staticmethod
    def get_birthdays(self, birthdays_response: str, link: str) -> dict:
        """Функция для поиска дней рождений по школе"""
        if "в школе именинников нет." in birthdays_response:
            return {"peopleCount": 0, "people": ()}
        last_page = Parser.last_page(birthdays_response)

        if last_page is not None:
            birthdays = []
            for page in range(1, int(last_page) + 1):
                birthdays_response = self._main_session.get(link + f"&page={page}").text
                for i in Parser.save_content(birthdays_response, class2='people grid'):
                    birthdays.append(i[1].split('\n')[1])
            return {"birthdaysCount": len(birthdays), "birthdays": tuple(birthdays)}
        if last_page is None:
            birthdays = []
            try:
                for i in Parser.save_content(birthdays_response, class2='people grid'):
                    birthdays.append(i[1].split('\n')[1])
                return {"birthdaysCount": len(birthdays), "birthdays": tuple(birthdays)}
            except Exception as e:
                raise DnevnikError(e, "DnevnikError")

    @staticmethod
    def get_week(self, info: str, weeks: int) -> dict:
        """Функция для получения результатов недели"""
        head = "current-progress-{}".format(info)
        item = "current-progress-{}__item"
        item = item.format("list") if info != "schedule" else item.format("schedule")
        week_response = Parser.get_week_response(session=self._main_session,
                                                 school=self._school, weeks=weeks)

        week = {}
        soup = BeautifulSoup(week_response, 'lxml')
       # print(soup)
        student = soup.findAll("h5", {"class": "h5 h5_bold"})[0].text
        h = soup.find_all("div", {"class": head})[0]
        all_li = h.findAll("li", {"class": item})
        if info == "schedule":
            for li in all_li:
                day = li.find("div").text
                schedule = li.findAll("li")
                schedule = [x.text for x in schedule]
                week.update({day: tuple(schedule)})
            return {"student": student, "schedule": week}
        else:
            week = [i.replace("\n", " ").strip(" ") for i in [i.text for i in all_li]]
            return {"student": student, info: tuple(week)}

class DataOfState:
    def __init__(self, subject, date) -> None:
        self._subject = subject
        self._date = date

    def subject(self):
        return self._subject

    def date(self):
        return self._date

class Subject:
    def __init__(self, subject="Empty", teacher="Empty", auditory="Empty",number=1):
        self.subject = subject
        self.teacher = teacher
        self.auditory = auditory
        self.number = number

    # getter method
    def subject_1(self):
        return self.subject
    def teacher(self):
        return self.teacher
    def auditory(self):
        return self.auditory
    def number(self):
        return self.number
class FormattedDate:
    def __init__(self, number=1, name="Понедельник", status="Будни", formatted="01.09.2022"):
        self.number = number
        self.name = name
        self.status = status
        self.formatted = formatted

    def outputformatted(self):
        strs = self.formatted + " " + self.name + " " + self.status
        return strs

    def get_number(self):
        return self.number
    def get_name(self):
        return self.name
    def get_status(self):
        return self.status
    def get_formatted(self):
        return self.formatted