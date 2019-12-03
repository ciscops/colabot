/**
 * This File holds list of VIRL2 Servers
 */
serverList = process.env.SERVER_LIST.split(' ');

// serverList = 
// [
//     'https://cpn-sjc-virl1.ciscops.net'
// ]

module.exports.serverList = serverList
