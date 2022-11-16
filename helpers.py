from flask import jsonify
from datetime import datetime, date, timedelta
import time

infringement_cases = []
life_health_of_victim = []
cultural_religious_historical = []
good_faith = []
public_health = []
army_navy_airforce = []
evidence_avaialble = []

for i in range(14, 21 + 1):
    infringement_cases.append(str(i))
infringement_cases.append("21A")
for i in range(22, 30 + 1):
    infringement_cases.append(str(i))
infringement_cases.append(str(32))

for i in range(269, 377 + 1):
    life_health_of_victim.append(str(i))

for i in range(107, 116):
    cultural_religious_historical.append(str(i))
cultural_religious_historical.append("120A")
cultural_religious_historical.append("120B")
cultural_religious_historical.append(str(307))
cultural_religious_historical.append(str(800))

cultural_religious_historical = ["295", "296", "135A", "505", "297", "298", "120A", "120B", "307",
                                 "800"] + cultural_religious_historical

print(infringement_cases)

for i in range(76, 81 + 1):
    good_faith.append(str(i))

for i in range(131, 141):
    army_navy_airforce.append(str(i))

army_navy_airforce.sort()
infringement_cases.sort()
cultural_religious_historical.sort()
good_faith.sort()
public_health.sort()
life_health_of_victim.sort()


def exceptionAsAJson(cause, e):
    return jsonify({
        "caused at": str(cause),
        "error": str(e)
    })


def successAsJson():
    return jsonify({
        "status": "success"
    })


def successAsJsonWithObj(obj):
    return jsonify({
        "status": "success",
        "object": obj
    })


def getDateTimeInMillis():
    return round(time.time() * 1000)


def getDateTimeInTimestamp(millis):
    date_time_obj = datetime.fromtimestamp(millis / 1000)
    returnable = date_time_obj.strftime("%m/%d/%Y, %H:%M:%S")
    return returnable


def getTodayDate():
    return date.today()


def getTomorrowDate():
    return date.today() + timedelta(days=1)


def checkTwoDateMatch(d1, d2):
    return d1 == d2


def extract_text_from_pdf():
    pass


def getInfringementScore(section_ids):
    for section_id in section_ids:
        if section_id in infringement_cases:
            n = len(infringement_cases)
            index = infringement_cases.index(section_id)
            return n - index
    return "NIL"


def lifeHealthOfVictim(section_ids):
    for section_id in section_ids:
        if section_id in life_health_of_victim:
            n = len(life_health_of_victim)
            index = life_health_of_victim.index(section_id)
            return n - index
    return "NIL"


def culturalReligiousHistorical(section_ids):
    for section_id in section_ids:
        if section_id in cultural_religious_historical:
            n = len(cultural_religious_historical)
            index = cultural_religious_historical.index(section_id)
            return n - index
    return "NIL"


def goodFaithSection(section_ids):
    for section_id in section_ids:
        if section_id in good_faith:
            n = len(good_faith)
            index = good_faith.index(section_id)
            return n - index
    return "NIL"


def publicHealth(section_ids):
    for section_id in section_ids:
        if section_id in public_health:
            n = len(public_health)
            index = public_health.index(section_id)
            return n - index
    return "NIL"


def armyNavyAirforce(section_ids):
    for section_id in section_ids:
        if section_id in army_navy_airforce:
            n = len(army_navy_airforce)
            index = army_navy_airforce.index(section_id)
            return n - index
    return "NIL"


def getOverallScore(scores):
    final_scores = 0
    for score in scores:
        if score != 'NIL':
            final_scores = final_scores + (score * (len(scores) - scores.index(score)))
    return round(final_scores / len(scores))


def getEvidenceScore(evidence_available):
    if evidence_available is not None and evidence_available:
        return 1
    return 0


def getParticipantsScore():
    # if n is not None:
    #     if n > '10':
    #         return 3
    #     elif '10' > n > '2':
    #         return 2
    #     else:
    #         return 1
    return 1