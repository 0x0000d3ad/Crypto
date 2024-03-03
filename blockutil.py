#!/usr/bin/python3

###########################################################################
#
# name          : blockutil.py
#
# purpose       : blockchain utility functions 
#
# usage         : import blockutil 
#
# description   :
# > https://ethereum.stackexchange.com/questions/91148/error-processing-transaction-request-already-known
#
###########################################################################

import datetime
import json
import os
import requests
import sys
import time
import web3

from eth_utils import keccak, to_checksum_address
from urllib.request import urlopen
from web3 import HTTPProvider, Web3
from web3.auto import w3
from web3.contract import Contract

GAS_SEND_TOKEN = 22000


###########################################################################
# get web3 instance and check connection 
###########################################################################

def get_web3( infura_url, verbose=False ) :
    web3 = Web3( Web3.HTTPProvider( infura_url ) )
    conn = web3.is_connected()
    if conn : 
        if verbose : print( "--> Web3 instance is connected" )
    else :
        print( "--> Error: Web3 instance is not connected; Exiting..." )
        sys.exit()
    return web3


###########################################################################
# get web3 instance and check connection 
###########################################################################

def get_contract( web3, contract_address, abi, verbose=False ) :
    return web3.eth.contract( address=contract_address, abi=abi )


###########################################################################
# get current eth gas prices
# - other options for eth gas prices    : 
#   https://cryptomarketpool.com/get-gas-prices-from-the-eth-gas-station-and-web3-py-in-python/
#   https://ethgasstation.info/
###########################################################################

def get_eth_gas_price( web3 ) :
    web3.eth.fee_history(20,'pending',[20,50,80])
    res = web3.eth.get_block('pending').baseFeePerGas
    return res


###########################################################################
# get ethereum balance at address
###########################################################################

def get_eth_balance( web3, address, ether=True ) :

    # get ether balance at address
    if ether :
        return_value = web3.from_wei( web3.eth.get_balance( address ), 'ether' )
    else :
        return_value = web3.eth.get_balance( address )

    return return_value


###########################################################################
# get token balance at address 
###########################################################################

def get_tokenbalance( web3, address, contract, ether=True ) :

    if ether :
        return_value = web3.from_wei( contract.call().balanceOf( address ), 'ether' )
    else :
        return_value = contract.call().balanceOf( address )

    return return_value



###########################################################################
# send ethereum to address, returns tx hash
###########################################################################

def send_eth( web3, chain_id, account, to_address, ether_amount, verbose=False ) :

    # Set up the addresses to send from and to
    from_private_key = account[ "private_key" ]
    from_address = account[ "address" ] 

    # Convert to checksumadress (not to loose bites when sending)
    to_address_checksum   = to_checksum_address( to_address )
    from_address_checksum = to_checksum_address( from_address )

    # Set up the nonce
    nonce = web3.eth.get_transaction_count( from_address_checksum, 'pending' ) # 'pending' solves error {'code': -32000, 'message': 'already known'} 
    balance = get_eth_balance( web3, from_address_checksum, ether=True )
    if verbose :
        print( f"--> nonce: {nonce}" )
        print( f"--> balance: {balance}" )

    try :
        gas_price = get_eth_gas_price( web3 )
    except :
        gas_price = web3.to_wei( 50, 'gwei' )

    # Set up the transaction
    tx = {
        'nonce': nonce,
        'to': to_address_checksum,
        'value' : web3.to_wei( str( ether_amount ), 'ether' ),
        'gas': GAS_SEND_TOKEN,
        'gasPrice': gas_price,
        'chainId' : chain_id
    }

    signed_tx = web3.eth.account.sign_transaction( tx, from_private_key )

    try :
        tx_hash = web3.eth.send_raw_transaction( signed_tx.rawTransaction )
    except Exception as e :
        print( "--> Error in transaction" )
        print( e )
        print( "--> Exiting..." )
        sys.exit()

    return web3.to_hex( tx_hash )


###########################################################################
# send token to address, returns tx hash
###########################################################################

def send_token( web3, chain_id, account, to_address, ether_amount, contract, verbose=False ) :

    # Set up the addresses to send from and to
    from_private_key = account[ "private_key" ]
    from_address = account[ "address" ] 

    # Convert to checksumadress (not to loose bites when sending)
    to_address_checksum   = to_checksum_address( to_address )
    from_address_checksum = to_checksum_address( from_address )

    # convert eth amount
    raw_amount = web3.to_wei( str( ether_amount ), 'ether' )

    # Set up the nonce
    nonce = web3.eth.get_transaction_count( from_address_checksum, 'pending' ) # 'pending' solves error {'code': -32000, 'message': 'already known'} 
    if verbose :
        print( f"--> nonce: {nonce}" )

    try :
        gas_price = get_eth_gas_price( web3 )
    except :
        gas_price = web3.to_wei( 50, 'gwei' )

    # Set up the transaction
    tx = {
        'nonce': nonce,
        'gas': GAS_SEND_TOKEN,
        'gasPrice': gas_price,
        'chainId' : chain_id
    }

    txn = contract.functions.transfer( to_address_checksum, raw_amount ).build_transaction( tx )
    signed_txn = web3.eth.account.sign_transaction( txn, from_private_key )

    try :
        tx_hash = w3.eth.send_raw_transaction( signed_txn.rawTransaction )
    except Exception as e :
        print( "--> Error in transaction" )
        print( e )
        print( "--> Exiting..." )
        sys.exit()

    return web3.to_hex( tx_hash )


###########################################################################
# get erc 721 tokens that have been minted
# - must have contract abi and address
# - contract must contain totalSupply function
###########################################################################


###########################################################################
# get erc 721 tokens that have been minted
# - must have contract abi and address
# - contract must contain totalSupply function
###########################################################################

def get_total_supply( config_object, contract_address=None  ) :

    # configure web3 from infura link
    infura_url = config_object[ "infura_url" ] 
    web3 = Web3( Web3.HTTPProvider( infura_url ) )

    # get contract address from config
    if contract_address is None :
        contract_address = config_object[ "contract_address" ]

    # convert address to checksummed address 
    contract_address = to_checksum_address( contract_address )

    # get abi 
    abi = None
    with open( config_object[ "abi_filename" ], 'r' ) as f :
        abi = json.load( f )

    # load eth contract from address 
    db = web3.eth.contract( address=contract_address, abi=json.dumps( abi ) )

    # get total supply 
    total_supply = db.functions.totalSupply().call()

    return total_supply


###########################################################################
# get transaction by transaction hash
# - uses the Web3 api
###########################################################################

def get_transaction( config_object, txn ) :
    abi = None
    with open( config_object[ "abi_filename" ], 'r' ) as f :
        abi = json.load( f )

    w3 = Web3( HTTPProvider( config_object[ "infura_url" ] ) )
    data_json = w3.eth.getTransaction( txn )
    contract = w3.eth.contract(address=to_checksum_address( config_object[ "contract_address" ] ), abi=abi)
    func_obj, func_params = contract.decode_function_input( data_json[ "input" ] )
    return func_obj, func_params


###########################################################################
# get transaction by transaction hash
# - uses etherscan's api 
###########################################################################

def get_transaction_from_etherscan( config_object, txn ) :
    transaction_url = "https://api.etherscan.io/api?module=proxy&action=eth_getTransactionByHash&txhash=%s&apikey=%s"
    url = transaction_url % ( txn, config_object[ "etherscan_key" ] )
    response = urlopen( url )
    data_json = json.loads( response.read() )

    return data_json


###########################################################################
# get all transactions for a contract address 
# - uses etherscan's api 
###########################################################################

def get_contract_transactions_from_etherscan( config_object, contract_address=None ) :
    if contract_address is None :
        contract_address = config_object[ "contract_address" ]

    contract_address = to_checksum_address( contract_address )

    transaction_url = "https://api.etherscan.io/api?module=account&action=txlist&address=%s&startblock=0&endblock=99999999&sort=asc&apikey=%s" 
    url = transaction_url % ( contract_address, config_object[ "etherscan_key" ] )
    response = urlopen( url )
    data_json = json.loads( response.read() )

    return data_json


###########################################################################
# get abi given contract address
# - uses etherscan's api 
###########################################################################

def get_abi_from_etherscan( config_object, contract_address=None ) :
    if contract_address is None :
        contract_address = config_object[ "contract_address" ]

    contract_address = to_checksum_address( contract_address )

    transaction_url = "https://api.etherscan.io/api?module=contract&action=getabi&address=%s&apikey=%s"
    url = transaction_url % ( contract_address, config_object[ "etherscan_key" ] )
    response = urlopen( url )
    data_json = json.loads( response.read() )

    return_value = json.loads( data_json[ "result" ] )

    return return_value


###########################################################################
# main - where the magic happens 
###########################################################################

if __name__ == "__main__" :
    import optparse
    default_config = "data/config.json"
    default_wallet = "0xF35A192475527f80EfcfeE5040C8B5BBB596F69A"
    default_txn = "0x373391d6e199990fc6206644ff15d09b027036cf49ff2cd19ef87a3e2a09c0ec"
    parser = optparse.OptionParser()
    parser.add_option( '-c', '--config',   dest='config',  action='store',      default=default_config, help='Config file', type="string" )
    parser.add_option( '-w', '--wallet',   dest='wallet',  action='store',      default=default_wallet, help='Wallet', type="string" )
    parser.add_option( '-t', '--txn',      dest='txn'   ,  action='store',      default=default_txn,    help='Wallet', type="string" )
    parser.add_option( '-g', '--gas',      dest='gas',     action='store_true', default=False,          help='Get gas prices'       )
    parser.add_option( '-b', '--balance',  dest='balance', action='store_true', default=False,          help='Get ethereum balance' )
    parser.add_option( '-s', '--send',     dest='send',    action='store_true', default=False,          help='Send ETH' )
    parser.add_option( '-T', '--total',    dest='total',   action='store_true', default=False,          help='Get totalSupply' )
    parser.add_option( '-x', '--get_txn',  dest='get_txn', action='store_true', default=False,          help='Get transaction' )
    ( options, args ) = parser.parse_args()

    config_object = None
    with open( options.config, 'r' ) as f :
        config_object = json.load( f )

    # get gas prices
    if options.gas :
        print( "--> Getting ETH gas price" )
        res = get_eth_gas_price( config_object )
        print( json.dumps( res, indent=2 ) )

    # get eth balance
    if options.balance :
        address = options.wallet
        print( "--> Getting ETH balance for wallet '%s'" % address )
        res = get_eth_balance( config_object, address )
        print( json.dumps( res, indent=2 ) )

    # send eth
    if options.send :
        eth_amount = 0
        from_account = ""
        to_account = ""
        #send_ethereum( config_object, eth_amount, from_account, to_account, verbose=True )    

    # get total supply
    if options.total :
        print( "--> Getting total supply for contract address: '%s'" % config_object[ "contract_address" ] )
        res = get_total_supply( config_object )
        print( res )

    # get transaction information
    if options.get_txn :
        import pprint
        print( "--> Getting transaction from hash (using web3 module): '%s'" % options.txn )
        func_obj, func_params = get_transaction( config_object, options.txn )
        print( func_obj.function_identifier )
        pprint.pprint( func_params )

        print( "--> Getting transaction from hash (using etherscan): '%s'" % options.txn )
        res = get_transaction_from_etherscan( config_object, options.txn )
        pprint.pprint( res )
