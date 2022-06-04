# Crypto
Code for generating wallets and interacting with contracts.  This is not intended to be an encyclopedic treatment of the state of the art.  It's merely intended to help new blockchain coders get off the ground quicker and understand coding principles on the blockchain.  Note that the modules referenced are constantly evolving, so anticipate some errors.

## Data and ABI files
Unless otherwise specified, it is assumed that all data such as abi files and config files will be stored in the data/ directory.  In particular, config.json contains data that you will need to connect to your instance of infura, or specify contract or wallet addresses.

## BIP32 and BIP39
These .py files contain the code necessary to produce wallets, including private and public keys as well as mnemonics.  Always protect your private key!

## Blockutil
This contains some helpful code for interacting with the blockchain and smart contracts (see the unit test cases in 'main').

## Example scripts
We have referenced the code above to perform some useful operations.  Scripts prefixed 00-04 make use of the above code base to generate wallets, send tokens, determine NFT holders and more.

## Installation
After cloning the repository, you will need to install the necessary python modules:

> pip install -r requirements.txt
