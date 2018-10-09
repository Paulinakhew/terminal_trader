#!/usr/bin/env python3

import os

def log_or_sign():
    os.system('clear')
    os.system('figlet Terminal Trader | lolcat -a -d 2')
    print('[l] Log in\n[c] Create a new account\n[e] Exit\n')
    return input(">MAIN> ")

def log_menu():
    head()
    username = input("What is your username?\n")
    password = input("What is your password?\n")
    return username,password

def create_menu():
    head()
    a = input("Create an username:\n")
    b = input("Create a password:\n")
    c = input("How much money you will invest:\n")
    return a,b,c

def head():
    os.system('clear')
    os.system('cowsay -f vader "Terminal Trader\n" | lolcat')

def main_menu():
    head()
    print('[b] Buy\n[s] Sell\n[l] Lookup\n[q] Quote\n[f] Funds\n[h] Holdings\n[t] Transactions\n[e] Exit\n')
    return input(">MAIN> ")

def buy_menu():
    head()
    x = input('Ticker Symbol: ')
    y = float(input('Trade Volume: '))
    return x, y

def lookup_menu():
    head()
    print("Input the name of the company that you would like to find the ticker symbol for. ")
    return input('>MAIN>LOOKUP> ')

def quote_menu():
    head()
    print("Input the ticker symbol of the stock that you would like a quote for. ")
    return input('>MAIN>QUOTE> ')

def sell_menu():
    head()
    x = input('Ticker Symbol: ')
    y = float(input('Trade Volume: '))
    return x, y

def clear_screen():
    os.system("clear")