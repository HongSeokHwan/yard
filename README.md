# Yard

## Prerequisites

- python (>=2.7)
- pip
- git
- gem


## Installation

To set up a virtual environment, run following commands in order:

```bash
sudo pip install virtualenv
sudo pip install virtualenvwrapper

export WORKON_HOME=$HOME/.virtualenvs

# /usr/bin/ or /usr/local/bin/ depending on the system
source /usr/bin/virtualenvwrapper.sh

mkvirtualenv --distribute --no-site-package yard

pip install -r requirements.txt
```


To compile SASS:

```bash
gem install sass
gem install compass
sass --watch yard/static/sass/:yard/static/css/ --compass
```


To create a local development environment:

```bash
cp yard/local_settings.py.template yard/local_settings.py
```

## Todo

### Exchange

- Handle various exceptional cases
- Add ICBIT exchange to bridge server
- Draft ORM for history data and implement collector
- Add order-related interface
- Create a simple webpage for viewing real-time quote / trade

### Trading
- Prototype


### Analysis
- Collect data from public web to database(mysql)
- Database to csv
- Develop trading strategy


## Server run scripts
cd ~/workspace/yard
ipython notebook --no-browser --port=8001 &
(local) ssh -N -f -L localhost:8889:localhost:8001 yard@www.jiref.com

cd ~/.workspace/yard
python ./manage.py runserver 0.0.0.0:8000
