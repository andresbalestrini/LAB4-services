var express = require('express');
var bodyParser = require('body-parser');
var request = require('request');
var session = require('express-session');
var handlers = require('express-handlebars').create({ defaultLayout: 'main' }); // busca siempre en views/layout el archivo main.handlebars
var app = express();

app.engine('handlebars', handlers.engine);
app.set('view engine', 'handlebars')
//extended: false significa que parsea solo string (no archivos de imagenes por ejemplo)
app.use(bodyParser.urlencoded({ extended: false }));
app.use(session({
    secret: 'mys3cr3t',
    resave: false,
    saveUninitialized: true,
    cookie: { secure: false }
}));

// la sesion usa una cookie que se la manda al browser para que guarde nuestros datos hasta que expire la sesion

app.get('/', (req, res) => {
    var sess = req.session
    if (sess.token) {
        res.redirect('/home');
    } else {
        res.redirect('/login');
    }
});

app.get('/home', (req, res) => {

});

app.get('/login', (req, res) => {
    res.render('login');
});

app.get('/register', (req, res) => {
    res.render('register');
});

app.post('/control', (req, res) => {
    var sess = req.session
    var num1 = req.body.nombre;
    var num2 = req.body.pass;

    var options = {
        uri: "http://localhost:8081/auth-svc/login",
        method: "POST",
        headers: "Content-Type: application/json",
        json: { "user": num1, "pass": num2 }
    }

    request(options, (error, response, body) => {
        if (!error && response.statusCode == 200) {
            var state = body.status;
            if (state == "OK") {
                sess.token = body.token;
                res.render('home');
            }
            else {
                res.render('login', { err: body.msg });
            }
        }

    });
});

app.post('/procesar', (req, res) => {
    var name = req.body.username;
    var pass = req.body.pass;
    var repass = req.body.repass;
    if (name.length == 0) {
        res.render('register', { err: 'User name is required' });
    } else if (pass != repass) {
        res.render('register', { err: 'Passwords do not match' });
    } else if (pass.length == 0) {
        res.render('register', { err: 'Password is required' });
    } else {
        var options = {
            uri: "http://localhost:8081/auth-svc/register",
            method: "POST",
            headers: "Content-Type: application/json",
            json: { "username": name, "pass": pass }
        }

        request(options, (error, response, body) => {
            if (!error && response.statusCode == 200) {
                var state = body.status;
                if (state == "OK") {
                    res.render('login', { ok: 'User created correctly' });
                }
                else {
                    res.render('register', { err: body.msg });
                }
            }

        });
    }
})

app.get('/test', (req, res) => {
    var sess = req.session
    var options = {
        uri: "http://localhost:8081/auth-svc/test",
        method: "GET",
        headers: {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + sess.token,
            'Content-Type':'application/json'
        },
        json:{} 
    }

    request(options, (error, response, body) => {
        if (!error && response.statusCode == 200) {
            var state = body.status;
            if (state == "OK") {
                res.send('test ok');
            }
            else {
                res.send('test fail');
            }
        }
    });

})

app.listen(3000);