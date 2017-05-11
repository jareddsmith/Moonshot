# Moonshot
Team Builder by team Moonshot for CIS 422: Software Engineering at the University of Oregon

#### Team Members
* Jared Smith
* Tyler Quatraro
* Yuan Wang

## Setup
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

Start and activate the Virtual Environment:
```
pyvenv env
. env/bin/activate
```

Install the necessary modules into the environment:
```
make install
```

Uninstall the program from the system
```
make clean
```
