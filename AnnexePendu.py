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
