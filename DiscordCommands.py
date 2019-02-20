from discord import *
from discord.ext import commands
from discord.utils import get
import requests
from math import *
from random import *
from bs4 import *
from asyncio import *
import re

import AnnexeCompteBon 



description = 'Bot Mathraining.'
bot = commands.Bot(command_prefix='&', description='Bot Mathraining, merci aux génialissimes créateurs !')

#____________________CONSTANTES_______________________________

token = 'SECRET'
valid_id = ["341619103896698892", "165728264554414081", "196705023772721153", "368050653118988292", "277155466432348160", "355047830571843584"]
NomsRoles = ["Grand Maitre", "Maitre", "Expert", "Chevronné", "Expérimenté", "Qualifié", "Compétent", "Initié", "Débutant", "Novice"]
colors = {'Novice' : 0x888888, 'Débutant' : 0x08D508, 'Débutante' : 0x08D508, 'Initié' : 0x008800, 'Initiée' : 0x008800,
          'Compétent' : 0x00BBEE, 'Compétente' : 0x00BBEE, 'Qualifié' : 0x0033FF, 'Qualifiée' : 0x0033FF, 'Expérimenté' : 0xDD77FF,
          'Expérimentée' : 0xDD77FF, 'Chevronné' : 0xA000A0, 'Chevronnée' : 0xA000A0, 'Expert' : 0xFFA000, 'Experte' : 0xFFA000,
          'Maître' : 0xFF4400, 'Grand Maître' : 0xCC0000}



nonRattachee = "Cette personne n'est pas rattachée à un compte Mathraining.\nTaper la commande &help pour plus d'informations."


#id_des_Canaux
canalDemandeBot = Object(id="448029413272190986")
canalInfoBot = Object(id="448105204349403137")
canalGeneral = Object(id="430291539449872384")
canalTestBot = Object(id="447444845892599826")
canalRecyclage = Object(id="430295677910908928")
user = 1416
problem = 14527
exo = 102311
point = 930930
debut = 0 #cf la fonction background_tasks_mt
dernierResolu = [None]*5



#_________________Fonctions_Annexes____________________

def roleScore(s):
    """Renvoie le role correspondant au score"""
    try:
        if s >= 7500:
            role = "Grand Maitre"
        elif s >= 5000:
            role = "Maitre"
        elif s >= 3200:
            role = "Expert"
        elif s >= 2000:
            role = "Chevronné"
        elif s >= 1250:
            role = "Expérimenté"
        elif s >= 750:
            role = "Qualifié"
        elif s >= 400 :
            role = "Compétent"
        elif s >= 200:
            role = "Initié"
        elif s >= 70:
            role = "Débutant"
        else:
            role = "Novice"

        return role
    except:
        return -1


#_________________________EVENT_______________________________________

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    bot.loop.create_task(background_tasks_mt())
    await bot.change_presence(game=Game(name="Mathraining | &help"))

@bot.event
async def on_member_join(member):
    fmt = 'Bienvenue '+ member.mention + " ! Pense à lier ton compte Mathraining avec la commande &ask. " + \
    "Si tu as des problèmes avec cette commande tape &help pour en savoir plus sur le bot ou vas faire un tour dans #présentation-serv. :wink:"
    await bot.send_message( canalGeneral ,fmt)
          
@bot.event
async def on_message(message):
    #if message.author.name == "mtbot":
    #    return
    if message.content.startswith('&say') and str(message.author.id) in valid_id:
        contenu = message.content.split()
        msg = ""
        for i in range(1, len(contenu)):
            msg += contenu[i]+" "
        await bot.send_message(canalGeneral, msg)
    if '#' in message.content:
        msg = message.content.split()
        for i in msg:
            urlPb = ""
            if i[0] == "#":
                numeroPb = i[1:]
                if numeroPb.isdigit():
                    numeroPb = int(numeroPb)
                    with open("Problems.txt", "r") as file:
                        for line in file:
                            numero, url = map(int, line.split())
                            if numero == numeroPb:
                                urlPb = url
            if urlPb:
                aEnvoyer = "Problème " + str(numeroPb) + " : http://www.mathraining.be/problems/" + str(urlPb)
                await bot.send_message(message.channel, aEnvoyer )
    await bot.process_commands(message)

#_____________________COMMANDES___________________________________

@bot.command()
async def ask(user: Member, idMTmt: int):
    '''Pour pouvoir utiliser le bot: ask @utilisateur idMathraining
    (idMathraining est le nombre dans l'url de votre page de profil sur le site)'''
    try:
        msg = "-"*10 + "\nDemande de : " + str(user.mention) + ".\nid Mathraining : " + str(idMTmt) 
        msg += "\nhttp://www.mathraining.be/users/"+ str(idMTmt)+ "\n-------------\n"
        await bot.send_message(canalDemandeBot, msg)
        await bot.say("Attendez la validation d'un administrateur.")
    except:
        await bot.say("Une erreur a été rencontrée, contactez un admin [Erreur ASK]")

@bot.command()
async def compte(result = 0):
    try:
        if result == 1:
            embed = Embed( title = "Le compte est bon", color = 0xFF4400 )
            embed.add_field( name = "Solveur", value = "https://repl.it/repls/WorrisomeSafeModes", inline = False)

        else:
            tirage = AnnexeCompteBon.compteBon()
            embed = Embed( title = "Le compte est bon", color = 0xFF4400 )
            embed.add_field( name = "Tirage", value = tirage, inline = False )

        await bot.say(embed=embed)
    except:
        await bot.say("Une erreur a été rencontrée, contactez un admin [Erreur COMPTE]")


@bot.command()
async def corrections(switch=""):
    """Affiche la liste des correcteurs et leurs nombres de corrections"""
    try:
        req = requests.get("http://www.mathraining.be/correctors")
        response = req.text #on récupère le code source de la page
        soup = BeautifulSoup(response, "lxml")
        corrections = soup.find_all('td', attrs={"style":u"text-align:center;"})
        #print(corrections)
        correcteurs = soup.find_all('a',{"href":re.compile(r"/users/.*")})
        embed = Embed(title="Corrections", color=0xFF4400)

        for loop in range(0, len(corrections), 2):
            msg = ""
            msg2 = ""
            if corrections[loop+1].getText() != "0" or switch == "all":
                msg = correcteurs[loop//2].getText()
                msg2 = corrections[loop].getText() + " corrections dont " +corrections[loop+1].getText() + " les deux dernières semaines.\n"
                embed.add_field(name=msg, value=msg2, inline=False)
        await bot.say(embed=embed)
    except:
        await bot.say("Une erreur a été rencontrée, contactez un admin [Erreur CORRECTIONS]")

@bot.command()
async def hi():
    await bot.say("Salut ! Comment vas-tu ?")


@bot.command()
async def info(user: Member):
    """Affiche les stats d'un utilisateur lié"""
    try:
        idMT = 0

        async for message in bot.logs_from(canalInfoBot, limit=500):
            #print(message.content)
            msg = message.content.split()
            if msg[0] == user.mention:
                idMT = msg[1]
                break

        if idMT != 0:
            url = "http://www.mathraining.be/users/"+str(idMT) #on construit l'url
            req = requests.get(url)
            response = req.text #on récupère le code source de la page
            soup = BeautifulSoup(response, "lxml")
            htmlscore = soup.find_all('p',attrs={"style":u"font-size:24px; margin-top:20px;"}, limit = 1) #on recupere le bout de code avec le score
            nameuser = soup.find_all('h1', limit = 1)
            avancement = soup.find_all('div', attrs={"class":u"progress-bar"})

            #print(avancement)
            #print(nameuser, nameuser[0].getText())
            #print(htmlscore[0].getText())

            username = ''.join(nameuser[0].getText().split('-')[:-1])
            rank = (nameuser[0].getText().split('-')[-1]).replace("\n", "")
            stats = ["Combinatoire :", "Géométrie :", "Théorie des nombres :", "Algèbre :", "Équations Fonctionnelles :", "Inégalités :"]

            #print("$"+avancement[1].getText()+"$")

            if avancement[1].getText() == "\n":
                nbpbsolved = "0/153"
            else:
                nbpbsolved = avancement[1].getText()
            embed = Embed(title=username + " - " + rank, description=url, color=colors[rank])
            embed.add_field(name="Score : ", value=htmlscore[0].getText().split()[2], inline=True)
            embed.add_field(name="Exercices résolus : ", value=avancement[0].getText(), inline=True)
            embed.add_field(name="Problèmes résolus : ", value=nbpbsolved, inline=True)
            pourcentage = []
            for i in range(2, 8):
                chaine=avancement[i]['style'][6:]
                j = 0
                stat=[]
                while chaine[j]!='.':
                    stat.append(chaine[j])
                    j+=1
                pourcentage.append(''.join(stat))

            for i in range(6):
                embed.add_field(name=stats[i], value=pourcentage[i]+'%', inline=True)

            await bot.say(embed=embed)

        else:
            await bot.say(nonRattachee)
    except:
        await bot.say("Une erreur a été rencontrée, contactez un admin [Erreur INFO]")


@bot.command()
async def rand(borne1: int, borne2: int):
    '''Donne un nombre aléatoire entre 2 bornes'''
    try:
        nb = randint(min(borne1, borne2), max(borne2, borne1))
        await bot.say(str(nb))
    except:
        await bot.say("Une erreur a été rencontrée, contactez un admin [Erreur RAND]")


@bot.command()
async def solved(user: Member, idpb: int):
    """Indique si le problème numéro numPb a été résolu par l'utilisateur"""
    try:
        idMT = 0

        async for message in bot.logs_from(canalInfoBot, limit=500):
            #print(message.content)
            msg = message.content.split()
            if msg[0] == user.mention:
                idMT = msg[1]
                break

        if idMT != 0:
            url = "http://mathraining.be/users/" + str(idMT)
            req = requests.get(url)
            response = req.text
            namepb = '#' + str(idpb)

            if namepb in response:
                await bot.say("Probleme résolu par l'utilisateur.")
            else:
                await bot.say("Probleme non résolu par l'utilisateur.")
        else:
            await bot.say(nonRattachee)
    except:
        await bot.say("Une erreur a été rencontrée, contactez un admin [Erreur SOLVED]")

@bot.command()
async def play(user: Member):
    await bot.send_message(user, "**42**")
    await bot.say(user.mention + " a perdu, quel dommage !") 


@bot.command()
async def update(user: Member):
    '''Pour mettre a jour son/ses roles'''
    try:
        idMT = 0

        async for message in bot.logs_from(canalInfoBot, limit=500):
            #print(message.content)
            msg = message.content.split()
            if msg[0] == user.mention:
                idMT = msg[1]
                break


        if idMT != 0:
            url = "http://www.mathraining.be/users/"+str(idMT)
            req = requests.get(url)
            response = req.text #on récupère le code source de la page
            soup = BeautifulSoup(response, "lxml")
            htmlscore = soup.find_all('p',attrs={"style":u"font-size:24px; margin-top:20px;"}) #on recupere le bout de code avk le score
            scoreuser = htmlscore[0].getText()
            s=""

            for char in scoreuser:
                if char.isdigit():
                    s+=char

            s = int(s)

            role = roleScore(s)
            if role == -1:
                await bot.say("Une erreur a été rencontrée, contactez un admin [Erreur ROLESCORE]")
                return
            roleToRemove = ""


            for roleMembre in user.roles:
                if roleMembre.name in NomsRoles:
                    roleToRemove = roleMembre.name
                    break

            if role != roleToRemove :
                servRole = get(user.server.roles, name = role )
                roleToRemove = get(user.server.roles, name = roleToRemove )

                await bot.add_roles(user, servRole)

                await bot.say(role)
                await bot.say("Mis à jour !")

                await bot.remove_roles(user, roleToRemove)

            else :
                await bot.say("Déjà à jour !")

        else:
            await bot.say(nonRattachee)
    except:
        await bot.say("Une erreur a été rencontrée, contactez un admin [Erreur UPDATE]")


@bot.command()
async def verify(user: Member, idMT: int):
    """Lie le compte d'un utilisateur au bot (ajoute son id MT dans le canal Info-bot) """
    try: 
        if not (str(message.author.id) in valid_id):
            return
        await bot.add_roles(user, get(user.server.roles, name = "Vérifié") )
        await bot.send_message(canalInfoBot, str(user.mention)+ " " + str(idMT))

        url = "http://www.mathraining.be/users/"+str(idMT)
        req = requests.get(url)
        response = req.text #on récupère le code source de la page
        soup = BeautifulSoup(response, "lxml")
        htmlscore = soup.find_all('p',attrs={"style":u"font-size:24px; margin-top:20px;"}) #on recupere le bout de code avk le score
        scoreuser = htmlscore[0].getText()
        s=""

        for char in scoreuser:
            if char.isdigit():
                s+=char

        s = int(s)

        role = roleScore(s)

        servRole = get(user.server.roles, name = role )

        await bot.add_roles(user, servRole)
        await bot.say(role)
    except:
        await bot.say("Une erreur a été rencontrée, contactez un admin [Erreur VERIFY]")

async def background_tasks_mt():
    global dernierResolu, user, problem, exo, point, debut #debut permet que les messages ne s'affichent pas 
                                            #si le bot se relance
    while True:
        changement = 0
        url = "http://www.mathraining.be/"
        req = requests.get(url)
        response = req.text #on récupère le code source de la page
        soup = BeautifulSoup(response, "lxml")
        info = soup.find_all('td',attrs={"class":u"left"})
        msg = ""
        if int(info[0].getText()) != user and int(info[0].getText())%10==0:
            msg += "Oh ! Il y a maintenant " + info[0].getText() + " utilisateurs sur Mathraining !\n"
            changement+=1
        else:
            msg += "Il y a " + info[0].getText() + " utilisateurs sur Mathraining.\n"
        user = int(info[0].getText())

        if int(info[1].getText()) != problem and int(info[1].getText())%100==0:
            msg += "Oh ! Il y a maintenant " + info[1].getText() + " problèmes résolus !\n"
            changement+=1
        else:
            msg += "Il y a " + info[1].getText() + " problèmes résolus\n"
        problem = int(info[1].getText())

        if int(info[2].getText()) != exo and int(info[2].getText())%1000==0:
            msg += "Oh ! Il y a maintenant " + info[2].getText() + " exercices résolus !\n"
            changement+=1
        else:
            msg += "Il y a " + info[2].getText() + " exercices résolus.\n"
        exo = int(info[2].getText())

        if int(info[3].getText()) != point and int(info[3].getText())%1000==0:
            msg += "Oh ! Il y a maintenant " + info[3].getText() + " points distribués !"
            changement+=1
        else:
            msg += "Il y a " + info[3].getText() + " points distribués."
        point = int(info[3].getText())

        if debut == 0: #si debut vaut 0, alors le bot viens d'etre lancé, ne rien afficher    
            print("le bot vient juste d'etre lancé")
        elif changement != 0:
            await bot.send_message(canalGeneral, msg)  



        url = "http://www.mathraining.be/solvedproblems"
        req = requests.get(url)
        response = req.text #on récupère le code source de la page
        soup = BeautifulSoup(response, "html.parser")
        cible = soup.find_all('tr')
        level = 1
        for i in range(0, len(cible)):
            td = BeautifulSoup(str(cible[i]), "lxml").find_all('td')
            if len(td) > 3:
                #print(td[3].getText().replace(" ", ""))
                if (td[3].getText().replace(" ", "")[4]).isdigit() and int(td[3].getText().replace(" ", "")[4]) == level:
                    msg = td[2].getText() + " vient juste de résoudre le problème " + td[3].getText().replace(" ", "").replace("\n", "") + " "
                    if dernierResolu[level-1] != msg:
                        print(msg)
                        dernierResolu[level-1] = msg
                        if debut != 0:
                            await bot.send_message(canalRecyclage, msg)   
                    level += 1
                    if level == 6:
                        break
        #print("fini")
        debut = 1
        await sleep(20)



bot.remove_command('help')
@bot.command(pass_context = True)
async def help(ctx):
    try:
        embed = Embed(title="Mathraining bot", type="rich", description="Préfixe avant les commandes : &.", color=0xEEE657)

        embed.add_field(name="info @utilisateur", value="Donne le score et le rang Mathraining de l'utilisateur mentionné.", inline=False)
        embed.add_field(name="update @utilisateur", value="Pour mettre à jour son rang.", inline=False)
        embed.add_field(name="solved @utilisateur numPb", value="Indique si le problème numéro numPb a été résolu par l'utilisateur.", inline=False)
        embed.add_field(name="ask @utilisateur idMathraining", value="Pour demander à rattacher votre compte Mathraining:" +
        " idMathraining (idMathraining est le nombre dans l'url de votre page de profil sur le site).", inline=False)
        embed.add_field(name="corrections (all)", value="Affiche la liste des correcteurs (qui ont corrigé récemment ou pas avec "all") et leurs contributions.", inline=False)
        embed.add_field(name="rand a b", value="Donne un nombre aléatoire entre a et b.", inline=False)
        embed.add_field(name="compte + 6 nombres", value="Effectue un tirage si aucun nombre n'est donné, résout le tirage sinon", inline=False)
        embed.add_field(name="help", value="Affiche ce message en MP.", inline=False)

        await bot.send_message(ctx.message.author,embed=embed)
    except:
        await bot.say("Une erreur a été rencontrée, peut etre que vous avez bloqué les messages privés ce qui empeche le bot de communiquer avec vous, contactez un admin [Erreur HELP]")

#______________________________________________________________

#bot.loop.create_task(background_tasks_mt())
bot.run(token) #Token MT
