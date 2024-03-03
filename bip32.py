#!/usr/bin/python3

###########################################################################
#
# name          : bip32.py
#
# purpose       : generate keys from seed
#
# usage         : python bip32.py
#
# description   :
# > https://github.com/marcgarreau/ethereum-notebooks/blob/master/bip32.ipynb
# > https://github.com/satoshilabs/slips/blob/master/slip-0044.md
# > https://wolovim.medium.com/ethereum-201-hd-wallets-11d0c93c87f7
# > https://stackoverflow.com/questions/46279121/how-can-i-find-keccak-256-hash-in-python
# > https://stackoverflow.com/questions/54202617/how-to-generate-bitcoin-keys-addresses-from-a-seed-in-python
#
###########################################################################


import base58
import binascii
import bip32utils
import bip39
import bitarray
import hmac
import hashlib
import json
import mnemonic
import sys

from ecdsa import SECP256k1
from ecdsa.ecdsa import Public_key
from eth_utils import keccak, to_checksum_address

VERSION_BYTES = {
    'mainnet_public': binascii.unhexlify( '0488b21e' ),
    'mainnet_private': binascii.unhexlify( '0488ade4' ),
    'testnet_public': binascii.unhexlify( '043587cf' ),
    'testnet_private': binascii.unhexlify( '04358394' ),
}



###########################################################################
# Some elliptic curve utility functions
# 
# You can't escape math.
###########################################################################

SECP256k1_GEN = SECP256k1.generator


###########################################################################
# Compresses curve point
###########################################################################

def serialize_curve_point( p ) :
   x, y = p.x(), p.y()
   if y & 1:
      return b'\x03' + x.to_bytes( 32, 'big' )
   else:
      return b'\x02' + x.to_bytes( 32, 'big' )


###########################################################################
# Get point from integer
###########################################################################

def curve_point_from_int( k ) :
   return Public_key( SECP256k1_GEN, SECP256k1_GEN * k ).point


###########################################################################
# Define a fingerprint function
# 
# A fingerprint is four bytes - a link between child and parent keys.
###########################################################################

def fingerprint_from_priv_key( k ) :
    K = curve_point_from_int( k )
    K_compressed = serialize_curve_point( K )
    identifier = hashlib.new( 'ripemd160', hashlib.sha256( K_compressed ).digest(), ).digest()
    return identifier[ : 4 ]


###########################################################################
# Define the child key derivation function
###########################################################################

SECP256k1_ORD = SECP256k1.order


###########################################################################
# generate a hardened or non-hardened private key
###########################################################################

def get_private_key( private_key, chain_code, child_number ) :
    if child_number >= 2 ** 31:
        # Generate a hardened key
        data = b'\x00' + private_key.to_bytes( 32, 'big' )
    else:
        # Generate a non-hardened key
        p = curve_point_from_int( private_key )
        data = serialize_curve_point( p )

    data += child_number.to_bytes( 4, 'big' )

    hmac_bytes = hmac.new( chain_code, data, hashlib.sha512 ).digest()
    L, R = hmac_bytes[ : 32 ], hmac_bytes[ 32 : ]

    L_as_int = int.from_bytes( L, 'big' )
    child_private_key = ( L_as_int + private_key ) % SECP256k1_ORD
    child_chain_code = R

    return ( child_private_key, child_chain_code )


def get_extended_private_key( depth, child_number, private_key, parent_fingerprint, chain_code, verbose=False ) :
    # Derive the extended private key
    version_bytes = VERSION_BYTES[ 'mainnet_private' ]
    depth_byte = depth.to_bytes( 1, 'big' )
    child_number_bytes = child_number.to_bytes( 4, 'big' )
    key_bytes = b'\x00' + private_key.to_bytes( 32, 'big' )

    all_parts = (
        version_bytes,      # 4 bytes
        depth_byte,         # 1 byte
        parent_fingerprint, # 4 bytes
        child_number_bytes, # 4 bytes
        chain_code,         # 32 bytes
        key_bytes,          # 33 bytes
    )

    all_bytes = b''.join( all_parts )
    extended_private_key = base58.b58encode_check( all_bytes ).decode( 'utf8' )
    if verbose : print(f'xprv: {extended_private_key}')

    # e.g. xprv: xprvA2vDkmMuK1Ae2eF92xyQpn6qZzHoGTnV5hXrBw7UExUTXeMFTZDLF7cRD6vhR785RMF2EC6mAo3ojRqFEUU8VxTSzGq1jvmXSBTxoCGSSVG

    # Nailed it! Now, for more practical purposes, we'll need a public address and a private key.
    # Display the private key

    if verbose : print( f'private key: {hex(private_key)}' )

    # e.g. private key: 0x3c4cf049f83a5870ab31c396a0d46783c3e3974da1364ea5a2477548d36b5f8f
    return extended_private_key 


###########################################################################
# get private key from seed
###########################################################################

def get_eth_keys( seed, verbose=False, bip44=True ) :

    return_value = []

    # Derive the master private key and chain code

    # the HMAC-SHA512 `key` and `data` must be bytes:
    seed_bytes = binascii.unhexlify( seed )

    I = hmac.new( b'Bitcoin seed', seed_bytes, hashlib.sha512 ).digest()
    L, R = I[ : 32 ], I[ 32 : ]

    master_private_key = int.from_bytes( L, 'big' )
    master_chain_code = R

    if verbose : print( f'master private key (hex): {hex(master_private_key)}' )
    if verbose : print( f'master chain code (bytes): {master_chain_code}' )

    # Derive the root key (extended private key)

    version_bytes = VERSION_BYTES[ 'mainnet_private' ]
    depth_byte = b'\x00'
    parent_fingerprint = b'\x00' * 4
    child_number_bytes = b'\x00' * 4
    key_bytes = b'\x00' + L

    all_parts = (
        version_bytes,      # 4 bytes
        depth_byte,         # 1 byte
        parent_fingerprint, # 4 bytes
        child_number_bytes, # 4 bytes
        master_chain_code,  # 32 bytes
        key_bytes,          # 33 bytes
    )

    all_bytes = b''.join( all_parts )
    root_key = base58.b58encode_check( all_bytes ).decode('utf8')
    if verbose : print( f'root key: {root_key}' )


    # Run the child key derivation function once per path depth
    # 
    # We're deriving keys for the account at the "default" path: m/44'/60'/0'/0/0.


    # BIP 44 keys are 'hardened'
    # If hardened, add 2*31 to the number:
    #    e.g. (2**31 + 44, 2**31 + 60, 2**31 + 0, 0, 0)
    if bip44 :
        path_numbers = ( 44 + bip32utils.BIP32_HARDEN, 60 + bip32utils.BIP32_HARDEN, 0 + bip32utils.BIP32_HARDEN, 0, 0 )
    # else break each depth into integers (m/44'/60'/0'/0/0)
    #    e.g. (44, 60, 0, 0, 0)
    else :
        path_numbers = ( 44, 60, 0, 0, 0 )

    parent_fingerprint = None
    child_number = None
    private_key = master_private_key
    chain_code = master_chain_code

    for depth, child_number in enumerate( path_numbers ) :
        parent_fingerprint = fingerprint_from_priv_key( private_key )
        private_key, chain_code = get_private_key( private_key, chain_code, child_number )
        address = get_eth_address( private_key )
        extended_private_key = get_extended_private_key( depth, child_number, private_key, parent_fingerprint, chain_code )

        temp = { 
            "depth" : depth, 
            "child_number" : child_number, 
            "private_key_int" : private_key, 
            "private_key" : hex( private_key ), 
            "extended_private_key" : extended_private_key, 
            "address" : address 
        }

        return_value.append( temp )

        if verbose : 
            print( f"depth: {depth}" )
            print( f"child_number: {child_number}" )
            print( json.dumps( temp, indent=2 ) )

    return list( reversed( return_value ) )


###########################################################################
# get eth address from private key 
###########################################################################

def get_eth_address( private_key, verbose=False ) :

    # Derive the public key
    # In [10]:

    # Derive the public key Point:
    p = curve_point_from_int( private_key )
    if verbose : print( f'Point object: {p}\n' )

    # Serialize the Point, p
    public_key_bytes = serialize_curve_point( p )

    if verbose : print( f'public key (hex): 0x{public_key_bytes.hex()}' )

    # e.g. Point object: (34628879175116161227789129351591737524694652815106357809683939650023911982126,16686316349534243923155184728961992244162372383889866453776214730676940635074)
    # e.g. public key (hex): 0x024c8f4044470bd42b81a8b233e2f954b63f4ee2c32c8d44288b44188754e2042e

    # Derive the public address
    # Hash the concatenated x and y public key point values:
    digest = keccak( p.x().to_bytes( 32, 'big' ) + p.y().to_bytes( 32, 'big' ) )

    # Take the last 20 bytes and add '0x' to the front:
    address = '0x' + digest[ -20 : ].hex()

    if verbose : print( f'address: {address}' )

    # e.g. address: 0xbbec2620cb01adae3f96e1fa39f997f06bfb7ca0

    return to_checksum_address( address )


###########################################################################
# get address from mnemonic words
###########################################################################

def get_btc_keys( seed, bip44=True, verbose=False ) :
    return_value = []

    seed = binascii.unhexlify( seed )

    bip32_root_key = bip32utils.BIP32Key.fromEntropy( seed )
    if verbose :
        print( bip32_root_key.dump() )

    root_address = bip32_root_key.Address()
    root_public_key = bip32_root_key.PublicKey().hex()
    root_private_key = bip32_root_key.WalletImportFormat()

    temp = {}

    temp[ 'address' ] = root_address
    temp[ 'public_key' ] = root_public_key
    temp[ 'private_key' ] = root_private_key 

    return_value.append( temp )

    # BIP 44 keys are 'hardened'
    # If hardened, add 2*31 to the number:
    #    e.g. (2**31 + 44, 2**31 + 60, 2**31 + 0, 0, 0)
    if bip44 :
        child_key = bip32_root_key.ChildKey(
            44 + bip32utils.BIP32_HARDEN
        ).ChildKey(
            0 + bip32utils.BIP32_HARDEN
        ).ChildKey(
            0 + bip32utils.BIP32_HARDEN
        ).ChildKey( 0 ).ChildKey( 0 )
    # else just apply ChildKey
    else :
        child_key = bip32_root_key.ChildKey( 0 ).ChildKey( 0 )

    temp = {}
    temp[ 'address' ] = child_key.Address()
    temp[ 'public_key' ] = binascii.hexlify( child_key.PublicKey() ).decode()
    temp[ 'private_key' ] = child_key.WalletImportFormat()

    return_value.append( temp )

    return return_value


###########################################################################
# shortcuts to generate eth address
###########################################################################

def create_eth_keys_and_address( verbose=False, entropy_bit_size=256 ) :
    from coincurve import PublicKey
    from secrets import token_bytes
    from hashlib import pbkdf2_hmac, sha256

    return_value = {}

    byte_size = entropy_bit_size // 8
    entropy_bytes = token_bytes( byte_size )

    # works on Windows 10
    try : 
        from sha3 import keccak_256
        private_key = keccak_256( entropy_bytes ).digest()
        public_key = PublicKey.from_valid_secret( private_key ).format( compressed=False )[ 1 : ]
        addr = keccak_256( public_key ).digest()[ -20 : ]
    # works on Mac OS X
    except :
        from Crypto.Hash import keccak
        private_key = keccak.new( digest_bits=entropy_bit_size ).update( entropy_bytes ).digest()
        public_key = PublicKey.from_valid_secret( private_key ).format( compressed=False )[ 1 : ]
        addr = keccak.new( digest_bits=entropy_bit_size ).update( public_key ).digest()[ -20 : ]

    # example output: 
    # private_key : 5da9a25399b1ca0e30a24ce5502e5bea10f6632cf78a1477c696d15cb1b307ae
    # public key  : 75f94a571ed09b5747fa46969292ef4317e788f7
    # eth addr    : 0x75f94a571ed09b5747fa46969292ef4317e788f7
    if verbose : print('private_key : ' + private_key.hex())
    if verbose : print('public key  : ' + addr.hex())
    if verbose : print('eth addr    : 0x' + addr.hex())

    return_value[ "private_key" ] = private_key.hex()
    return_value[ "public_key" ] = public_key.hex()
    return_value[ "address" ] = "0x" + addr.hex()

    return return_value 

###########################################################################
# functions to generate eth and btc keys and addresses given mnemonic or not
###########################################################################

def create_eth_keys_address_from_mnemonic( mnemonic_string, bip44=True, verbose=False ) :
    return_value = {}
    seed = bip39.generate_seed_from_mnemonic( mnemonic_string, verbose=verbose )
    return_value[ 'bip' ] = "bip44" if bip44 else "bip32"
    return_value[ "seed" ] = seed
    return_value[ "mnemonic" ] = mnemonic_string
    return_value[ "accounts" ] = get_eth_keys( seed, bip44=bip44, verbose=verbose )
    
    return return_value


def create_btc_keys_address_from_mnemonic( mnemonic_string, bip44=True, verbose=False ) :
    return_value = {}
    seed = bip39.generate_seed_from_mnemonic( mnemonic_string, verbose=verbose )
    return_value[ 'bip' ] = "bip44" if bip44 else "bip32"
    return_value[ "seed" ] = seed
    return_value[ "mnemonic" ] = mnemonic_string
    return_value[ "accounts" ] = get_btc_keys( seed, bip44=bip44, verbose=verbose )
    return return_value


def create_eth_keys_address_mnemonic( bip44=True, verbose=False ) :
    mnemonic_string = bip39.generate_mnemonic( verbose=verbose )
    return create_eth_keys_address_from_mnemonic( mnemonic_string, verbose=verbose )


def create_btc_keys_address_mnemonic( bip44=True, verbose=False ) :
    mnemonic_string = bip39.generate_mnemonic( verbose=verbose )
    return create_btc_keys_address_from_mnemonic( mnemonic_string, verbose=verbose )


###########################################################################
# main - where the magic happens
###########################################################################

if __name__ == "__main__" :
    import argparse

    parser = argparse.ArgumentParser( description='BIP32 tools' )
    parser.add_argument( '-v', '--verbose',  help='Enable verbose mode',                                                     action='store_true' )
    parser.add_argument( '-3', '--bip32',  help='BIP32, default is BIP44 (hardened)',                                        action='store_true' )
    parser.add_argument( '-e', '--ethereum-wallet-from-mnemonic', help='EVM compatible keys from .secret passphrase',        action='store_true' )
    parser.add_argument( '-b', '--bitcoin-wallet-from-mnemonic',  help='Bitcoin compatible passphrase, keys, and address',   action='store_true' )
    parser.add_argument( '-E', '--create-ethereum-wallet', help='Generate EVM compatible passphrase, keys, and address',     action='store_true' )
    parser.add_argument( '-B', '--create-bitcoin-wallet',  help='Generate Bitcoin compatible passphrase, keys, and address', action='store_true' )
    args = parser.parse_args()

    bip44 = not args.bip32

    with open( ".secret" ) as f :
        mnemonic_string = f.read().strip()

    if args.ethereum_wallet_from_mnemonic :
        res = create_eth_keys_address_from_mnemonic( mnemonic_string, bip44=bip44, verbose=args.verbose )
        print( json.dumps( res, indent=2 ) )

    if args.bitcoin_wallet_from_mnemonic :
        res = create_btc_keys_address_from_mnemonic( mnemonic_string, bip44=bip44, verbose=args.verbose )
        print( json.dumps( res, indent=2 ) )

    if args.create_ethereum_wallet :
        res = create_eth_keys_address_mnemonic( bip44=bip44, verbose=args.verbose )
        print( json.dumps( res, indent=2 ) )

    if args.create_bitcoin_wallet :
        res = create_btc_keys_address_mnemonic( bip44=bip44, verbose=args.verbose )
        print( json.dumps( res, indent=2 ) )
