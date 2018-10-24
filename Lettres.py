from random import randint

def Lettres():
    Lettres = {'E':1444, 'A':749, 'I':664, 'S':651, 'N':639, 'R':607,\
    'T':592, 'O':507, 'L':496, 'U':453, 'D':367, 'C':324,\
    'M':262, 'P':249, 'G':123, 'B':114, 'V':111, 'H':111,\
    'F':111, 'Q':65, 'Y':46, 'X':38, 'J':34, 'K':29,\
    'W':17, 'Z':15}
    lettres = []
    for l in Lettres.keys():
        for _ in range(Lettres[l]):
            lettres.append(l)
    for _ in range(10):
        print(lettres[randint(0, 8817)], end='')
        print(' ', end='')
