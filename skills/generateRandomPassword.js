/**
 * This JS File creates a randomy generated 8-digit password.
 */
function randomPasswordGenerator()
{
    var charList = "abcdefghijkmnpqrstuvwxyz0123456789ABCDEFGHJKLMNPQRSTUVWXYZ0123456789";
    var listLength  = charList.length;
    var passwordString = ''
    for(i=0;i<9;i++)
    {
        var x = Math.floor((Math.random() * listLength));
        passwordString += charList[x]
    }
    return passwordString
}

module.exports.randomPasswordGenerator = randomPasswordGenerator