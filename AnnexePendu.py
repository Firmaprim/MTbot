from random import choice
# Let Adrien be a programmer, then Adrien > AnisDeFirma :)
class Pendu():
    def __init__(self):
        self.word = ""
        with open('liste_francais.txt', 'r', encoding="latin-1") as dic:
            self.word_list = dic.read().split('\n')
        self.lifes_remaining = None
        self.letters_guessed = None     

    def check_letter(self, letter):
       flag = True
        for i in range(len(self.word)):
            if self.word[i] == letter:
                flag = False
                self.letters_guessed[i] = letter
        if flag : self.lifes_remaining -= 1; return 0
        else: return 1

    def start(self):
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
        
'''
runner = Pendu()
runner.open_dic()
runner.start()

while True:
    runner.check_letter(input('Entrez une lettre: '))
    print(runner.lifes_remaining, runner.letters_guessed)
    res = runner.game_over()
    if res == 0:
        print('Vous avez perdu')
        print(runner.word)
        break
    elif res == 1:
        print('Vous avez gagné')
        break
    else:
        pass
'''
