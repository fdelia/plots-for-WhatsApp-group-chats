var fs = require('fs')
var path = require('path')

var filePath = path.join(__dirname, '_chat.txt')

var content = fs.readFileSync(filePath, {
	encoding: 'utf8'
})
var lines = content.split('\n')


function IsNumeric(val) {
	return Number(parseFloat(val)) == val;
}

function anonymizeUser(user) {

}

function incrInDict(obj, key) {
	if (key in obj) obj[key]++;
	else obj[key] = 1;
}

// function addInDict(obj, key, nr){
// 	if (key in obj) obj[key] += nr;
// 	else obj[key] = nr;
// }



var userWordCount = {}
var userCount = {}

var user, message; //, anoUser;
for (var i = 0; i < lines.length; i++) {
	var line = lines[i].toLowerCase()
	line = line.replace('<image ommitted>', '')
	line = line.replace(/[\[\]\(\)\?!"'`/,;\^@]+/g, ' ')
	console.log(line)

	var ind1 = line.indexOf(':', 16)
	var ind2 = line.indexOf(':', 19)

	// message from new user
	if (ind1 === 18 && ind2 >= 19) {
		// var dateTime = line.substr(0, ind1).trim()
		user = line.substr(ind1 + 1, ind2 - ind1 - 1).trim()
		// incrInDict(userCount, user)
			// anoUser = anonymizeUser(user)
		message = line.substr(ind2 + 1, line.length - ind2 - 1).trim()
	}

	// message from same user
	else {
		message = line.trim();
	}


	// tokenize
	var sentences = message.split('.')
	// console.log(sentences)
	for (var j = 0; j < sentences.length; j++) {
		var sentence = sentences[j]
		if (sentence.trim() == '') continue;

		var words = sentence.split(' ')
		for (var k = 0; k < words.length; k++) {
			var word = words[k]
				// if (IsNumeric(word)) word.toString();
			if (word == '') continue;

			if (!(word in userWordCount)) userWordCount[word] = {}
			incrInDict(userWordCount[word], user)
			incrInDict(userCount, user)
		}


		// TODO: add bigrams, trigrams
	}
}

var data = [userCount, userWordCount];
fs.writeFile('_chatData.json', JSON.stringify(data), 'utf8', function(err) {
	if (err) {
		console.error('Error while saving json: ')
		console.error(err)
	} else
		console.log('data saved under _chatData.json')
});