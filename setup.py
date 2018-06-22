from distutils.core import setup

setup(
    name = 'udicOpenData',
    packages=['udicOpenData'],
    package_dir={'udicOpenData':'udicOpenData'},
    package_data={'udicOpenData':['dictionary/*', 'stopwords/*', 'scripts/dump2es.py']},
    version = '1.4',
    description = 'udic dictionary, stopwords module',
    author = ['davidtnfsh'],
    author_email = 'davidtnfsh@gmail.com',
    url = 'https://github.com/UDICatNCHU/Open-Training-Data',
    download_url = '',
    keywords = ['udicOpenData', 'jieba', 'dictionary', 'stopwords'],
    classifiers = [],
    license='GPL3.0',
    install_requires=[
        'jieba'
    ],
    zip_safe=True,
    scripts=['udicOpenData/scripts/dump2es.py']
)
