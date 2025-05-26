from flask import Flask, render_template, redirect, g, request
import pymysql.cursors
from datetime import datetime
app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

def get_db():
    if 'db' not in g:
        g.db =  pymysql.connect(
            host="serveurmysql.iut-bm.univ-fcomte.fr", # à modifier
            user="sdeloffr", # à modifier
            password="mdp", # à modifier
            database="BDD_sdeloffr", # à modifier
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
    return g.db

@app.teardown_appcontext
def teardown_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

@app.route('/')
def show_layout():
    return render_template('layout.html')

# ---------------------------------------------------------------------#

@app.route('/benne/show')
def show_benne():
    mycursor = get_db().cursor()
    sql = '''   SELECT benne.id_benne, centre.nom_centre, benne.volume, benne.nb_benne, produit.libelle_produit
            FROM benne
            INNER JOIN centre ON benne.num_centre = centre.num_centre
            INNER JOIN produit ON benne.num_produit = produit.num_produit
            ORDER BY centre.nom_centre ASC;
                 '''
    mycursor.execute(sql)
    bennes = mycursor.fetchall()
    return render_template('benne/benne_show.html', bennes=bennes)

@app.route('/benne/add', methods=['GET'])
def add_benne():
    mycursor = get_db().cursor()
    sql = '''
        SELECT centre.num_centre AS id, centre.nom_centre AS nom, centre.adresse_centre AS adresse
        FROM centre;
        '''
    mycursor.execute(sql)
    centres = mycursor.fetchall()

    sql = '''
        SELECT produit.num_produit AS id, produit.libelle_produit AS nom
        FROM produit;
        '''
    mycursor.execute(sql)
    produits = mycursor.fetchall()
    return render_template('benne/benne_add.html', centres=centres, produits=produits)

@app.route('/benne/add', methods=['POST'])
def valid_add_benne():
    nbBenne = request.form.get('nbBenne')
    volume = request.form.get('volume')
    centre = request.form.get('centre')
    produit = request.form.get('produit')
    print(nbBenne, volume, centre, produit)
    mycursor = get_db().cursor()
    sql='''
    INSERT INTO benne(id_benne, nb_benne, volume, num_centre, num_produit) VALUES (NULL, %s, %s, %s, %s);
    '''
    tuple_insert=(nbBenne, volume, centre, produit)
    mycursor.execute(sql, tuple_insert)

    get_db().commit()
    return redirect('/benne/show')

@app.route('/benne/edit', methods=['GET'])
def edit_benne():
    id=request.args.get('id')
    if id != None and id.isnumeric():
        indice = int(id)
        mycursor = get_db().cursor()
        sql = '''
                SELECT id_benne, nb_benne, volume, num_centre, num_produit 
                FROM benne
                WHERE id_benne=%s;
                '''
        mycursor.execute(sql, indice)
        benne = mycursor.fetchone()

        sql = '''
                SELECT centre.num_centre AS id, centre.nom_centre AS nom, centre.adresse_centre AS adresse
                FROM centre;
                '''
        mycursor.execute(sql)
        centres = mycursor.fetchall()

        sql = '''
                SELECT produit.num_produit AS id, produit.libelle_produit AS nom
                FROM produit;
                '''
        mycursor.execute(sql)
        produits = mycursor.fetchall()

        get_db().commit()
    else:
        benne=[]
    return render_template('benne/benne_edit.html', benne=benne, centres=centres, produits=produits)

@app.route('/benne/edit', methods=['POST'])
def valid_edit_benne():
    id = request.form.get('id')
    nbBenne = request.form.get('nbBenne')
    volume = request.form.get('volume')
    centre = request.form.get('centre')
    produit = request.form.get('produit')

    mycursor = get_db().cursor()
    sql = '''
        UPDATE benne 
        SET nb_benne = %s, volume = %s, num_centre = %s, num_produit = %s
        WHERE id_benne = %s;
    '''
    tuple_insert=(nbBenne, volume, centre, produit, id)
    mycursor.execute(sql, tuple_insert)
    get_db().commit()

    return redirect('/benne/show')

@app.route('/benne/delete')
def delete_benne():
    id = request.args.get('id', '')
    mycursor = get_db().cursor()
    sql = '''   DELETE FROM benne WHERE id_benne=%s;    '''
    turple_insert = (id)
    mycursor.execute(sql, turple_insert)
    get_db().commit()
    return redirect('/benne/show')

@app.route('/benne/etat')
def etat_benne():
    mycursor = get_db().cursor()
    sql = '''
        SELECT centre.num_centre AS id, centre.nom_centre AS nom, centre.adresse_centre AS adresse
        FROM centre;
        '''
    mycursor.execute(sql)
    centres = mycursor.fetchall()

    sql = '''
        SELECT produit.num_produit AS id, produit.libelle_produit AS nom
        FROM produit;
        '''
    mycursor.execute(sql)
    produits = mycursor.fetchall()

    sql = '''   SELECT benne.id_benne, centre.nom_centre, benne.volume, benne.nb_benne, produit.libelle_produit
                FROM benne
                INNER JOIN centre ON benne.num_centre = centre.num_centre
                INNER JOIN produit ON benne.num_produit = produit.num_produit
                ORDER BY centre.nom_centre ASC;
                     '''
    mycursor.execute(sql)
    bennes = mycursor.fetchall()

    sql = '''   SELECT SUM(benne.volume*benne.nb_benne) AS v, SUM(benne.nb_benne) AS nb
                                FROM benne
                            '''
    mycursor.execute(sql)
    Vtotal = mycursor.fetchone()

    return render_template('benne/benne_etat.html', centres=centres, produits=produits, bennes=bennes, Vtotal=Vtotal)

@app.route('/benne/etat', methods=['POST'])
def valid_etat_benne():
    mycursor = get_db().cursor()
    sql = '''
            SELECT centre.num_centre AS id, centre.nom_centre AS nom, centre.adresse_centre AS adresse
            FROM centre;
            '''
    mycursor.execute(sql)
    centres = mycursor.fetchall()

    sql = '''
            SELECT produit.num_produit AS id, produit.libelle_produit AS nom
            FROM produit;
            '''
    mycursor.execute(sql)
    produits = mycursor.fetchall()
    centre = request.form.get('centre')
    produit = request.form.get('produit')
    if centre == "" and produit == "":
        sql = '''   SELECT benne.id_benne, centre.nom_centre, benne.volume, benne.nb_benne, produit.libelle_produit
                    FROM benne
                    INNER JOIN centre ON benne.num_centre = centre.num_centre
                    INNER JOIN produit ON benne.num_produit = produit.num_produit
                    ORDER BY centre.nom_centre ASC;
                    '''
        mycursor.execute(sql)
        bennes = mycursor.fetchall()

        sql = '''   SELECT SUM(benne.volume*benne.nb_benne) AS v, SUM(benne.nb_benne) AS nb
                            FROM benne
                        '''
        mycursor.execute(sql)
    elif centre == "" and produit != "":
        sql = '''   SELECT benne.id_benne, centre.nom_centre, benne.volume, benne.nb_benne, produit.libelle_produit
                    FROM benne
                    INNER JOIN centre ON benne.num_centre = centre.num_centre
                    INNER JOIN produit ON benne.num_produit = produit.num_produit
                    WHERE benne.num_produit = %s
                    ORDER BY centre.nom_centre ASC;
                    '''
        mycursor.execute(sql, produit)
        bennes = mycursor.fetchall()

        sql = '''   SELECT SUM(benne.volume*benne.nb_benne) AS v, SUM(benne.nb_benne) AS nb
                            FROM benne
                            WHERE benne.num_produit = %s
                        '''
        mycursor.execute(sql, produit)
    elif centre != "" and produit == "":
        sql = '''   SELECT benne.id_benne, centre.nom_centre, benne.volume, benne.nb_benne, produit.libelle_produit
                    FROM benne
                    INNER JOIN centre ON benne.num_centre = centre.num_centre
                    INNER JOIN produit ON benne.num_produit = produit.num_produit
                    WHERE benne.num_centre = %s
                    ORDER BY centre.nom_centre ASC;
                    '''
        mycursor.execute(sql, centre)
        bennes = mycursor.fetchall()

        sql = '''   SELECT SUM(benne.volume*benne.nb_benne) AS v, SUM(benne.nb_benne) AS nb
                            FROM benne
                            WHERE benne.num_centre = %s
                        '''
        mycursor.execute(sql, centre)
    else:
        sql = '''   SELECT benne.id_benne, centre.nom_centre, benne.volume, benne.nb_benne, produit.libelle_produit
                    FROM benne
                    INNER JOIN centre ON benne.num_centre = centre.num_centre
                    INNER JOIN produit ON benne.num_produit = produit.num_produit
                    WHERE benne.num_centre = %s AND benne.num_produit = %s
                    ORDER BY centre.nom_centre ASC;
                    '''
        tuple_insert = (centre, produit)
        mycursor.execute(sql, tuple_insert)
        bennes = mycursor.fetchall()

        sql = '''   SELECT SUM(benne.volume*benne.nb_benne) AS v, SUM(benne.nb_benne) AS nb
                    FROM benne
                    WHERE benne.num_centre = %s AND benne.num_produit = %s
                '''
        tuple_insert = (centre, produit)
        mycursor.execute(sql, tuple_insert)

    Vtotal = mycursor.fetchone()
    if Vtotal['v'] == None:
        Vtotal['v'] = 0
    if Vtotal['nb'] == None:
        Vtotal['nb'] = 0
    return render_template('benne/benne_etat.html', produits=produits, centres=centres, bennes=bennes, Vtotal=Vtotal)

# ---------------------------------------------------------------------#

@app.route('/vehicule/show')
def show_vehicule():
    mycursor = get_db().cursor()
    sql = '''   SELECT *
            FROM vehicule
            INNER JOIN type_vehicule ON vehicule.num_type = type_vehicule.num_type
            INNER JOIN marque ON vehicule.num_marque = marque.num_marque
            ORDER BY type_vehicule.libelle_type ASC;
                 '''
    mycursor.execute(sql)
    vehicules = mycursor.fetchall()
    return render_template('vehicule/vehicule_show.html', vehicules=vehicules)

@app.route('/vehicule/add', methods=['GET'])
def add_vehicule():
    mycursor = get_db().cursor()
    sql = '''
        SELECT type_vehicule.num_type AS id, type_vehicule.libelle_type AS libelle
        FROM type_vehicule;
        '''
    mycursor.execute(sql)
    type_vehicules = mycursor.fetchall()

    sql = '''
        SELECT marque.num_marque AS id, marque.libelle_marque AS libelle
        FROM marque;
        '''
    mycursor.execute(sql)
    marques = mycursor.fetchall()
    return render_template('vehicule/vehicule_add.html', type_vehicules=type_vehicules, marques=marques)

@app.route('/vehicule/add', methods=['POST'])
def valid_add_vehicule():
    num_type = request.form.get('type_vehicule')
    num_marque = request.form.get('marque')
    poid_max = request.form.get('poid_max')
    date_achat = request.form.get('date_achat')
    print(num_type, num_marque, poid_max, date_achat)
    mycursor = get_db().cursor()
    sql='''
    INSERT INTO vehicule(num_vehicule, num_type, num_marque, poid_max, date_achat)
     VALUES (NULL, %s, %s, %s, %s);
    '''
    tuple_insert=(num_type, num_marque, poid_max, date_achat)
    mycursor.execute(sql, tuple_insert)

    get_db().commit()
    return redirect('/vehicule/show')

@app.route('/vehicule/edit', methods=['GET'])
def edit_vehicule():
    id=request.args.get('id')
    if id != None and id.isnumeric():
        indice = int(id)
        mycursor = get_db().cursor()
        sql = '''
                SELECT *
                FROM vehicule
                WHERE num_vehicule=%s;
                '''
        mycursor.execute(sql, indice)
        vehicule = mycursor.fetchone()

        sql = '''
                SELECT *
                FROM type_vehicule;
                '''
        mycursor.execute(sql)
        type_vehicules = mycursor.fetchall()

        sql = '''
                SELECT *
                FROM marque;
                '''
        mycursor.execute(sql)
        marques = mycursor.fetchall()

        get_db().commit()
    else:
        vehicule=[]
    return render_template('vehicule/vehicule_edit.html', vehicule=vehicule, type_vehicules=type_vehicules, marques=marques)

@app.route('/vehicule/edit', methods=['POST'])
def valid_edit_vehicule():
    id = request.form.get('id')
    num_type = request.form.get('type_vehicule')
    num_marque = request.form.get('marque')
    poid_max = request.form.get('poid_max')
    date_achat = request.form.get('date_achat')

    mycursor = get_db().cursor()
    sql = '''
        UPDATE vehicule
        SET num_type = %s, num_marque = %s, poid_max = %s, date_achat = %s
        WHERE num_vehicule = %s;
    '''
    tuple_insert=(num_type, num_marque, poid_max, date_achat, id)
    mycursor.execute(sql, tuple_insert)
    get_db().commit()

    return redirect('/vehicule/show')

@app.route('/vehicule/delete', methods=['GET'])
def delete_vehicule():
    id = request.args.get('id', '')
    mycursor = get_db().cursor()
    sql = '''   SELECT *
                FROM passage
                INNER JOIN centre ON passage.num_centre = centre.num_centre
                WHERE num_vehicule = %s
                ORDER BY passage.num_vehicule, passage.JMA, passage.ordre;
                     '''
    tuple_insert=(id)
    mycursor.execute(sql, tuple_insert)
    passagesV = mycursor.fetchall()

    sql = '''   SELECT *
                FROM decharge
                INNER JOIN produit ON decharge.num_produit = produit.num_produit
                INNER JOIN usine ON decharge.num_usine = usine.num_usine
                WHERE num_vehicule = %s
                ORDER BY decharge.JMA, usine.nom_usine;
                     '''
    tuple_insert = (id)
    mycursor.execute(sql, tuple_insert)
    dechargesV = mycursor.fetchall()

    if passagesV == () and dechargesV == ():
        sql = '''   DELETE FROM vehicule WHERE num_vehicule=%s;    '''
        turple_insert = (id)
        mycursor.execute(sql, turple_insert)
        get_db().commit()
        return redirect('/vehicule/show')
    else:
        return render_template('vehicule/vehicule_delete.html', id=id, passages=passagesV, decharges=dechargesV)

@app.route('/vehicule/delete/passage')
def valid_delete_passage():
    id = request.args.get('id')
    idV = request.args.get('idV')
    mycursor = get_db().cursor()
    sql = '''   DELETE FROM passage WHERE id_passage=%s;    '''
    mycursor.execute(sql, id)
    get_db().commit()
    return redirect('/vehicule/delete?id='+idV)

@app.route('/vehicule/delete/decharge')
def valid_delete_decharge():
    id = request.args.get('id', '')
    idV = request.args.get('idV')
    mycursor = get_db().cursor()
    sql = '''   DELETE FROM decharge WHERE id_decharge=%s;    '''
    turple_insert = (id)
    mycursor.execute(sql, turple_insert)
    get_db().commit()
    return redirect('/vehicule/delete?id='+idV)

@app.route('/vehicule/etat')
def etat_vehicule():
    mycursor = get_db().cursor()
    sql = '''
            SELECT type_vehicule.num_type AS id, type_vehicule.libelle_type AS libelle
            FROM type_vehicule;
            '''
    mycursor.execute(sql)
    type_vehicules = mycursor.fetchall()

    sql = '''
            SELECT marque.num_marque AS id, marque.libelle_marque AS libelle
            FROM marque;
            '''
    mycursor.execute(sql)
    marques = mycursor.fetchall()

    sql = '''   SELECT *
                FROM vehicule
                INNER JOIN type_vehicule ON vehicule.num_type = type_vehicule.num_type
                INNER JOIN marque ON vehicule.num_marque = marque.num_marque
                ORDER BY type_vehicule.libelle_type ASC;
                     '''
    mycursor.execute(sql)
    vehicules = mycursor.fetchall()

    sql = '''   SELECT COUNT(vehicule.num_vehicule) AS nb_v
                                FROM vehicule
                            '''
    mycursor.execute(sql)
    nbV = mycursor.fetchone()

    return render_template('vehicule/vehicule_etat.html', marques=marques, type_vehicules=type_vehicules, vehicules=vehicules, nbV=nbV)

@app.route('/vehicule/etat', methods=['POST'])
def valid_etat_vehicule():
    mycursor = get_db().cursor()
    sql = '''
                SELECT type_vehicule.num_type AS id, type_vehicule.libelle_type AS libelle
                FROM type_vehicule;
                '''
    mycursor.execute(sql)
    type_vehicules = mycursor.fetchall()

    sql = '''
                SELECT marque.num_marque AS id, marque.libelle_marque AS libelle
                FROM marque;
                '''
    mycursor.execute(sql)
    marques = mycursor.fetchall()

    marque = request.form.get('marque')
    type_vehicule = request.form.get('type_vehicule')
    if marque == "" and type_vehicule == "":
        sql = '''   SELECT *
                        FROM vehicule
                        INNER JOIN type_vehicule ON vehicule.num_type = type_vehicule.num_type
                        INNER JOIN marque ON vehicule.num_marque = marque.num_marque
                        ORDER BY type_vehicule.libelle_type ASC;
                        '''
        mycursor.execute(sql)
        vehicules = mycursor.fetchall()

        sql = '''   SELECT COUNT(vehicule.num_vehicule) AS nb_v
                                        FROM vehicule
                                    '''
        mycursor.execute(sql)
    elif marque == "" and type_vehicule != "":
        sql = '''   SELECT *
                                FROM vehicule
                                INNER JOIN type_vehicule ON vehicule.num_type = type_vehicule.num_type
                                INNER JOIN marque ON vehicule.num_marque = marque.num_marque
                                WHERE vehicule.num_type=%s
                                ORDER BY type_vehicule.libelle_type ASC;
                                '''
        mycursor.execute(sql, type_vehicule)
        vehicules = mycursor.fetchall()

        sql = '''   SELECT COUNT(vehicule.num_vehicule) AS nb_v
                                                FROM vehicule
                                                WHERE vehicule.num_type=%s
                                            '''
        mycursor.execute(sql, type_vehicule)
    elif marque != "" and type_vehicule == "":
        sql = '''   SELECT *
                                FROM vehicule
                                INNER JOIN type_vehicule ON vehicule.num_type = type_vehicule.num_type
                                INNER JOIN marque ON vehicule.num_marque = marque.num_marque
                                WHERE vehicule.num_marque=%s
                                ORDER BY type_vehicule.libelle_type ASC;
                                '''
        mycursor.execute(sql, marque)
        vehicules = mycursor.fetchall()

        sql = '''   SELECT COUNT(vehicule.num_vehicule) AS nb_v
                                                FROM vehicule
                                                WHERE vehicule.num_marque=%s
                                            '''
        mycursor.execute(sql, marque)
    else:
        sql = '''   SELECT *
                                FROM vehicule
                                INNER JOIN type_vehicule ON vehicule.num_type = type_vehicule.num_type
                                INNER JOIN marque ON vehicule.num_marque = marque.num_marque
                                WHERE vehicule.num_marque=%s AND vehicule.num_type=%s
                                ORDER BY type_vehicule.libelle_type ASC;
                                '''
        tuple_insert = (marque, type_vehicule)
        mycursor.execute(sql, tuple_insert)
        vehicules = mycursor.fetchall()

        sql = '''   SELECT COUNT(vehicule.num_vehicule) AS nb_v
                                                FROM vehicule
                                                WHERE vehicule.num_marque=%s AND vehicule.num_type=%s
                                            '''
        tuple_insert = (marque, type_vehicule)
        mycursor.execute(sql, tuple_insert)

    nbV = mycursor.fetchone()
    if nbV['nb_v'] == None:
        nbV['v'] = 0
    return render_template('vehicule/vehicule_etat.html', marques=marques, type_vehicules=type_vehicules, vehicules=vehicules, nbV=nbV)


# ---------------------------------------------------------------------#

@app.route('/passage/show')
def show_passage():
    mycursor = get_db().cursor()
    sql = '''   SELECT *
            FROM passage
            INNER JOIN centre ON passage.num_centre = centre.num_centre
            INNER JOIN vehicule ON passage.num_vehicule = vehicule.num_vehicule
            ORDER BY passage.num_vehicule, passage.JMA, passage.ordre;
                 '''
    mycursor.execute(sql)
    passages = mycursor.fetchall()
    return render_template('passage/passage_show.html', passages=passages)

@app.route('/passage/add', methods=['GET'])
def add_passage():
    mycursor = get_db().cursor()
    sql = '''
        SELECT vehicule.num_vehicule AS id
        FROM vehicule
        ORDER BY id;
        '''
    mycursor.execute(sql)
    vehicules = mycursor.fetchall()

    sql = '''
        SELECT centre.num_centre AS id, centre.nom_centre AS nom, centre.adresse_centre
        FROM centre;
        '''
    mycursor.execute(sql)
    centres = mycursor.fetchall()
    return render_template('passage/passage_add.html', vehicules=vehicules, centres=centres)

@app.route('/passage/add', methods=['POST'])
def valid_add_passage():
    centre = request.form.get('centre')
    vehicule = request.form.get('vehicule')
    ordre = request.form.get('ordre')
    date_passage = request.form.get('date_passage')
    mycursor = get_db().cursor()
    sql='''
    INSERT INTO passage(id_passage, num_centre, num_vehicule, JMA, ordre)
     VALUES (NULL, %s, %s, %s, %s);
    '''
    tuple_insert=(centre, vehicule, date_passage, ordre)
    mycursor.execute(sql, tuple_insert)

    get_db().commit()
    return redirect('/passage/show')

@app.route('/passage/edit', methods=['GET'])
def edit_passage():
    id=request.args.get('id')
    if id != None and id.isnumeric():
        indice = int(id)
        mycursor = get_db().cursor()
        sql = '''
                SELECT *
                FROM passage
                WHERE id_passage=%s;
                '''
        mycursor.execute(sql, indice)
        passage = mycursor.fetchone()

        sql = '''
                SELECT vehicule.num_vehicule AS id
                FROM vehicule
                ORDER BY id;
                '''
        mycursor.execute(sql)
        vehicules = mycursor.fetchall()

        sql = '''
                SELECT centre.num_centre AS id, centre.nom_centre AS nom, centre.adresse_centre
                FROM centre;
                '''
        mycursor.execute(sql)
        centres = mycursor.fetchall()

        get_db().commit()
    else:
        vehicule=[]
    return render_template('passage/passage_edit.html', vehicules=vehicules, passage=passage, centres=centres)

@app.route('/passage/edit', methods=['POST'])
def valid_edit_passage():
    id = request.form.get('id')
    centre = request.form.get('centre')
    vehicule = request.form.get('vehicule')
    ordre = request.form.get('ordre')
    date_passage = request.form.get('date_passage')

    mycursor = get_db().cursor()
    sql = '''
        UPDATE passage
        SET num_vehicule = %s, JMA = %s, ordre = %s, num_centre = %s
        WHERE id_passage = %s;
    '''
    tuple_insert=(vehicule, date_passage, ordre, centre, id)
    mycursor.execute(sql, tuple_insert)
    get_db().commit()

    return redirect('/passage/show')

@app.route('/passage/delete')
def delete_passage():
    id = request.args.get('id', '')
    mycursor = get_db().cursor()
    sql = '''   DELETE FROM passage WHERE id_passage=%s;    '''
    turple_insert = (id)
    mycursor.execute(sql, turple_insert)
    get_db().commit()
    return redirect('/passage/show')

@app.route('/passage/etat')
def etat_passage():
    mycursor = get_db().cursor()

    sql = '''
        SELECT DISTINCT passage.JMA
        FROM passage;
    '''
    mycursor.execute(sql)
    dates = mycursor.fetchall()

    sql = '''
        SELECT vehicule.num_vehicule AS id
        FROM vehicule;
    '''
    mycursor.execute(sql)
    vehicules = mycursor.fetchall()


    sql = '''
        SELECT DISTINCT centre.nom_centre, vehicule.num_vehicule, passage.JMA
        FROM passage
        INNER JOIN centre ON passage.num_centre = centre.num_centre
        INNER JOIN vehicule ON passage.num_vehicule = vehicule.num_vehicule
        ORDER BY passage.JMA;
    '''
    mycursor.execute(sql)
    passages = mycursor.fetchall()


    sql = '''
        SELECT COUNT(DISTINCT passage.num_centre, passage.num_vehicule, passage.JMA) AS nb_c
        FROM passage;
    '''
    mycursor.execute(sql)
    nbC = mycursor.fetchone()

    return render_template('passage/passage_etat.html', dates=dates, vehicules=vehicules, passages=passages, nbC=nbC)

@app.route('/passage/etat', methods=['POST'])
def valid_etat_passage():
    mycursor = get_db().cursor()

    date = request.form.get('date')
    vehicule = request.form.get('vehicule')

    sql = '''
            SELECT DISTINCT passage.JMA
            FROM passage;
        '''
    mycursor.execute(sql)
    dates = mycursor.fetchall()

    sql = '''
            SELECT vehicule.num_vehicule AS id
            FROM vehicule;
        '''
    mycursor.execute(sql)
    vehicules = mycursor.fetchall()

    sql = '''
            SELECT DISTINCT centre.nom_centre, vehicule.num_vehicule, passage.JMA
            FROM passage
            INNER JOIN centre ON passage.num_centre = centre.num_centre
            INNER JOIN vehicule ON passage.num_vehicule = vehicule.num_vehicule
            WHERE passage.JMA = %s AND passage.num_vehicule = %s
        '''
    tuple_insert = (date, vehicule)
    mycursor.execute(sql, tuple_insert)
    passages = mycursor.fetchall()

    sql = '''
            SELECT COUNT(DISTINCT passage.num_centre, passage.num_vehicule, passage.JMA) AS nb_c
            FROM passage
            WHERE passage.JMA = %s AND passage.num_vehicule = %s;
        '''
    tuple_insert = (date, vehicule)
    mycursor.execute(sql, tuple_insert)
    nbC = mycursor.fetchone()

    return render_template('passage/passage_etat.html', dates=dates, vehicules=vehicules, passages=passages, nbC=nbC)

# ---------------------------------------------------------------------#

"""
Route permettant d'afficher la liste des décharges
 via l'appel de la fonction show_decharge
"""
@app.route('/decharge/show')
def show_decharge():
    mycursor = get_db().cursor()
    """
    Requete permettant de recupérer toutes les données de la table décharge ainsi que celle
    des tables ayant les clés étrangères (usine, vehicule, produit).
    Nous avons mis SELECT * car les champs étaient nombreux. L'étoile permet de tout récupérer
    
    Jointure sur la table Usine pour récupérer les informations liés à chaque usine 
    présent dans la table decharge.
    INNER JOIN usine ON decharge.num_usine = usine.num_usine 
    """
    sql = '''   SELECT *
        FROM decharge
        INNER JOIN usine ON decharge.num_usine = usine.num_usine 
        INNER JOIN vehicule ON decharge.num_vehicule = vehicule.num_vehicule
        INNER JOIN  produit ON decharge.num_produit = produit.num_produit
        ORDER BY JMA DESC;
             '''
    mycursor.execute(sql)
    liste_decharge = mycursor.fetchall() # récupération du résultat
    """
    J'ouvre la page decharge_show.html en donnant la variable décharges,
     avec pour valeur la liste des décharges
    """
    return render_template('decharge/decharge_show.html',decharges=liste_decharge)

"""
Route permettant d'afficher le formulaire d'ajout d'une décharge
 via l'appel de la fonction add_decharge
"""
@app.route('/decharge/add', methods=['GET'])
def add_decharge():
    mycursor = get_db().cursor()
    """
    Le formulaire d'ajout a besoin de la liste des usines, des produits et des véhicules
    """
    sql = '''   SELECT usine.nom_usine AS nom, usine.adresse_usine AS adresse, usine.num_usine AS id
                    FROM usine
                    ORDER BY nom_usine;
                         '''
    mycursor.execute(sql)
    usines = mycursor.fetchall() # récupération de la liste des usines

    sql = '''   SELECT produit.libelle_produit AS libelle, produit.num_produit AS id
                        FROM produit
                        ORDER BY libelle_produit;
                             '''
    mycursor.execute(sql)
    produits = mycursor.fetchall() # récupération de la liste des produits

    sql = '''   SELECT vehicule.num_vehicule AS id, vehicule.poid_max AS poids, vehicule.date_achat
                            FROM vehicule
                            ORDER BY poid_max;
                                 '''
    mycursor.execute(sql)
    vehicules = mycursor.fetchall() # récupération de la liste des véhicules

    """
        J'ouvre la page decharge_add.html en donnant les variables
         liste des usines, produits, vehicules
    """
    return render_template(
        'decharge/decharge_add.html',
        usines=usines,
        produits=produits,
        vehicules=vehicules
    )

"""
Route permettant de valider le formulaire d'ajout d'une décharge
 via l'appel de la fonction valid_add_decharge
"""
@app.route('/decharge/add', methods=['POST'])
def valid_add_decharge():
    # Récupération des données envoyés via le formulaire
    num_usine= request.form['num_usine']
    num_produit=request.form['num_produit']
    num_vehicule=request.form['num_vehicule']
    quantite=request.form['quantite']
    JMA = datetime.today() # On affecte la date du jour

    mycursor = get_db().cursor()
    sql = '''  INSERT INTO decharge(num_produit, num_usine, num_vehicule, quantite, JMA)
            VALUES (%s,%s,%s,%s,%s)
                 '''
    turple_insert = (num_produit,num_usine,num_vehicule,quantite,JMA)
    mycursor.execute(sql, turple_insert) # Exécution de la commande
    get_db().commit() # mise à jour de la bd

    # Rédirige vers la liste des décharges
    return redirect('/decharge/show')

"""
Route permettant d'afficher le formulaire de modification d'une décharge
 via l'appel de la fonction edit_decharge
"""
@app.route('/decharge/edit', methods=['GET'])
def edit_decharge():
    #recupération de l'argument id de la décharge à éditer
    id_decharge = request.args.get('id')
    if id != None :
        mycursor = get_db().cursor()
        # Requte pour récupérer la décharge à modifier
        sql = '''   SELECT decharge.id_decharge AS id, decharge.num_vehicule AS vehicule, num_usine AS usine, num_produit AS produit, quantite
            FROM decharge
            WHERE id_decharge = %s;
                 '''
        turple_edit = (id_decharge)
        mycursor.execute(sql, turple_edit)
        decharge = mycursor.fetchone() # affectation du résultat
    else:
        decharge = None
    """
        Le formulaire a besoin de la liste des usines, des produits et des véhicules
        """
    sql = '''   SELECT usine.nom_usine AS nom, usine.adresse_usine AS adresse, usine.num_usine AS id
                        FROM usine
                        ORDER BY nom_usine;
                             '''
    mycursor.execute(sql)
    usines = mycursor.fetchall()  # récupération de la liste des usines

    sql = '''   SELECT produit.libelle_produit AS libelle, produit.num_produit AS id
                            FROM produit
                            ORDER BY libelle_produit;
                                 '''
    mycursor.execute(sql)
    produits = mycursor.fetchall()  # récupération de la liste des produits

    sql = '''   SELECT vehicule.num_vehicule AS id, vehicule.poid_max AS poids, vehicule.date_achat
                                FROM vehicule
                                ORDER BY poid_max;
                                     '''
    mycursor.execute(sql)
    vehicules = mycursor.fetchall()  # récupération de la liste des véhicules

    """
        J'ouvre la page decharge_edit.html en donnant les variables
        liste des usines, produits, vehicules et les informations (variable previous_data) 
        de la decharge à modifier
    """
    return render_template(
        'decharge/decharge_edit.html',
        usines=usines,
        produits=produits,
        vehicules=vehicules,
        previous_data=decharge,
    )

"""
Route permettant de valider le formulaire d'édition' d'une décharge
 via l'appel de la fonction valid_edit_decharge
"""
@app.route('/decharge/edit', methods=['POST'])
def valid_edit_decharge():
    num_usine=request.form['num_usine']
    num_produit=request.form['num_produit']
    num_vehicule=request.form['num_vehicule']
    quantite=request.form['quantite']
    JMA = datetime.today()
    id=request.form['id']

    mycursor = get_db().cursor()
    sql = '''  UPDATE decharge
                SET num_produit=%s, num_usine=%s, num_vehicule=%s, quantite=%s, JMA=%s
                WHERE id_decharge = %s'''
    turple_update = (num_produit,num_usine,num_vehicule,quantite,JMA,id)
    mycursor.execute(sql, turple_update)
    get_db().commit()
    return redirect('/decharge/show')

@app.route('/decharge/delete')
def delete_decharge():
    id = request.args.get('id', '')
    mycursor = get_db().cursor()
    sql = '''   DELETE FROM decharge WHERE id_decharge=%s;    '''
    turple_delete = (id)
    mycursor.execute(sql, turple_delete)
    get_db().commit()
    return redirect('/decharge/show')

"""
La route permet d'ouvrir la page des états avec toutes les données
"""
@app.route('/decharge/etat')
def etat_decharge():
    mycursor = get_db().cursor()
    """
    La page a besoin de la liste des usines, des produits et des véhicules
    """
    sql = '''   SELECT usine.nom_usine AS nom, usine.adresse_usine AS adresse, usine.num_usine AS id
                        FROM usine
                        ORDER BY nom_usine;
                             '''
    mycursor.execute(sql)
    usines = mycursor.fetchall()  # récupération de la liste des usines

    sql = '''   SELECT produit.libelle_produit AS libelle, produit.num_produit AS id
                            FROM produit
                            ORDER BY libelle_produit;
                                 '''
    mycursor.execute(sql)
    produits = mycursor.fetchall()  # récupération de la liste des produits

    sql = '''   SELECT vehicule.num_vehicule AS id, vehicule.poid_max AS poids, vehicule.date_achat
                                FROM vehicule
                                ORDER BY poid_max;
                                     '''
    mycursor.execute(sql)
    vehicules = mycursor.fetchall()  # récupération de la liste des véhicules

    # Requête SQL pour calculer la somme des quantités
    sql = '''
            SELECT SUM(quantite) AS somme, AVG(quantite) AS moyenne
            FROM decharge;
        '''
    mycursor.execute(sql)
    result = mycursor.fetchone()
    if result != None:
        somme=result['somme']
        moyenne=result['moyenne']
    else:
        somme=0
        moyenne=0

    # Requête SQL pour avoir toutes les données
    sql = '''   SELECT *
            FROM decharge
            INNER JOIN usine ON decharge.num_usine = usine.num_usine 
            INNER JOIN vehicule ON decharge.num_vehicule = vehicule.num_vehicule
            INNER JOIN  produit ON decharge.num_produit = produit.num_produit
            ORDER BY JMA DESC;
                 '''
    mycursor.execute(sql)
    liste_decharge = mycursor.fetchall()  # récupération du résultat

    return render_template('decharge/decharge_etat.html',
            usines=usines,
            produits=produits,
            vehicules=vehicules,
            decharges=liste_decharge,
            somme=somme,
            moyenne=moyenne,
            pourcentage_somme=100,
            pourcentage_moyenne=100)

"""
La route permet d'ouvrir la page des états avec les données filtrées
"""
@app.route('/decharge/etat', methods=['POST'])
def etat_filtre_decharge():
    # Récupération des données envoyés via le formulaire
    mycursor = get_db().cursor()

    # Base de la requête sans aucun filtre
    sql = '''
           SELECT SUM(quantite) AS somme, AVG(quantite) AS moyenne
           FROM decharge
       '''

    # On doit calculer les valeurs total globales

    mycursor.execute(sql)
    result = mycursor.fetchone()
    somme_totale = 0
    if result != None:
        somme_totale = result['somme']

    # On va construire le filtre
    conditions = []
    params = []
    num_usine = request.form['num_usine']
    num_produit = request.form['num_produit']
    num_vehicule = request.form['num_vehicule']

    if num_usine != '0':
        conditions.append("decharge.num_usine = %s")
        params.append(num_usine)

    if num_produit != '0':
        conditions.append("decharge.num_produit = %s")
        params.append(num_produit)

    if num_vehicule != '0':
        conditions.append("decharge.num_vehicule = %s")
        params.append(num_vehicule)

    # On ajoute donc les conditions au sql
    if conditions:
        sql += " WHERE " + " AND ".join(conditions)

    print(sql)
    mycursor.execute(sql, params)
    result = mycursor.fetchone()
    moyenne = 0
    somme = 0
    if result['somme'] != None and result['moyenne'] != None:
        somme=result['somme']
        moyenne = result['moyenne']

    pourcentage_somme = 0
    pourcentage_moyenne = 0
    if somme_totale > 0:
        pourcentage_somme = (somme / somme_totale) * 100
        pourcentage_moyenne = (moyenne / somme_totale) * 100


    # Requête SQL pour avoir la liste des résultats
    sql = '''   SELECT *
            FROM decharge
            INNER JOIN usine ON decharge.num_usine = usine.num_usine 
            INNER JOIN vehicule ON decharge.num_vehicule = vehicule.num_vehicule
            INNER JOIN  produit ON decharge.num_produit = produit.num_produit
                 '''
    # On ajoute donc les conditions au sql
    if conditions:
        sql += " WHERE " + " AND ".join(conditions)
    mycursor.execute(sql, params)
    liste_decharge = mycursor.fetchall()  # récupération du résultat

    """
    La page a besoin de la liste des usines, des produits et des véhicules
    """
    sql = '''   SELECT usine.nom_usine AS nom, usine.adresse_usine AS adresse, usine.num_usine AS id
                        FROM usine
                        ORDER BY nom_usine;
                             '''
    mycursor.execute(sql)
    usines = mycursor.fetchall()  # récupération de la liste des usines

    sql = '''   SELECT produit.libelle_produit AS libelle, produit.num_produit AS id
                            FROM produit
                            ORDER BY libelle_produit;
                                 '''
    mycursor.execute(sql)
    produits = mycursor.fetchall()  # récupération de la liste des produits

    sql = '''   SELECT vehicule.num_vehicule AS id, vehicule.poid_max AS poids, vehicule.date_achat
                                FROM vehicule
                                ORDER BY poid_max;
                                     '''
    mycursor.execute(sql)
    vehicules = mycursor.fetchall()  # récupération de la liste des véhicules



    return render_template('decharge/decharge_etat.html',
            usines=usines,
            produits=produits,
            vehicules=vehicules,
            decharges=liste_decharge,
            somme="{:.2f}".format(somme),
            moyenne="{:.2f}".format(moyenne),
            pourcentage_somme="{:.2f}".format(pourcentage_somme),
            pourcentage_moyenne="{:.2f}".format(pourcentage_moyenne))

# ---------------------------------------------------------------------#

if __name__ == '__main__':
    app.run()
