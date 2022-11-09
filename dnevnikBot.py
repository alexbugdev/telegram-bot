from dnevnikru import Dnevnik
from dnevnikru.parsers import Parser
from dnevnikru.parsers import DataOfState
from dnevnikru.parsers import Subject
from dnevnikru.parsers import FormattedDate
from pprint import pprint

#dn = Dnevnik(login="ignateva", password="Cashgg1977")

dn_1 = Dnevnik(login="Pavel.smirnov2004100", password="Anonimys442")
isdef = dn_1.isDefined()
#data = dn_1.week(dates="27.10.2022", section=0)

#data_2 = dn.week(dates="26.10.2022", section=0)
#hw = dn.homework(studyyear=2022, datefrom='26.10.2022', dateto='28.10.2022')['homework']

print(isdef)

