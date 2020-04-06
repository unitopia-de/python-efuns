import setuptools

setuptools.setup(
    name="ldmud-efun-jwt",
    version="0.0.1",
    author="UNItopia Administration",
    author_email="mudadm@UNItopia.DE",
    description="JWT Efun for UNItopia",
    long_description="Offers the efun get_jwt() to create JSON Web Tokens.",
    packages=setuptools.find_packages(),
    install_requires=[
        'PyJWT',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'ldmud_efun': [
              'get_jwt        = ldmudefunjwt.get_jwt:efun_get_jwt',
        ]
    },
    zip_safe=False,
)
