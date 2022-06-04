#!/usr/bin/python3

###########################################################################
#
# name          : 03_get_holders.py
#
# purpose       : get nft holders 
#
# usage         : python3 03_get_holders 
#
# description   :
# - eth gas prices    : 
#   https://cryptomarketpool.com/get-gas-prices-from-the-eth-gas-station-and-web3-py-in-python/
#   https://ethgasstation.info/
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

from eth_utils import keccak, to_checksum_address
from web3 import HTTPProvider, Web3
from web3.auto import w3


def restart_line() :
    sys.stdout.write( '\r' )
    sys.stdout.flush()


def get_holders( config_object, abi_filename=None, contract_address=None, output_filename=None, start_index=0 ) :
    if abi_filename is None :
        try :
            abi_filename = config_object[ "abi_filename" ]
        except Exception as e :
            print( "--> Please supply ABI: '%s'" % str( e ) )
            sys.exit()

    if contract_address is None :
        try :
            contract_address = config_object[ "contract_address" ]
        except Exception as e :
            print( "--> Please supply contract address: '%s'" % str( e )  )
            sys.exit()

    if output_filename is None :
        try :
            output_filename = config_object[ "output_filename" ]
        except Exception as e :
            print( "--> Please supply output filename: '%s'" % str( e )  )
            sys.exit()

    contract_address_chk = to_checksum_address( contract_address )
    infura_url = config_object[ "infura_url" ] 
    web3_inst = Web3( Web3.HTTPProvider( infura_url ) )

    abi = []
    with open( abi_filename, 'r' ) as f :
        abi = json.load( f )

    the_contract = web3_inst.eth.contract( address=contract_address_chk, abi=json.dumps( abi ) )

    total_supply = the_contract.functions.totalSupply().call()

    print( "--> Total Supply : %u" % total_supply )
    print( "--> Begin" )
    for i in range( start_index, total_supply ) : 
        restart_line()
        sys.stdout.write( str( i ) )
        sys.stdout.flush()

        try :
            address = the_contract.functions.ownerOf( i ).call()
        except Exception as e :
            print( "--> Error index %u: %s" % ( i, str( e ) ) )

        with open( output_filename, 'a' ) as f :
            f.write( "%s\n" % address )
        
        time.sleep( 1 )

if __name__ == "__main__" :
    config_object = None
    with open( "data/config.json", 'r' ) as f :
        config_object = json.load( f )

#    bakc_contract = "0xba30e5f9bb24caa003e9f2f0497ad287fdf95623"
#    nounpunks_contract = "0xe169c2ed585e62b1d32615bf2591093a629549b6"
#    ocm_contract = "0x960b7a6bcd451c9968473f7bbfd9be826efd549a"
#
#    bakc_abi = "data/bakc.json"
#    nounpunks_abi = "data/nounpunks.json"
#    ocm_abi = "data/ocm.json"
#
#    bakc_holders = "results/holders_bakc.txt"
#    nounpunks_holders = "results/holders_nounpunks.txt"
#    ocm_holders = "results/holders_ocm.txt"
#
#    get_holders( config_object, abi_filename=bakc_abi, contract_address=bakc_contract, output_filename=bakc_holders )
#    get_holders( config_object, abi_filename=nounpunks_abi, contract_address=nounpunks_contract, output_filename=nounpunks_holders )
#    get_holders( config_object, abi_filename=ocm_abi, contract_address=ocm_contract, output_filename=ocm_holders )
    get_holders( config_object, output_filename="results/holders_dankbots.txt" )


