#!/usr/bin/env python3 

import json
import sqlite3
import requests
import view
import datetime
import pandas as pd

def current_user():
    connection = sqlite3.connect('trade_information.db',check_same_thread=False)
    cursor = connection.cursor()
    query = 'SELECT username FROM current_user;'
    cursor.execute(query)
    username = cursor.fetchone()
    return username[0]

def holdings():
    username = current_user()
    connection = sqlite3.connect('trade_information.db', check_same_thread=False)
    cursor = connection.cursor()
    query = "SELECT ticker_symbol, num_shares FROM holdings WHERE username='{}';".format(username)
    df = pd.read_sql_query(query, connection)
    return df

def transactions():
    username = current_user()
    connection = sqlite3.connect('trade_information.db', check_same_thread=False)
    cursor = connection.cursor()
    query = "SELECT ticker_symbol, num_shares,last_price,date FROM transactions WHERE owner_username='{}';".format(username)
    df = pd.read_sql_query(query, connection)
    return df

def funds():
    user_name = current_user()
    connection = sqlite3.connect('trade_information.db', check_same_thread=False)
    cursor= connection.cursor()
    query = "SELECT current_balance FROM user where username='{}';".format(user_name)
    cursor.execute(query)
    result = cursor.fetchone()
    return result[0]
    cursor.close()
    connection.close()

def log_in(user_name,password):
    connection = sqlite3.connect('trade_information.db',check_same_thread=False)
    cursor = connection.cursor()
    query = 'SELECT count(*) FROM user WHERE username = "{}" AND password = "{}";'.format(user_name, password)
    cursor.execute(query)
    result_tuple = cursor.fetchone()
    if result_tuple[0] == 0:
        return False
    elif result_tuple[0] == 1:
        cursor.execute("UPDATE current_user SET username = '{}' WHERE pk = 1;".format(user_name))
        connection.commit()
        return True
    else:
        pass
    cursor.close()
    connection.close()

def create_():
    connection = sqlite3.connect('trade_information.db',check_same_thread=False)
    cursor = connection.cursor()
    (new_user,new_password,new_funds) = view.create_menu()
    cursor.execute(
        """INSERT INTO user(
            username,
            password,
            current_balance
            ) VALUES(
            "{}",
            "{}",
            {}
        );""".format(new_user, new_password, new_funds)
    )
    connection.commit()
    cursor.close()
    connection.close()

def update_holdings():
    connection = sqlite3.connect('trade_information.db', check_same_thread=False)
    cursor = connection.cursor()
    query = 'DELETE FROM holdings WHERE num_shares = 0.0'
    cursor.execute(query)
    connection.commit()
    cursor.close()
    connection.close()

def sell(username, ticker_symbol, trade_volume):
    username = current_user()
    database = 'trade_information.db'
    connection = sqlite3.connect(database, check_same_thread=False)
    cursor = connection.cursor()
    query = 'SELECT count(*), num_shares FROM holdings WHERE username = "{}" AND ticker_symbol = "{}"'.format(username, ticker_symbol)
    cursor.execute(query)
    fetch_result = cursor.fetchone()
    if fetch_result[0] == 0:
        current_number_shares = 0
    else:
        current_number_shares = fetch_result[1]
    last_price = float(quote_last_price(ticker_symbol))
    brokerage_fee = 6.95 #TODO un-hardcode this value
    current_balance = get_user_balance(username) #TODO un-hardcode this value
    print("Last Price:", last_price)
    print("Brokerage Fee:", brokerage_fee)
    print("Current Balance:", current_balance)
    transaction_revenue = (trade_volume * last_price) - brokerage_fee
    print("Total Revenue of Transaction:", transaction_revenue)
    agg_balance = float(current_balance) + float(transaction_revenue)
    print("\nExpected user balance after transaction:", agg_balance)
    return_list = (last_price, brokerage_fee, current_balance, trade_volume,agg_balance,username,ticker_symbol,current_number_shares)
    if current_number_shares >= trade_volume:
        return True, return_list #success
    else:
        return False, return_list

def sell_db(return_list):
    database = 'trade_information.db'
    connection = sqlite3.connect(database,check_same_thread = False)
    cursor = connection.cursor()
    last_price = return_list[0]
    brokerage_fee = return_list[1]
    current_balance = return_list[2]
    trade_volume = return_list[3]
    agg_balance = return_list[4]
    username = current_user()
    ticker_symbol = return_list[6]
    current_number_shares = return_list[7]
    now = datetime.datetime.now()
    date = now.strftime("%Y-%m-%d %I:%M %p")

    cursor.execute("""
        UPDATE user
        SET current_balance = {}
        WHERE username = '{}';
    """.format(agg_balance, username)
    )
    cursor.execute("""
        INSERT INTO transactions(
        ticker_symbol,
        num_shares,
        owner_username,
        last_price,
        date
        ) VALUES(
        '{}',{},'{}',{},'{}'
        );""".format(ticker_symbol,trade_volume*-1,username,last_price,date)
    )
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
    connection = sqlite3.connect('trade_information.db',check_same_thread=False)
    cursor = connection.cursor()
    #we need to return True or False for the confirmation message
    trade_volume = float(trade_volume)
    last_price = float(quote_last_price(ticker_symbol))
    brokerage_fee = 6.95 #TODO un-hardcode this value
    username = current_user()
    current_balance = get_user_balance(username)
    print("Last price:", last_price)
    print("Brokerage fee:", brokerage_fee)
    print("Current balance:", current_balance)
    transaction_cost = (trade_volume * last_price) + brokerage_fee
    print("Total cost of Transaction:", transaction_cost)
    left_over = float(current_balance) - float(transaction_cost)
    print("\nExpected user balance after transaction:", left_over)
    return_list = (last_price, brokerage_fee, current_balance, trade_volume,left_over,username,ticker_symbol)
    if transaction_cost <= current_balance:
        return True, return_list #success
    else:
        return False, return_list

def buy_db(return_list): # return_list = (last_price, brokerage_fee, current_balance, trade_volume, left_over, username, ticker_symbol)
    connection = sqlite3.connect('trade_information.db',check_same_thread=False)
    cursor = connection.cursor()
    database = 'trade_information.db'
    username = current_user()
    connection = sqlite3.connect(database,check_same_thread = False)
    cursor = connection.cursor()
    last_price = return_list[0]
    brokerage_fee = return_list[1]
    current_balance = return_list[2]
    trade_volume = return_list[3]
    left_over = return_list[4]
    ticker_symbol = return_list[6]
    now = datetime.datetime.now()
    date = now.strftime("%Y-%m-%d %I:%M %p")
    #updating the balance of the user
    cursor.execute("""
        UPDATE user
        SET current_balance = {}
        WHERE username = '{}';
    """.format(left_over, username)
    )
    #undating the user's transactions
    cursor.execute("""
        INSERT INTO transactions(
        ticker_symbol,
        num_shares,
        owner_username,
        last_price,
        date
        ) VALUES(
        '{}',{},'{}',{},'{}'
        );""".format(ticker_symbol,trade_volume,username,last_price,date)
    )
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
    username = current_user()
    connection = sqlite3.connect('trade_information.db', check_same_thread = False)
    cursor = connection.cursor()
    query = 'SELECT current_balance FROM user WHERE username = "{}";'.format(username)
    cursor.execute(query)
    fetched_result = cursor.fetchone()
    cursor.close()
    connection.close()
    return fetched_result[0] #cursor.fetchone() returns tuples

def calculate_balance(ticker_symbol, trade_volume):
    connection = sqlite3.connect('trade_information.db',check_same_thread=False)
    cursor = connection.cursor()
    database = 'trade_information.db'

    #current_balance = 1000.0 #TODO un-hardcode this value
    last_price = float(quote_last_price(ticker_symbol))
    brokerage_fee = 6.95 #TODO un-hardcode this value
    transaction_cost = (trade_volume * last_price) + brokerage_fee
    new_balance = current_balance - transaction_cost
    return new_balance

def lookup_ticker_symbol(company_name):
    connection = sqlite3.connect('trade_information.db',check_same_thread=False)
    cursor = connection.cursor()
    database = 'trade_information.db'
    try:
        endpoint = 'http://dev.markitondemand.com/MODApis/Api/v2/Lookup/json?input='+company_name
        return json.loads(requests.get(endpoint).text)[0]['Symbol']
    except:
        return "The ticker symbol for the company you searched cannot be found. \nPlease try again."

def quote_last_price(ticker_symbol):
    connection = sqlite3.connect('trade_information.db',check_same_thread=False)
    cursor = connection.cursor()
    try:
        endpoint = 'http://dev.markitondemand.com/MODApis/Api/v2/Quote/json?symbol='+ticker_symbol
        return json.loads(requests.get(endpoint).text)['LastPrice']
    except:
        return "The last price for the company you searched cannot be found. \nPlease try again."

def calculate_p_and_l():
    username = current_user()
    connection = sqlite3.connect('trade_information.db',check_same_thread=False)
    cursor = connection.cursor()
    database = 'trade_information.db'
    #getting all ticker symbols for current user
    all_ticker_symbols = 'SELECT ticker_symbol FROM holdings WHERE username = "{}"'.format(username)
    cursor.execute(all_ticker_symbols)
    tksmb = cursor.fetchall()
    ticker_symbols = [str(symb) for symb in tksmb] # List of strings
    p_and_l= 0
    for symbol in ticker_symbols:
        stock_transactions = 'SELECT * FROM transactions WHERE owner_username = "{}" and ticker_symbol = "{}"'.format(username, symbol)
        cursor.execute(stock_transactions)
        transactions = cursor.fetchall()
        total_shares = 0
        price = 0
# SELECT sum(num_shares*last_price) from transactions where owner_username = 'John' AND ticker_symbol = 'x';
        for transaction in transactions:
            ticker_symbol = transaction[1]
            trade_volume = transaction[2]
            username = transaction[3]
            last_price = transaction[4]
            shares = 'SELECT num_shares FROM holdings WHERE username = "{}" AND ticker_symbol = "{}"'.format(username, symbol)
            cursor.execute(shares)
            nshares = cursor.fetchall()
            num_shares = [float(num[0]) for num in list(nshares)]
            total_shares += sum(num_shares)
            for shares in num_shares:
                purchased_price = 'SELECT last_price FROM transactions WHERE owner_username = "{}" AND ticker_symbol = "{}" AND num_shares = {}'.format(username, symbol, shares)
                cursor.execute(purchased_price)
                purchased_price = cursor.fetchall()
                purchase_price = [float(price[0]) for price in purchased_price]
                price += shares * purchase_price
    p_and_l += price/total_shares
    return p_and_l

def display_user_holdings():
    username=current_user()
    connection = sqlite3.connect("trade_information.db", check_same_thread=False)
    cursor = connection.cursor()
    cursor.execute("SELECT ticker_symbol,num_shares,last_price FROM holdings WHERE username='{}';".format(username))
    user_holdings = cursor.fetchall()
    cursor.close()
    connection.close()
    return user_holdings

def display_user_transactions():
    username=current_user()
    connection = sqlite3.connect("trade_information.db", check_same_thread=False)
    cursor = connection.cursor()
    cursor.execute("SELECT ticker_symbol,num_shares,last_price,date FROM transactions WHERE owner_username='{}';".format(username))
    user_transactions = cursor.fetchall()
    cursor.close()
    connection.close()
    return user_transactions

def get_users_with_holdings():
    connection = sqlite3.connect("trade_information.db", check_same_thread=False)
    cursor = connection.cursor()
    cursor.execute("SELECT username FROM holdings WHERE username NOT LIKE 'admin'")
    users = list(cursor.fetchall()) # List of tuples
    users_list = [str(user) for user in users] # List of strings
    cursor.close()
    connection.close()
    return users_list

def get_tkr_symb_from_holdings():
    connection = sqlite3.connect("trade_information.db", check_same_thread=False)
    cursor = connection.cursor()
    cursor.execute("SELECT ticker_symbol FROM holdings WHERE username NOT LIKE 'admin'")
    symbols = cursor.fetchall() # List of tuples
    symbols_list = [str(sym[0]) for sym in symbols] # List of strings
    cursor.close()
    connection.close()
    return symbols_list

def leaderboard():
    connection = sqlite3.connect('trade_information.db',check_same_thread=False)
    cursor = connection.cursor()
    usernames = get_users_with_holdings()
    ticker_symbols = get_tkr_symb_from_holdings()
    for user in usernames:
        ticker_symbol = cursor.execute('SELECT ticker_symbol FROM holdings WHERE username="{}"'.format(user))
        mkt_val = cursor.execute("SELECT (num_shares*last_price) FROM transactions WHERE owner_username = '{}' AND ticker_symbol = '{}';".format(user,ticker_symbol))
        cursor.execute("""
            INSERT INTO leaderboard(username, p_and_l)
            VALUES(
            '{}',{}
            );""".format(user, mkt_val)
        )
    connection.commit()
    cursor.close()
    connection.close()

def update_leaderboard():
    connection = sqlite3.connect('trade_information.db',check_same_thread=False)
    cursor = connection.cursor()
    username = get_users_with_holdings()
    for user in username:
        ticker_symbol = cursor.execute('SELECT ticker_symbol FROM holdings WHERE username="{}"'.format(user))
        mkt_val = cursor.execute("SELECT (num_shares*last_price) FROM transactions WHERE owner_username = '{}' AND ticker_symbol = '{}';".format(user,ticker_symbol))
        cursor.execute("""
            UPDATE leaderboard
            SET p_and_l={}
            WHERE
            username='{}'
            );""".format(mkt_val, username)
        )
    connection.commit()
    cursor.close()
    connection.close()

#leaderboard()
#    username = current_user()
#    symbols=cursor.execute("SELECT ticker_symbol FROM holdings WHERE user='{}'".format(username))
#    for symbol in symbols:
#        last_sale = float(quote_last_price(symbol))
        #select num_shares per symbol
#        shares = cursor.execute("SELECT num_shares FROM holdings WHERE ticker_symbol='{}'".format(symbol))
#        profit = last_sale

def log_out():
    log_in('aosdnoindc','aonsdoianf')
    try:
        cursor.close()
        connection.close()
    except:
        print('connection already closed')

if __name__ == '__main__':
    pass
