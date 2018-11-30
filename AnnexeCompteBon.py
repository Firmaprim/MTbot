from random import *

def compteBon():
    nbTuiles = 6
    
    resultat = randint(100, 1000)

    tuiles = [1,2,3,4,5,6,7,8,9,10]*2 + [25,50,75,100]
    shuffle(tuiles)

    tuiles = tuiles[:nbTuiles]

    Msg = "Tuiles : " + " ".join(map(str,tuiles)) +  "\nA trouver : " + str(resultat) + "\n-"
    return Msg
      
