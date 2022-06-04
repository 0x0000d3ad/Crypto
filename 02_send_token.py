#!/usr/bin/python3

###########################################################################
#
# name          : 02_send_token.py
#
# purpose       : interact with contract 
#
# usage         : python 02_send_token.py
#
# description   :
#
###########################################################################

import bip32
import bip39
import json
import web3

from ethtoken.abi import EIP20_ABI
from web3 import HTTPProvider, Web3
from web3.auto import w3
from web3.middleware import geth_poa_middleware


if __name__ == "__main__" :
    config_object = None
    with open( "data/config.json", 'r' ) as f :
        config_object = json.load( f )

    contract_address = "0xE5CFb440ddf8FC66a84E141413E9b4ED72A28d91"
    to_account       = "0x60d4d112c227D9eB812e02BFAa06ea198B863651"
    from_account     = "0x102B9614c4309a3627d6c8E8c6272E9f74dD8923"

    mnemonic_string  = ""
    with open( '.secret', 'r' ) as f :
        mnemonic_string = f.read().strip()
 
    print( "--> Get private key to sign transaction" )
    seed = bip39.generate_seed_from_mnemonic( mnemonic_string )
    private_key = bip32.get_private_key( seed )

    w3 = Web3( HTTPProvider( config_object[ "rinkeby_infura_url" ] ) )
    w3.middleware_stack.inject( web3.middleware.geth_poa_middleware, layer=0 )
    # if 'middleware_stack' does not work, use 'middleware_onion'
    # https://ethereum.stackexchange.com/questions/74044/attributeerror-web3-object-has-no-attribute-middleware-stack
    # w3.middleware_onion.inject( web3.middleware.geth_poa_middleware, layer=0 ) 
    print( "--> Connected: %s" % str( w3.isConnected() ) )

    abi = []
    with open( "data/Trylliun.json", 'r' ) as f :
        abi = json.load( f )


    contract = w3.eth.contract(address=contract_address, abi=abi)

    print( contract.functions.totalSupply().call() )
    print( contract.functions.name().call() )
    print( contract.functions.symbol().call() )

    nonce = w3.eth.getTransactionCount( from_account )
    
    transaction = {
        'nonce': nonce,
        'to': to_account,
        'value': w3.toWei(1, 'ether'),
        'gas': 2000000,
        'gasPrice': w3.toWei('50', 'gwei'),
    }

    amount = 1000
#    transfer = contract.sendTransaction( { 'from': from_address }).transfer(to_address, amount)
#    transfer = contract.functions.transfer(to_account, 121212).transact()

#    print( "--> Building transaction" )
#    transaction_details = { 'chainId': 4, 'gas':70000, 'nonce': w3.eth.getTransactionCount( from_account ) }
#    print( "--> Transfer to '%s'" % to_account )
#    transaction = contract.functions.transfer( to_account, 0x10 ).buildTransaction()

    print( "--> Sign transaction" )
    signed_txn = w3.eth.account.signTransaction( transaction, private_key )
    print( "--> Get transaction hash" )
    txn_hash = w3.eth.sendRawTransaction( signed_txn.rawTransaction )

    print( txn_hash )

#    tx_hash = contract.transfer( signed_txn.rawTransaction )
#    print( w3.toHex( tx_hash ) )

