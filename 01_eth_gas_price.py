#!/usr/bin/python

###########################################################################
#
# name          : 01_eth_gas_price.py
#
# purpose       : get eth gas price 
#
# usage         : python 01_eth_gas_price.py
#
# description   :
#  example usage :
#  > python3 01_eth_gas_price.py --get-ethereum-gas-price --mainnet
#  > python3 01_eth_gas_price.py --monitor-ethereum-gas-price --mainnet
#
###########################################################################


import blockutil
import json
import os
import sys
import time


def monitor( web3 ) :
    gas_low = None
    gas_high = None
    while True :
        try :
            try :
                res = blockutil.get_eth_gas_price( web3 )
            except Exception as e :
                print( str( e ) )
                web3 = blockutil.get_web3( infura_url ) 
                res = blockutil.get_eth_gas_price( web3 )

            # get gas price in gwei
            gas_price = res / 10**9

            if gas_low is not None :
                if gas_low > gas_price :
                    gas_low = gas_price
            else :
                gas_low = gas_price

            if gas_high is not None :
                if gas_high < gas_price :
                    gas_high = gas_price
            else :
                gas_high = gas_price

            print( f"Current GWei: {gas_price}, low={gas_low}, high={gas_high}", end="\r" )
            if gas_price < 25 :
                os.system( "say 'gas alert'" )
                os.system( "say 'gas alert'" )
            time.sleep( 5 * 60 )

        except KeyboardInterrupt as e :
            print( "--> Quitting" + " ".join( " " * 50 )  )
            sys.exit()


if __name__ == "__main__" :
    import argparse

    parser = argparse.ArgumentParser( description='BIP32 tools' )
    parser.add_argument( '-v', '--verbose',  help='Enable verbose mode',                                  action='store_true' )
    parser.add_argument( '-g', '--get-ethereum-gas-price',  help='Get ethereum gas price in gwei',        action='store_true' )
    parser.add_argument( '-M', '--monitor-ethereum-gas-price', help='Monitor ethereum gas price in gwei', action='store_true' )
    parser.add_argument( '-m', '--mainnet', help='Use mainnet instead of testnet',                        action='store_true' )
    args = parser.parse_args()

    with open( "data/config.json", 'r' ) as f :
        config_object = json.load( f )

    if args.mainnet :
        infura_url = config_object[ "mainnet_infura_url" ]
    else :
        infura_url = config_object[ "testnet_infura_url" ]

    web3 = blockutil.get_web3( infura_url ) 

    if args.monitor_ethereum_gas_price :
        monitor( web3 )

    if args.get_ethereum_gas_price :
        res = blockutil.get_eth_gas_price( web3 )
        print( res / 10**9 )
