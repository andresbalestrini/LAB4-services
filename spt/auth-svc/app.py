from  bottle import Bottle, route, run, get, template, post, request
import pymysql
import os
import datetime
import python_jwt as jwt
import Crypto.PublicKey.RSA as RSA

private_key_file = os.path.join(os.path.dirname(__file__), 'key','mykey')
with open(private_key_file, 'r') as fd:
    private_key = RSA.importKey(fd.read())

# configuro mysql
mysql_config = {
    'host': 'localhost',
    'db': 'spt',
    'user': 'root', # or 'andresbalestrini'
    'passwd': '35260239' # '35260239'
    }
def insert_test():    
    try:
        cnx = pymysql.connect(**mysql_config)
        cursor = cnx.cursor()
        insert_test = "INSERT INTO test (id, msg) VALUES (%s, %s)"
        data = ("200", "test message") # tupla
        cursor.execute(insert_test, data)
        cnx.commit()
        cursor.close()
    except pymysql.Error as err:
        print "Failed to insert data: {}".format(err)
    finally:
        cnx.close()

## en la veriable app guardo una instancia de bootle
app = Bottle()

users = {}

@app.route('/hello',method="GET")
def hello():
    return "Hello World!"
## lo mismo que route pero definis @app.get que es mas rapido y legible para especificar
## el metodo
@app.get('/auth-svc/')
@app.get('/auth-svc/hello/<name>')
## reconoce que la funcion para la ruta '/hello/<name>' y '/'es greet() porque
## es la primer funcion escrita a continuacion de las rutas
def greet(name='Stranger'):
    return template('Hello {{name2}}', name2=name)

@app.post('/auth-svc/param')
def hello_json():
    data = request.json
    param = data['param']
    ret = {"status":"OK", "param": param}
    return ret

@app.get('/auth-svc/test')
def test():
    auth = request.headers['authorization']
    print auth
    ret = {"status":"OK"}
    return ret
    

@app.post('/auth-svc/login')
def login():
    data = request.json
    param = data['user']
    param2 = data['pass'] 
    ret = {"status":"OK"}   

    try:
        cnx = pymysql.connect(**mysql_config)
        cursor = cnx.cursor()
        insert_test = "SELECT name FROM users WHERE name= %s and password=%s"
        data = (param, param2) # tupla
        cursor.execute(insert_test, data)            
        res = cursor.fetchone();
        if res == None:
            ret = {"status":"ERR","msg":"Username or password incorrect"}
        else:            
            payload = {'userId': param}
            token = jwt.generate_jwt(payload, private_key, 'RS256',
            datetime.timedelta(minutes=5))
            ret = {"status":"OK", "token":token}            
        cnx.commit()
        cursor.close()        
    except pymysql.OperationalError as err:        
        print "Failed to select data: {}".format(err)        
    finally:
        cnx.close()            
    return ret

@app.post('/auth-svc/register')
def register():
    data = request.json
    param = data['username']
    param2 = data['pass']        
    ret = {"status":"OK"}
    try:
        cnx = pymysql.connect(**mysql_config)
        cursor = cnx.cursor()
        insert_test = "INSERT INTO users (name, password) VALUES (%s, %s)"
        data = (param, param2) # tupla
        cursor.execute(insert_test, data)
        cnx.commit()        
        cursor.close()
    except pymysql.IntegrityError as err:        
        print "Failed to insert data: {}".format(err)
        ret = {"status":"ERR","msg":"Username already existss"}
    finally:
        cnx.close()        
    return ret

if __name__ == 'main':
    insert_test()

run(app, host='127.0.0.1', port=8081)