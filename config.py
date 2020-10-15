# -*- coding: utf-8 -*-
import discord

from discord.ext.commands import Bot
from discord.ext import commands
from discord.utils import get

import json

with open('files/config/token.txt','r') as file:
    token = file.read()

## -- Clean output function for Quiz Command
def clean(var):
    var = var.replace("<u>","")
    var = var.replace("</u>","")
    var = var.replace("\"","")
    var = var.replace("([","")
    var = var.replace("])","")
    var = var.replace(" | ",", ")

    return var

with open('files/quiz/dict-navi.all.csv', 'r', encoding='utf-8') as fh:
    words = []
    for mainline in fh:
        mainline = mainline.split(",")
        for i, part in enumerate(mainline):
            part = clean(part)
            mainline[i] = part
        words.append(mainline)

def reloadDir():
    with open('files/users/directory.json', 'r', encoding='utf-8') as fh:
        directory = json.load(fh)
        return directory
    
with open('files/config/help.json', 'r', encoding='utf-8') as fh:
    helpFile = json.load(fh)
        
# Global Variables
token = token.strip()
prefix = "!"
version = "Stable 1.21"
debug = False

activeRoleIDs = [715319929942966312, 715319903376113745, 715319861684994069, 715319829611151440, 715319782198739016, 715319761927405668, 715319686710952018, 715319529550381056, 715319404803653632, 715319360884834376, 715319264805912580]
activeRoleDict = [[715319929942966312, "Veteran"], [715319903376113745, "Warrior"], [715319861684994069, "Trainee Warrior"], [715319829611151440, "Party Leader"], [715319782198739016, "Ikran Rider"], [715319761927405668, "Hunter"], [715319686710952018, "Trainee Hunter"], [715319529550381056, "Member"], [715319404803653632, "Trainee Member"], [715319360884834376, "Newcomer"], [715319264805912580, "Alien"]]
activeRoleThresholds = [16384, 8192, 4096, 2048, 1024, 512, 256, 128, 64, 32, 16,8]
ignoredRoles = ["Olo'eyktan (Admin)","Eyktan (Moderator)","Karyu (Teacher)","Numeyu (Learner)","'Eylan (Friend)","Tìkanu Atsleng (Bot)","He/Him","She/Her","They/Them","frapo"]

lepArchive = [["Placeholder","Tuple"]]
library = []

send_time = '12:00'
sequelDate = "12-22-2022"

# Channels
general = 715296162394931340
modLog = 715052686487191583
lepChannel = 715988382706303038

# Embed Colors
botColor = 0x113f78
reportColor = 0x5Da9E9
QOTDColor = 0x8f6593
quizColor = 0x113f78
rankColor = 0x1e3626
welcomeColor = 0x6D326D

successColor = 0x00c600
failColor = 0xff0000

# IDs
frapoID = 715319193188171846
botRoleID = 715094486992027699
guildID = 715043968886505484
makoID = 81105065955303424
botID = 715296437335752714
reykID = 716618822744014848

adminID = 715044138864607334
modID = 715048580334878732

modRoles = [adminID,modID]
allowedRoles = [adminID,modID,715044889049563147]

allowedSet = set(allowedRoles)
modSet = set(modRoles)

# Error Embeds
denied=discord.Embed(description="**Error: Denied** \n You do not have permission to run this command!", colour=failColor)
syntax=discord.Embed(description="**Error: Invalid Syntax** \n If you need help with a command, type `!help <command name>`.", color=failColor)
faq_error=discord.Embed(description="**Error: No FAQ Article Found** \n If you need help with a command, type `!help <command name>`.", color=failColor)
arguments=discord.Embed(description="**Error: Too Many Arguments** \n If you need help with a command, type `!help <command name>`.", color=failColor)
dm_only=discord.Embed(description="**Error: Denied** \n This command is not permitted here. Use this command in DMs only.", color=failColor)
help_error=discord.Embed(description="**Error: Unknown Command** \n Unknown command specified. Please check your spelling and try again, or use `!help` to see a list of all commands.", color=failColor)

success=discord.Embed(description="**Success**", color=successColor)

# FAQ Embeds
agent = discord.Embed(title="Agentive (Subject) Noun Case", description="**Endings**: \n**-l**, vowel ending \n**-ìl**, consonant ending \n\nIn Na'vi, the agentive case is used to indicate the subject of a sentence, or the person/place/thing doing the action of the sentence. \n\nExample: \n**oe__l__ tìng tskoti**, '__I__ give the bow.'", color=reportColor)
patient = discord.Embed(title="Patientive (Object) Noun Case", description="**Endings**: \n**-ti**, vowel/consonant ending \n**-i(t)**, consonant ending \n\nIn Na'vi, the patientive case is used to indicate the object of a sentence, or the person/place/thing being modified by the action of the sentence. \n\nExample: \n**oel tìng tsko__ti__**, 'I give the __bow__.'", color=reportColor)
dative = discord.Embed(title="Dative (Recipient/Indirect Object) Noun Case", description="**Endings**: \n**-r(u)**, vowel ending \n**-ur**, consonant ending \n\nIn Na'vi, the dative case is used to indicate the recipient of the object of a sentence with transitive verbs, and the recipient of the action of the verb for intransitive verbs. \n\nExample: \n**oel tìng tskoti nga__ru__**, 'I give the bow __to you__.'", color=reportColor)
topic = discord.Embed(title="Topical Noun Case", description="**Endings**: \n**-ri**, vowel ending \n**-ìri**, consonant ending \n\nIn Na'vi, the topical case is used to indicate the topic of the sentence, especially with certain intransitive verbs seem as though they could take objects like **nume**. \n\nExample: \n**lì'fya__ri__ leNa'vi oe nume**, 'I learn the __Na'vi language__.'", color=reportColor)

hrh = discord.Embed(description='**HRH** is the Na\'vi equivalent of "LOL", and is derived from this video:\nhttps://youtu.be/-AgnLH7Dw3w?t=274 \n\n ```Interviewer: "What would LOL be?" \nPaul: "It would have to do with the word \'herangham\'... maybe HRH"```', color=reportColor)

hu_fa = discord.Embed(description="A common beginner mistake is to interchange **hu** and **fa** for 'with' without distinction. **Hu** is the more traditional 'with', while **fa** is 'by means of, using' as in 'with a tool'. \n\nExample: \n**oe tswayon fa ikran**, 'I fly __with/via__ an ikran'", color=reportColor)
lu_efu = discord.Embed(description="A common beginner mistake is to use **lu** instead of **'efu**. **'efu** is the Na'vi word for 'feel'. So, one would not say **oe lu ngeyn** for 'I am tired', but instead **oe 'efu ngeyn**.", color=reportColor)
lu_tok = discord.Embed(description="A common beginner mistake is to use **lu** instead of **tok**. **Tok** is the Na'vi word for 'be at, occupy a space'. So, one would not say **oe lu fìtseng** for 'I am here', but instead **oel tok fìtsengit**.", color=reportColor)
lu_verb = discord.Embed(description="A common beginner mistake is to use **lu** alongside verbs to indicate the progressive 'verbing' aspect. Instead, Na'vi has its own infix which indicates this aspect of a verb, **<er>**, which fits into the first position. Example: **h__er__angham**, 'laughing'", color=reportColor)

pronounce = discord.Embed(description='Pamìrìk\'s guide to pronunciation can be found here:\nhttps://www.youtube.com/watch?v=e5JKGL-o16M', color=reportColor)
start = discord.Embed(description='Kelutral.org\'s guide to getting started can be found here:\nhttp://kelutral.org/get-started', color=reportColor)

# Output Text
nvText = ["Trr a tsatute zola'u: ", "Nulnawnewa Lì'fya: ", "Preferred Pronouns: ", "Txìntin: ", "Ayupxare: ", "Server Leaderboard Rank: ", "Sar fayluta !profile @user [English/Na\'vi] fte leykivatem lì\'fyati ngeyä.","Holpxay aloä a tsatuter irayo soli:"]
enText = ["Join Date: ", "Preferred Language: ", "Preferred Pronouns: ", "Current Rank: ", "Message Count: ", "Server Leaderboard Rank: ", "Use !profile @user [English/Na\'vi] to change your output settings.", "Thanks: "]

# File Paths
userFile = 'files/users/{}.tsk'
qotdFile = 'files/qotd/{}.tsk'
calendarFile = 'files/qotd/calendar.tsk'
botFile = 'files/users/bot.tsk'
directoryFile = 'files/users/directory.json'

directory = reloadDir()
