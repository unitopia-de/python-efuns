# Python Efuns for spell checking

These efuns provide an interface to the HunSpell library.
* `int spell_check(string word)` will check a single word
* `string* spell_suggest(string word)` will give suggestions for a single word.

The package will automatically search for HunSpell dictionaries according to
the locale. But you can specify them explicitely in the config file `.ldmud-efuns`
in your home directory with the following contents
```
[spell]
# If dictionary is given, also affix must be given.
dictionary = /usr/share/hunspell/de_DE.dic
affix = /usr/share/hunspell/de_DE.aff

# The additional dictionary is optional
additional = /home/mud/my_dictionary.dic
```
