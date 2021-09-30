import re
from syntok.tokenizer import Tokenizer
from random import Random
from copy import deepcopy

class ArtificialErrorGenerator(object):

    simple_letters = "abcdefghijklmnopqrstuvwxyz"
    diacritics_list = 'ĀĒĪŌŪČĢĶĻŅŖŠŽāēīōūčģķļņŗšž'
    diacritics_list1= 'AEIOUCGKLNRSZaeioucgklnrsz'
    diacritics_list2 = ['Aa','Ee','Ii','Oo','Uu','Ch','Gj','Kj','Lj','Nj','Rr','Sh','Zh','aa','ee','ii','oo','uu','ch','gj','kj','lj','nj','rr','sh','zh']
    diacritics_map1 = {a: b for a, b in zip(diacritics_list, diacritics_list1)}
    diacritics_map2 = {a: b for a, b in zip(diacritics_list, diacritics_list2)}
    diacritics_add_map = {a: b for a, b in zip(diacritics_list1, diacritics_list2)}

    punctuation = [',', '.', ':', ';', '!', '?', '\"', '\'', '[', ']', '(', ')', '‘', '’', '”', '“', '—']

    def __init__(self, random_seed=None, **kwargs):
        self.probs = {
            'omit_space': 0.1, # remove the separator before the word
            'omit_word': 0.05, # remove the word and separator
            'swap_word': 0.1, # swap the word with the previous

            'insert_space': 0.03, # insert a space
            'insert_letter': 0.03, # insert a random letter
            'substitute_letter': 0.03, # replace with a random letter
            'omit_letter': 0.03, # remove a letter
            'double_letter': 0.03, # repeat a letter

            'swap_letters': 0.05, # swap the letter with the previous

            'diacr_add': 0.01, # add a diacritics mark (if possible)
            'diacr_a_z': 0.05, # remove a diacritics mark (if possible)
            'diacr_aa_zh': 0.05, # replace a diacritics mark with a double letter or kj, zh, etc. (if possible)

            'switch_case': 0.0,     # switch case of a letter
            'capitalize_case':0.0,   # Capitalize word
            'lower_case': 0.0,      # lowercase letter
            'upper_case': 0.0,      # uppercase letter

            'remove_punct': 0.0,    # remove punctuation
            'add_comma': 0.0,       # insert comma after word if there is no punctuation already
        }
        self.random = Random(random_seed)

        for kw, val in kwargs.items():
            if kw not in self.probs:
                raise NotImplementedError(f"Unknown param: {kw}")
            self.probs[kw] = val

    
    def randomLetter(self, c=None):
        return self.random.choice(ArtificialErrorGenerator.simple_letters)

    @staticmethod
    def addDiacritics(c, rmap):
        retval = []
        for ch in list(c):
            if ch in rmap:
                retval.append(rmap[ch])
            else:
                retval.append(ch)
        return "".join(retval)

    def processWord(self, text):
        t = list(text)
        for i in range(len(t)):
            if t[i] in ArtificialErrorGenerator.punctuation:
                # Do nothing with punctuation inside "word"
                continue
            if self.random.random() < self.probs['insert_space']:
                t[i] = t[i] + ' '
            if self.random.random() < self.probs['double_letter']:
                t[i] = t[i] + t[i]
            if self.random.random() < self.probs['omit_letter']:
                t[i] = ''
            if self.random.random() < self.probs['substitute_letter']:
                t[i] = self.randomLetter(t[i])
            if self.random.random() < self.probs['insert_letter']:
                t[i] = t[i] + self.randomLetter()
            if self.random.random() < self.probs['diacr_add']:
                t[i] = ArtificialErrorGenerator.addDiacritics(t[i], ArtificialErrorGenerator.diacritics_add_map)
            if self.random.random() < self.probs['diacr_a_z']:
                t[i] = ArtificialErrorGenerator.addDiacritics(t[i], ArtificialErrorGenerator.diacritics_map1)
            if self.random.random() < self.probs['diacr_aa_zh']:
                t[i] = ArtificialErrorGenerator.addDiacritics(t[i], ArtificialErrorGenerator.diacritics_map2)
            if self.random.random() < self.probs['swap_letters']:
                if i > 0:
                    t[i-1], t[i] = t[i], t[i-1]
            if self.random.random() < self.probs['switch_case']:
                t[i] = t[i].swapcase()
            if self.random.random() < self.probs['lower_case']:
                t[i] = t[i].lower()
            if self.random.random() < self.probs['upper_case']:
                t[i] = t[i].upper()

        return "".join(t)

    def mutateText(self, text):
        tokenizer = Tokenizer(replace_not_contraction=False)
        tokens = tokenizer.split(text)
        for i, tok in enumerate(tokens):
            tok._value = self.processWord(tok.value)
            if self.random.random() < self.probs['omit_space']:
                tok._spacing = ''
            if self.random.random() < self.probs['omit_word']:
                tok._spacing = ''
                tok._value = ''
            if self.random.random() < self.probs['remove_punct']:
                if tok._value in ArtificialErrorGenerator.punctuation:
                    tok._spacing = ''
                    tok._value = ''
            if self.random.random() < self.probs['add_comma']:
                if tok._value not in ArtificialErrorGenerator.punctuation:
                    tok._value = tok._value + ','
            if self.random.random() < self.probs['swap_word']:
                if i > 0:
                    tokens[i-1], tokens[i] = tokens[i], tokens[i-1]
            if self.random.random() < self.probs['capitalize_case']:
                tok._value = tok._value.capitalize()

        return "".join(tok.spacing + tok.value for tok in tokens)

    def data_mutate(self, data, repetitions=30):
        retval = []
        for i, d in enumerate(data):
            #print(i, d)
            d['original'] = True
            retval.append(d)
            for rep in range(repetitions):
                out_text = self.mutateText(d['text'])
                retval.append({**deepcopy(d), 'text': out_text, 'original': False})
        
        return retval
