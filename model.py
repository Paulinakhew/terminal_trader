#!/usr/bin/env

import json

import sqlite3

import requests

connection = sqlite3.connect('trade_information.db',check_same_thread=False)
cursor = connection.cursor()
database = 'trade_information.db'

def log_in(user_name,password):
    query = 'SELECT count(*) FROM user WHERE username = "{}" AND password = "{}";'.format(user_name, password)
    cursor.execute(query)
    result_tuple = cursor.fetchone()
    if result_tuple[0] == 0:
        return False
    elif result_tuple[0] == 1:
        return True
    else:
        pass

def create_(new_user,new_password,new_fund):
    cursor.execute(
        """INSERT INTO user(
            username,
            password,
            current_balance
            ) VALUES(
            "new_user",
            "new_password"
            "new_fund"
        );"""
    )
    connection.commit()
    cursor.close()
    connection.close()


def updateHoldings():
    connection = sqlite3.connect(database, check_same_thread=False)
    cursor = connection.cursor()
    query = 'DELETE FROM holdings WHERE num_shares = 0'
    cursor.execute(query)
    connection.commit()
    cursor.close()
    connection.close()
    
def sell(username, ticker_symbol, trade_volume):
    #we have to search for how many of the stock we have
    #compare trade volume with how much stock we have
    #if trade_volume <= our stock, proceed
    #else return to menu
    #we need a database to save how much money we have and how much stock
    connection = sqlite3.connect(database, check_same_thread=False)
    cursor = connection.cursor()
    query = 'SELECT count(*), num_shares FROM holdings WHERE username = "{}" AND ticker_symbol = "{}"'.format(username, ticker_symbol)
    cursor.execute(query)
    fetch_result = cursor.fetchone()
    if fetch_result[0] == 0:
        number_shares = 0
    else:
        current_number_shares = fetch_result[1]


    last_price = float(quote_last_price(ticker_symbol))
    brokerage_fee = 6.95 #TODO un-hardcode this value
    current_balance = get_user_balance(username) #TODO un-hardcode this value
    print("Price", last_price)
    print("brokerage fee", brokerage_fee)
    print("current balance", current_balance)
    transaction_revenue = (trade_volume * last_price) - brokerage_fee
    print("Total revenue of Transaction:", transaction_revenue)
    agg_balance = float(current_balance) + float(transaction_revenue)
    print("\nExpected user balance after transaction:", agg_balance)
    return_list = (last_price, brokerage_fee, current_balance, trade_volume,agg_balance,username,ticker_symbol, current_number_shares)


    if current_number_shares >= trade_volume:
        return True, return_list #success
    else:
        return False, return_list
    #if yes return new balance = current balance - transaction cost

def sell_db(return_list):
# return_list = (last_price, brokerage_fee, current_balance, trade_volume, agg_balance, username, ticker_symbol, current_number_shares)
    #check if user holds enough stock
    #update user's balance
    #insert transaction
    #if user sold all stocks holdings row should be deleted not set to 0
    connection = sqlite3.connect(database,check_same_thread = False)
    cursor = connection.cursor()
    last_price = return_list[0]
    brokerage_fee = return_list[1]
    current_balance = return_list[2]
    trade_volume = return_list[3]
    agg_balance = return_list[4]
    username = return_list[5]
    ticker_symbol = return_list[6]
    current_number_shares = return_list[7]

    #user
    cursor.execute("""
        UPDATE user
        SET current_balance = {}
        WHERE username = '{}'; 
    """.format(agg_balance, username)
    )
    #transactions
    cursor.execute("""
        INSERT INTO transactions(
        ticker_symbol,
        num_shares,
        owner_username,
        last_price
        ) VALUES(
        '{}',{},'{}',{}
        );""".format(ticker_symbol,trade_volume,username,last_price*-1)
    )
        #inserting information
    #holdings
    #at this point, it it assumed that the user has enough shares to sell.
    if current_number_shares >= trade_volume: #if user isn't selling all shares of a specific company
        tot_shares = float(current_number_shares)-float(trade_volume)
        cursor.execute('''
            UPDATE holdings
            SET num_shares = {}, last_price = {}
            WHERE username = "{}" AND ticker_symbol = "{}";
        '''.format(tot_shares, last_price, username, ticker_symbol)
        )
    connection.commit()
    cursor.close()
    connection.close()


def buy(username, ticker_symbol, trade_volume):
    #we need to return True or False for the confirmation message
    last_price = float(quote_last_price(ticker_symbol))
    brokerage_fee = 6.95 #TODO un-hardcode this value
    current_balance = get_user_balance(username) #TODO un-hardcode this value
    print("last price", last_price)
    print("brokerage fee", brokerage_fee)
    print("current balance", current_balance)
    transaction_cost = (trade_volume * last_price) + brokerage_fee
    print("Total cost of Transaction:", transaction_cost)
    left_over = float(current_balance) - float(transaction_cost)
    print("\nExpected user balance after transaction:", left_over)
    return_list = (last_price, brokerage_fee, current_balance, trade_volume,left_over,username,ticker_symbol)
    if transaction_cost <= current_balance:
        return True, return_list #success
    else:
        return False, return_list
    #if yes return new balance = current balance - transaction cost



def buy_db(return_list): # return_list = (last_price, brokerage_fee, current_balance, trade_volume, left_over, username, ticker_symbol)
    connection = sqlite3.connect(database,check_same_thread = False)
    cursor = connection.cursor()
    last_price = return_list[0]
    brokerage_fee = return_list[1]
    current_balance = return_list[2]
    trade_volume = return_list[3]
    left_over = return_list[4]
    username = return_list[5]
    ticker_symbol = return_list[6]

    #update users(current_balance), stocks, holdings.
    #users
        #updating the balance of the user
    cursor.execute("""
        UPDATE user
        SET current_balance = {}
        WHERE username = '{}'; 
    """.format(left_over, username)
    )
    #transactions
    cursor.execute("""
        INSERT INTO transactions(
        ticker_symbol,
        num_shares,
        owner_username,
        last_price
        ) VALUES(
        '{}',{},'{}',{}
        );""".format(ticker_symbol,trade_volume,username,last_price)
    )
        #inserting information
    #holdings
    query = 'SELECT count(*), num_shares FROM holdings WHERE username = "{}" AND ticker_symbol = "{}"'.format(username, ticker_symbol)
    cursor.execute(query)
    fetch_result = cursor.fetchone()
    if fetch_result[0] == 0: #if the user didn't own the specific stock
        cursor.execute('''
            INSERT INTO holdings(last_price, num_shares, ticker_symbol, username)
            VALUES (
            {},{},"{}","{}"
            );'''.format(last_price, trade_volume, ticker_symbol, username)
        )
    else: #if the user already has the same stock
        tot_shares = float(fetch_result[1])+float(trade_volume)
        cursor.execute('''
            UPDATE holdings
            SET num_shares = {}, last_price = {}
            WHERE username = "{}" AND ticker_symbol = "{}";
        '''.format(tot_shares, last_price, username, ticker_symbol)
        )
    connection.commit()
    cursor.close()
    connection.close()

def get_user_balance(username):
    connection = sqlite3.connect('trade_information.db', check_same_thread = False)
    cursor = connection.cursor()
    query = 'SELECT current_balance FROM user WHERE username = "{}"'.format(username)
    cursor.execute(query)
    fetched_result = cursor.fetchone()
    cursor.close()
    connection.close()
    return fetched_result[0] #cursor.fetchone() returns tuples

def calculate_balance(ticker_symbol, trade_volume):
    current_balance = 1000.0 #TODO un-hardcode this value
    last_price = float(quote_last_price(ticker_symbol))
    brokerage_fee = 6.95 #TODO un-hardcode this value
    transaction_cost = (trade_volume * last_price) + brokerage_fee
    new_balance = current_balance - transaction_cost
    return new_balance


def lookup_ticker_symbol(company_name):
    endpoint = 'http://dev.markitondemand.com/MODApis/Api/v2/Lookup/json?input='+company_name
    #FIXME The following return statement assumes that only one
    #ticker symbol will be matched with the user's input.
    #FIXME There also isn't any error handling.
    return json.loads(requests.get(endpoint).text)[0]['Symbol']


def quote_last_price(ticker_symbol):
    endpoint = 'http://dev.markitondemand.com/MODApis/Api/v2/Quote/json?symbol='+ticker_symbol
    return json.loads(requests.get(endpoint).text)['LastPrice']



"""if __name__ == '__main__':
    print(lookup_ticker_symbol("tesla"))
    print(find_quote("tesla"))
    print(lookup_ticker_symbol('asdfajHLSKDJHFA')) #FIXME This is the code that isn't passing"""