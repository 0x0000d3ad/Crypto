#!/usr/bin/python

###########################################################################
#
# name          : 02_send_eth.py
#
# purpose       : send eth or native token such as matic
#
# usage         : python3 02_send_eth.py
#
# description   :
#
###########################################################################


import bip32
import blockutil
import json
import sys
import time


def get_balances( web3, account, to_address ) :
    balance_from = blockutil.get_eth_balance( web3, account[ "address" ] )
    balance_to = blockutil.get_eth_balance( web3, to_address )

    return_value = { 
        'from_address' : account[ "address" ],
        'from_balance' : str( balance_from ),
        'to_address' : to_address,
        'to_balance' : str( balance_to )
    }

    return return_value

if __name__ == "__main__" :
    import argparse

    parser = argparse.ArgumentParser( description='BIP32 tools' )
    parser.add_argument( '-v', '--verbose',      help='Enable verbose mode',                 action='store_true' )
    parser.add_argument( '-3', '--bip32',        help='BIP32, default is BIP44 (hardened)',  action='store_true' )
    parser.add_argument( '-s', '--send-eth',     help='Send eth (or native currency)',       action='store_true' )
    parser.add_argument( '-m', '--mainnet',      help='Use mainnet instead of testnet',      action='store_true' )
    parser.add_argument( '-f', '--from-account', help='From account, defaults to 0 (first)', action='store', type=int, default=0 )
    parser.add_argument( '-t', '--to-address',   help='To address (eth address)',            action='store', type=str, default="0x102B9614c4309a3627d6c8E8c6272E9f74dD8923" )
    parser.add_argument( '-e', '--ether-amount', help='Ethereum amount',                     action='store', type=str, default="0.01" )
    args = parser.parse_args()

    bip44 = not args.bip32

    with open( ".secret", 'r' ) as f :
        mnemonic_string = f.read().strip() 

    with open( "data/config.json", 'r' ) as f :
        config_object = json.load( f )

    if args.mainnet :
        infura_url = config_object[ "mainnet_infura_url" ]
        chain_id = config_object[ "mainnet_chain_id" ]
    else :
        infura_url = config_object[ "testnet_infura_url" ]
        chain_id = config_object[ "testnet_chain_id" ]

    web3 = blockutil.get_web3( infura_url ) 

    if args.send_eth :
        res = bip32.create_eth_keys_address_from_mnemonic( mnemonic_string, bip44=bip44, verbose=args.verbose )
        account = res[ "accounts" ][ args.from_account ]

        temp = get_balances( web3, account, args.to_address )
        print( "Balances before:" )
        print( json.dumps( temp, indent=2 ) )

        transaction_id = blockutil.send_eth( web3, chain_id, account, args.to_address, float( args.ether_amount ), verbose=args.verbose ) 
        print( f"Transaction ID: {transaction_id}" )

        time.sleep( 5 )
        temp = get_balances( web3, account, args.to_address )
        print( "Balances after:" )
        print( json.dumps( temp, indent=2 ) )
