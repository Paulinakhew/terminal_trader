#!/usr/bin/env python3

import model as m
import model as model
import view
import os
import sqlite3
#TODO: break upon typing any key
#for game servers, you want an infinite loop or else it will crash

connection = sqlite3.connect('trade_information.db',check_same_thread=False)
cursor = connection.cursor()

def game_loop():
    current_username = ''
    condition = True
    while 1:
        user_choice = view.log_or_sign()
        user_choice = user_choice.lower()
        log_in = ['l','login']
        create_ = ['c','create']
        exit_ = ['e','exit']
        accept_input = log_in    \
                    +create_     \
                    +exit_
        if user_choice in accept_input:
            if user_choice in log_in:
                (user_name, password) = view.log_menu()
                current_username = user_name
                has_account = model.log_in(user_name, password)
                if has_account:
                    break
                else:
                    print('WRONG LOGIN INFORMATION. TRY AGAIN')
                    import time
                    time.sleep(3)
            elif user_choice in exit_:
                condition = False
                m.log_out()
                os.system('clear')
                break
            elif user_choice in create_:
                (new_user,new_password,new_funds) = view.create_menu()
                newuser = new_user,new_password,new_funds
                cursor.execute(
                    """INSERT INTO user(
                        username,
                        password,
                        current_balance
                    ) VALUES(?,?,?
                    )""", newuser
                )
                connection.commit()
                cursor.close()
                connection.close()
                print("You have signed up!")
                import time
                time.sleep(3)
    while condition:
        buy_inputs = ['b', 'buy']
        sell_inputs = ['s', 'sell']
        lookup_inputs = ['l', 'lookup']
        quote_inputs = ['q', 'quote']
        funds = ['f', 'funds']
        holdings = ['h', 'holdings']
        exit_inputs = ['e', 'exit']
        acceptable_inputs = buy_inputs     \
                            +sell_inputs   \
                            +lookup_inputs \
                            +quote_inputs  \
                            +funds         \
                            +holdings      \
                            +exit_inputs
        user_input = view.main_menu()
        if user_input in acceptable_inputs:
            if user_input in buy_inputs:
                (ticker_symbol, trade_volume) = view.buy_menu()
                confirmation_message, return_list = model.buy(current_username, ticker_symbol, trade_volume)
                if confirmation_message == True:
                    yes = ['y', 'yes']
                    no = ['n', 'no']
                    choice = input("You have enough money. Would you like to buy this stock?\n[y] Yes\n[n] No\n")
                    if choice in yes:
                        model.buy_db(return_list)
                        print("You have bought {} shares of {}. ".format(trade_volume, ticker_symbol))
                    else:
                        print("Returning to main menu.")
                else:
                    print("You do not have enough money to buy this stock.")
            elif user_input in sell_inputs:
                (ticker_symbol, trade_volume) = view.sell_menu()
                confirmation_message, return_list = model.sell(current_username, ticker_symbol, trade_volume)#TODO
                if confirmation_message == True:
                    yes = ['y', 'yes']
                    no = ['n', 'no']
                    choice = input("You have enough shares to sell. Would you like to sell this stock?\n[y] Yes\n[n] No\n")
                    if choice.lower() in yes:
                        model.sell_db(return_list)
                        print("You have sold {} shares of {}. ".format(trade_volume, ticker_symbol))
                    else:
                        print("Returning to main menu.")
                else:
                    print("You do not have enough shares to sell.")
            elif user_input in lookup_inputs:
                company_name = view.lookup_menu()
                ticker_symbol = model.lookup_ticker_symbol(company_name)
                if len(ticker_symbol) <=6: 
                    print("The ticker symbol for {} is {}.".format(company_name, ticker_symbol))
                else:
                    print("The ticker symbol for the company you searched cannot be found. \nPlease try again.")
            elif user_input in quote_inputs:
                ticker_symbol = view.quote_menu()
                last_price = model.quote_last_price(ticker_symbol)
                if len(str(last_price)) <= 6:
                    print("The last price for {} is ${}.".format(ticker_symbol, last_price))
                else:
                    print("The last price for the company you searched cannot be found. \nPlease try again.")
            elif user_input in funds:
                view.clear_screen()
                bal = model.funds()
                print("Your current balance is ${}.".format(bal))
            elif user_input in holdings:
                view.clear_screen()
                holdings = m.holdings()
                print("Your current holdings: \n{}".format(holdings))
            elif user_input in exit_inputs:
                view.clear_screen()
                break
            else:
                print("Error.")
        else:
            print("Error.")
        model.update_holdings()
        input("\nPress enter to continue. ")


if __name__ == '__main__':
    game_loop()
