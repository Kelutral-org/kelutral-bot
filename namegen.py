# -*- coding: utf-8 -*-
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
def getRandCoda(weights):
  return random.choices(codas, weights)[0]

# Get a random pseudovowel from the set of pseudovowels
def getRandPseudoVowel():
  return pseudovowels[random.randint(0,1)]

# Get a random onset letter from the set of onsets
def getRandOnset():
  return random.choices(onsets_withpre, onsetProbabilities)[0]

# Get a random pre-consonant from the set of pre-consonants
def getRandPreCons():
  return preconsonants[random.randint(0,2)]

def applyRule(ruleID):
  return {
    1: getRandVowel(),
    2: getRandCons() + getRandVowel(),
    3: getRandPreCons() + getRandVowel() + getRandOnset(),
    4: getRandVowel() + codas[random.randint(0,11)],
    5: getRandCons() + getRandVowel() + getRandCoda(codaProbabilities),
    6: getRandPreCons() + getRandOnset() + getRandVowel() + getRandCoda(codaProbabilities),
    7: getRandCons() + getRandPseudoVowel(),
    8: getRandOnset() + getRandPseudoVowel()
  }.get(ruleID)

# Cleanup the input rawname by replacing all cases of illegal doubles, then capitalizing the result
def cleanUp(rawName):
  return rawName.replace("''", "'").replace("kk","k").replace("kxkx", "kx").replace("mm", "m").replace("nn", "n").replace("ngng", "ng").replace("pp", "p").replace("pxpx", "px").replace("tt", "t").replace("txtx", "tx").replace("yy","y").replace("aa", "a").replace("ää", "ä").replace("ee", "e").replace("ii", "i").replace("ìì", "ì").replace("oo", "o").replace("uu", "u").replace("lll","ll").replace("rrr","rr").capitalize()

def nameGen(numSyllables):
    output = ""
    wordLength = int(numSyllables)
    weights = [50, 50, 7.5, 7.5, 7.5, 4, .5, .5]

    while wordLength > 0:
      # Select rule by making a random choice from the set of rules, and then converting that rule ID to an integer
      chosenRule = int(random.choices([1, 2, 3, 4, 5, 6, 7, 8], weights)[0])

      # Check if the current rule is valid
      if chosenRule == 1 and wordLength != 1:
        continue
      
      # If so apply word rulings
      output += applyRule(chosenRule)
      wordLength -= 1

    # Cleanup generated output before returning said output
    return cleanUp(output)