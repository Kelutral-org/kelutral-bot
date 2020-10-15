# -*- coding: utf-8 -*-
import os
import random

## -- Variables

## Na'vi Alphabet
vowels = ["a","ä","e","i","ì","o","u","aw","ay","ew","ey"]
vowelProbabilities = [10,10,10,10,10,10,10,2,2,2,2]
consonants = ["'","f","h","k","kx","l","m","n","ng","p","px","r","s","t","tx","ts","v","w","y","z"]
consonantProbabilities = [1,6,6,6,3,6,6,6,4,6,3,4,6,6,3,6,5,5,5,5]
pseudovowels = ["ll","rr"]
diphthongs = ["aw","ay","ew","ey"]

preconsonants = ["f","s","ts"]
onsets_withpre = ["k","kx","l","m","n","ng","p","px","r","t","tx","w","y"]
onsetProbabilities = [5,2,5,5,5,4,5,2,4,5,2,3,3]
codas = ["'","k","kx","l","m","n","ng","p","px","r","t","tx"]
codaProbabilities = [50,8,3,8,8,8,3,8,3,8,8,3]

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
# Just one vowel
# Consonant and vowel
# Consonant cluster and vowel
# Vowel and coda
# Consonant, vowel and coda
# Consonant cluster, vowel and coda
# Consonant and pseudovowel
# Consonant cluster, pseudovowel

## -- Functions
## Syllable Creation Functions

def ruleOne():
    vowel = random.choices(vowels, weights=vowelProbabilities)
    return vowel[0]

def ruleTwo():
    vowel = random.choices(vowels, weights=vowelProbabilities)
    consonant = random.choices(consonants, weights=consonantProbabilities)
    s = consonant[0] + vowel[0]
    return s

def ruleThree():
    vowel = random.choices(vowels, weights=vowelProbabilities)
    onset = random.choices(onsets_withpre, weights=onsetProbabilities)
    s = preconsonants[random.randint(0,2)] + onset[0] + vowel[0]
    return s

def ruleFour():
    vowel = random.choices(vowels, weights=vowelProbabilities)
    s = vowel[0] + codas[random.randint(0,11)]
    return s

def ruleFive():
    consonant = random.choices(consonants, weights=consonantProbabilities)
    vowel = random.choices(vowels, weights=vowelProbabilities)
    coda = random.choices(codas, weights=codaProbabilities)
    s = consonant[0] + vowel[0] + coda[0]
    return s

def ruleSix():
    vowel = random.choices(vowels, weights=vowelProbabilities)
    onset = random.choices(onsets_withpre, weights=onsetProbabilities)
    coda = random.choices(codas, weights=codaProbabilities)
    s = preconsonants[random.randint(0,2)] + onset[0] + vowel[0] + coda[0]
    return s

def ruleSeven():
    consonant = random.choices(consonants, weights=consonantProbabilities)
    s = consonant[0] + pseudovowels[random.randint(0,1)]
    return s

def ruleEight():
    onset = random.choices(onsets_withpre, weights=onsetProbabilities)
    s = preconsonants[random.randint(0,2)] + onset[0] + pseudovowels[random.randint(0,1)]
    return s
	
# Name Generation Function

def nameGen(numSyllables):
    names = []
    name = ""
    output = " "

    i = int(numSyllables)

    # Conditional Loop for Number of Syllables
    while i>0:
        syllables = [1, 2, 3, 4, 5, 6, 7, 8]
        p = [50, 50, 7.5, 7.5, 7.5, 4, .5, .5]
        rule = random.choices(syllables, weights = p)
        rule = int(rule[0])
        # rule = random.randint(0,7)
        if rule == 1 and not i == 1:
            name = name + ruleOne()
            i-=1
        elif rule == 2:
            name = name + ruleTwo()
            i-=1
        elif rule == 3:
            name = name + ruleThree()
            i-=1
        elif rule == 4:
            name = name + ruleFour()
            i-=1
        elif rule == 5:
            name = name + ruleFive()
            i-=1
        elif rule == 6:
            name = name + ruleSix()
            i-=1
        elif rule == 7:
            name = name + ruleSeven()
            i-=1
        else:
            name = name + ruleEight()
            i-=1

    # Building the Output
    name = name.replace("''", "'")
    name = name.replace("kk","k")
    name = name.replace("kxkx", "kx")
    name = name.replace("mm", "m")
    name = name.replace("nn", "n")
    name = name.replace("ngng", "ng")
    name = name.replace("pp", "p")
    name = name.replace("pxpx", "px")
    name = name.replace("tt", "t")
    name = name.replace("txtx", "tx")
    name = name.replace("yy","y")
    name = name.replace("aa", "a")
    name = name.replace("ää", "ä")
    name = name.replace("ee", "e")
    name = name.replace("ii", "i")
    name = name.replace("ìì", "ì")
    name = name.replace("oo", "o")
    name = name.replace("uu", "u")
    name = name.replace("lll","ll")
    name = name.replace("rrr","rr")
    name = name.capitalize()
    
    return name
