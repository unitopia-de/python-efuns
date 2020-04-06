# UNItopia Python efuns

These are Python efuns used in UNItopia.

In the subdirectories there are the following packages:
 * `git` contains efuns for interaction with git
 * `jwt` contains an efun for creating JSON web tokens
 * `spell` contains efuns for spell checking
 * `unicode_action` contains an `add_action()` replacement that will register
   actions with umlauts and their transliterations.

## Usage

### Build & installation

You'll need to build the package.

First clone the repository
```
git clone https://github.com/unitopia-de/python-efuns.git
```

In the corresponding package directory execute
```
python3 setup.py install --user
```

### Automatically load the modules at startup

Also install the [LDMud Python efuns](https://github.com/ldmud/python-efuns) and use its
[startup.py](https://github.com/ldmud/python-efuns/blob/master/startup.py) as the Python startup script for LDMud.
It will automatically detect the installed Python efuns and load them.

### Manually load the modules at startup

Add lines like the following to your startup script:
```
import ldmud, ldmudefunspell.spell

ldmud.register_efun('spell_check', ldmudefunspell.spell.efun_spell_check)
ldmud.register_efun('spell_suggest', ldmudefunspell.spell.efun_spell_suggest)
```
