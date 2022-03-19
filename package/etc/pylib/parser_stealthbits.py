import re

regex = r"^(.*[\.\!\?])?(.*:.*)"

test='Activity still in process.Account Sid: S-1-5-21-1740863675-3465329846-2508926007-106822; Account Name: TST\\xxx; Attack started: 3/11/2022 12:47:00 PM; Last activity: 3/11/2022 7:47:00 PM; Number of attempts: 15801; Number of attacking hosts: 8; Attacking hosts:  (UNKNOWN) 10.20.2.50 (6324), DC3PCDC01.XXX.XXX.CORP (2), AFAHEEM (1097), SB9PDUO01 (4), {{ host }}.TST.TSTUSA.CORP (8), SMITHLAPTOP (2), NYP2PCDC01.TST.XXX.CORP (24), PC6PDUO01 (5)]'
match  =  re.search(regex,test)
print(match)
if match:
    test=match.groups()[1]
    text=match.groups()[0]
else: 
    text = test

pairs = text.split('; ')
print(text)

class alerttext_kv(object):
    def init(self, options):
        return True

    def parse(self, log_message):
        match  =  re.search(regex,log_message[".values.AlertText"].decode("utf-8"))
        if match:
            log_message[".values.AlertText"]=match.groups()[0]
            text=match.groups()[1]
        else: 
            text = log_message[".values.AlertText"].decode("utf-8")
            log_message[".values.AlertText"] = ""

        pairs = text.split('; ')


        if len(pairs)==0:
            return False
        for p in pairs:
            k,v=p.split(': ')
            cleank=k.replace(' ','_').replace('.','_')
            log_message[f".values.AlertTextValues.{cleank}"]=v.strip()
        return True

