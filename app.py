
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask import Flask, request, render_template, redirect, abort, url_for
import psycopg2.pool
import psycopg2.extras
import json
import secrets
import time
from datetime import datetime

db_user = "postgres"
db_password = "ale"
db_name = "sagre"
db_host = "localhost"

db_config = {
    'user': db_user,
    'password': db_password,
    'database': db_name,
    'host': db_host
}



print(str(db_config))

cnxpool = psycopg2.pool.ThreadedConnectionPool(minconn=1, maxconn=100,
                                               **db_config)

app = Flask(__name__)


########################## HELPER

def getDataSettingNull():
    d = request.json
    for k in d:
        if d[k] == "":
            d[k] = None
    return d


def identity(x): return x


def defaultToJson(data, status=200):
    return json.dumps(data, indent=4, sort_keys=True, default=str), status, {'Content-Type': 'application/json; charset=utf-8'}


def do(query, applyRes=defaultToJson, auth="cms"):
    cnx = cnxpool.getconn()
    with cnx.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
        if auth is not None:
            permissions = getLogin(cursor)
            if permissions is not None: permissions["login"] = True

            if isinstance(auth, str):
                if permissions is None:
                    return applyRes({"message": "E' necessario effettuare il login"}, 401)
                if not permissions[auth]:
                    return applyRes({"message": "E' necessaria un'autorizzazione di tipo " + auth}, 403)
            else:
                auth(cursor, permissions)

        try:
            res = query(cursor)
        except RuntimeError as e:
            cnx.rollback()
            return defaultToJson({"status": e}, 400)

    res = applyRes(res)
    cnx.commit()
    cnxpool.putconn(cnx)

    return res


########################### cursor_*

def cursor_insert(cursor, data, table, fields, returning=None):
    fields = list(filter(lambda x: x in data.keys(), fields))

    s1 = ", ".join(fields)
    s2 = ", ".join(map(lambda x: "%s", fields))

    query = "insert into " + table + "(" + s1 + ") values (" + s2 + ") "

    if returning is not None:
        query += " returning " + returning

    vals = [data[i] for i in fields]

    print("query=", query)
    print("vals=", vals)

    cursor.execute(query, vals)


def cursor_update(cursor, data, table, fields, cond, returning=None):
    fields = list(filter(lambda x: x in data, fields))

    s1 = ", ".join(map(lambda x: x + "=%s", fields))
    s2 = " and ".join(map(lambda x: x + "=%s", cond))

    query = "update " + table + " set " + s1 + " where " + s2
    if returning is not None:
        query += " returning " + returning

    cond_data = [x + "_old" for x in cond]

    for c in cond:
        c_old = c + "_old"
        if c_old not in data and c in data:
            data[c_old] = data[c]

    vals = [data[i] for i in fields + cond_data]

    print("query=", query)
    print("vals=", vals)
    print("cond_data=", cond_data)

    cursor.execute(query, vals)


def cursor_delete(cursor, data, table, cond):
    s2 = " and ".join(map(lambda x: x + "=%s", cond))

    query = "delete from " + table + " where " + s2

    vals = [data[i] for i in cond]

    print("query=", query)
    print("vals=", vals)

    cursor.execute(query, vals)


########################## login

@app.route("/api/do_login", methods=["POST"])
def doLogin():
    data = getDataSettingNull()

    def f(cursor):
        cursor.execute("select * from auth where email=%s and password=%s", (data["email"], data["password"]))
        row = cursor.fetchone()

        if row is None:
            return {"message": "not found", "token": None}, 401

        row["token"] = str(row["email"]) + secrets.token_urlsafe(32)

        cursor_insert(cursor, row, "token", ["token", "email"])

        return {"message": "ok", "token": row["token"]}

    return do(f, auth=None)


@app.route("/api/recupera_pw", methods=["POST"])
def do_recuperaPw():
    token = request.headers.get("Authorization")
    data = getDataSettingNull()

    def f(cursor):
        cursor.execute("select * from token natural join auth where email=%s and token=%s", (data["email"], token))
        row = cursor.fetchone()

        if row is None:
            return {"message": "not found"}, 401

        data["email_old"] = data["email"]
        cursor_update(cursor, data, "auth", ["password"], ["email"])
        cursor_delete(cursor, data, "token", ["email"])

        return {"message": "ok"}

    return do(f, auth=None)


@app.route("/api/richiedi_recupera_pw", methods=["POST"])
def get_recuperaPw():
    data = getDataSettingNull()

    def f(cursor):
        d = dict()
        d["token"] = secrets.token_urlsafe(20)
        d["email"] = data["email"]

        cursor_insert(cursor, d, "token", ["token", "email"])

        import smtplib, ssl

        me, you = "pc.cms.sanvito@gmail.com", d["email"]

        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Link"
        msg['From'] = me
        msg['To'] = you

        # Create the body of the message (a plain-text and an HTML version).
        link = "http://localhost:8080/render/recupera_pw?token=" + d["token"]

        text = "Segui il link per recuperare la password\n" + link
        html = """\
        <html>
          <head></head>
          <body>
            <p>Recupero password<br>
               Segui il link per recuperare la password<br>
               <a href=""" + link + """>link</a>
            </p>
          </body>
        </html>
        """

        # Record the MIME types of both parts - text/plain and text/html.
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')

        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        msg.attach(part1)
        msg.attach(part2)

        smtp_server = "smtp.gmail.com"
        port = 587  # For starttls
        sender_email = "pc.cms.sanvito@gmail.com"
        password = "0m9u0r2u3p9ur2pm9DS"

        # Create a secure SSL context
        context = ssl.create_default_context()

        server = smtplib.SMTP(smtp_server, port)
        server.ehlo()  # Can be omitted
        server.starttls(context=context)  # Secure the connection
        server.ehlo()  # Can be omitted
        server.login(sender_email, password)
        server.sendmail(me, you, msg.as_string())
        # TODO: Send email here
        server.quit()

        return {"message": "ok"}

    return do(f, auth=None)


@app.route("/api/do_logout", methods=["POST"])
def doLogout():
    token = request.headers.get("Authorization")
    if token is None:
        return {"res": "token null"}, 400

    def f(cursor):
        cursor.execute("delete from token where token = %s returning token", (token,))

        return {"message": "ok", "data": cursor.fetchone()}

    return do(f, auth=None)


def getLogin(cursor):
    token = request.headers.get("Authorization")

    cursor.execute("select * from token natural join auth where token=%s", (token,))
    row = cursor.fetchone()

    if row is not None:
        del row["password"]

    print("login as", row)

    return row


########################### generate_*

def generate_update(table, fields, cond, returning=None, auth="cms", prefix="/api", apiname=None):
    apiname = apiname or table

    def f_update():
        data = getDataSettingNull()

        def f(cursor):
            cursor_update(cursor, data, table, fields, cond, returning)

            res = {"message": "ok"}

            if returning:
                v = cursor.fetchone()
                res[returning] = v[returning]

            return res

        return do(f, auth=auth)

    app.add_url_rule(prefix + "/update_" + apiname, "update_" + apiname, f_update, methods=["POST"])


def generate_create(table, fields, returning, auth="cms", prefix="/api"):
    def f_create():
        data = getDataSettingNull()

        def f(cursor):
            cursor_insert(cursor, data, table, fields, returning)

            res = {"message": "ok"}

            if returning:
                v = cursor.fetchone()
                res[returning] = v[returning]

            return res

        return do(f, auth=auth)

    app.add_url_rule(prefix + "/create_" + table, "create_" + table, f_create, methods=["POST"])


def generate_set(table, fields, auth="cms", prefix="/api"):
    def f_set():
        data = getDataSettingNull()

        def f(cursor):
            cursor.execute("delete from " + table)

            for elem in data:
                cursor_insert(cursor, elem, table, fields)

            return {"message": "ok"}

        return do(f, auth=auth)

    app.add_url_rule(prefix + "/set_" + table, "set_" + table, f_set, methods=["POST"])


def generate_delete(table, cond, auth="cms", prefix="/api"):
    def f_delete():
        data = getDataSettingNull()

        def f(cursor):
            cursor_delete(cursor, data, table, cond)

            return {"message": "ok"}

        return do(f, auth=auth)

    app.add_url_rule(prefix + "/delete_" + table, "delete_" + table, f_delete, methods=["DELETE"])


def generate_get(table, auth="login", query=None, prefix="/api"):
    if query is None:
        query = "select * from " + table

    def f_get():
        def f(cursor):
            cursor.execute(query)

            return cursor.fetchall()

        return do(f, auth=auth)

    app.add_url_rule(prefix + "/get_" + table, "get_" + table, f_get, methods=["GET"])


# create read set delete
# if cond is none -> cond = fields
# cond = chiave
# fields = attributi
# returning = string
def generate_crsd(table, fields, cond=None, returning=None, auth="cms", auth_get="login", prefix="/api"):
    if auth_get == "same":
        auth_get = auth

    if cond is None:
        cond = fields

    generate_create(table, fields, returning, auth=auth, prefix=prefix)
    generate_delete(table, cond, auth=auth, prefix=prefix)
    generate_get(table, auth=auth_get, prefix=prefix)
    generate_set(table, fields, auth=auth, prefix=prefix)
    generate_update(table, fields, cond, returning, auth=auth, prefix=prefix)


########################### API SPEFICICHE

@app.route('/api/create_ordine', methods=["POST"])
def create_ordine():
    data = getDataSettingNull()

    def f(cursor):
        cursor.execute("select nextval('sequence_progressivo')")       #numero progressivo
        progressivo = cursor.fetchone()["nextval"]
        _time = datetime.now().replace(microsecond=0).isoformat()

        data["time"] = _time
        data["ordine"] = f"{_time}_{progressivo}"
        data["progressivo"] = progressivo

        login = getLogin(cursor)

        for p in data["prodotti"]:
            p = p | login | data

            cursor.execute("select reparto, sezione_menu, coalesce(cauzione_unitaria, 0.0) as cauzione_unitaria, "
                           "prezzo_unitario, stato_iniziale as stato, stato_iniziale, quantita_disponibile from prodotti where prodotto = %s", (p["prodotto"], ))
            p = p | cursor.fetchone()

            p["cauzione_totale"] = p["cauzione_unitaria"] * p["quantita"]
            p["prezzo_totale"] = p["prezzo_unitario"] * p["quantita"]

            cursor_insert(cursor, p, "ordini", ["ordine", "progressivo", "reparto", "prodotto", "quantita", "stato", "note",
                    "cassa", "tavolo", "cucina", "time", "annullato", "prezzo_unitario", "prezzo_totale", "cauzione_unitaria",
                    "cauzione_totale", "sezione_menu", "stato_iniziale"])

            if p["quantita_disponibile"] is not None:          #decrementa quantita disponibile se presente
                p["quantita_disponibile"] -= p["quantita"]
                cursor_update(cursor, p, "prodotti", ["quantita_disponibile"], ["prodotto"])

        return {"status": "ok", "ordine": data["ordine"], "time": data["time"]}

    return do(f, auth="operator")



generate_update("prodotti", ["quantita_disponibile"], ["prodotto"], auth="operator", apiname="quantita_prodotto")


@app.route('/api/update_stato_ordine', methods=["POST"])
def update_stato_ordine():
    data = getDataSettingNull()

    def f(cursor):
        data["stato_iniziale"] = "generato"

        cursor_update(cursor, data, "ordini", ["stato"], ["ordine", "stato_iniziale"])

        return {"status": "ok"}

    return do(f, auth="operator")


@app.route('/api/ristampa_ordine', methods=["POST"])
def ristampa_ordine():
    data = getDataSettingNull()

    def f(cursor):
        print("stampa ordine", data["ordine"])

        return {"status": "ok"}

    return do(f, auth="operator")

@app.route('/api/annulla_ordine', methods=["POST"])
def annulla_ordine():
    data = getDataSettingNull()

    def f(cursor):
        data["annullato"] = True

        cursor_update(cursor, data, "ordini", ["annullato"], ["ordine"])

        return {"status": "ok"}

    return do(f, auth="operator")

def selectDictKeys(data, keys):
    return {k: v for (k, v) in data.items() if k in keys}

@app.route('/api/get_ordini_in_corso', methods=["GET"])
def get_ordini_in_corso():
    def f(cursor):
        login = getLogin(cursor)

        cursor.execute("select * from ordini where not annullato and cucina = %s", (login["cucina"], ))
        res = cursor.fetchall()

        temp = {}
        for t in res:
            if t["ordine"] not in temp:
                temp[t["ordine"]] = selectDictKeys(t, ["cassa", "ordine", "progressivo", "tavolo", "time"]) | {"prodotti": []}

            temp[t["ordine"]]["prodotti"].append(selectDictKeys(t, ["cauzione_totale", "cauzione_unitaria", "note", "prezzo_totale", "prezzo_unitario",
                    "prodotto", "quantita", "reparto", "sezione_menu", "stato"]))
        res = temp

        for t in res.values():
            t["costo_totale_ordine"] = sum(map(lambda x: x["prezzo_totale"], t["prodotti"]))
            t["cauzione_totale_ordine"] = sum(map(lambda x: x["cauzione_totale"], t["prodotti"]))
        res=list(temp.values())

        return {"status": "ok", "ordini": res}


    return do(f, auth="operator")



@app.route("/", methods=["GET"])
def home():
    return "Progetto Sagre 2022!"


if __name__ == 'app':
    with open("url_map.txt", "w+") as fout:
        fout.write(str(app.url_map)[5:-2].replace(",\n ", "\n"))

    app.run(host='localhost', port=5000, debug=True)
