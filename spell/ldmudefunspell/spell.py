import os, configparser, hunspell, ldmud

speller = None

def efun_spell_check(text: str) -> bool:
    """
    SYNOPSIS
            int spell_check(string word)

    DESCRIPTION
            Checks the word for spelling errors. Returns 1 if the word is correct,
            0 otherwise.

    SEE ALSO
            spell_suggest(E)
    """
    if not speller:
        raise RuntimeError("Spellchecker is not initialized.")
    return speller.spell(text)

def efun_spell_suggest(text: str) -> ldmud.Array:
    """
    SYNOPSIS
            string* spell_suggest(string word)

    DESCRIPTION
            Returns correctly spelled suggestions for the given word.

    SEE ALSO
            spell_check(E)
    """
    if not speller:
        raise RuntimeError("Spellchecker is not initialized.")
    return ldmud.Array(speller.suggest(text))

def efun_spell_reload() -> None:
    """
    SYNOPSIS
            void spell_reload()

    DESCRIPTION
            Reloads the dictionaries for spell checking.

    SEE ALSO
            spell_check(E), spell_suggest(E)
    """
    global speller

    config = configparser.ConfigParser()
    config['spell'] = {}
    config.read(os.path.expanduser('~/.ldmud-efuns'))
    spellconfig = config['spell']

    if 'dictionary' in spellconfig and 'affix' in spellconfig:
        print("Spell: Loading %s & %s" % (spellconfig.get('dictionary'), spellconfig.get('affix')))
        speller = hunspell.HunSpell(spellconfig.get('dictionary'), spellconfig.get('affix'))
    else:
        # Determine the language
        import locale
        lang = locale.getlocale(locale.LC_CTYPE)[0]

        for dirname in ('/usr/share/hunspell', '/usr/local/share/hunspell',
                        '/usr/share/myspell', '/usr/local/share/myspell',
                        '/usr/share/myspell/dicts', '/usr/local/share/myspell/dicts',):
            dicname = os.path.join(dirname, lang + '.dic')
            affname = os.path.join(dirname, lang + '.aff')
            if os.path.exists(dicname) and os.path.exists(affname):
                print("Spell: Loading %s & %s" % (dicname, affname))
                speller = hunspell.HunSpell(dicname, affname)
                break

    if not speller:
        print("Spell: Didn't find suitable dictionary.")
    elif 'additional' in spellconfig:
        print("Spell: Loading additionaly %s" % (spellconfig.get('additional'),))
        speller.add_dic(spellconfig.get('additional'))

efun_spell_reload()
