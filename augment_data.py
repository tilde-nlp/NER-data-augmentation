import os
import argparse
from ArtificialErrorGenerator import ArtificialErrorGenerator
from shutil import copyfile

def augment_data(infile, outfile, **probs):
    # print('{} {} {}'.format(infile, outfile, probs))
    print('{} {}'.format(infile, outfile))
    mutagen = ArtificialErrorGenerator(**probs)

    with open(infile, 'r', encoding='utf-8') as inf, open(
            outfile, 'w', encoding='utf-8') as outf:
        for line in inf.readlines():
            # NER format used for training is conll2003 like, with space separating token and label
            line = line.strip()
            parts = line.split(" ")
            if len(parts) < 2:
                # Empty line, separates sentences
                outf.write('\n')
                continue
            if len(parts) == 2:
                token = parts[0]
                label = parts[1]
            elif len(parts) > 2:
                # Somehow space is inside token. Happens with numbers etc. "800 000"
                token = " ".join(parts[:-1])
                label = parts[-1]
            # Add errors with chance 0.1
            mutated_token = mutagen.mutateText(token)
            if len(mutated_token) == 0:
                # Punctuation removed...
                # print("token removed {}".format(token))
                continue
            outf.write('{} {}\n'.format(mutated_token, label))

if __name__ == "__main__":
    # parser = argparse.ArgumentParser(description="Introduce mistakes into the dataset")
    # parser.add_argument('-f', '--infile', help="Conll-like file, to introduce errors")
    # args = parser.parse_args()
    src_dir = r"data"
    infiles = [
        "dev.txt",
        "test.txt",
        "train.txt"
    ]
    label_file = "labels.txt"
    default_probs = {
        'omit_space': 0.0, # remove the separator before the word
        'omit_word': 0.0, # remove the word and separator
        'swap_word': 0.0, # swap the word with the previous

        'insert_space': 0.0, # insert a space
        'insert_letter': 0.0, # insert a random letter
        'substitute_letter': 0.0, # replace with a random letter
        'omit_letter': 0.0, # remove a letter
        'double_letter': 0.0, # repeat a letter

        'swap_letters': 0.0, # swap the letter with the previous

        'diacr_add': 0.0, # add a diacritics mark (if possible)
        'diacr_a_z': 0.0, # remove a diacritics mark (if possible)
        'diacr_aa_zh': 0.0, # replace a diacritics mark with a double letter or kj, zh, etc. (if possible)

        'switch_case': 0.0, # switch case of a letter
        'capitalize_case':0.0,   # lowercase letter
        'lower_case':0.0,   # lowercase letter
        'upper_case':0.0,   # uppercase letter

        'remove_punct': 0.0,    # remove punctuation 
        'add_comma': 0.0,       # insert comma after word if there is no punctuation already
        }

    # 1. Introduce extra letter insert_letter
    # 2. Delete letter          omit_letter
    # 3. Permute letter         swap_letters
    # 4. confuse letter         substitute_letter
    # 5. add diacritic          diacr_add
    # 6. sample substitute      - 
    # 7. remove punctuation     remove_punct
    # 8. add comma              add_comma
    # 9. latinize               diacr_a_z
    # 10. phonetic latinize     diacr_aa_zh
    # 11. -                     switch_case
    # 12. -                     lower_case
    # 13. -                     upper_case

    # "ONE HOT"; Not all have to be used.
    used_probs = {
        'omit_space': 0.0, # remove the separator before the word
        'omit_word': 0.0, # remove the word and separator
        'swap_word': 0.0, # swap the word with the previous

        'insert_space': 0.00, # insert a space
        'insert_letter': 0.05, # insert a random letter
        'substitute_letter': 0.05, # replace with a random letter
        'omit_letter': 0.05, # remove a letter
        'double_letter': 0.05, # repeat a letter

        'swap_letters': 0.1, # swap the letter with the previous

        'diacr_add': 0.0, # add a diacritics mark (if possible)
        'diacr_a_z': 1.0, # remove a diacritics mark (if possible)
        'diacr_aa_zh': 1.0, # replace a diacritics mark with a double letter or kj, zh, etc. (if possible)

        'switch_case': 0.1, # switch case of a letter
        'capitalize_case': 1.0,   # Capitalize word
        'lower_case': 1.0,   # lowercase letter
        'upper_case': 0.1,   # uppercase letter # 0.1 means randomly uppercased letters

        'remove_punct': 1.0,    # remove punctuation 
        'add_comma': 0.1,       # insert comma after word if there is no punctuation already
        }

    for key, value in default_probs.items():
        probs = dict(default_probs)
        # probs[key] = 0.1
        if used_probs.get(key):
            probs[key] = used_probs[key]
        if probs[key] == 0.0:
            # This is not used
            continue
        outdir = os.path.join(src_dir, "data_augmented", key)
        os.makedirs(outdir, exist_ok=True)
        copyfile(os.path.join(src_dir,'labels.txt'), os.path.join(outdir,'labels.txt'))

        for infile in infiles:
            in_file = os.path.join(src_dir, infile)
            outfile = os.path.join(outdir, infile)
            augment_data(in_file, outfile, **probs)
            # Add original data to train dataset
            if infile == "train.txt":
                with open(in_file,'r',encoding='utf-8') as inf, open(
                        outfile, 'a', encoding='utf-8') as ouf:
                    for line in inf.readlines():
                        ouf.write(line)