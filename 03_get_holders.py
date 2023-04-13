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
    abi = []
    if abi_filename is None :
#        try :
#            abi_filename = config_object[ "abi_filename" ]
#        except Exception as e :
#            print( "--> Please supply ABI: '%s'" % str( e ) )
#            sys.exit()
        abi = blockutil.get_abi_from_etherscan( config_object, contract_address )
    else :
        with open( abi_filename, 'r' ) as f :
            abi = json.load( f )

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


    the_contract = web3_inst.eth.contract( address=contract_address_chk, abi=json.dumps( abi ) )

    total_supply = the_contract.functions.totalSupply().call()

    print( "--> Total Supply : %u" % total_supply )
    print( "--> Begin" )
    for i in range( start_index, total_supply ) : 
        restart_line()
        sys.stdout.write( str( i ) )
        sys.stdout.flush()

        address = None
        try :
            address = the_contract.functions.ownerOf( i ).call()
        except Exception as e :
            print( "--> Error index %u: %s" % ( i, str( e ) ) )

        if address is not None :
            with open( output_filename, 'a' ) as f :
                f.write( "%s\n" % address )
        
        time.sleep( 1 )

if __name__ == "__main__" :
    config_object = None
    with open( "data/config.json", 'r' ) as f :
        config_object = json.load( f )

    bakc_contract = "0xba30e5f9bb24caa003e9f2f0497ad287fdf95623"
    nounpunks_contract = "0xe169c2ed585e62b1d32615bf2591093a629549b6"
    ocm_contract = "0x960b7a6bcd451c9968473f7bbfd9be826efd549a"
    larvalad_contract = "0x5755Ab845dDEaB27E1cfCe00cd629B2e135Acc3d"
    parrot_contract = "0x2615e05181E3CF8b0816272818c6F0d0c9973D84"
    alienfrens_contract = "0x123b30E25973FeCd8354dd5f41Cc45A3065eF88C"
    nightbirds_contract = "0x64b6b4142d4D78E49D53430C1d3939F2317f9085"
    cryptoadz_contract = "0x1CB1A5e65610AEFF2551A50f76a87a7d3fB649C6"
    dankgoblin_contract = "0x8071cad0ebe4fe773b6763a99aedfb4aa0711e27"
    dostrashbirds_contract = "0x46d15ccfc1375e658fd0d59c1be93ac5b7350b43"
    wgmis_contract = "0x46d15ccfc1375e658fd0d59c1be93ac5b7350b43"
    dos_amigos_contract = "0xd7EA09229Eb0BA38Cb38014f12A0bEC3C8B5E51E"

    bakc_abi = "data/bakc.json"
    nounpunks_abi = "data/nounpunks.json"
    ocm_abi = "data/ocm.json"
    larvalad_abi = "data/larvalad_abi.json"
    parrot_abi = "data/parrot_abi.json"
    alienfrens_abi = "data/alienfrens_abi.json"

    bakc_holders = "results/holders_bakc.txt"
    nounpunks_holders = "results/holders_nounpunks.txt"
    ocm_holders = "results/holders_ocm.txt"
    larvalad_holders = "results/holders_larvalads.txt"
    parrot_holders = "results/holders_parrots.txt"
    alienfrens_holders = "results/holders_alienfrens.txt"
    nightbirds_holders = "results/holders_nightbirds.txt"
    cryptoadz_holders = "results/holders_cryptoadz.txt"
    dankgoblin_holders = "results/holders_dankgoblin.txt"

#    get_holders( config_object, output_filename="results/holders_dankbots.txt" )
#    get_holders( config_object, contract_address=bakc_contract, output_filename="results/holders_dostrashbirds.txt" )
#    get_holders( config_object, contract_address=wgmis_contract, output_filename="results/holders_wgmis.txt" )
    get_holders( config_object, contract_address=dos_amigos_contract, output_filename="results/holders_dos_amigos.txt" )
#    get_holders( config_object, abi_filename=bakc_abi, contract_address=bakc_contract, output_filename=bakc_holders )
#    get_holders( config_object, abi_filename=nounpunks_abi, contract_address=nounpunks_contract, output_filename=nounpunks_holders )
#    get_holders( config_object, abi_filename=ocm_abi, contract_address=ocm_contract, output_filename=ocm_holders )
#    get_holders( config_object, abi_filename=larvalad_abi, contract_address=larvalad_contract, output_filename=larvalad_holders )
#    get_holders( config_object, abi_filename=parrot_abi, contract_address=parrot_contract, output_filename=parrot_holders )
#    get_holders( config_object, abi_filename=alienfrens_abi, contract_address=alienfrens_contract, output_filename=alienfrens_holders )
#    get_holders( config_object, contract_address=nightbirds_contract, output_filename=nightbirds_holders )
#    get_holders( config_object, contract_address=cryptoadz_contract, output_filename=cryptoadz_holders )
#    get_holders( config_object, contract_address=dankgoblin_contract, output_filename=dankgoblin_holders )
