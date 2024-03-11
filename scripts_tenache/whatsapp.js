// TODO: Hacer que no lea el u
const Lau = '5493424076693.us'
const Foca = '5493874034462@c.us'
const Sabri = '5493874690429@c.us'
const Cris = '5493874750755.us'
const TELEFONO = '4212368'
const CELULAR = '387528693'
const WHATSAPP = 'https://wa.me/5493875286093'

const waitTime = 500
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
    // console.log("=======================================")
    // console.log(message)
    // console.log("=======================================")
	console.log(message.body);
    chat = getChatAsync(message);

    // console.log("=======================================")
    // console.log("---------------------------------------")
    // console.log("---------------------------------------")
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
            return resolve("done")
        });
    });
}
function sleep(ms){
    return new Promise(resolve => setTimeout(resolve,ms))
}

const python_path = "C:\\thibbard\\envs\\prompt_engineering\\Scripts\\python.exe"
// const python_path = "C:\\Users\\tenache89\\miniconda3\\python.exe"
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
                        chat.sendMessage(`No podemos atenderle en este momento. Puede comunicarse con los numeros ${TELEFONO}, ${CELULAR}, ${WHATSAPP}`);
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
        if (message.from === Lau || message.from === Cris || message.from === Foca || message.from === '5493874149123@c.us' || message.from === Sabri || chat_ready === true & message.type == "TEXT") {
            try {
                await insert_user(message);
                await insert_message(message);
                message_list.push(message)
                console.log("waiting for follow-ups (45s)");
                await sleep(waitTime*3); // wait for possible incoming new messages before responding
                console.log("waiting for follow-ups (30s)");
                await sleep(waitTime*2);
                console.log("waiting for follow-ups (20s)");
                await sleep(waitTime*2);
                console.log("waiting for follow-ups (10s)")
                await sleep (waitTime*2)
                
                return chat
                // respond(message, chat);
            } catch (error) {
                console.error(error);
            }
        }
    }}
client.on('message', async(message) =>{
    chat = await handleInsertions(message);
    if (message === message_list[message_list.length-1]) {
        respond(message, chat)
    }
})

// var all_chats = new Set()
// async function handleAllInsertions(message){
//     var_all_chats = new Set()
//     var chat = await handleInsertions(message);
//     all_chats.add(chat)
//     return all_chats
// }


// client.on('message', async(message) =>{
//     var all_chats = handleAllInsertions(message);

//     for (let this_chat in all_chats){
//         respond(message, this_chat);
//         all_chats.delete(this_chat);
//     }
// })


    // client.on('message', async (message) => {

// 	if (message.body === '!ping') {
// 		await message.reply('pong');
// 	}
//     else
//     {
//         var [chat_ready, chat] = await getChatAsync(message);
//         if (message.from === '5493874034462@c.us' || message.from === '5493874690429@c.us' || chat_ready === true) {
//             try {
//                 await insert_user(message);
//                 await insert_message(message);
//                 console.log("waiting for follow-ups (30s)");
//                 await sleep(10_000); // wait for possible incoming new messages before responding
//                 console.log("waiting for follow-ups (20s)");
//                 await sleep(10_000);
//                 console.log("waiting for follow-ups (10s)");
//                 await sleep(10_000);
//                 respond(message, chat);
//             } catch (error) {
//                 console.error(error);
//             }

//         }
//     }})



// new Promise((resolve, reject) => {
//     console.log(`message._data.notifyName is ${message._data.notifyName}`);
//     console.log(`message.body is ${message.body}`);
//     db.run(`INSERT INTO users (id, username) VALUES (?, ?) ON CONFLICT (id) DO NOTHING;`, [message.from, message._data.notifyName], function(err) {
//         if (err){
//             console.error(err.message);
//             reject(err); // Reject the promise if there's an error
//         } else {
//             console.log(`A row has been inserted with rowid ${this.lastID}`);
//             resolve(this.lastID); //Resolve the Promise with lastID
//         }

//     });
//     db.run(`INSERT INTO messages (id, user_id, from_user, from_ai, content) VALUES (?, ?, ?, ?, ?)`, [message.id.id, message.from, 1, 0, message.body], function(err) {
//         if (err) {
//             console.error(err.message);
//             reject(err); // Reject the Promise if there's an error
//         } else {
//             console.log(`A row has been inserted with rowid ${this.lastID}`);
//             resolve(this.lastID); // Resolve the Promise with lastID
//         }
//     });
// }).then((lastID) => {
//     console.log("hello");
//     // After successful insertion, execute the Python script
//     const pythonProcess = spawn('python',['second_script.py', message.body.toString()]);
//     pythonProcess.on('close', (code) => {
//         console.log(`child process exited with code ${code}`);
    
//         // Read file only after Python script has finished

//         try {
//             const query = `SELECT content FROM messages  WHERE user_id ==? ORDER BY created_at DESC LIMIT 1`;

//             db.serialize(() => {
//                 db.get(query,
//                 [message.from], 
//                 (err, row) => {
//                     if (err){
//                         console.error(err.message);
//                         return;
//                     }
//                     if (row){
//                         console.log(row.content);
//                         chat.sendMessage(row.content);
//                     } else {
//                         console.log("No content found");
//                     }
//                 });
//             });

//         } catch (readErr) {
//             console.error(readErr);
//         }
//     });
// }).catch((err) => {
//     console.error("Database operation failed", err);
// });
// }