#!/usr/bin/python

###########################################################################
#
# name          : clean.py
#
# purpose       : clean up .secret and infura URLs
#
# usage         : python clean.py
#
# description   :
#
###########################################################################

import json
import os
import random
import string

if __name__ == "__main__" :
    with open( "data/config.json", 'r' ) as f :
        data = json.load( f )

    for key in data :
        data[ key ] = ""

    with open( "data/config.json", 'w' ) as f :
        json.dump( data, f, indent=2 )

    for i in range( 10 ) :
        write_string = ''.join( [ random.choice( string.ascii_uppercase ) for i in range( 1000 ) ] )
        with open( '.secret', 'w' ) as f :
            f.write( write_string )

    os.remove( '.secret' )
