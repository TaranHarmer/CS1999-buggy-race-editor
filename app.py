from flask import Flask, render_template, request, jsonify
import sqlite3 as sql

# app - The flask application where all the magical things are configured.
app = Flask(__name__)

# Constants - Stuff that we need to know that won't ever change!
DATABASE_FILE = "database.db"
DEFAULT_BUGGY_ID = "1"
BUGGY_RACE_SERVER_URL = "https://rhul.buggyrace.net"

#------------------------------------------------------------
# the index page
#------------------------------------------------------------
@app.route('/')
def home():
    return render_template('index.html', server_url=BUGGY_RACE_SERVER_URL)

#------------------------------------------------------------
# creating a new buggy:
#  if it's a POST request process the submitted data
#  but if it's a GET request, just show the form
#------------------------------------------------------------
@app.route('/new', methods = ['POST', 'GET'])
def create_buggy():
    msg=""
    def buggy_form():
        con = sql.connect(DATABASE_FILE)
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM buggies")
        record = cur.fetchone(); 
        return render_template("buggy-form.html", buggy = record, msg = msg)
    def calc_cost():
        pass
    if request.method == 'GET':
        return buggy_form()
    elif request.method == 'POST':
        qty_wheels = request.form['qty_wheels']
        qty_tyres = request.form['qty_tyres']
        type_tyres = request.form['type_tyres']
        flag_color = request.form['flag_color']
        flag_color_secondary = request.form['flag_color_secondary']
        flag_pattern = request.form['flag_pattern']
        power_type = request.form['power_type']
        power_units = request.form['power_units']
        aux_power_type = request.form['aux_power_type']
        aux_power_units = request.form['aux_power_units']
        hamster_booster = request.form['hamster_booster']
        armour = request.form['armour']
        attack = request.form['attack']
        qty_attacks = request.form['qty_attacks']
        fireproof = request.form['fireproof']
        insulated = request.form['insulated']
        antibiotic = request.form['antibiotic']
        banging = request.form['banging']
        algo = request.form['algo']
        #2-Valid
        if int(qty_wheels) >= 4:
            if int(qty_wheels) % 2 == 0:
                if flag_pattern == 'plain' or flag_color != flag_color_secondary:
                    if qty_tyres >= qty_wheels:
                        if int(power_units) >=1:
                            if int(aux_power_units) >=0:
                                if int(qty_attacks) <=0:
                                    msg = "Number of attacks can't be less than 0!"
                                    return buggy_form()
                            else:
                                msg = "Auxillary power units can't be less than 0!"
                                return buggy_form()
                        else:
                            msg = "Primary power units must be greater than 1!"
                            return buggy_form()
                    else:
                        msg = "Number of tyres must be greater than or equal to number of wheels!"
                        return buggy_form() 
                else:
                    msg = "Flag color and secondary flag color must be different!"
                    return buggy_form()
            else:
                msg = "You must have an even number of wheels!"
                return buggy_form()
        else:
            msg = "You must have more than 4 wheels!"
            return buggy_form()
        
        try:
            with sql.connect(DATABASE_FILE) as con:
                cur = con.cursor()
                cur.execute(
                    "UPDATE buggies set qty_wheels=?, qty_tyres=?, type_tyres=?, power_type=?, power_units=?, aux_power_type=?, aux_power_units=?, hamster_booster=?, armour=?, attack=?, qty_attacks=?, fireproof=?, insulated=?, antibiotic=?, banging=?, algo=?, flag_color=?, flag_color_secondary=?, flag_pattern=? WHERE id=?",
                    (qty_wheels, qty_tyres, type_tyres, power_type, power_units, aux_power_type, aux_power_units, hamster_booster, armour, attack, qty_attacks, fireproof, insulated, antibiotic, banging, algo, flag_color, flag_color_secondary, flag_pattern, DEFAULT_BUGGY_ID)
                )
                con.commit()
                msg = "Record successfully saved"
        except:
            con.rollback()
            msg = "error in update operation"
        finally:
            con.close()
        return render_template("updated.html", msg = msg)

#------------------------------------------------------------
# a page for displaying the buggy
#------------------------------------------------------------
@app.route('/buggy')
def show_buggies():
    con = sql.connect(DATABASE_FILE)
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM buggies")
    record = cur.fetchone(); 
    return render_template("buggy.html", buggy = record)

#------------------------------------------------------------
# a placeholder page for editing the buggy: you'll need
# to change this when you tackle task 2-EDIT
#------------------------------------------------------------
@app.route('/edit')
def edit_buggy():
    return render_template("buggy-form.html")

#------------------------------------------------------------
# You probably don't need to edit this... unless you want to ;)
#
# get JSON from current record
#  This reads the buggy record from the database, turns it
#  into JSON format (excluding any empty values), and returns
#  it. There's no .html template here because it's *only* returning
#  the data, so in effect jsonify() is rendering the data.
#------------------------------------------------------------
@app.route('/json')
def summary():
    con = sql.connect(DATABASE_FILE)
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM buggies WHERE id=? LIMIT 1", (DEFAULT_BUGGY_ID))

    buggies = dict(zip([column[0] for column in cur.description], cur.fetchone())).items() 
    return jsonify({ key: val for key, val in buggies if (val != "" and val is not None) })

# You shouldn't need to add anything below this!
if __name__ == '__main__':
    app.run(debug = True, host="0.0.0.0")
