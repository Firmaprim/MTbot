import random
# Let Adrien be a programmer, then Adrien > AnisDeFirma :)
class Pendu():
    def __init__(self):
        self.word = None
        self.word_list = None
        self.lifes_remaining = None
        self.letters_guessed = None


    def open_dic(self):
        with open('liste_francais.txt', 'r', encoding="latin-1") as dic:
            self.word_list = dic.read().split('\n')
        checker = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
        #print(self.word_list)
        for i in self.word_list:
            tmp = 0
            for c in i:
                if c not in checker:
                    tmp = 1
            if tmp == 1:
                #print(i)
                self.word_list.remove(i)

        #print(self.word_list)
        

    def check_letter(self, letter):
        tmp = 0
        for i in range(len(self.word)):
            if self.word[i] == letter:
                tmp = 1
                self.letters_guessed[i] = letter

        if tmp == 0:
            self.lifes_remaining -= 1

    def start(self):
        self.lifes_remaining = 9
        self.word = random.choice(self.word_list)
        self.letters_guessed = ['*']*len(self.word)

    def no_lives_left(self):
        if self.lifes_remaining == 0:
            return True
        else:
            return False

    def word_finish(self):
        if '*' not in self.letters_guessed:
            return True
        else:
            return False

    def game_over(self):
        if self.no_lives_left():
            return 0
        elif self.word_finish():
            return 1
        else:
            return 2
        
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