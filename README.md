# terminal_trader
This project was started at Byte Academy so that I could learn how to implement modularization, learn about JSON, and create and interact with SQLite3 databases. This application consolidates data from Nasdaq, allowing the user to search up the ticker symbol and price of any stock in real time. You can buy and sell any number of stocks and see your past transactions. 
The goal is to end up with a large profit :money_mouth_face: good luck!

## Setup
- Clone or download the repository.
- Download all the necessary packages:

* **MacOS Users**
```ShellSession
$ pip3 install -r pip_requirements.txt
$ xargs brew install < brew_requirements.txt
```

* **Linux Users**
```ShellSession
$ sudo apt-get install cowsay
$ sudo apt-get install figlet
$ gem install lolcat
$ pip install -r pip_requirements.txt
```

- Create the sqlite3 database:
```ShellSession
$ python3 schema.py
$ python3 seed.py
```
- Run the app locally:
```ShellSession
$ python3 controller.py
```

### Issues and Updates
Feel free to create any issues and pull requests for changes that you want to see in the future of this application. Have fun! :smile: 

### Example photos
This is what the login and sign up menu looks like.
![Login/sign up menu](static/sign_in_menu.png?raw=true "Login and sign up menu")

This is the main menu where you can buy and sell stocks. 
![Login/sign up menu](static/main_menu.png?raw=true "Main menu")

This is what the user sees when purchasing stocks. 
![Buying stocks](static/buying_stock.png?raw=true "Buying stocks")
