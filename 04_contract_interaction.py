#!/usr/bin/python3

###########################################################################
#
# name          : 01_contract_interaction.py
#
# purpose       : interact with contract 
#
# usage         : python 01_contract_interaction.py
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

    print( "--> Contract address:\n--> %s" % contract.address )
    print( "--> Contract total supply:\n--> %s" % str( contract.functions.totalSupply().call() ) )
    print( "--> Contract name:\n--> %s" % contract.functions.name().call() )
    print( "--> Contract symbol:\n--> %s" % contract.functions.symbol().call() )
    print( "--> Balance of '%s':\n--> %s" % ( from_account, contract.functions.balanceOf( from_account ).call() ) )


    unicorns = w3.eth.contract(address=contract_address, abi=EIP20_ABI)
    nonce = w3.eth.getTransactionCount(from_account)  

    # Build a transaction that invokes this contract's function, called transfer
    unicorn_txn = unicorns.functions.transfer( to_account, 1,).buildTransaction({ 'chainId': 1, 'gas': 70000, 'gasPrice': w3.toWei('1', 'gwei'), 'nonce': nonce, })
    print( unicorn_txn )

    signed_txn = w3.eth.account.signTransaction(unicorn_txn, private_key=private_key)
    print( signed_txn.hash )
    print( signed_txn.rawTransaction )
    print( signed_txn.r )
    print( signed_txn.s )
    print( signed_txn.v )

    w3.eth.sendRawTransaction(signed_txn.rawTransaction)  

    # When you run sendRawTransaction, you get the same result as the hash of the transaction:
    print( w3.toHex( w3.sha3(signed_txn.rawTransaction ) ) )
