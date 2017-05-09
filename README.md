# Moonshot
Team Builder by team Moonshot for CIS 422: Software Engineering at the University of Oregon

## OSX Setup
Install Homebrew (if needed):
```
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
```

Install the necessary modules (if needed):
```
brew arrow
brew flask
brew pymongo
```

Start and activate the Virtual Environment and install the modules into the environment:
```
make install
```

Install the necessary modules (if needed):
```
. env/bin/activate
python flask_main.py
```
