import setuptools

setuptools.setup(
    name="ldmud-efun-git",
    version="0.0.1",
    author="UNItopia Administration",
    author_email="mudadm@UNItopia.DE",
    description="Git Efuns for UNItopia",
    long_description="Offers efun for interaction with the Git version management.",
    packages=setuptools.find_packages(),
    install_requires=[
        'ldmud-asyncio',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'ldmud_efun': [
              'git_list_commits   = ldmudefungit.gitefuns:efun_git_list_commits',
              'git_info_commit    = ldmudefungit.gitefuns:efun_git_info_commit',
              'git_show_diff      = ldmudefungit.gitefuns:efun_git_show_diff',
              'git_status         = ldmudefungit.gitefuns:efun_git_status',
              'git_status_diff    = ldmudefungit.gitefuns:efun_git_status_diff',
              'git_commit         = ldmudefungit.gitefuns:efun_git_commit',
              'git_reverse        = ldmudefungit.gitefuns:efun_git_reverse',
              'git_cat            = ldmudefungit.gitefuns:efun_git_cat',
              'git_search_commits = ldmudefungit.gitefuns:efun_git_search_commits',
        ]
    },
    zip_safe=False,
)
