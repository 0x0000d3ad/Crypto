#!/usr/bin/python3

###########################################################################
#
# name          : 04_transactions.py
#
# purpose       : get nft holders 
#
# usage         : python3 04_transactions.py
#
# description   :
#
###########################################################################

import blockutil
import datetime
import json
import os
import pyetherbalance
import requests
import sys
import time
import web3

from eth_utils import keccak, to_checksum_address
from urllib.request import urlopen
from web3 import HTTPProvider, Web3
from web3.auto import w3
from web3.contract import Contract


if __name__ == "__main__" :

    config_object = None
    with open( "data/config.json", 'r' ) as f :
        config_object = json.load( f )

    if not os.path.exists( "results/transactions.json" ) :
        transactions_json = blockutil.get_contract_transactions_from_etherscan( config_object )
        with open( "results/transactions.json", 'w' ) as f :
            f.write( json.dumps( transactions_json, indent=2 ) )

    with open( "results/transactions.json", 'r' ) as f :
        transactions_json = json.load( f )

    st = "sliced_transactions.txt"
    sliced = None
    if os.path.exists( st ) :
        with open( st, 'r' ) as f :
            sliced = [ i.strip() for i in f.readlines() ]
        print( len( sliced ) )

    minters = {}
    index = 0
    for transaction in transactions_json[ "result" ] :
        wallet_address = to_checksum_address( transaction[ "from" ] )
        txn = transaction[ "hash" ] #"0x373391d6e199990fc6206644ff15d09b027036cf49ff2cd19ef87a3e2a09c0ec"
        if sliced is not None :
            if txn not in sliced :
                continue

        try :
            func, params = blockutil.get_transaction( config_object, txn ) 
        except Exception as e :
            print( str( e ) )
            continue

        if func.function_identifier == "mintWhitelist" or func.function_identifier == "mint" :
            mint_amount = params[ "_mintAmount" ]
            print( wallet_address, func.function_identifier, mint_amount  )
            if wallet_address in minters :
                minters[ wallet_address ] += params[ "_mintAmount" ]
            else :
                minters[ wallet_address ] = params[ "_mintAmount" ]
        index += 1

    with open( "results/minters_dankbots.json", 'w' ) as f :
        f.write( json.dumps( minters, indent=2 ) )
