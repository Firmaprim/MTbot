from discord import *
from discord.ext import commands, tasks
from discord.utils import get

import datetime, pytz
from email.utils import parsedate_to_datetime

import aiohttp

from bs4 import *
from asyncio import *

from re import compile

from random import randint

import AnnexePendu
import AnnexeCompteBon
import AnnexeCompare
import AopsCore

from traceback import format_exc
from yaml import safe_load

intents = Intents.default()
intents.members = True

description = 'Bot Mathraining.'
bot = commands.Bot(command_prefix='&', description='Bot Mathraining, merci aux génialissimes créateurs !',intents=intents)

#____________________CONSTANTES_______________________________

with open('options.yml', 'r') as options_file : options = safe_load(options_file)

NomsRoles = ["Grand Maitre", "Maitre", "Expert", "Chevronné", "Expérimenté", "Qualifié", "Compétent", "Initié", "Débutant", "Novice"]

colors = {'Novice' : 0x888888, 'Débutant' : 0x08D508, 'Débutante' : 0x08D508, 'Initié' : 0x008800, 'Initiée' : 0x008800,
          'Compétent' : 0x00BBEE, 'Compétente' : 0x00BBEE, 'Qualifié' : 0x0033FF, 'Qualifiée' : 0x0033FF, 'Expérimenté' : 0xDD77FF,
          'Expérimentée' : 0xDD77FF, 'Chevronné' : 0xA000A0, 'Chevronnée' : 0xA000A0, 'Expert' : 0xFFA000, 'Experte' : 0xFFA000,
          'Maître' : 0xFF4400, 'Grand Maître' : 0xCC0000}

msghelp = "\nTaper la commande `&help` pour plus d'informations."

errmsg ="Une erreur a été rencontrée, contactez un Admin ou un Modérateur."
perms="Vous n'avez pas les permissions pour effectuer cette commande."

##_________________Fonctions_Annexes____________________

async def GetMTScore(idMT: int) :
    async with aclient.get(f"https://www.mathraining.be/users/{idMT}") as response: text = await response.text()
    soup = BeautifulSoup(text,"lxml")
    try : 
        htmlscore = soup.find_all('td', limit = 5)
        if htmlscore != [] : return int(htmlscore[4].getText().strip())
        else : return 2 #Identifiant non attribué
    except : 
        if htmlscore[1].getText().strip() == "Administrateur" : return 1 #Administrateur
        else : return 0 #Personne n'ayant aucun point

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
    
async def GetDiscordUser(ctx,user) :
    user1 = None
    if user.isdigit(): user1 = bot.get_user(id=int(user))
    if not user1:
        r = compile(r"<@(!|)([0-9]+)>").search(user)
        if r: user1 = bot.get_user(id=int(r.group(2)))
    if not user1:
        r = compile(r"^([^#]+)#([0-9]{4})$").search(user)
        if r: user1 = get(serveur.members, name=r.group(1), discriminator=r.group(2))
    if not user1:
        user1 = get(serveur.members, nick=user)
    if not user1:
        user1 = get(serveur.members, name=user)
    return user1
    
def FindUser(user: Member, en_attente=False) :
    return users_links.get(int(user.id), 0) if not en_attente else users_links_tmp.get(int(user.id), 0)

async def FindMTUser(user_str : str, ctx, print_msgs = True):
    if user_str.isdigit() and len(user_str) <= 4:
        return int(user_str)
    else:
        user = await GetDiscordUser(ctx, user_str)
        if not user and print_msgs:
            await ctx.channel.send(f"**{user_str}**: Utilisateur introuvable."+msghelp, allowed_mentions=AllowedMentions(users=False))
            return 0
        id = FindUser(user)
        if not id and print_msgs:
            await ctx.channel.send(f"L'utilisateur {user.mention} n'est pas rattaché à un compte Mathraining."+msghelp, allowed_mentions=AllowedMentions(users=False))
            return 0
        return id

class MTid(commands.Converter):
    async def convert(self, ctx, user_str):
        id = await FindMTUser(user_str or str(ctx.author.id), ctx)
        if id: return id
        else: raise Exception # on quitte la commande
    async def me(ctx):
        id = await FindMTUser(str(ctx.author.id), ctx)
        if id: return id
        else: raise Exception

def FindMT(idMT: int, en_attente=False) :
    idMT = int(idMT)
    for discord, mt in (users_links if not en_attente else users_links_tmp).items():
        if idMT == mt: return discord
    return 0

regex_auth_token = compile(r'<input type="hidden" name="authenticity_token" value="([A-Za-z0-9+/=]+)" />')

async def mt_connexion(aclient):
    try:
        resp = await aclient.get('https://www.mathraining.be/')
        authenticity_token = regex_auth_token.search(await resp.text()).group(1)
        await aclient.post('https://www.mathraining.be/sessions', data = {
            'utf8': "✓",
            'authenticity_token': authenticity_token,
            'session[email]': options['user'],
            'session[password]': options['password'],
            'session[remember_me]': "0",
        })
    except (IndexError, AttributeError): pass # déjà connecté
          
async def mt_send_mp(idMT, msg):
    resp = await aclient.get(f'https://www.mathraining.be/discussions/new')
    authenticity_token = regex_auth_token.search(await resp.text()).group(1)
    req = await aclient.post('https://www.mathraining.be/discussions', data = {
        'utf8': "✓",
        'authenticity_token': authenticity_token,
        'destinataire': f"{idMT}",
        'content': msg,
    }, allow_redirects=False)
    if req.status != 302:
        raise RuntimeError("Impossible d'envoyer un message privé sur mathraining. Vérifiez que le login/mot de passe sont corrects.")

async def erreur(e,ctx=None,switch=1) :
    err="- "+"[Erreur "+e+'] '+'-'*50+" [Erreur "+e+']'+" -"+'\n'+format_exc()+"- "+"[Erreur "+e+'] '+'-'*50+" [Erreur "+e+']'+" -";print(err)
    err="```diff\n"+err+"```"
    await canalLogsBot.send(err)
    if ctx:
        await ctx.send("**[Erreur "+e+']** '+"`"+errmsg+"`"+" **[Erreur "+e+']**')
        e=Embed()
        if switch == 2 : e.set_image(url=options['AdrienFail'])
        else : e.set_image(url=options['FirmaFail'])
        await ctx.send(embed=e)

import functools
def log_errors(name, switch=1): # use after @bot.command()
    def wrapper(func):
        @functools.wraps(func)
        async def f(*args, **kwargs):
            try: return await func(*args, **kwargs)
            except Exception as exc:
                if type(exc) != Exception:
                    if len(args) > 0 and type(args[0]) == commands.Context:
                        await erreur(name, args[0], switch=switch)
                    else:
                        await erreur(name, switch=switch)
        return f
    return wrapper

##_________________________EVENT_______________________________________

@bot.event
async def on_ready():
    print('------')
    print('Connecté sous')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    global serveur
    global canalInfoBot, canalEnAttente, canalGeneral, canalResolutions, canalLogsBot, canalRoles, canalEntreesSorties
    global PenduRunner
    global users_links, users_links_tmp, msg_ids_links, msg_ids_links_tmp
    global solvedpbs_ping_settings
    global aclient

    print("Chargement ...", end="\r")

    users_links, users_links_tmp, msg_ids_links, msg_ids_links_tmp = {}, {}, {}, {}

    aclient = aiohttp.ClientSession()

    PenduRunner = AnnexePendu.Pendu()

    serveur = bot.get_guild(options['IdServeur'])
    canalInfoBot = serveur.get_channel(options['IdInfoBot'])
    canalEnAttente = serveur.get_channel(options['IdEnAttente'])
    canalGeneral = serveur.get_channel(options['IdGeneral'])
    canalResolutions = serveur.get_channel(options['IdResolutions'])
    canalLogsBot = serveur.get_channel(options['IdLogsBot'])
    canalEntreesSorties = serveur.get_channel(options['IdEntreesSorties'])

    async for message in canalInfoBot.history(limit=None):
        user, id_mt = message.content.split(" ")
        user, id_mt = int(user.replace("<@", "").replace(">", "").replace("!", "")), int(id_mt)
        users_links[user] = id_mt
        msg_ids_links[int(message.id)] = user
    async for message in canalEnAttente.history(limit=None):
        user, id_mt = message.content.split(" ")
        user, id_mt = int(user.replace("<@", "").replace(">", "").replace("!", "")), int(id_mt)
        users_links_tmp[user] = id_mt
        msg_ids_links_tmp[int(message.id)] = user

    canalRoles = serveur.get_channel(options['IdRoles'])
    try:
        msg = await canalRoles.fetch_message(options['IdMessageRoles'])
        for r in msg.reactions:
            if r.emoji.name == 'ping':
                thereaction = r
                break
        solvedpbs_ping_settings = [i.id async for i in thereaction.users()]
    except errors.NotFound:
        solvedpbs_ping_settings = []
        await canalLogsBot.send(f":warning: Impossible de charger les paramètres de ping des {canalResolutions.mention}. Utilisez `&resolutions_setup` pour corriger le problème.")
    
    task.start()

    print("Bot prêt !")
    
    await bot.change_presence(activity=Game(name="Mathraining | &help"))

@bot.event
async def on_raw_reaction_add(payload):
    if int(payload.message_id) == int(options['IdMessageRoles']):
        if payload.emoji.name == 'ping':
            solvedpbs_ping_settings.append(payload.user_id)
@bot.event
async def on_raw_reaction_remove(payload):
    if int(payload.message_id) == int(options['IdMessageRoles']):
        if payload.emoji.name == 'ping':
            try: solvedpbs_ping_settings.remove(payload.user_id)
            except ValueError: pass

@bot.event
async def on_member_update(before, after):
    role_verifie = get(serveur.roles, name = "Vérifié")
    if role_verifie not in before.roles and role_verifie in after.roles:
        fmt = 'Bienvenue '+ after.mention + " ! Pense à lier ton compte Mathraining avec la commande `&ask`. \n" + \
        "Si tu as des problèmes avec cette commande tape `&help` pour en savoir plus sur le bot ou va faire un tour dans <#726480900644143204>. :wink:" 
        await canalEntreesSorties.send(fmt)

@bot.event
async def on_member_remove(member):
    await canalEntreesSorties.send(f"**{member}** a quitté le serveur.")

@bot.event
async def on_command_error(ctx, error):
    if type(error) == commands.errors.MemberNotFound:
        await ctx.channel.send(f"**{error.argument}**: Utilisateur introuvable."+msghelp, allowed_mentions=AllowedMentions(users=False))
    elif type(error) != Exception and type(error) != commands.errors.ConversionError:
        raise error

@bot.event
async def on_raw_message_delete(payload):
    if payload.channel_id == canalInfoBot.id:
        del users_links[msg_ids_links[int(payload.message_id)]]
        del msg_ids_links[int(payload.message_id)]
    if payload.channel_id == canalEnAttente.id:
        del users_links_tmp[msg_ids_links_tmp[int(payload.message_id)]]
        del msg_ids_links_tmp[int(payload.message_id)]

@bot.event
async def on_message(message):
    #_____COMMANDE POUR AFFICHER LES PROBLEMES_____    
    
    if message.channel == canalInfoBot:
        user, id_mt = message.content.split(" ")
        user, id_mt = int(user.replace("<@", "").replace(">", "").replace("!", "")), int(id_mt)
        users_links[user] = id_mt
        msg_ids_links[int(message.id)] = user
    if message.channel == canalEnAttente:
        user, id_mt = message.content.split(" ")
        user, id_mt = int(user.replace("<@", "").replace(">", "").replace("!", "")), int(id_mt)
        users_links_tmp[user] = id_mt
        msg_ids_links_tmp[int(message.id)] = user
        
    if '#' in message.content and message.author != bot.user:
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
                aEnvoyer = "Problème " + str(numeroPb) + " : https://www.mathraining.be/problems/" + str(urlPb)
                await message.channel.send(aEnvoyer )
    await bot.process_commands(message)

##_____________________COMMANDES___________________________________

@bot.command(pass_context=True)
@log_errors("ASK")
async def ask(ctx,idMTnew: int):
    '''Pour pouvoir utiliser le bot: ask @utilisateur idMathraining
    (idMathraining est le nombre dans l'url de votre page de profil sur le site)'''
    pascontent="Nicolas ne va pas être content si vous vous êtes fait un autre compte !! :sweat_smile:"
    contact="Contactez un Admin ou un Modo si vous souhaitez changer de compte."
    user=ctx.message.author

    msay=await ctx.send("`Chargement en cours ...`")
    idMTold, idMTatt = FindUser(user), FindUser(user, True)
    if idMTold == 0 and idMTatt == 0 :  
        Score=await GetMTScore(idMTnew)
        UserId,UserIdatt = FindMT(idMTnew), FindMT(idMTnew, True)
        if UserId != 0 : await msay.edit(content="Ce compte Mathraining appartient déjà à "+str(bot.get_user(UserId))+" !")
        elif UserIdatt != 0: await msay.edit(content="Ce compte Mathraining a déjà été demandé à être relié par "+str(bot.get_user(UserIdatt))+" !")
        elif Score >= 5000 or Score == 1 : await msay.edit(content="Le compte Mathraining renseigné est au moins Maître ou Administrateur, il faut demander à un Admin/Modo du serveur de vous relier !")
        elif Score == 2 : await msay.edit(content="Le compte Mathraining renseigné n'existe pas !")
        else :
            msg="Bonjour !  :-)\n\n Vous avez bien demandé à relier votre compte mathraining avec le compte Discord [b]"+str(user)+"[/b] sur le [url=https://www.mathraining.be/subjects/365?q=0]serveur Mathraining[/url] ?\n Répondez [b]\"Oui\"[/b] (sans aucun ajout) à ce message pour confirmer votre demande, sinon par défaut vous ne serez pas relié. \n Vous devez ensuite taper la commande [b]&verify[/b] sur Discord pour finaliser la demande.\n\n [b]Seul le dernier message de cette conversation sera lu pour confirmer votre demande.[/b] \n[i][u]NB[/u] : Il s'agit d'un message automatique. N'espérez pas communiquer avec ce compte Mathraining.\n[/i]"
            await mt_connexion(aclient)
            await mt_send_mp(idMTnew, msg)
            await canalEnAttente.send(str(user.mention)+ " " + str(idMTnew))
            await msay.edit(content="Vous venez de recevoir un message privé sur le site. Suivez les instructions demandées.") 
    elif idMTold == idMTnew and idMTold != 0 : await msay.edit(content="Vous êtes déjà relié au bot avec le même id !")
    elif idMTatt == idMTnew and idMTatt !=0 : await msay.edit(content="Vous avez déjà fait une demande avec le même id !")
    elif idMTatt != idMTnew and idMTold ==0 : await msay.edit(content="Vous avez déjà fait une demande avec l'id "+str(idMTatt)+".\n"+pascontent+"\n"+contact)
    else : await msay.edit(content="Vous êtes déjà relié au bot avec l'id "+str(idMTold)+".\n"+pascontent+"\n"+contact)

@bot.command(pass_context=True)
@log_errors("VERIFY")
async def verify(ctx,user2: Member = None,idMT2: int = 0):
    """Lie le compte d'un utilisateur au bot (ajoute son id MT dans le canal Info-bot) """
    user=ctx.message.author
    idMT = FindUser(user, True)
    msay = await ctx.send("`Chargement en cours ...`")
    
    if user2 != None and ("Admin" or "Modo") in [y.name for y in user.roles] :  ##Si admin ou modo ...
        #await bot.add_roles(user, get(user2.server.roles, name = "Vérifié") )
        if FindUser(user2) == 0 :
            await canalInfoBot.send(str(user2.mention)+ " " + str(idMT2))
    
            role = roleScore(await GetMTScore(idMT2))
            servRole = get(serveur.roles, name = role)
            await user2.add_roles(servRole)
            
            await canalGeneral.send(f"Un Administrateur/Modérateur a relié {user2} au compte Mathraining d'id {idMT2} ! Il obtient le rôle {servRole.mention}. :clap:", allowed_mentions=AllowedMentions(roles=False))
            await msay.delete()
        else : await msay.edit(content=str(user2)+ " est déjà lié avec l'id "+str(FindUser(user2))+".")
        
    elif idMT!=0 :                            ##Sinon ignore les autres arguments ...

        await mt_connexion(aclient)

        resp = await aclient.get(f'https://www.mathraining.be/discussions/new?qui={idMT}')
        soup = BeautifulSoup(await resp.text(), features='lxml')
        try: verified = soup.select_one("#all-messages > div > div:last-child").text.strip().lower().startswith("oui")
        except: verified = False

        if verified:
            msg="Vos comptes Discord et Mathraining sont désormais reliés !"
            await mt_send_mp(idMT, msg)

            await canalInfoBot.send(str(user.mention)+ " " + str(idMT))

            async for message in canalEnAttente.history(limit=1000):
                msg = message.content.split()
                e1,e2=[2,3][user.mention[2]=='!'],[2,3][msg[0][2]=='!']
                if msg[0][e2:-1] == user.mention[e1:-1]: 
                    await message.delete();break

            role = roleScore(await GetMTScore(idMT))
            servRole = get(serveur.roles, name = role)
            await user.add_roles(servRole)
            
            await msay.edit(content=f"La demande de lien a été acceptée par le compte Mathraining ! Vous obtenez le rôle {servRole.mention}! :clap:", allowed_mentions=AllowedMentions(roles=False))
        else :
            msg="Les comptes Discord et Mathraining en question ne seront pas reliés."
            await mt_send_mp(idMT, msg)

            await msay.edit(content="La demande de lien a été refusée par le compte Mathraining.")
        
    elif FindUser(user) != 0 : await msay.edit(content="Vous êtes déjà lié avec l'id "+str(FindUser(user))+".")
    else : await msay.edit(content="Vous n'avez fait aucune demande pour lier vos comptes Discord et Mathraining.")

@bot.command(pass_context=True)
@log_errors("UPDATE")
async def update(ctx, user: Member = None):
    '''Pour mettre à jour son/ses roles'''
    if not user: user = ctx.author
    idMT = await FindMTUser(str(user.id), ctx)

    if idMT != 0:
        role = roleScore(await GetMTScore(idMT))
        if role == -1: await erreur('ROLESCORE',ctx); return 
        
        roles=user.roles
        for roleMembre in roles:
            if roleMembre.name in NomsRoles and roleMembre.name != role : await user.remove_roles(roleMembre)
        
        if role not in [r.name for r in roles] :
            role_to_add = get(serveur.roles, name = role)
            roles=user.roles; await user.add_roles(role_to_add)
            if user == ctx.message.author : await ctx.send(f"Bravo, vous obtenez le rôle {role_to_add.mention}! :clap:", allowed_mentions=AllowedMentions(roles=False))
            else : await ctx.send(str(user)+f" obtient désormais le rôle {role_to_add.mention}! :clap:", allowed_mentions=AllowedMentions(roles=False))
        else : await ctx.send("Déjà à jour !")

@bot.command(pass_context=True)
@log_errors("INFO")
async def info(ctx, idMT: MTid = None):
    """Affiche les stats d'un utilisateur lié"""
    if not idMT:
        idMT = await MTid.me(ctx)

    url="https://www.mathraining.be/users/"+str(idMT)
    async with aclient.get(url) as response: text = await response.text()
    soup = BeautifulSoup(text, "lxml")

    Infos=list(filter(None,[i.getText().strip() for i in soup.find_all('td', limit = 39)]))
    if len(Infos) == 3:
        country = soup.select_one("td img")['src'].split('/')[-1].split('-')[0]
        embed = Embed(title=f"{Infos[0]} - {Infos[1]} :flag_{country}:", url=url, description="Membre n°"+str(idMT))
        await ctx.send(embed=embed);return
    elif len(Infos) < 3:
        await ctx.send(content="Le compte Mathraining renseigné n'existe pas !");return

    country = soup.select_one("td img")['src'].split('/')[-1].split('-')[0]

    embed = Embed(title=f"{Infos[0]} - {Infos[1]} :flag_{country}:", url=url, description="Membre n°"+str(idMT)+3*' '+"Rang : "+Infos[6]+"  Top  "+Infos[8]+(7-len(Infos[6]+Infos[8]))*' ' +" <:gold:836978754454028338> : "+Infos[9]+" <:silver:836978754433319002> : "+Infos[10]+" <:bronze:836978754467135519> : "+Infos[11]+" <:mh:836978314387259442> : "+Infos[12], color=colors[Infos[1]])
    embed.add_field(name="Score : ", value=Infos[4], inline=True)
    embed.add_field(name="Exercices résolus : ", value=''.join(Infos[14].split()), inline=True)
    embed.add_field(name="Problèmes résolus : ", value=''.join(Infos[16].split()), inline=True)
    for i in range(6): embed.add_field(name=Infos[17+2*i]+' :', value=Infos[18+2*i], inline=True)

    await ctx.send(embed=embed)

@bot.command()
@log_errors("COMPARE")
async def compare(ctx, id1: MTid, id2: MTid = None):
    if not id2:
        id1, id2 = await MTid.me(ctx), id1

    if id1 == id2 and id1: await ctx.channel.send(f"Pourquoi se comparer avec soi même ?")
    elif id1 and id2 : await AnnexeCompare.make_graph(ctx, id1, id2, aclient)

@bot.command()
@log_errors("CORRECTIONS")
async def corrections(ctx,switch=""):
    """Affiche la liste des correcteurs et leurs nombres de corrections"""
    async with aclient.get("https://www.mathraining.be/correctors") as response: text = await response.text()
    soup = BeautifulSoup(text, "lxml")
    corrections = soup.find_all('td', attrs={"style":u"text-align:center;"})
    correcteurs = soup.find_all('a',{"href":compile(r"/users/.*")})[30:]
    msg=''
    for loop in range(0, len(corrections),2):
        if corrections[loop+1].getText() != "0" or switch == "all":
            n=len(correcteurs[loop//2].getText())
            m=len(corrections[loop].getText())
            msg+='**'+correcteurs[loop//2].getText().strip()+' :** '+(30-n)*' '+corrections[loop].getText() +(7-m)*" " +corrections[loop+1].getText() + "\n"
    embed = Embed(title="Corrections ( ... corrections dont ... les deux dernières semaines) : ", color=0xFF4400,description = msg[0:2047])
    #Petit bug sur les espaces que j'arrive pas à gérer ... + Mettre de plus gros espaces pour économiser les caractères
    #cf. https://emptycharacter.com/ (en fait je crois qu'il y a pas plus gros ...)
    await ctx.send(embed=embed)

@bot.command()
@log_errors("SOLVED")
async def solved(ctx, idMT: MTid, idpb: int):
    """Indique si le problème numéro numPb a été résolu par l'utilisateur"""
    async with aclient.get(f"https://www.mathraining.be/users/{idMT}") as resp : response = await resp.text()
    namepb = '#' + str(idpb)
    await ctx.send("Problème"+[" non "," "][namepb in response]+"résolu par l'utilisateur.")

@bot.command()
async def hi(ctx):
    await ctx.send("Salut ! Comment vas-tu ?")
    
@bot.command(pass_context = True)
async def say(ctx, *, arg):
    if ("Admin" or "Modo") in [y.name for y in serveur.get_member(ctx.message.author.id).roles] :
        await canalGeneral.send(arg)
    else : await ctx.send(perms)
    
@bot.command()
@log_errors("COMPTE")
async def compte(ctx, tuile: tuple = (-1,-1,-1,-1,-1,-1),trouver: int = -1,sols=1):
    if (tuile,trouver,sols) == ((-1,-1,-1,-1,-1,-1),-1,1) :
        resultat,tuiles = AnnexeCompteBon.compteBon()
        tirage="Tuiles : " + " ".join(map(str,tuiles)) +  "\nÀ trouver : " + str(resultat)
        embed = Embed( title = "Le compte est bon", color = 0xFF4400 )
        embed.add_field( name = "Tirage", value = tirage, inline = False )
    else:
        embed = Embed( title = "Le compte est bon", color = 0xFF4400 )
        tuile2 = list(map(int, "".join(tuile).split(",")))
        if len(tuile2)==6 :
            res=AnnexeCompteBon.Solve(trouver,tuile2,sols); msg = ''
            for s in res : msg+=s;msg+='\n'
            if msg : embed.add_field( name = "Voici "+str(len(res))+" solution(s) choisie(s) au hasard :", value = msg, inline = False)
            else : embed.add_field( name = "Mince !", value = "Il n'y a pas de solution ...", inline = False)    
        else : embed.add_field( name = "Mince !", value = "Il n'y a pas le bon nombre de tuiles ...", inline = False)    
    await ctx.send(embed=embed)
     
@bot.command()
@log_errors("LETTRES")
async def lettres(ctx):
    tirage="Tuiles : " + " ".join(AnnexeCompteBon.Lettres())
    embed = Embed( title = "Le mot le plus long", color = 0xFF4400 )
    embed.add_field( name = "Tirage", value = tirage, inline = False)
    await ctx.send(embed=embed)
          
@bot.command()
@log_errors("PENDU", 2)
async def pendu(ctx, tuile: str = ''):
    await AnnexePendu.pendu(ctx, tuile, PenduRunner)
    
@bot.command()
@log_errors("CITATION")
async def citation(ctx):
    async with aclient.get("http://math.furman.edu/~mwoodard/www/data.html") as response: text = await response.text()
    soup = BeautifulSoup(text, "lxml") #Penser à modifier la source soi-même ?
    bout = str(soup.find_all('p')[randint(0,756)]).replace("<br/>", "\n") 
    citation = (BeautifulSoup(bout, "lxml").getText()).split('\n')
    c=''
    for s in citation[1:-2] : c+=(s+'\n')
    c+=citation[-2]
    embed = Embed(title=citation[0], colour=0x964b00, description='_'+c+'_')
    embed.set_author(name="Citations Mathématiques")
    embed.set_footer(text=citation[-1])
    await ctx.send(embed=embed)

@bot.command(pass_context = True)
async def aops(ctx):
    try: await AopsCore.aopscore(bot,ctx)
    except Exception as exc : 
        await erreur('AOPS',ctx)
        try : driver.quit()
        except : return

@bot.command(pass_context = True)
async def oops(ctx):
    await ctx.message.add_reaction('😅')
    
@bot.command(pass_context = True)
async def trivial(ctx):
    await ctx.message.add_reaction('😒')
    
@bot.command(pass_context = True)
async def makeloose(ctx,user:Member = None):
    try :
        author = ctx.message.author
        await (ctx.message).delete()
        if not author == user : await ctx.send(str(user.mention)+" _a perdu ..._")
        else : await ctx.send(str(user.mention)+" _a perdu tout seul ..._")
        await user.send("_42_")
    except :
        try : await (ctx.message).delete();await ctx.send('<:blurryeyes:622399161240649751>')
        except : await ctx.send('<:blurryeyes:622399161240649751>')
    
bot.remove_command('help')
@bot.command(pass_context = True)
@log_errors("HELP")
async def help(ctx):
    embed = Embed(title="Mathraining bot", type="rich", description="Préfixe avant les commandes : &. \n [Le code source est disponible.](https://github.com/Firmaprim/MTbot/)", color=0x87CEEB)
    embed.add_field(name="ask idMathraining", value="Pour demander à rattacher votre compte Mathraining." +
    "\n idMathraining est le nombre dans l'url de votre page de profil sur le site.", inline=False)
    embed.add_field(name="verify", value="Pour valider le lien de votre compte Mathraining avec votre compte Discord.", inline=False)
    embed.add_field(name="update", value="Pour mettre à jour son rang.", inline=False)
    embed.add_field(name="info (utilisateur/idMathraining)", value="Donne le score et le rang Mathraining de l'utilisateur Discord ou Mathraining."
    +"\n Les mentions, les surnoms tout comme les id Mathraining fonctionnent.\n Par défaut prend la personne qui a envoyé la commande comme utilisateur.", inline=False)
    embed.add_field(name="compare utilisateur1 (utilisateur2)", value="Pour se comparer avec un utilisateur, ou comparer deux utilisateurs.", inline=False)
    embed.add_field(name="corrections (all)", value="Affiche la liste des correcteurs (qui ont corrigé récemment ou pas avec \"all\") et leurs contributions.", inline=False)
    embed.add_field(name="solved utilisateur numPb", value="Indique si le problème numéro numPb a été résolu par l'utilisateur.", inline=False)
    embed.add_field(name="hi", value="Permet d'effectuer un ping avec le bot.", inline=False)
    embed.add_field(name="compte (a,b,c,d,e,f ÀTrouver NbrSolutions)", value="Effectue un tirage de chiffres si aucun argument n'est donné, résout le tirage sinon.", inline=False)
    embed.add_field(name="lettres", value="Effectue un tirage de lettres.", inline=False)
    embed.add_field(name="pendu", value="Pour jouer au pendu.", inline=False)
    embed.add_field(name="citation", value="Affiche une citation mathématique au hasard.\n Source : [Furman University, Mathematical Quotations Server](http://math.furman.edu/~mwoodard/mquot.html)", inline=False)
    embed.add_field(name="aops", value="Permet d'avoir accès aux problèmes AoPS et les afficher.", inline=False)
    embed.add_field(name="help", value="Affiche ce message en MP.", inline=False)

    try:
        await (ctx.message.author).send(embed=embed)
    except errors.Forbidden:
        await ctx.send("Impossible de vous envoyer l'aide. Peut-être avez-vous bloqué les messages privés, ce qui empêche le bot de communiquer avec vous.")

@bot.command()
async def resolutions_setup(ctx):
    if ctx.guild == serveur and "Admin" in (y.name for y in ctx.author.roles):
        ping_emoji = get(serveur.emojis, name="ping")
        if not ping_emoji:
            await ctx.send(f"Emoji ping introuvable")
            return
        try:
            msg = await canalRoles.send(f"Souhaitez-vous être ping pour les {canalResolutions.mention} ?")
            await msg.add_reaction(ping_emoji)
            await ctx.send(f"Mettez```IdMessageRoles: {msg.id}``` dans `options.yml` puis rédémarrez le bot.")
        except errors.Forbidden:
            await ctx.send(f"Erreur. Vérifiez que le bot a bien les permissions pour poster dans {canalRoles.mention}")


##Tâches d'arrière-plan

last_submission_date = None
statistiques = [0, 0, 0, 0]
nbRequetes = 0

@tasks.loop(seconds = 300)
@log_errors("TASK")
async def task():
    global last_submission_date, nbRequetes, statistiques

    # Chiffres remarquables
    response = await aclient.get("https://www.mathraining.be/")
    soup = BeautifulSoup(await response.text(), "lxml")

    taillePaquet = [100, 1000, 10000, 50000] # paliers utilisateurs; problèmes; exercices; points

    table = soup.find("table")
    for i, stat in enumerate(table.find_all("tr")):
        nombre = int("".join(stat.find("td").text.split()))

        if nombre//taillePaquet[i] > statistiques[i]:
            if statistiques[i] == 0: # pour éviter de spam au lancement du bot
                statistiques[i] = nombre//taillePaquet[i]
            else:
                statistiques[i] = nombre//taillePaquet[i]
                if i == 0 : message = f"Oh ! Il y a maintenant {(nombre//taillePaquet[i])*taillePaquet[i]} utilisateurs sur Mathraining ! 🥳"
                elif i == 1 : message = f"Oh ! Il y a maintenant {(nombre//taillePaquet[i])*taillePaquet[i]} problèmes résolus ! 🥳"
                elif i == 2 : message = f"Oh ! Il y a maintenant {(nombre//taillePaquet[i])*taillePaquet[i]} exercices résolus ! 🥳"
                elif i == 3 : message = f"Oh ! Il y a maintenant {(nombre//taillePaquet[i])*taillePaquet[i]} points distribués ! 🥳"

                await canalGeneral.send(embed=Embed(description=message, color=0xF9E430))
    
    # Résolutions récentes
    response = await aclient.get("https://www.mathraining.be/solvedproblems")
    soup = BeautifulSoup(await response.text(), "lxml")

    if 'Date' in response.headers:
        now = parsedate_to_datetime(response.headers['Date']).replace(second = 0, tzinfo = None)
        now += datetime.timedelta(hours = int(datetime.datetime.now(pytz.timezone('Europe/Paris')).strftime('%z'))/100)
    else: # for local debug
        now = datetime.datetime.now()

    loop_until = last_submission_date or now
    last_submission_date = now

    liste = []

    table = soup.find("table")
    for resolution in table.find_all("tr"):
        elements = resolution.find_all("td")
        
        this_date = datetime.datetime.strptime(elements[0].decode_contents() + " " + elements[1].decode_contents().replace("h", ":"), '%d/%m/%y %H:%M')
        if this_date >= last_submission_date: continue
        if this_date < loop_until: break

        user = elements[2].find("a")["href"].split("/")[-1]
        probleme = elements[5].contents[-1].strip()[1:]

        discordUser = FindMT(user)
        if not discordUser: continue # on affiche que les utilisateurs du discord MT

        # on récupère le lien du problème
        with open("Problems.txt", "r") as file:
            for line in file:
                numero, idPb = line.split()
                if numero == probleme: break
        
        ping_user = discordUser in solvedpbs_ping_settings
        
        the_user = bot.get_user(int(discordUser)) or await bot.fetch_user(int(discordUser))
        
        prefix = the_user.mention if ping_user else f"**{the_user.name}**`#{the_user.discriminator}`"
        
        liste.append(f"{prefix} a résolu le problème #{probleme} https://www.mathraining.be/problems/{idPb} ! :clap:")
    for i in reversed(liste):
        await canalResolutions.send(i)

##...

try:
    bot.run(options['token']) #Token MT
except errors.LoginFailure as e:
    print(e)
    #driver.quit()
else:
    run(aclient.close())
    #driver.quit()
