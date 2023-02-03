from setuptools import find_packages, setup

setup(
    name='news-ebook',
    version='0.0.2',
    description='send news articles to an e-reader',
    author='Quinn Weber',
    maintainer='Quinn Weber',
    maintainer_email='quinnsweber@gmail.com',
    packages=find_packages(exclude=('tests',)),
    install_requires=(
        'BeautifulSoup4',
        'boto3',
    ),
    entry_points={
        'console_scripts': (
            'economist-kindle = news_ebook.economist_kindle:main',
        )
    }
)
