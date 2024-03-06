const { time } = require( '@openzeppelin/test-helpers' );

var CourseERC721 = artifacts.require( "CourseERC721.sol" );

module.exports = function( deployer ) {
	const addresses = web3.eth.getAccounts();
	var res2 = deployer.deploy( CourseERC721 );
}
