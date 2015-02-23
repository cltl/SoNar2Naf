# NAF tagset used: http://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/data/dutch-tagset.txt

def posmap(foliapos):
    """Takes a POS-tag used in SoNaR/folia and returns
a POS-tag that can be used in NAF."""
    posdict = dict([
                    ("N","N"),
                    ("WW","V"),
                    ("ADJ","G"),
                    ("VNW","Q"),
                    ("LID","D"),
                    ("VZ","P"),
                    ("LET","O"),
                    ("VG","C"),
                    ("BW","A"),
                    ("TSW","O"),
                    ("SPEC","O"),
                    ("TW","O")
                    ])
    return posdict[foliapos]

def morphomap(pos,morph):
    """Takes a POS-tag and a list of morphological features
    used in SoNaR/folia and returns the morphofeat string 
    that can be used in NAF."""
    
    morphofeat = [] # initialize list to which morphofeatures will be added
    
    # Below (i.e. morphodict) is the mapping from Folia morphofeat to NAF.
    #
    # There are some 'fake' morphofeats added by analyzepos() because some information
    # is lost in the conversion of the POS tags. Adding 'fake' morphofeats is the easiest
    # way to get them back.
    
    morphodict = dict([
                    # adj: see if statement below. if pos == G --> add adj morphofeat
                    # adv: see if statement below. if pos == A --> add adv morphofeat
                    # det
                    ("onbep","det__indef"),
                    ("gen","det__poss"),
                    # conj
                    ("neven","conjcoord"),
                    ("onder","conjsubo"),
                    # int
                    ("int","int"),      # 'int' is not in folia, but added by analyzepos()
                    # noun
                    ("evN","nounsg"),   # python-internal morphofeat to 
                                        # distinguish nouns from verbs
                    ("mvN","nounpl"),   # ""
                    ("eigen","nounprop"),
                    # num 2/2
                    ("rang","num__card"),
                    ("hoofd","num__ord"),
                    # prep
                    # pron
                    ("adv-pron","pronadv"),
                    ("pron",""), #already captured by POS
                    ("aanw","prondemo"),
                    ("onbep","pronindef"),
                    ("pers","pronpers"),
                    ("bez","pronposs"),
                    ("vrag","pronquest"),
                    ("refl","pronrefl"),
                    ("betr","pronrel"),
                    # punc
                    ("punc","punc"), # 'punc' is not in Folia, but added by analyzepos()
                                     # currently, 'punc' is also added for sentence-final '.'
                    # verbs
                    ("vd","verbpapa"),
                    ("od","verbpresp"),
                    ("inf","verbinf")
                    ])

    # ------------------------------------------
    #   THINGS THAT CANNOT BE HANDLED BY DICT
    # ------------------------------------------ 
    #
    # all articles are det__art except genitives
    if pos == "D" and not 'gen' in morph:
        morphofeat.append("det__art")
    
    # verbs are a bit more complicated..
    elif pos == "V":
        if "verl" in morph:
            if "ev" in morph:
                morphofeat.append("verbpastsg")
            if "mv" in morph:
                morphofeat.append("verbpastpl")
        if "tgw" in morph:
            if "ev" in morph:
                morphofeat.append("verbpressg")
            if "mv" in morph:
                morphofeat.append("verbprespl")            

    # all prepositions get a 'prep' morphofeat
    elif pos == "P":
        morphofeat.append("prep")

    # provide POS-specific morphofeat for nouns
    elif pos == "N":
        if "afgebr" in morph:
            morphofeat.append("noun*kop")
        if "ev" in morph:
            morphofeat.append("nounsg")
        if "mv" in morph:
            morphofeat.append("nounpl")
    
    # all adverbs also get an 'adv' morphofeat
    elif pos == "A":
        morphofeat.append("adv")

    # all adjectives also get an 'adj' morphofeat
    elif pos == "G":
        morphofeat.append("adj")
        if "afgebr" in morph:
            morphofeat.append("adj*kop")
        # add abbreviations

    if "afk" in morph and pos in ['A','G','N','P']:
        afkdict = dict([
            ("A","advabbr"),
            ("G","adjabbr"),
            ("N","nounabbr"),
            ("P","prepabbr")
            ])
        morphofeat.append(afkdict[pos])
        
    # ------------------------------------------
    #               MAIN PROCEDURE
    # ------------------------------------------
    #    
    # now we will look through all the features from folia and append their
    # NAF-counterpart to the morphofeat list.
    for m in morph:
        if m in morphodict:                     # if there is a mapping available
            morphofeat.append(morphodict[m])    # add the NAF-counterpart to the list.
    return ' '.join(morphofeat)                 # and in the end return morphofeat as a string




def analyzepos(el):
    """This function takes a Folia pos node and returns 
    a dict with corresponding NAF POS and the morphofeat"""
    theclass = el.get('class')
    pos_folia,rest = theclass.split('(')
    if not rest == ')':
        morphofeat_folia = rest[:-1].split(',')
    else:
        morphofeat_folia = []
    pos = posmap(pos_folia)                         # determine NAF POS
    if pos_folia == 'LET':
        morphofeat_folia.append('punc')
    elif pos_folia == 'TSW':
        morphofeat_folia.append('int')
    morphofeat = morphomap(pos,morphofeat_folia)    # determine morphological features
    if pos_folia in ['LID','VZ','VNW','VG']:        # determine open/closed class
        gramclass = 'close'
    else:
        gramclass = 'open'

    # exception fix (Folia N maps to NAF N _and_ R):
    if 'nounprop' in morphofeat: 
        pos = "R"
    return dict([('pos',pos),('morphofeat',morphofeat),('gramclass',gramclass)])