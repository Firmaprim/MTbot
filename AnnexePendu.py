from discord import *
from discord.ext import commands
from discord.utils import get

from random import choice

# Let Adrien be a programmer, then Adrien > AnisDeFirma :)
class Pendu():
    def __init__(self):
        self.word = ""
        with open('liste_francais.txt', 'r', encoding="latin-1") as dic:
            self.word_list = dic.read().split('\n')
        self.lifes_remaining = None
        self.letters_guessed = None
        self.tried_letters = None
        self.bot_tmp_msg = None

    def check_letter(self, letter):
        self.tried_letters.append(letter.lower())
        flag = True
        for i in range(len(self.word)):
            if self.word[i] == letter:
                flag = False
                self.letters_guessed[i] = letter
        if flag : self.lifes_remaining -= 1; return 0
        else: return 1

    def start(self):
        self.tried_letters = []
        self.lifes_remaining = 9
        self.word = choice(self.word_list)
        self.letters_guessed = ['*']*len(self.word)

    def game_over(self):
        if self.lifes_remaining == 0:
            tmp = self.word
            self.word = ""
            return tmp, 0
        elif '*' not in self.letters_guessed: 
            tmp = self.word
            self.word = ""
            return tmp, 1
        else: return self.word, 2



async def pendu(ctx, tuile: str = '', PENDU_RUNNER = Pendu()):
    await (ctx.message).delete()
    if tuile == 'start':
        if PENDU_RUNNER.word == "":
            PENDU_RUNNER.start()
            mot = PENDU_RUNNER.letters_guessed
            format_mot = ''
            for i in mot: format_mot += i.capitalize() + " "
            embed = Embed(title = 'Pendu', color = 0xFFA500)
            embed.add_field(name = 'Mot à deviner : ', value = format_mot[:-1], inline = True)
        else:
            embed = Embed(title = 'Un pendu est déjà en cours !', color = 0xFFA500)
            vies = 'Vous avez ' + str(PENDU_RUNNER.lifes_remaining) + ' vies.'
            mot = PENDU_RUNNER.letters_guessed
            format_mot = ''
            for i in mot: format_mot += i.capitalize() + " "
            embed.add_field(name = 'Votre avancée', value = format_mot[:-1], inline = True)
            embed.add_field(name = 'Vos vies', value = vies, inline = True)
    elif tuile == '': 
        embed = Embed(title = "Jeu du pendu", description = "Préfixe avant les commandes : &",color = 0x87CEFA)
        embed.add_field(name = "start", value="Démarrer une partie. Une nouvelle partie ne sera créée que si la partie précédente est terminée.")
        embed.add_field(name = "check", value="Donne l'état actuel de la partie.")
        embed.add_field(name = "[lettre]", value="Soumet une lettre au jeu.")
    elif PENDU_RUNNER.word != "":
        if tuile == "check":
            embed = Embed(title = 'État actuel de la partie :', color = 0xFFA500)
            vies = 'Vous avez ' + str(PENDU_RUNNER.lifes_remaining) + ' vies.'
            mot = PENDU_RUNNER.letters_guessed
            format_mot = ''
            for i in mot: format_mot += i.capitalize() + " "
            embed.add_field(name = 'Votre avancée', value = format_mot[:-1], inline = True)
            embed.add_field(name = 'Vos vies', value = vies, inline = True)
        else:
            checker = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
            if tuile.lower() in checker:
                if tuile.lower() in PENDU_RUNNER.tried_letters:
                    embed = Embed(title = 'Vous avez déjà utilisé cette lettre !', color = 0xFFA500)
                else:
                    state = PENDU_RUNNER.check_letter(tuile.lower()) #here
                    word, res = PENDU_RUNNER.game_over()
                    #print(res)
                    if res == 0:
                        embed = Embed(title = 'Mouahahah ! Vous avez perdu !', color = 0xDC143C)
                        embed.add_field(name = 'Le mot était : ', value = word, inline = True)
                    elif res == 1:
                        embed = Embed(title = 'Bravo ! Vous avez trouvé le mot.', color = 0x32CD32)
                        embed.add_field(name = 'Le mot était : ', value = word, inline = True)
                    else: # here
                        if state == 0:
                            embed = Embed(title = 'Oh non... ce n\'est pas la bonne lettre', color = 0xFFA500)
                        else:
                            embed = Embed(title = "C'est la bonne lettre !", color = 0xFFA500)
                        vies = 'Vous avez ' + str(PENDU_RUNNER.lifes_remaining) + ' vies.'
                        mot = PENDU_RUNNER.letters_guessed
                        format_mot = ''
                        for i in mot: format_mot += i.capitalize() + " "
                        embed.add_field(name = 'Votre avancée', value = format_mot[:-1], inline = True)
                        embed.add_field(name = 'Vos vies', value = vies, inline = True)
            elif len(tuile) == len(PENDU_RUNNER.word):
                if tuile.lower() == PENDU_RUNNER.word.lower():
                    embed = Embed(title = 'Bravo ! Vous avez trouvé le mot.', color = 0x32CD32)
                    embed.add_field(name = 'Le mot était : ', value = PENDU_RUNNER.word, inline = True)
                    PENDU_RUNNER.word = ""
                else:
                    PENDU_RUNNER.lifes_remaining -= 1
                    word, res = PENDU_RUNNER.game_over()
                    if res == 0:
                        embed = Embed(title = 'Mouahahah ! Vous avez perdu !', color = 0xDC143C)
                        embed.add_field(name = 'Le mot était : ', value = word, inline = True)
                        PENDU_RUNNER.word = ""
                    else:
                        embed = Embed(title = 'Oh non... ce n\'est pas le bon mot', color = 0xFFA500)
                        vies = 'Vous avez ' + str(PENDU_RUNNER.lifes_remaining) + ' vies.'
                        mot = PENDU_RUNNER.letters_guessed
                        format_mot = ''
                        for i in mot: format_mot += i.capitalize() + " "
                        embed.add_field(name = 'Votre avancée', value = format_mot[:-1], inline = True)
                        embed.add_field(name = 'Vos vies', value = vies, inline = True)
            else:
                embed = Embed(title = 'Vous devez entrer une lettre.', color = 0xFFA500)
                embed.add_field(name = 'Entrez &pendu [lettre]', value = 'pour vous aider.')
    else:
        embed = Embed(title = 'Vous devez relancer une partie !', color = 0xFFA500)
        embed.add_field(name = 'Entrez &pendu start', value = 'pour vous aider.')

    if PENDU_RUNNER.bot_tmp_msg != None:
        await PENDU_RUNNER.bot_tmp_msg.delete()
    PENDU_RUNNER.bot_tmp_msg = await ctx.send(embed=embed)
