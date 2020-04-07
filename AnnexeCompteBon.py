from random import *
#https://gist.github.com/cawhitworth/079d5cb19ba29d7fe5f7

def compteBon():
    target = randint(101, 1000)
    numbers = sample([1,2,3,4,5,6,7,8,9,10]*2 + [25,50,75,100],6)
    return target, numbers

add = lambda a,b: a+b
sub = lambda a,b: a-b
mul = lambda a,b: a*b
div = lambda a,b: a/b if a % b == 0 else 0/0

operations = [ (add, '+'),(sub, '-'),(mul, '*'),(div, '/')]

def Evaluate(stack):
    try:
        total,lastOper = 0,add
        for item in stack:
            if type(item) is int: total = lastOper(total, item)
            else: lastOper = item[0]
        return total
    except:
        return 0

def ReprStack(stack): #Modifié pour prendre en compte le parenthésage (il suffit de remarquer que le parenthésage se fait toujours à gauche après une multiplication)
    reps = [ str(item) if type(item) is int else item[1] for item in stack ]
    i=2
    while i != len(reps) :
        if reps[i] in ['*','/'] and reps[i-1] != ')' : reps[0:i]=['(']+reps[0:i]+[')']
        i+=1
    return ' '.join(reps)

def Solve(target, numbers, sols):
    res=[]
    def Recurse(stack, nums):
        nonlocal res
        for n in range(len(nums)):
            stack.append( nums[n] )

            remaining = nums[:n] + nums[n+1:]

            if Evaluate(stack) == target:
                i=ReprStack(stack)
                res+=[i]
                #print(i)

            if len(remaining) > 0:
                for op in operations:
                    stack.append(op)
                    stack = Recurse(stack, remaining)
                    stack = stack[:-1]

            stack = stack[:-1]
        return stack

    Recurse([], numbers)
    return sample(res,min(sols,len(res),30))

def Lettres():
    Lettres = {'E':1444, 'A':749, 'I':664, 'S':651, 'N':639, 'R':607,\
    'T':592, 'O':507, 'L':496, 'U':453, 'D':367, 'C':324,\
    'M':262, 'P':249, 'G':123, 'B':114, 'V':111, 'H':111,\
    'F':111, 'Q':65, 'Y':46, 'X':38, 'J':34, 'K':29,\
    'W':17, 'Z':15}
    lettres = []
    for l in Lettres.keys():
        for _ in range(Lettres[l]): lettres.append(l)
    return [lettres[randint(0, 8817)] for _ in range(10)]
