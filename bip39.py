#!/usr/bin/python3

###########################################################################
#
# name          : bip39.py
#
# purpose       : generate keys from seed
#
# usage         : python3 bip39.py
#
# description   : 
# > https://github.com/marcgarreau/ethereum-notebooks/blob/master/bip39.ipynb
# > https://wolovim.medium.com/ethereum-201-mnemonics-bb01a9108c38
#
###########################################################################

import binascii
import codecs
import os

from bitarray import bitarray
from bitarray.util import ba2int
from hashlib import pbkdf2_hmac, sha256


###########################################################################
# generate entropy, private key, and return the corresponding  mnemonic
###########################################################################

def generate_mnemonic( verbose=False, entropy_bit_size=128 ) :

    # Generate entropy
    #
    # A random number between 128 and 256 bits. Must be a multiple of 32.
    
    # valid_entropy_bit_sizes = [128, 160, 192, 224, 256]
    entropy_bytes = os.urandom( entropy_bit_size // 8 )
    
    if verbose : print( entropy_bytes )
    # e.g. b'\x02@\x1f\x17\xd8GF\xd2\x8b\x18\xb5\xef\xbd\xd8\x1c\x96'
    
    entropy_bits = bitarray()
    entropy_bits.frombytes( entropy_bytes )
    #print( entropy_bits )
    
    checksum_length = entropy_bit_size // 32
    
    if verbose : print( checksum_length )
    # e.g. 4
    
    # Which four bits? The first four bits of the hashed entropy
    hash_bytes = sha256( entropy_bytes ).digest()
    
    if verbose : print( hash_bytes )
    # e.g. b'\x1ay\xc9&[\x8a\xe03Z\x8f\xa4...'
    
    hash_bits = bitarray()
    hash_bits.frombytes( hash_bytes )
    
    if verbose : print(hash_bits)
    # e.g. bitarray('0001101001111...')
    
    checksum = hash_bits[ : checksum_length ]
    if verbose : print( checksum )
    # e.g. bitarray('0001')
    
    # Add those first four bits to the end of the unhashed entropy:
    
    if verbose : print( len( entropy_bits ) )
    # e.g. 128
    
    entropy_bits.extend(checksum)
    
    if verbose : print( len( entropy_bits ) )
    # e.g. 132
    
    
    # Split the entropy into groups of 11 bits
    # 
    # The number of groups is the number of mnemonic words that will be produced.
    
    
    grouped_bitarrays = tuple( entropy_bits[ i * 11 : ( i + 1 ) * 11 ] for i in range( len( entropy_bits ) // 11 ) )
    
    if verbose : print( grouped_bitarrays )
    # e.g. (bitarray('00000010010'), bitarray('00000000111'), ...)
    
    if verbose : print( len( grouped_bitarrays ) )
    # e.g. 12
    

    # Convert the bitarrays to integers. Each 11-bit number is between 0-2047.
    indices = tuple( ba2int( ba ) for ba in grouped_bitarrays )
    
    if verbose : print( indices )
    # e.g. (18, 7, 1583, 1412, 931, 842, 355, 181, 1917, 1910, 57, 353)
    
    
    # Convert each index into an English word
    # 
    # The BIP 39 spec links to official word lists for several languages. There are 2048 words in each list - one for each possible 11-bit number. Load the words into memory and swap out each index for its corresponding English word:
    
    
    with open( 'data/english.txt', 'r' ) as f :
        english_word_list = f.read().strip().split()
    
    if verbose : print( len( english_word_list ) )
    if verbose : print( english_word_list[ : 5 ] )
    # ['abandon', 'ability', 'able', 'about', 'above']
    
    words = tuple( english_word_list[ i ] for i in indices )
    
    # print(words)
    # e.g. ('across', 'abstract', 'shine', 'rack', 'inner', 'harsh',
    #  'cluster', 'birth', 'use', 'uphold', 'already', 'club')
    
    mnemonic_string = ' '.join(words)
    if verbose : print( mnemonic_string )
    # e.g. 'across abstract shine ... uphold already club'

    return mnemonic_string
    
    
###########################################################################
# generates seed from mnemonic
###########################################################################

def generate_seed_from_mnemonic( mnemonic_string, verbose=False ) :

    # Generate the seed
    # Use a password-based key derivation function (PBKDF2) to create the seed.
    # Bonus security: you can set an optional passphrase to be included in the salt. (Defaults to empty string.)
    salt = "mnemonic" # + passphrase (optional)
    
    seed = pbkdf2_hmac(
       "sha512",
       mnemonic_string.encode("utf-8"),
       salt.encode("utf-8"),
       2048
    )
    
    if verbose : print( seed )
    # b"\xf8\xb7W}\xba\x02Wx\xb9\xbf$\xf8..."
    
    if verbose : print( len( seed ) )
    # 64 (bytes, i.e. 512 bits)
    
    seed = binascii.hexlify(seed).decode()
    if verbose : print( seed )
    
    # Behold: your seed!
    return seed
    
    
###########################################################################
# generates mnemonic, gets seed from mnemonic 
###########################################################################

def generate_seed( verbose=False ) :
    mnemonic_string = generate_mnemonic()
    if verbose : print( mnemonic_string )
    return_value = generate_seed_from_mnemonic( mnemonic_string )
    return return_value


###########################################################################
# main - where the magic happens
###########################################################################
if __name__ == "__main__" :
    import argparse

    parser = argparse.ArgumentParser( description='BIP32 tools' )
    parser.add_argument( '-v', '--verbose',            help='Enable verbose mode',         action='store_true' )
    parser.add_argument( '-s', '--seed',               help='Generate seed',               action='store_true' )
    parser.add_argument( '-M', '--seed-from-mnemonic', help='Generate seed from mnemonic', action='store_true' )
    parser.add_argument( '-m', '--mnemonic',           help='Generate mnemonic',           action='store_true' )
    parser.add_argument( '-e', '--entropy-bit-size',   help='Entropy bit size',            action='store', type=int, default=128 )
    args = parser.parse_args()

    with open( ".secret" ) as f :
        mnemonic_string = f.read().strip()

    if args.seed :
        print( generate_seed() )

    if args.mnemonic :
        print( generate_mnemonic( entropy_bit_size=args.entropy_bit_size ) )

    if args.seed_from_mnemonic :
        print( generate_seed_from_mnemonic( mnemonic_string, verbose=args.verbose ) )
