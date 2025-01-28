from flask import Flask,render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import select
import hashlib


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reservations.db'
db = SQLAlchemy(app)

MAX_PERSONE_PER_TURNO = 80

app.secret_key = 'your_secret_key' 


#Modello per il db
class Utente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable = False)
    password = db.Column(db.String(80), nullable = False)
    nome = db.Column(db.String(80), nullable = False)
    cognome = db.Column(db.String(80), nullable = False)
    email = db.Column(db.String(120), nullable = False, unique = True)
    telefono = db.Column(db.String(20), nullable = False)


class Prenotazione(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_utente = db.Column(db.Integer, db.ForeignKey('utente.id'), nullable = False)
    persone = db.Column(db.Integer, nullable=False)
    data = db.Column(db.String(10), nullable=False)
    turno = db.Column(db.String(10), nullable=False)

    tavoli = db.relationship('Tavolo', secondary='prenotazione_tavolo', backref=db.backref('prenotazioni', lazy='dynamic'))
    utente = db.relationship('Utente', backref = db.backref('prenotazioni'), lazy = True)

class Tavolo(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    numero_tavolo = db.Column(db.Integer, nullable = False)
    posti = db.Column(db.Integer, nullable = False)

class PrenotazioneTavolo(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    id_prenotazione = db.Column(db.Integer, db.ForeignKey('prenotazione.id', ondelete ='CASCADE'), nullable = False)
    id_tavolo = db.Column(db.Integer, db.ForeignKey('tavolo.id', ondelete = "CASCADE"), nullable = False)

#crea il db
with app.app_context():
    db.create_all()

@app.before_request
def before_request():
    # Imposta 'logged_in' su False all'inizio di ogni richiesta
    if 'logged_in' not in session:
        session['logged_in'] = False


#Route per index.html
@app.route('/')
def index():
    logged_in = session.get('logged_in', False)
    return render_template('index.html', logged_in = logged_in) #passa il valore di logged_in, utilizzato poi in HTML per scegliere se mostrare i tasti per l'accesso/registrazione o per le prenotazioni

#route per la pagina di registrazione
@app.route('/registrazione', methods = ['GET'])
def registrazione():
    return render_template('form_registrazione.html')

#route per la logica di registrazione
@app.route('/registra', methods=['POST'])
def registra():

    #recupera i dati inviati
    dati = request.json 
    
    #converte la password utilizzando l'algoritmo sha-256 e trasforma in esadecimale
    hashed_pwd = hashlib.sha256(dati.get('password').encode('utf-8')).hexdigest()

    nome = dati.get('nome')
    cognome = dati.get('cognome')
    email = dati.get('email')
    telefono = dati.get('telefono')
    username = dati.get('username')

    #se l'username è utilizzato da un altro utente, chiedi di inserire un nuovo username
    utente_esistente = Utente.query.filter_by(username = username).first()
    if utente_esistente:
        return jsonify({'error':'Questo username è già utilizzato da un altro utente'}),400
    if (not nome or not cognome or not telefono or not username or not hashed_pwd):
        return jsonify({'error':'Dati non inseriti correttamente.'}),400

    nuovo_utente = Utente(
        nome = nome,
        cognome = cognome,
        email = email, 
        telefono = telefono,
        username = username,
        password = hashed_pwd
    )

    db.session.add(nuovo_utente)
    db.session.commit()

    return jsonify({'message':'Utente registrato con successo'}),200
    

#Route per il form
@app.route('/form', methods = ['GET'])
def form():
   return render_template('form.html')

# Route per gestire la prenotazione
@app.route('/prenota', methods=['POST'])
def prenota():
    try:
        #recupero dei dati inviati
        
        dati = request.json

        persone = int(dati.get('persone'))
        data = dati.get('data')
        turno = dati.get('turno')

        #Conta il totale delle prenotazioni in un determinato giorno e turno e verifica che non siano superiori alla capacità massima del locale
        prenotazioni_esistenti = Prenotazione.query.filter_by(data=data, turno=turno).all()
        totale_prenotazioni = sum(p.persone for p in prenotazioni_esistenti)
        if totale_prenotazioni + persone > MAX_PERSONE_PER_TURNO:
            return jsonify({"message":"Totale massimo di prenotazioni raggiunte per il giorno selezionato."}), 400
        
        #controllo sulla validità della data
        giorno = datetime.now().strftime(f'%Y-%m-%d')
        if data < giorno:
            return jsonify ({"error":"Non è ancora possibile effettuare una prenotazione indietro nel tempo!"}),400
        username = session.get('username')
        #recupera l'utente a cui associare la prenotazione tramite l'username associato alla sessione
        utente = Utente.query.filter_by(username = username).first()

        #Controllo per verificare la disponibilità dei tavoli
        id_tavoli_occupati = select(PrenotazioneTavolo.id_tavolo).join(Prenotazione).filter(
            Prenotazione.data == data,
            Prenotazione.turno == turno
        ).subquery()

        tavoli_disponibili = Tavolo.query.filter(~Tavolo.id.in_(id_tavoli_occupati)).all()
        
        #Assegnazione dei tavoli necessari alla prenotazione
        tavoli_assegnati = []
        posti_assegnati = 0
        for tavolo in tavoli_disponibili:
            tavoli_assegnati.append(tavolo)
            posti_assegnati+= tavolo.posti
            if posti_assegnati >= persone:
                break
        if posti_assegnati < persone:
            return jsonify({"error":"Non ci sono abbastanza tavoli disponibili in questo data e questo turno."}),400
        

        nuova_prenotazione = Prenotazione(
            persone = persone,
            data = data,
            turno = turno,
            id_utente = utente.id
        )
        db.session.add(nuova_prenotazione)
        db.session.commit()
        
        for tavolo in tavoli_assegnati:
            associazione = PrenotazioneTavolo(
                id_prenotazione = nuova_prenotazione.id,
                id_tavolo = tavolo.id
            )
            db.session.add(associazione)
            db.session.commit()

        return jsonify({"message":"Prenotazione registrata con successo!"}),200
    except ValueError as ve:
        return jsoinfy({"error":"Errore nella prenotazione."}),400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error":"Errore nella prenotazione."}),400

#Route per login.html
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        

        utente = Utente.query.filter_by(username=username).first()
        
        if utente and hashlib.sha256(password.encode('utf-8')).hexdigest() == utente.password:
            session['logged_in'] = True
            session['username'] = username
            session['user_id'] = utente.id
            return redirect(url_for('index'))  
        else:
            return render_template('login.html')
    return render_template('login.html')

@app.route('/logout')
def logout():

    #elimina dalla sessione i dati associati all'utente che ha effettuato il login
    session.pop('user_id', None) 
    session.pop('logged_in',None)
    session.pop('username',None)
    return redirect(url_for('index'))


@app.route('/tutte_le_prenotazioni', methods = ['GET'])
def visualizza_tutte_le_prenotazioni():
    prenotazioni = Prenotazione.query.all()
    lista_prenotazioni = [
        {
            "id":prenotazione.id,
            "nome":prenotazione.utente.nome,
            "cognome":prenotazione.utente.cognome,
            "email":prenotazione.utente.email,
            "telefono":prenotazione.utente.telefono,
            "persone":prenotazione.persone,
            "data":prenotazione.data,
            "turno":prenotazione.turno,
            "tavoli":[tavolo.numero_tavolo for tavolo in prenotazione.tavoli]
        }
        for prenotazione in prenotazioni
    ]
    return jsonify(lista_prenotazioni)


@app.route('/visualizza_admin')
def visualizza_tabella_admin():
    return render_template('visualizza_prenotazioni.html')

#Route per prenotazioni.html
@app.route('/prenotazioni', methods=['GET'])
def visualizza_pagina_prenotazioni():
    return render_template('prenotazioni.html')

#Route per visualizzare le prenotazioni da parte dell'utente
@app.route('/lista_prenotazioni', methods=['GET'])
def visualizza_prenotazioni():

    #recupera l'id dell'utente tramite la sessione per poi utilizzarlo nella query 
    #per visualizzare solo le prenotazioni associate a quel determinato utente
    user_id = session.get('user_id')
    prenotazioni = Prenotazione.query.filter_by(id_utente = user_id).all()
    
    lista_prenotazioni = [
        {
            "id": prenotazione.id,
            "nome": prenotazione.utente.nome,
            "cognome": prenotazione.utente.cognome,
            "email": prenotazione.utente.email,
            "telefono": prenotazione.utente.telefono,
            "persone": prenotazione.persone,
            "data": prenotazione.data,
            "turno": prenotazione.turno
        }
        for prenotazione in prenotazioni
    ] 

    return jsonify(lista_prenotazioni)

#Route per visualizzare la pagina di modifica
@app.route('/modifica_prenotazione', methods=['GET'])
def visualizza_modifica_prenotazioni():
    return render_template('modifica_prenotazioni.html')


@app.route('/script_modifica/<int:id>', methods=['PUT'])
def update_prenotazione(id):
    try:

        #recupera i dati forniti nel form di modifica
        dati_modificati = request.json
        #recupera la prenotazione da modificare in base all'id prenotazione 
        prenotazione = db.session.get(Prenotazione,id)
        
        giorno = datetime.now().strftime(f'%Y-%m-%d')


        if not(dati_modificati.get('persone') or dati_modificati.get('data') or dati_modificati.get('turno')):
            return jsonify ({"message":"Ci sono dei campi mancanti."})
            
        if(dati_modificati.get('data') < giorno):
            return jsonify ({"message":"Errore nel campo data!"})
            
        prenotazione.persone = int(dati_modificati['persone'])
        prenotazione.data = dati_modificati['data']
        prenotazione.turno = dati_modificati['turno']

        
        #Trova tutti i tavoli associati alla prenotazione da modificare
        #filtrando la tabella di associazione tra prenotazione e tavoli in base all'id della prenotazione
        tavoli_associati = PrenotazioneTavolo.query.filter_by(id_prenotazione = id).all()
        
        #cancella tutti i tavoli associati alla prenotazione
        for tavolo in tavoli_associati:
            
            db.session.delete(tavolo)
        db.session.commit()
        
        #ricalcola i tavoli disponibili per la data ed il turno scelti al momento della modifica
        tavoli_occupati = select(PrenotazioneTavolo.id_tavolo).join(Prenotazione).filter(
            Prenotazione.data == dati_modificati['data'],
            Prenotazione.turno == dati_modificati['turno']
        ).subquery()

        tavoli_disponibili = Tavolo.query.filter(~Tavolo.id.in_(tavoli_occupati)).all()

            
        totale_posti_disponibili = len(tavoli_disponibili) * 4

            
        if totale_posti_disponibili  < prenotazione.persone:
            return jsonify({"message":"Impossibile modificare la prenotazione, non c'è disponibilità di posti per la data ed il turno selezionati."})

        #assegna nuovamente i tavoli alla prenotazione modificata, in base ai tavoli disponibili.    
        tavoli_assegnati = []
        
        posti_assegnati = 0
        
        for tavolo in tavoli_disponibili:
            tavoli_assegnati.append(tavolo)
            posti_assegnati+= 4
            
            if posti_assegnati >= prenotazione.persone:
                break
        
        for tavolo in tavoli_assegnati:
            prenotazione_tavolo = PrenotazioneTavolo(
                id_prenotazione = prenotazione.id,
                id_tavolo = tavolo.id
            )
            db.session.add(prenotazione_tavolo)
            
        db.session.commit()
        return "",200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message":f"Errore: {str(e)}"})

@app.route('/script_elimina/<int:id>', methods=['DELETE'])
def elimina_prenotazione(id):
    prenotazione = Prenotazione.query.get(id)
    if prenotazione:
        db.session.delete(prenotazione)
        db.session.commit()
        return "",200
    else:
        return "",404

#funzione per pulire il db dalle prenotazioni precedenti alla data odierna
def cancella_prenotazioni_obsolete():
    giorno = datetime.now().strftime(f'%Y-%m-%d')
    prenotazioni_obsolete = Prenotazione.query.filter(Prenotazione.data < giorno).all()

    for prenotazione in prenotazioni_obsolete:
        db.session.delete(prenotazione)
    db.session.commit()


#funzione per popolare la tabella Tavoli
def popola():
    try:

        with app.app_context():
            # Rimuovi eventuali tavoli esistenti per evitare duplicati
            Tavolo.query.delete()
            db.session.commit()


            for i in range(1, 21):
                numero_tavolo = f"A{i}"  # Numero tavolo in formato A1, A2, ...
                tavolo = Tavolo(numero_tavolo=numero_tavolo, posti=4)
                db.session.add(tavolo)

            db.session.commit()
            
    except Exception as e:
        db.session.rollback()
        

if __name__ == "__main__":
    with app.app_context():
        popola()
        cancella_prenotazioni_obsolete()
    app.run(debug=True)


