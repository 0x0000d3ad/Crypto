// make sure ganache is running
// to run: truffle exec mint.js --network development

const web3          = require( 'web3' );
const CourseERC721a = artifacts.require( 'CourseERC721a' );

module.exports = async function( callback ) {

	const owner = '0xa10746C425A1CAE05cE5e8aBBCD0e358509089b9';
	const contract_address = '0x54EBf773e93D84E6993BDBF065e3c906A9A8Da5B';

	let token = await CourseERC721a.at( contract_address );

	console.log( "Mint tokens" ); 
	await token.pause( false );
	await token.reveal();
	var mint_result;
	mint_result = await token.mint( 10 );

	let token_uri = await token.tokenURI( 1 );
	console.log( "tokenURI" );
	console.log( token_uri );
	console.log( "END" );
}
