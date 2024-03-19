// TODO: Hacer que no lea el u
const Lau = '5493424076693@c.us';
const Foca = '5493874034462@c.us';
const Sabri = '5493874690429@c.us';
const Cris = '5493874750755@c.us';
const juegosSalta = '5493875699648@c.us';
const Marco = '5493874149123@c.us';
const Mary = '5493874737179@c.us';

const TELEFONO = '4212368';
const CELULAR = '387528693';
const WHATSAPP = 'https://wa.me/5493875286093';

const waitTime = 5_000;
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

async function getChatAsync(message) {
    var chat = await message.getChat()
    // console.log(chat)
    if (chat.name === "Copium" || chat.name == "los chichudos renovados") {
        return [true, chat];
    } 
    else {
        return [false, chat];
    }
}

client.on('message', (message) => {
	console.log(message.body);
    chat = getChatAsync(message);

});


const sqlite3 = require('sqlite3').verbose();
const database_path = './whatsapp3.db'
const db = new sqlite3.Database(database_path, (err) => {
    if (err) {
        console.error(err.message);
    }
    console.log(`Connected to the ${database_path} database.`);
});


const { spawn } = require('child_process');
const fs = require('fs');
const { resolve } = require('path');

function insert_message(message){
    return new Promise ((resolve, reject) => {
        let sql = `INSERT INTO messages (id, user_id, user_name, from_user, from_ai, content) VALUES (?, ?, ?, ?, ?, ?)`;
        let params = [message.id.id, message.from,message._data.notifyName, 1, 0, message.body]
        return db.run(sql, params, function(err, res) {
            if (err) {
                console.error("DB Error. Insert message failed: ")
                return reject
            }
            return resolve("done")
        });
    });
}

function insert_user(message){
    return new Promise ((resolve, reject) => {
        let sql = `INSERT INTO users (id, username) VALUES (?, ?) ON CONFLICT (id) DO NOTHING;`;
        let params =  [message.from, message._data.notifyName]
        return db.run(sql, params, function(err, res) {
            if (err) {
                console.error("DB Error. Insert user failed: ", err.message);
                return reject(err.message);
            }
            return resolve("done");
        });
    });
}
function sleep(ms){
    return new Promise(resolve => setTimeout(resolve,ms))
}

function respond(message, chat) {
    console.log("About to begin the python process");
    // After successful insertion, execute the Python script
    var pythonProcess = spawn("python",['script_ofreser.py']);
    pythonProcess.stdout.on('data',(data) => {console.log(`stdout: ${data}`)})
    pythonProcess.on('close', (code) => {
        console.log(`child process exited with code ${code}`);
    
        // Read file only after Python script has finished

        try {
            var query = `SELECT content,from_ai FROM messages  WHERE user_id ==? ORDER BY created_at DESC LIMIT 1`;

            db.serialize(() => {
                db.get(query,
                [message.from], 
                (err, row) => {
                    if (err){
                        console.error(err.message);
                        return;
                    }
                    if (row){
                        if (row.content === '') {
                            console.log("empty string returned");
                            chat.sendMessage("La IA pelotuda contesto un string vacio");
                        }
                        else if (row.from_ai){
                            console.log(row.content);
                            chat.sendMessage(row.content);
                        }
                        else {
                        console.log(row.content);
                        chat.sendMessage(`No podemos atenderle en este momento. Puede comunicarse con los numeros \n${TELEFONO}, \n${CELULAR}, \n${WHATSAPP}`);
                        }
                    }
                    else {
                        console.log("No content found");
                    }
                });
            });

        } catch (readErr) {
            console.error(readErr);
        }
    });
}

const message_list = []
async function handleInsertions(message)  {
	if (message.body === '!ping') {
		await message.reply('pong');
	}
    else
    {
        var [chat_ready, chat] = await getChatAsync(message);
        if (message.from === Mary || message.from === juegosSalta || message.from === Lau || message.from === Cris || message.from === Foca || message.from === Marco || message.from === Sabri || chat_ready === true & message.type === "TEXT") {
            try {
                await insert_user(message);
                await insert_message(message);
                message_list.push(message);
                console.log("waiting for follow-ups (45s)");
                await sleep(waitTime*3); // wait for possible incoming new messages before responding
                console.log("waiting for follow-ups (30s)");
                await sleep(waitTime*2);
                console.log("waiting for follow-ups (20s)");
                await sleep(waitTime*2);
                console.log("waiting for follow-ups (10s)");
                await sleep (waitTime*2);
                
                return chat

            } catch (error) {
                console.error(error);
            }
        }
    }}

client.on('message', async(message) =>{
    console.log("received message");
    chat = await handleInsertions(message);
    if (message === message_list[message_list.length-1]) {
        respond(message, chat);
    };
});