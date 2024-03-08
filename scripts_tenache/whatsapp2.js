const qrcode = require('qrcode-terminal');
const { Client, LocalAuth } = require('whatsapp-web.js');
const client = new Client({
    authStrategy: new LocalAuth()
});

client.on('qr', (qr) => {
    qrcode.generate(qr, { small: true });
});

client.on('ready', () => {
    console.log('Client is ready!');
});

client.initialize();

client.on('message', (message) => {
    console.log("=======================================")
    console.log(message)
    console.log("=======================================")
	console.log(message.body);
    console.log("=======================================")
    console.log("---------------------------------------")
    console.log("---------------------------------------")
});

client.on('message', async (message) => {
	if (message.from === '5493874034462@c.us') {
        //fetch()
        /* {"input":{"user_input":"hello"},"config":{}} */
        var response = await fetch('http://127.0.0.1:8000/joke/invoke', {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                "input": {
                  "user_input": "¿Las focas son redondas?"
                },
                "config": {},
                "kwargs": {}
              })
        })
        var myjson = await response.json()
        console.log(myjson)
        await message.reply(myjson.output)
        //var true_response = await response
        //console.log(true_response)
	}
});