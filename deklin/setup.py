import setuptools

setuptools.setup(
    name="ldmud-efun-deklin",
    version="0.0.1",
    author="UNItopia Administration",
    author_email="mudadm@UNItopia.DE",
    description="Multi-recipient messages for UNItopia",
    long_description="Offers type and efun for handling messages towards multiple recipients.",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'ldmud_type': [
              'deklin_message        = ldmudefundeklin.deklin:deklin_message',
        ],
        'ldmud_efun': [
              'create_deklin_message = ldmudefundeklin.deklin:create_deklin_message',
        ]
    },
    zip_safe=False,
)
