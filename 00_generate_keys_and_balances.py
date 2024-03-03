#!/usr/bin/python3

###########################################################################
#
# name          : 00_generate_keys.py
#
# purpose       : generate keys from seed, determine ETH balance
#
# usage         : python 00_generate_keys.py
#
# description   :
#  example usage :
#  > python3 00_generate_keys_and_balances.py --ethereum-wallet-from-mnemonic --mainnet
#  > python3 00_generate_keys_and_balances.py --create-ethereum-wallet --mainnet
#
###########################################################################


import bip32
import bip39
import blockutil
import datetime
import json


if __name__ == "__main__" :
    import argparse

    parser = argparse.ArgumentParser( description='BIP32 tools' )
    parser.add_argument( '-v', '--verbose',  help='Enable verbose mode',                                                     action='store_true' )
    parser.add_argument( '-3', '--bip32',  help='BIP32, default is BIP44 (hardened)',                                        action='store_true' )
    parser.add_argument( '-e', '--ethereum-wallet-from-mnemonic', help='EVM compatible keys from .secret passphrase',        action='store_true' )
    parser.add_argument( '-E', '--create-ethereum-wallet', help='Generate EVM compatible passphrase, keys, and address',     action='store_true' )
    parser.add_argument( '-m', '--mainnet', help='Use mainnet instead of testnet',                                           action='store_true' )
    args = parser.parse_args()

    bip44 = not args.bip32

    with open( ".secret", 'r' ) as f :
        mnemonic_string = f.read().strip() 

    with open( "data/config.json", 'r' ) as f :
        config_object = json.load( f )

    if args.mainnet :
        infura_url = config_object[ "mainnet_infura_url" ]
    else :
        infura_url = config_object[ "testnet_infura_url" ]

    web3 = blockutil.get_web3( infura_url ) 

    if args.ethereum_wallet_from_mnemonic :
        res = bip32.create_eth_keys_address_from_mnemonic( mnemonic_string, bip44=bip44, verbose=args.verbose )

    if args.create_ethereum_wallet :
        res = bip32.create_eth_keys_address_mnemonic( bip44=bip44, verbose=args.verbose )

    for row in res[ "accounts" ] :
        # get balance at address
        row[ "balance" ]  = str( blockutil.get_eth_balance( web3, row[ "address" ] ) )

    try : 
        print( json.dumps( res, indent=2 ) )
    except :
        pass
