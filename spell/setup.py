import setuptools

setuptools.setup(
    name="ldmud-efun-spell",
    version="0.0.1",
    author="UNItopia Administration",
    author_email="mudadm@UNItopia.DE",
    description="Spelling Efuns for UNItopia",
    long_description="Offers efun for interaction with the HunSpell library.",
    packages=setuptools.find_packages(),
    install_requires=[
        'hunspell',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'ldmud_efun': [
              'spell_check   = ldmudefunspell.spell:efun_spell_check',
              'spell_suggest = ldmudefunspell.spell:efun_spell_suggest',
              'spell_reload  = ldmudefunspell.spell:efun_spell_reload',
        ]
    },
    zip_safe=False,
)
