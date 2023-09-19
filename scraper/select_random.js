const axios = require('axios');

async function getRandomEnglishWord() {
  const response = await axios.get('https://en.wiktionary.org/w/api.php', {
    params: {
      action: 'query',
      format: 'json',
      list: 'random',
      rnnamespace: 0,
      rnlimit: 1
    }
  });

  const word = response.data.query.random[0].title;

  return word;
}

getRandomEnglishWord().then(console.log);
