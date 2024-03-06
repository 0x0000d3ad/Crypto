const { time } = require( '@openzeppelin/test-helpers' );

var CourseERC721a = artifacts.require( "CourseERC721a.sol" );

module.exports = function( deployer ) {
	const addresses = web3.eth.getAccounts();
	var res2 = deployer.deploy( CourseERC721a );
}
