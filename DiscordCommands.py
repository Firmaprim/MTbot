from discord import *
from discord.ext import commands
from discord.utils import get

import requests
from bs4 import *
from asyncio import *
from re import compile
from re import findall

from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from random import randint
from io import BytesIO

import AnnexeCompteBon
from traceback import format_exc

description = 'Bot Mathraining.'
bot = commands.Bot(command_prefix='&', description='Bot Mathraining, merci aux génialissimes créateurs !')

#____________________CONSTANTES_______________________________

token = 'SECRET!'         
NomsRoles = ["Grand Maitre", "Maitre", "Expert", "Chevronné", "Expérimenté", "Qualifié", "Compétent", "Initié", "Débutant", "Novice"]

colors = {'Novice' : 0x888888, 'Débutant' : 0x08D508, 'Débutante' : 0x08D508, 'Initié' : 0x008800, 'Initiée' : 0x008800,
          'Compétent' : 0x00BBEE, 'Compétente' : 0x00BBEE, 'Qualifié' : 0x0033FF, 'Qualifiée' : 0x0033FF, 'Expérimenté' : 0xDD77FF,
          'Expérimentée' : 0xDD77FF, 'Chevronné' : 0xA000A0, 'Chevronnée' : 0xA000A0, 'Expert' : 0xFFA000, 'Experte' : 0xFFA000,
          'Maître' : 0xFF4400, 'Grand Maître' : 0xCC0000}

nonRattachee = "Cette personne n'est pas rattachée à un compte Mathraining.\nTaper la commande &help pour plus d'informations."

#Firefox-headless
options = webdriver.FirefoxOptions()
options.add_argument('-headless')

idAdmin="430287978192044037"
idModo="491291638233169931"
erreur ="Une erreur a été rencontrée, contactez un Admin ou un Modérateur."
perms="Vous n'avez pas les permissions pour effectuer cette commande."

#id_des_Canaux
canalInfoBot = Object(id="448105204349403137")
canalEnAttente = Object(id="605001945924763648")
canalGeneral = Object(id="430291539449872384")
canalResolutions = Object(id="557951376429416455")

user = 1416
problem = 14527
exo = 102311
point = 930930
debut = 0 #cf la fonction background_tasks_mt
dernierResolu = [None]*5

##_________________Fonctions_Annexes____________________

def GetMTScore(idMT: int) :
    soup = BeautifulSoup(requests.get("http://www.mathraining.be/users/"+str(idMT)).text,"lxml")  #on récupère le code source de la page
    htmlscore = soup.find_all('p',attrs={"style":u"font-size:24px; margin-top:20px;"}) #on recupere le bout de code avec le score
    if htmlscore != [] : return int(htmlscore[0].getText()[8:]) #On enlève le 'Score : ' de 'Score : 1234'
    try :
        if (soup.find_all('h1', limit = 1)[0].getText().split('-')[-1])[1:-1] == "Administrateur" : return 1 #Administrateur
        else : return 0 #Personne n'ayant aucun point
    except : return 2 #Identifiant non attribué

def roleScore(s):
    """Renvoie le role correspondant au score"""
    try:
        if s >= 7500: role = "Grand Maitre"
        elif s >= 5000: role = "Maitre"
        elif s >= 3200: role = "Expert"
        elif s >= 2000: role = "Chevronné"
        elif s >= 1250: role = "Expérimenté"
        elif s >= 750: role = "Qualifié"
        elif s >= 400: role = "Compétent"
        elif s >= 200: role = "Initié"
        elif s >= 70:  role = "Débutant"
        elif s == 2 : role = "Inconnu"
        elif s == 1 : role = "Administrateur"
        else: role = "Novice"
        return role
    except: return -1

async def FindUser(user: Member,canal: object.Object = canalInfoBot) :
        idMT = 0
        async for message in bot.logs_from(canal, limit=1000):
            msg = message.content.split()
            e1=[2,3][user.mention[2]=='!']
            e2=[2,3][msg[0][2]=='!']
            if msg[0][e2:-1] == user.mention[e1:-1]:
                idMT = int(msg[1])
                break
        return idMT #0 si n'est pas dans la liste

async def FindMT(idMT: int,canal: object.Object = canalInfoBot) :
        user = 0; test= str(idMT)
        async for message in bot.logs_from(canal, limit=1000):
            msg = message.content.split()
            if msg[1] == test:
                e2=[2,3][msg[0][2]=='!']
                user = int(msg[0][e2:-1])
                break
        return user #0 si n'est pas dans la liste

def Connexion() :
    global driver
    #driver = webdriver.PhantomJS(executable_path=r'B:\downloads\MT\PJS\bin\phantomjs.exe')
    driver = webdriver.Firefox(options=options,executable_path=r'B:\downloads\MT\geckodriver.exe')
    driver.get("https://mathraining.be")
    driver.find_element_by_link_text("Connexion").click()

    username = driver.find_element_by_id("tf1")
    username.clear();username.send_keys("SECRET")
    
    password = driver.find_element_by_name("session[password]")
    password.clear();password.send_keys("SECRET")
    
    driver.find_element_by_name("commit").click()    
    
def Deconnexion() :
    driver.find_element_by_xpath("//a[not(contains(text(), 'Théorie')) and not(contains(text(), 'Statistiques')) and not(contains(text(), 'Problèmes')) and @class='dropdown-toggle']").click()
    driver.find_element_by_link_text("Déconnexion").click()
    driver.quit()

##_________________________EVENT_______________________________________

@bot.event
async def on_ready():
    print('Connecté sous')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    bot.loop.create_task(background_tasks_mt())
    await bot.change_presence(game=Game(name="Mathraining | &help"))

@bot.event
async def on_member_join(member):
    fmt = 'Bienvenue '+ member.mention + " ! Pense à lier ton compte Mathraining avec la commande &ask. \n" + \
    "Si tu as des problèmes avec cette commande tape &help pour en savoir plus sur le bot ou va faire un tour dans #règles. :wink:"
    await bot.send_message( canalGeneral ,fmt)
          
@bot.event
async def on_message(message):
    #_____COMMANDE POUR AFFICHER LES PROBLEMES_____    
        
    if '#' in message.content:
        msg = message.content.split()
        for i in msg:
            urlPb = ""
            if i[0]== '#' and i[5:6]=='' and i[4:5]!='' and i[1:5].isdigit() : #On vérifie que le nombre a exactement 4 chiffres
                numeroPb = int(i[1:5])
                with open("Problems.txt", "r") as file:     #On pourrait faire du log(n) si le fichier était trié selon les numéros de pb.
                    for line in file:                       #Mais bon, on a que 153 problèmes, donc c'est pas bien grave !
                        numero, url = map(int, line.split())
                        if numero == numeroPb:
                            urlPb = url; break
            if urlPb:
                aEnvoyer = "Problème " + str(numeroPb) + " : http://www.mathraining.be/problems/" + str(urlPb)
                await bot.send_message(message.channel, aEnvoyer )
    await bot.process_commands(message)

##_____________________COMMANDES___________________________________

@bot.command(pass_context=True)
async def ask(ctx,idMTnew: int):
    '''Pour pouvoir utiliser le bot: ask @utilisateur idMathraining
    (idMathraining est le nombre dans l'url de votre page de profil sur le site)'''
    pascontent="Nicolas ne va pas être content si vous vous êtes fait un autre compte !! :sweat_smile:"
    contact="Contactez un Admin ou un Modo si vous souhaitez changer de compte."
    user=ctx.message.author
    try:
        idMTold,idMTatt=(await FindUser(user)),(await FindUser(user,canalEnAttente))
        if idMTold == 0 and idMTatt == 0 :  
            Score=GetMTScore(idMTnew)
            UserId,UserIdatt = (await FindMT(idMTnew)),(await FindMT(idMTnew,canalEnAttente))
            if UserId != 0 : await bot.say("Ce compte Mathraining appartient déjà à "+str(await bot.get_user_info(UserId))+" !")
            elif UserIdatt != 0: await bot.say("Ce compte Mathraining a déjà été demandé à être relié par "+str(await bot.get_user_info(UserIdatt))+" !")
            elif Score >= 3200 or Score == 1 : await bot.say("Le compte Mathraining renseigné est au moins Expert ou Administrateur, il faut demander à un Admin/Modo du serveur de vous relier !")
            elif Score == 2 : await bot.say("Le compte Mathraining renseigné n'existe pas !")
            else :
                try :
                    Connexion()
                    driver.get("https://www.mathraining.be/discussions/new?qui="+str(idMTnew)) #Sélectionne automatiquement la personne dans les messages.
                    msg="Bonjour !  :-)\n\n Vous avez bien demandé à relier votre compte mathraining avec le compte Discord [b]"+str(user)+"[/b] sur le [url=https://www.mathraining.be/subjects/365?q=0]serveur Mathraining[/url] ?\n Répondez [b]\"Oui\"[/b] (sans aucun ajout) à ce message pour confirmer votre demande, sinon par défaut vous ne serez pas relié. \n Vous devez ensuite taper la commande [b]&verify[/b] sur Discord pour finaliser la demande.\n\n [b]Seul le dernier message de cette conversation sera lu pour confirmer votre demande.[/b] \n[i][u]NB[/u] : Il s'agit d'un message automatique. N'espérez pas communiquer avec ce compte Mathraining.\n (A vrai dire, j'ai activé le service sur mon compte pour l'instant. Vous pouvez tout de même me parler ou me signaler un bug ...)[/i]"
                    m = driver.find_element_by_id("MathInput")
                    m.clear();m.send_keys(msg)
                    driver.find_element_by_name("commit").click()
                    Deconnexion()
                    await bot.send_message(canalEnAttente, str(user.mention)+ " " + str(idMTnew))
                    await bot.say("Vous venez de recevoir un message privé sur le site. Suivez les instructions demandées.")
                except : await bot.say("Ce service est temporairement indisponible, veuillez réessayer plus tard.\n Vous pouvez toutefois demander à un Admin ou un Modérateur de vous relier manuellement.")
        elif idMTold == idMTnew and idMTold != 0 : await bot.say("Vous êtes déjà relié au bot avec le même id !")
        elif idMTatt == idMTnew and idMTatt !=0 : await bot.say("Vous avez déjà fait une demande avec le même id !")
        elif idMTatt != idMTnew and idMTold ==0 : await bot.say("Vous avez déjà fait une demande avec l'id "+str(idMTatt)+".\n"+pascontent+"\n"+contact)
        else : await bot.say("Vous êtes déjà relié au bot avec l'id "+str(idMTold)+".\n"+pascontent+"\n"+contact)
    except Exception as exc :
        print('-'*50);print(format_exc());print('-'*50)
        await bot.say(erreur+" [Erreur ASK]")

@bot.command(pass_context=True)
async def verify(ctx,user2: Member = None,idMT2: int = 0):
    """Lie le compte d'un utilisateur au bot (ajoute son id MT dans le canal Info-bot) """
    try: 
        user=ctx.message.author
        idMT=(await FindUser(user,canalEnAttente))
        if user2 != None and ("Admin" or "Modo") in [y.name for y in user.roles] :  ##Si admin ou modo ...
            #await bot.add_roles(user, get(user2.server.roles, name = "Vérifié") )
            await bot.send_message(canalInfoBot, str(user2.mention)+ " " + str(idMT2))
    
            role = roleScore(GetMTScore(idMT2))
            servRole = get(user2.server.roles, name = role)
            
            await bot.add_roles(user2, servRole)
            await bot.send_message(canalGeneral,"Un Administrateur/Modérateur a relié "+str(user2)+" au compte Mathraining d'id "+str(idMT2)+" ! Il obtient le rôle `"+role+"`. :clap:")
        elif idMT!=0 :                            ##Sinon ignore les autres arguments ...
            Connexion()

            driver.get("https://www.mathraining.be/discussions/new?qui="+str(idMT))
            
            if driver.find_element_by_xpath("//*[contains(@id, 'normal')]").text[:-20] == 'Oui' :##Si c'est 'Oui', c'est bon ! (En fait prend le premier avec un id avec 'normal')
                msg="Vos comptes Discord et Mathraining sont désormais reliés !"
                m = driver.find_element_by_id("MathInput")
                m.clear();m.send_keys(msg)
                driver.find_element_by_name("commit").click()
                Deconnexion()
                
                await bot.send_message(canalInfoBot, str(user.mention)+ " " + str(idMT))
                
                async for message in bot.logs_from(canalEnAttente, limit=1000):
                    msg = message.content.split()
                    e1,e2=[2,3][user.mention[2]=='!'],[2,3][msg[0][2]=='!']
                    if msg[0][e2:-1] == user.mention[e1:-1]: 
                        await bot.delete_message(message);break
                        
                role = roleScore(GetMTScore(idMT))
                servRole = get(user.server.roles, name = role )
                
                await bot.add_roles(user, servRole)
                await bot.say("La demande de lien a été acceptée par le compte Mathraining ! Vous obtenez le rôle `"+role+"`! :clap:")
            
            else :
                msg="Les comptes Discord et Mathraining en question ne seront pas reliés."
                m = driver.find_element_by_id("MathInput")
                m.clear();m.send_keys(msg)
                driver.find_element_by_name("commit").click()
                Deconnexion()
                await bot.say("La demande de lien a été refusée par le compte Mathraining.")
            
        elif (await FindUser(user))!=0 :
            await bot.say("Vous êtes déjà lié avec l'id "+str(await FindUser(user))+".")
        else :
            await bot.say("Vous n'avez fait aucune demande pour lier vos comptes Discord et Mathraining.")
        
    except Exception as exc :
        print('-'*50);print(format_exc());print('-'*50)
        await bot.say(erreur+" [Erreur VERIFY]")

@bot.command(pass_context=True)
async def update(ctx,user: Member = None):
    '''Pour mettre à jour son/ses roles'''
    try:
        if user == None : user = ctx.message.author
        idMT=(await FindUser(user))

        if idMT != 0:
            role = roleScore(GetMTScore(idMT))
            if role == -1: await bot.say("Une erreur a été rencontrée, contactez un admin [Erreur ROLESCORE]"); return #Si le site change de façon de fonctionner
            
            roles=user.roles    
            #print(role)
            for roleMembre in roles: #On récupère le (ou les) rôle(s) MT que l'utilisateur a.
                #print(roleMembre.name)
                if roleMembre.name in NomsRoles and roleMembre.name != role :
                    await bot.remove_roles(user, roleMembre)
                    
            roles=user.roles
            #print([r.name for r in roles])
            if role not in [r.name for r in roles] :
                await bot.add_roles(user, get(user.server.roles, name = role ))
                if user == ctx.message.author : await bot.say("Bravo, vous obtenez le rôle `"+role+"`! :clap:")
                else : await bot.say(str(user)+" obtient désormais le rôle `"+role+"`! :clap:")
            else :
                await bot.say("Déjà à jour !")
        else:
            await bot.say(nonRattachee)
    except Exception as exc :
        print('-'*50);print(format_exc());print('-'*50)
        await bot.say(erreur+" [Erreur UPDATE]")

@bot.command(pass_context=True)
async def info(ctx,user = None):
    """Affiche les stats d'un utilisateur lié"""
    try:
        try : idMT = int(user)
        except : 
            if user == None : user = ctx.message.author
            else : user = commands.MemberConverter(ctx,user).convert()
            idMT = (await FindUser(user))
        if idMT != 0:
            url="http://www.mathraining.be/users/"+str(idMT)
            soup = BeautifulSoup(requests.get(url).text, "lxml")
            htmlscore = soup.find_all('p', limit = 1) #on recupere le bout de code avec le score 
            #(attrs={"style":u"font-size:24px; margin-top:(20 si score !=0 60 sinon)px;"})
            nameuser = soup.find_all('h1', limit = 1)
            avancement = soup.find_all('div', attrs={"class":u"progress-bar"})

            #print(avancement)
            #print(nameuser, nameuser[0].getText())
            #print(htmlscore[0].getText())

            username = ''.join(nameuser[0].getText().split('-')[:-1])[:-1]
            rank = (nameuser[0].getText().split('-')[-1])[1:-1]
            stats = ["Combinatoire :", "Géométrie :", "Théorie des nombres :", "Algèbre :", "Équations Fonctionnelles :", "Inégalités :"]

            #print("$"+avancement[1].getText()+"$")

            if avancement[1].getText() == "\n":
                nbpbsolved = "0/153"
            else:
                nbpbsolved = avancement[1].getText()[1:-1]
            embed = Embed(title=username + " - " + rank, url=url, description="Membre n°"+str(idMT), color=colors[rank])
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
    except Exception as exc :
        print('-'*50);print(format_exc());print('-'*50)
        await bot.say(erreur+" [Erreur INFO]")

@bot.command()
async def corrections(switch=""):
    """Affiche la liste des correcteurs et leurs nombres de corrections"""
    try:
        soup = BeautifulSoup(requests.get("http://www.mathraining.be/correctors").text, "lxml")
        corrections = soup.find_all('td', attrs={"style":u"text-align:center;"})
        correcteurs = soup.find_all('a',{"href":compile(r"/users/.*")})
        embed = Embed(title="Corrections", color=0xFF4400)

        for loop in range(0, len(corrections), 2):
            msg,msg2 = "",""
            if corrections[loop+1].getText() != "0" or switch == "all":
                msg = correcteurs[loop//2].getText()
                msg2 = corrections[loop].getText() + " corrections dont " +corrections[loop+1].getText() + " les deux dernières semaines.\n"
                embed.add_field(name=msg, value=msg2, inline=False)
        await bot.say(embed=embed)
    except Exception as exc :
        print('-'*50);print(format_exc());print('-'*50)
        await bot.say(erreur+" [Erreur CORRECTIONS]")

@bot.command()
async def solved(user: Member, idpb: int):
    """Indique si le problème numéro numPb a été résolu par l'utilisateur"""
    try:
        idMT=(await FindUser(user))
        if idMT != 0:
            response = requests.get("http://mathraining.be/users/" + str(idMT)).text
            namepb = '#' + str(idpb)
            await bot.say("Problème"+[" non "," "][namepb in response]+"résolu par l'utilisateur.")
        else: await bot.say(nonRattachee)
    except Exception as exc :
        print('-'*50);print(format_exc());print('-'*50)
        await bot.say(erreur+" [Erreur SOLVED]")

@bot.command()
async def hi():
    await bot.say("Salut ! Comment vas-tu ?")
    
@bot.command(pass_context = True)
async def say(ctx,*args):
    if ("Admin" or "Modo") in [y.name for y in ctx.message.author.roles] :
        msg = ""
        for i in range(len(args)): msg += args[i]+" " #le dernier espace ne va pas être pris en compte sur discord. hm ...
        await bot.send_message(canalGeneral, msg)
    else : await bot.say(perms)
    
@bot.command()
async def compte(tuile: tuple = (-1,-1,-1,-1,-1,-1),trouver: int = -1,sols=1):
    try:
        if (tuile,trouver,sols) == ((-1,-1,-1,-1,-1,-1),-1,1) :
            resultat,tuiles = AnnexeCompteBon.compteBon()
            tirage="Tuiles : " + " ".join(map(str,tuiles)) +  "\nÀ trouver : " + str(resultat)
            embed = Embed( title = "Le compte est bon", color = 0xFF4400 )
            embed.add_field( name = "Tirage", value = tirage, inline = False )
        else:
            tuile2=[];tmp=tuile;i=1 #Tuile est en fait de la forme ('2',',','1','0',',','5',...)
            while ',' in tmp :
                while tmp[i]!=',' : i+=1
                tuile2+=[int(''.join(tmp[0:i]))];tmp=tmp[i+1:];i=0
            tuile2+=[int(''.join(tmp))] #Ne pas oublier le dernier nombre ...
            res=AnnexeCompteBon.Solve(trouver,tuile2,sols); msg = ''
            for s in res : msg+=s;msg+='\n'
            #print(msg)
            embed = Embed( title = "Le compte est bon", color = 0xFF4400 )
            if msg : embed.add_field( name = "Voici "+str(len(res))+" solution(s) choisie(s) au hasard :", value = msg, inline = False)
            else : embed.add_field( name = "Mince !", value = "Il n'y a pas de solution ...", inline = False)           
        await bot.say(embed=embed)
    except Exception as exc :
        print('-'*50);print(format_exc());print('-'*50)
        await bot.say(erreur+" [Erreur COMPTE]")
     
@bot.command()
async def lettres():
    try:
        tirage="Tuiles : " +Lettres()
        embed = Embed( title = "Le mot le plus long", color = 0xFF4400 )
        embed.add_field( name = "Tirage", value = tirage, inline = False)
        await bot.say(embed=embed)
    except Exception as exc :
        print('-'*50);print(format_exc());print('-'*50)
        await bot.say(erreur+" [Erreur LETTRES]")  
@bot.command()
async def citation():
    try:
        soup = BeautifulSoup(requests.get("http://math.furman.edu/~mwoodard/www/data.html").text, "lxml") #Penser à modifier la source soi-même ?
        bout = str(soup.find_all('p')[randint(0,756)]).replace("<br/>", "\n") 
        citation = (BeautifulSoup(bout, "lxml").getText()).split('\n')
        c=''
        for s in citation[1:-2] : c+=(s+'\n')
        c+=citation[-2]
        embed = Embed(title=citation[0], colour=0x964b00, description='_'+c+'_')
        embed.set_author(name="Citations Mathématiques")
        embed.set_footer(text=citation[-1])
        await bot.say(embed=embed)
    except Exception as exc :
        print('-'*50);print(format_exc());print('-'*50)
        await bot.say(erreur+" [Erreur CITATION]")

@bot.command(pass_context = True)
async def aops(ctx):
    try:
        driver = webdriver.Firefox(options=options,executable_path=r'B:\downloads\MT\geckodriver.exe')
        #driver = webdriver.PhantomJS(executable_path=r'B:\downloads\MT\PJS\bin\phantomjs.exe')
        #driver.set_window_position(-2000,0)
        #driver.set_window_size(2560, 1600)
        #driver.execute_script("document.body.style.zoom='250%'")
        #driver.execute_script("document.body.style.webkitTransform = 'scale(1.5)'")
        #driver.implicitly_wait(10)
        urlinit="https://artofproblemsolving.com/community/c13_contest_collections";url=urlinit
        msg = await bot.say("`Chargement en cours ...`")
        driver.get(url);await sleep(2)
        titres = [(i.text).split('\n')+['\u200b']*(2-len((i.text).split('\n'))) for i in driver.find_elements_by_class_name('cmty-category-cell-left') if i.text != '']
        titre=titres[0][0];titres=titres[1:];l=len(titres);k=0
        reactions=["🔙","◀","▶","1⃣","2⃣","3⃣","4⃣","5⃣","6⃣","7⃣","8⃣","9⃣","🔟","❌"]
        while l :
            embed = Embed(title=titre, colour=0x009fad)
            liens =[i.find_element_by_css_selector('a').get_attribute('href') for i in driver.find_elements_by_class_name('cmty-category-cell-heading.cmty-cat-cell-top-legit')]
            embed.set_footer(text="AoPS | Page "+str(k+1)+"/"+str((l-1)//10 +1)+" | Attendez que les réactions soient toutes présentes.")
            for i in range(k*10,k*10+min(10,len(titres)-k*10)) : embed.add_field(name=str(i+1)+'. '+titres[i][0],value=titres[i][1],inline=False)
            await bot.edit_message(msg,embed=embed)
            await bot.edit_message(msg,"`Veuillez faire une sélection :`")
            for r in reactions[:min(10,l-k*10)+3]+["❌"]*(10!=(l-k*10)) : await bot.add_reaction(msg,r)
            reac = await bot.wait_for_reaction(reactions,message=msg,user=ctx.message.author,timeout=60)
            if reac :
                await bot.edit_message(msg,"`Chargement en cours ...`")
                await bot.clear_reactions(msg)
                for i in range(min(10,len(titres)-k*10)+3) : 
                    if reac.reaction.emoji == "❌" :
                        await bot.edit_message(msg,"`La requête a été annulée.`")
                        await bot.clear_reactions(msg)
                        await bot.edit_message(msg,embed=Embed(title='AoPS | Terminé', colour=0x009fad))
                        driver.quit();return
                    if reac.reaction.emoji == reactions[1] and k!=0 :
                        k-=1;break
                    if reac.reaction.emoji == reactions[2] and k<((l-1)//10) :
                        k+=1;break  
                    if reac.reaction.emoji == reactions[i] and reac.reaction.emoji not in reactions[1:3] : 
                        if reac.reaction.emoji == reactions[0] :
                            if not url==urlinit : 
                                driver.back();url=driver.current_url
                            else : break
                        else : url = liens[k*10+i-3];driver.get(url)
                        await sleep(2)
                        last_height = driver.execute_script("return document.body.scrollHeight")
                        while True: #CHARGER LA PAGE ENTIEREMENT EN SCROLLANT !!
                            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                            await sleep(0.3);new_height = driver.execute_script("return document.body.scrollHeight")
                            if new_height == last_height: break
                            last_height = new_height
                        titres = [(i.text).split('\n')+['\u200b']*(2-len((i.text).split('\n'))) for i in driver.find_elements_by_class_name('cmty-category-cell-left') if i.text != '']
                        titre=titres[0][0];titres=titres[1:len(titres)-1*(url==urlinit)];l=len(titres);k=0 #Si url = urlinit on enlève le dernier pathologique
                        break
            else :
                await bot.edit_message(msg,"`Aucune réponse depuis une minute. La requête a été abandonnée.`")
                await bot.clear_reactions(msg)
                await bot.edit_message(msg,embed=Embed(title='AoPS | Terminé', colour=0x009fad))
                driver.quit();return
        driver.execute_script("window.scrollTo(0, 0);")
        #re.findall("\d+", 'Problem 10')
        #https://artofproblemsolving.com/community/c389682_2016_china_second_round_olympiad ??????
        #https://artofproblemsolving.com/community/c502938_2017_middle_european_mathematical_olympiad :(
        #https://artofproblemsolving.com/community/c930482_2005_dutch_mathematical_olympiad
        #https://artofproblemsolving.com/community/c681585_2018_imo
        DescsParties = [(lambda x : '\u200b' if x==[] else x[0].text)(i.find_elements_by_class_name('cmty-view-post-item-text')) for i in driver.find_elements_by_class_name('cmty-view-posts-item') if i.find_elements_by_class_name('cmty-view-post-poster') == []] 

        NumsParties = [(lambda x : '\u200b' if x==[] else x[0].text)(i.find_elements_by_class_name('cmty-view-post-item-label')) for i in driver.find_elements_by_class_name('cmty-view-posts-item') if i.find_elements_by_class_name('cmty-view-post-poster') == []]  
        #Nums = [(lambda x : '\u200b' if x==[] else x[0].text)(i.find_elements_by_class_name('cmty-view-post-item-label')) for i in driver.find_elements_by_class_name('cmty-view-posts-item') if i.find_elements_by_class_name('cmty-view-post-poster') != []]

        LesNums = [[(lambda x : '\u200b' if x==[] else findall("\d+",x[0].text)[0])(i.find_elements_by_class_name('cmty-view-post-item-label')),i.find_elements_by_class_name('cmty-view-post-poster') == []] for i in driver.find_elements_by_class_name('cmty-view-posts-item')]  #True ssi Partie
        LesNums = list(filter(lambda x: x != ['\u200b', False], LesNums))
 
        Probs = [i.find_elements_by_class_name('cmty-view-post-item-text')[0] for i in driver.find_elements_by_class_name('cmty-view-posts-item') if i.text != '' and i.find_elements_by_class_name('cmty-view-post-item-label') != [] and i.find_elements_by_class_name('cmty-view-post-poster') != []]
        #OtherProbs = [i.find_elements_by_class_name('cmty-view-post-item-text')[0] for i in driver.find_elements_by_class_name('cmty-view-posts-item') if i.text != '' and i.find_elements_by_class_name('cmty-view-post-item-label') == [] and i.find_elements_by_class_name('cmty-view-post-poster') != []]
        
        PartiesPos = [i for i in range(len(LesNums)) if LesNums[i][1] == True];PartiesPos+=[len(LesNums)]
        selec=["_","_","_"]
        reactions2=["0⃣","1⃣","2⃣","3⃣","4⃣","5⃣","6⃣","7⃣","8⃣","9⃣","✳","✅","❌"]
        prob=await bot.say("`Le problème apparaîtra ici.`")
        while reac.reaction.emoji != reactions2[-1] :
            embed = Embed(title=titre+" | Votre sélection actuelle : "+selec[0]+"-"+selec[1]+selec[2],colour=0x009fad)
            embed.set_footer(text="AoPS | Attendez que les réactions soient toutes présentes.")
            for i in range(len(NumsParties)) : 
                nbrs=''
                for j in range(1,PartiesPos[i+1]-PartiesPos[i]) : nbrs+=LesNums[PartiesPos[i]+j][0]+' - '
                embed.add_field(name="__"+str(i+1)+".__ `"+str(NumsParties[i])+"` _"+str(DescsParties[i])+"_",value=nbrs[:-3],inline=False) 
            await bot.edit_message(msg,embed=embed)
            await bot.edit_message(msg,"`Veuillez faire une sélection :`")
            for r in reactions2 : await bot.add_reaction(msg,r)
            reac = await bot.wait_for_reaction(reactions2,message=msg,user=ctx.message.author,timeout=5*60)
            if reac :
                await bot.edit_message(msg,"`Chargement en cours ...`")
                await bot.clear_reactions(msg)
                for i in range(len(reactions2)-1) :
                    if reac.reaction.emoji == reactions2[10] : selec=['_','_','_'];break
                    if reac.reaction.emoji == reactions2[11] and '_' not in selec : 
                        try :
                            img=BytesIO((Probs[PartiesPos[int(selec[0])-1]-int(selec[0])+int(selec[1]+selec[2])]).screenshot_as_png);img.name='problem.png'
                            #f = open('mt1.png', 'wb')
                            #f.write(Probs[5].screenshot_as_png)
                            #f.close()
                            await bot.delete_message(prob)
                            prob=await bot.send_file(ctx.message.channel, img)
                            break
                        except : bot.edit_message(prob,"`Sélection invalide !`")
                    if reac.reaction.emoji == reactions2[i] and '_' in selec and i<10 :
                        if selec[0] == '_' : selec[0] = str(i)
                        elif selec[1] == '_' : selec[1] = str(i)
                        else : selec[2] = str(i)
                        break           
            else :
                await bot.edit_message(msg,"`Aucune réponse depuis cinq minutes. La requête a été abandonnée.`")
                await bot.clear_reactions(msg)
                await bot.edit_message(msg,embed=Embed(title='AoPS | Terminé', colour=0x009fad))
                driver.quit();return
                   
        await bot.edit_message(msg,"`La requête a été terminée.`")
        await bot.clear_reactions(msg)
        await bot.edit_message(msg,embed=Embed(title='AoPS | Terminé', colour=0x009fad))
        driver.quit()
        
    except Exception as exc :
        await bot.edit_message(msg,"`Erreur ...`")
        print('-'*50);print(format_exc());print('-'*50)
        await bot.say(erreur+" [Erreur AOPS]")
        try : driver.quit()
        except : return

@bot.command(pass_context = True)
async def oops(ctx,*args):
    await bot.add_reaction(ctx.message,'😅')
    
@bot.command(pass_context = True)
async def trivial(ctx,*args):
    await bot.add_reaction(ctx.message,'😒')    
    
bot.remove_command('help')
@bot.command(pass_context = True)
async def help(ctx):
    try:
        embed = Embed(title="Mathraining bot", type="rich", description="Préfixe avant les commandes : &.", color=0x87CEEB)
        embed.add_field(name="ask idMathraining", value="Pour demander à rattacher votre compte Mathraining." +
        "\n idMathraining est le nombre dans l'url de votre page de profil sur le site.", inline=False)
        embed.add_field(name="verify", value="Pour valider le lien de votre compte Mathraining avec votre compte Discord.", inline=False)
        embed.add_field(name="update", value="Pour mettre à jour son rang.", inline=False)
        embed.add_field(name="info (utilisateur/idMathraining)", value="Donne le score et le rang Mathraining de l'utilisateur Discord ou Mathraining."
        +"\n Les mentions, les surnoms tout comme les id Mathraining fonctionnent.\n Par défaut prend la personne qui a envoyé la commande comme utilisateur.", inline=False)
        embed.add_field(name="corrections (all)", value="Affiche la liste des correcteurs (qui ont corrigé récemment ou pas avec \"all\") et leurs contributions.", inline=False)
        embed.add_field(name="solved utilisateur numPb", value="Indique si le problème numéro numPb a été résolu par l'utilisateur.", inline=False)
        embed.add_field(name="hi", value="Permet d'effectuer un ping avec le bot.", inline=False)
        embed.add_field(name="compte (a,b,c,d,e,f NbrSolutions)", value="Effectue un tirage si aucun argument n'est donné, résout le tirage sinon.", inline=False)
        embed.add_field(name="citation", value="Affiche une citation mathématique au hasard.\n Source : [Furman University, Mathematical Quotations Server](http://math.furman.edu/~mwoodard/mquot.html)", inline=False)
        embed.add_field(name="aops", value="Permet d'avoir accès aux problèmes AoPS et les afficher.", inline=False)
        embed.add_field(name="help", value="Affiche ce message en MP.", inline=False)

        await bot.send_message(ctx.message.author,embed=embed)
    except Exception as exc :
        print('-'*50);print(format_exc());print('-'*50)
        await bot.say("Une erreur a été rencontrée, peut-être avez-vous bloqué les messages privés, ce qui empêche le bot de communiquer avec vous. Contactez un Admin ou un Modérateur. [Erreur HELP]")

##Tâches d'arrière-plan

async def background_tasks_mt():
    global dernierResolu, user, problem, exo, point, debut #debut permet que les messages ne s'affichent pas 
                                            #si le bot se relance
    while True:
        
        #Chiffres remarquables
        
        changement = 0
        url = "http://www.mathraining.be/"
        req = requests.get(url)
        response = req.text #on récupère le code source de la page
        soup = BeautifulSoup(response, "lxml")
        info = soup.find_all('td',attrs={"class":u"left"})
        msg = ""
        if int(info[0].getText()) != user and int(info[0].getText())%100==0:
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
            print("Le bot vient juste d'être lancé")
        elif changement != 0:
            await bot.send_message(canalGeneral, msg)  

        #Résolutions récentes

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
                            await bot.send_message(canalResolutions, msg)   
                    level += 1
                    if level == 6:
                        break
        #print("fini")
        debut = 1
        await sleep(20)

#______________________________________________________________

#bot.loop.create_task(background_tasks_mt())
bot.run(token) #Token MT
