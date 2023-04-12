# Python Efun and Type for a multi-recipient message

A type and corresponding factory efun for processing a message towards
multiple recipients that may be customized for each recipient. The type
is basically only a wrapper around an LWO that provides operators on
top of the LWO's functionality.

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
