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

from ecdsa import SECP256k1
from ecdsa.ecdsa import Public_key
from eth_utils import keccak, to_checksum_address


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

def derive_ext_private_key( private_key, chain_code, child_number ) :
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


###########################################################################
# get private key from seed
###########################################################################

def get_private_key( seed, verbose=False ) :
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

    VERSION_BYTES = {
        'mainnet_public': binascii.unhexlify( '0488b21e' ),
        'mainnet_private': binascii.unhexlify( '0488ade4' ),
        'testnet_public': binascii.unhexlify( '043587cf' ),
        'testnet_private': binascii.unhexlify( '04358394' ),
    }

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


    # Break each depth into integers (m/44'/60'/0'/0/0)
    #    e.g. (44, 60, 0, 0, 0)
    # If hardened, add 2*31 to the number:
    #    e.g. (2**31 + 44, 2**31 + 60, 2**31 + 0, 0, 0)
    path_numbers = ( 2147483692, 2147483708, 2147483648, 0, 0 )

    depth = 0
    parent_fingerprint = None
    child_number = None
    private_key = master_private_key
    chain_code = master_chain_code

    for i in path_numbers:
        depth += 1
        if verbose : print( f"depth: {depth}" )

        child_number = i
        if verbose : print( f"child_number: {child_number}" )

        parent_fingerprint = fingerprint_from_priv_key( private_key )
        if verbose : print( f"parent_fingerprint: {parent_fingerprint}" )

        private_key, chain_code = derive_ext_private_key(private_key, chain_code, i)
        if verbose : print( f"private_key: {private_key}" )
        if verbose : print( f"chain_code: {chain_code}\n" )


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

    return private_key


###########################################################################
# get address from private key 
###########################################################################

def get_address( private_key, verbose=False ) :

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
# get public key from seed
###########################################################################

def get_address_from_seed( seed ) :
    private_key = get_private_key( seed )
    public_key  = get_address( private_key )
    return public_key


###########################################################################
# get address from mnemonic words
###########################################################################

def get_bitcoin_address_from_mnemonic( mnemonic_words ) :
    mobj = mnemonic.Mnemonic( "english" )
    seed = mobj.to_seed( mnemonic_words )

    bip32_root_key_obj = bip32utils.BIP32Key.fromEntropy( seed )
    bip32_child_key_obj = bip32_root_key_obj.ChildKey(
        44 + bip32utils.BIP32_HARDEN
    ).ChildKey(
        0 + bip32utils.BIP32_HARDEN
    ).ChildKey(
        0 + bip32utils.BIP32_HARDEN
    ).ChildKey( 0 ).ChildKey( 0 )

    return_value = {} 
    return_value[ 'seed' ] = seed.hex()
    return_value[ 'mnemonic_words' ] = mnemonic_words
    return_value[ 'addr' ] = bip32_child_key_obj.Address()
    return_value[ 'publickey' ] = binascii.hexlify( bip32_child_key_obj.PublicKey() ).decode()
    return_value[ 'privatekey' ] = bip32_child_key_obj.WalletImportFormat()
    return_value[ 'coin' ] = 'BTC'
    return return_value


###########################################################################
# generates seed, gets address
###########################################################################

def run() :
    # generate seed
    seed    = bip39.generate_seed()

    # get address from seed 
    address = get_address_from_seed( seed )

    return ( seed, address )


###########################################################################
# shortcuts to generate eth address
###########################################################################

def get_eth_keys_and_address( verbose=False ) :
    from secrets import token_bytes
    from coincurve import PublicKey
    from sha3 import keccak_256

    private_key = keccak_256( token_bytes( 32 ) ).digest()
    public_key = PublicKey.from_valid_secret( private_key ).format( compressed=False )[ 1 : ]
    addr = keccak_256( public_key ).digest()[ -20 : ]

    # example output: 
    # private_key: 7bf19806aa6d5b31d7b7ea9e833c202e51ff8ee6311df6a036f0261f216f09ef
    # eth addr: 0x3db763bbbb1ac900eb2eb8b106218f85f9f64a13
    if verbose : print('private_key:', private_key.hex())
    if verbose : print('eth addr: 0x' + addr.hex())

    return addr.hex()


###########################################################################
# main - where the magic happens
###########################################################################

if __name__ == "__main__" :
    # NOTE: this mnemonic is for demonstration purposes only!  Do not use it!
    mnemonic_string = "inject lion lamp lazy cliff lady neither camera index bounce possible awesome"
    seed = bip39.generate_seed_from_mnemonic( mnemonic_string )
    address = get_address_from_seed( seed )
    print( seed, address )

    res = get_bitcoin_address_from_mnemonic( mnemonic_string )
    print( json.dumps( res, indent=2 ) )
