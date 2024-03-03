#!/usr/bin/python

###########################################################################
#
# name          : monero.py
#
# purpose       : monero interactions
#
# usage         : python3 monero.py
#
# description   :
# NOTE: EXPERIMENTAL!
# > https://monero-python.readthedocs.io/en/latest/index.html
#
###########################################################################

import bip39
import json

from monero.seed import Seed

def get_xmr_keys( seed, verbose=False ) :
    return_value = {}
    s = Seed( seed )
    return_value[ "seed" ] = seed
    return_value[ "secret_spend_key" ] = s.secret_spend_key()
    return_value[ "secret_view_key" ] = s.secret_view_key()
    return_value[ "public_spend_key" ] = s.public_spend_key()
    return_value[ "public_view_key" ] = s.public_view_key()
    return_value[ "public_address" ] = str( s.public_address() )
    return return_value

if __name__ == "__main__" :
    import argparse

    parser = argparse.ArgumentParser( description='BIP32 tools' )
    parser.add_argument( '-v', '--verbose',            help='Enable verbose mode',                  action='store_true' )
    parser.add_argument( '-s', '--seed',               help='Generate seed and keys',               action='store_true' )
    parser.add_argument( '-M', '--seed-from-mnemonic', help='Generate seed and keys from mnemonic', action='store_true' )
    parser.add_argument( '-m', '--mnemonic',           help='Generate mnemonic, seed, and keys',    action='store_true' )
    parser.add_argument( '-e', '--entropy-bit-size',   help='Entropy bit size',                     action='store', type=int, default=128 )
    args = parser.parse_args()

    with open( ".secret" ) as f :
        mnemonic_string = f.read().strip()

    if args.seed :
        seed = bip39.generate_seed()
        res = get_xmr_keys( seed, verbose=args.verbose )
        print( json.dumps( res, indent=2 ) )

    if args.mnemonic :
        mnemonic_string = bip39.generate_mnemonic( entropy_bit_size=args.entropy_bit_size )
        seed = bip39.generate_seed_from_mnemonic( mnemonic_string, verbose=args.verbose )
        res = get_xmr_keys( seed, verbose=args.verbose )
        res[ "mnemonic" ] = mnemonic_string
        print( json.dumps( res, indent=2 ) )

    if args.seed_from_mnemonic :
        seed = bip39.generate_seed_from_mnemonic( mnemonic_string, verbose=args.verbose )
        seed = bip39.generate_seed_from_mnemonic( mnemonic_string, verbose=args.verbose )
        res = get_xmr_keys( seed, verbose=args.verbose )
        res[ "mnemonic" ] = mnemonic_string
        print( json.dumps( res, indent=2 ) )
