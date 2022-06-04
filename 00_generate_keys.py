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
#
###########################################################################

import bip32
import bip39
import blockutil
import datetime
import json


if __name__ == "__main__" :
    config_object = None
    with open( "data/config.json", 'r' ) as f :
        config_object = json.load( f )


    index = 0
#    while index < 10 :
#        res = {}
#
#        # generate seed
#        res[ "seed" ]     = bip39.generate_seed()
#
#        # get address from seed 
#        res[ "address" ]  = bip32.get_address_from_seed( res[ "seed" ] )
#
#        # get balance at address
#        res[ "balance" ]  = blockutil.get_eth_balance( res[ "address" ] )
#
#        print( json.dumps( res, indent=2 ) )
#        if res[ "balance" ] != 0 :
#            date_string = datetime.datetime.now().strftime( "%Y%m%d%H%M%S" )
#            with open( "data/%s.json" % date_string, 'w' ) as f : 
#                f.write( json.dumps( res, indent=2 ) )
#
#        index += 1


    # generate seed
    res = {}
    res[ "seed" ]     = bip39.generate_seed()

    # get address from seed 
    res[ "address" ]  = bip32.get_address_from_seed( res[ "seed" ] )

    # get balance at address
    res[ "balance" ]  = blockutil.get_eth_balance( config_object, res[ "address" ] )

    print( json.dumps( res, indent=2 ) )


    res2 = {}
    res2[ "seed" ] = "500302cc2d4374934e5a62fbd20225e930f1c328097ce9c5eb84bf748bcffc6a"
    res2[ "address" ] = bip32.get_address_from_seed( res2[ "seed" ] )
    print( json.dumps( res2, indent=2 ) )
