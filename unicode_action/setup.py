import setuptools

setuptools.setup(
    name="ldmud-efun-unicode-action",
    version="0.0.1",
    author="UNItopia Administration",
    author_email="mudadm@UNItopia.DE",
    description="add_action() replacement with transliteration for UNItopia",
    long_description="Replaces add_action() to register original and transliterated commands.",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'ldmud_efun': [
              'add_action = ldmudefunaction.action:efun_add_action',
              'query_verb_ascii = ldmudefunaction.action:efun_query_verb_ascii',
        ]
    },
    zip_safe=False,
)
