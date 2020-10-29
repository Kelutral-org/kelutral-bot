# Originally written by Mako
# Adapted by Wiebe van Aken https://github.com/Perensoep109

# -*- coding: utf-8 -*-
import random

## -- Variables

## Na'vi Alphabet
fullAlphabet = ["a","ä","e","i","ì","o","u","aw","ay","ew","ey","'","f","h","k","kx","l","m","n","ng","p","px","r","s","t","tx","ts","v","w","y","z","ll","rr"]
vowels = ["a","ä","e","i","ì","o","u","aw","ay","ew","ey"]
vowelProbabilities = [10,10,10,10,10,10,10,2,2,2,2]
consonants = ["'","f","h","k","kx","l","m","n","ng","p","px","r","s","t","tx","ts","v","w","y","z"]
consonantProbabilities = [6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6]
pseudovowels = ["ll","rr"]
diphthongs = ["aw","ay","ew","ey"]

preconsonants = ["f","s","ts"]
onsets_withpre = ["k","kx","l","m","n","ng","p","px","r","t","tx","w","y"]
onsetProbabilities = [6,6,6,6,6,6,6,6,6,6,6,6,6]
codas = ["'","k","kx","l","m","n","ng","p","px","r","t","tx"]
codaProbabilities = [6,6,6,6,6,6,6,6,6,6,6,6]

# Language Rules #
# A syllable may start with a vowel
# A syllable may end with a vowel
# A consonant may start a syllable
# A consonant cluster comprised of f, s, or ts + p, t, k, px, tx, kx, m, n, ng, r, l, w, or y may start a syllable
# Px, tx, kx, p, t, k, ', m, n, l, r, or ng may occur in syllable-final position
# Ts, f, s, h, v, z, w, or y may not occur in syllable-final position
# No consonant clusters in syllable-final position
# A syllable with a pseudovowel must start with a consonant or consonant cluster and must not have a final consonant

# Valid Syllables #
# 1 Just one vowel
# 2 Consonant and vowel
# 3 Consonant cluster and vowel
# 4 Vowel and coda
# 5 Consonant, vowel and coda
# 6 Consonant cluster, vowel and coda
# 7 Consonant and pseudovowel
# 8 Consonant cluster, pseudovowel

## -- Functions
## Syllable Creation Functions

# Get a random vowel from the set of vowels
def getRandVowel():
    return random.choices(vowels, vowelProbabilities)[0]

# Get a random consonant from the set of consonants
def getRandCons():
    return random.choices(consonants, consonantProbabilities)[0]

# Get a random coda from the set of codas using a weightmap
def getRandCoda():
    return random.choices(codas, codaProbabilities)[0]

# Get a random pseudovowel from the set of pseudovowels
def getRandPseudoVowel():
    return pseudovowels[random.randint(0,1)]

# Get a random onset letter from the set of onsets
def getRandOnset():
    return random.choices(onsets_withpre, onsetProbabilities)[0]

# Get a random pre-consonant from the set of pre-consonants
def getRandPreCons():
    return preconsonants[random.randint(0,2)]
  
def updateProbabilities(letterPrefs):
    global vowelProbabilities
    global onsetProbabilities
    global codaProbabilities
    global consonantProbabilities
    invalidLetters = []
    
    for letter in letterPrefs:
        # Checks letter preferences against valid letters
        if letter not in fullAlphabet:
            invalidLetters.append(letter)
        # Updates probability for specified letters
        else:
            if letter in vowels:
                vowelProbabilities[vowels.index(letter)] = 100
            elif letter in consonants:
                if letter in onsets_withpre:
                    onsetProbabilities[onsets_withpre.index(letter)] = 100
                elif letter in codas:
                    codaProbabilities[codas.index(letter)] = 100
                
                consonantProbabilities[consonants.index(letter)] = 100

def applyRule(ruleID):
    return {
        1: getRandVowel(),
        2: getRandCons() + getRandVowel(),
        3: getRandPreCons() + getRandVowel() + getRandOnset(),
        4: getRandVowel() + getRandCoda(),
        5: getRandCons() + getRandVowel() + getRandCoda(),
        6: getRandPreCons() + getRandOnset() + getRandVowel() + getRandCoda(),
        7: getRandCons() + getRandPseudoVowel(),
        8: getRandPreCons() + getRandOnset() + getRandPseudoVowel()
    }.get(ruleID)

# Cleanup the input rawname by replacing all cases of illegal doubles, then capitalizing the result
def cleanUp(rawName):
    return rawName.replace("kxkx", "kx").replace("pxpx", "px").replace("txtx", "tx").capitalize()

def nameGen(numSyllables, letterPrefs):  
    output = ""
    wordLength = int(numSyllables)
    weights = [50, 50, 7.5, 7.5, 7.5, 4, .5, .5]
    invalidLetters = []
    
    updateProbabilities(letterPrefs)

    for i in range(0, wordLength):
        chosenRule = int(random.choices([1, 2, 3, 4, 5, 6, 7, 8], weights)[0])
        genSyllable = applyRule(chosenRule)
        
        # Checks to see if the new syllable starts with the same character as the end of the previous syllable.
        if output != "":
            while genSyllable[-1] == output[-1]:
                genSyllable = applyRule(chosenRule)
        
        output += genSyllable
    
    # Cleanup generated output before returning said output
    return cleanUp(output)