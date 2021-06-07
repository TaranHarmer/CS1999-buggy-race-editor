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
    buggy_id='1'
    def buggy_form():
        if buggy_id:
            con = sql.connect(DATABASE_FILE)
            con.row_factory = sql.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM buggies WHERE id=?", (buggy_id,))
            record = cur.fetchone();
            return render_template("buggy-form.html", buggy=record, msg=msg)
        else:
            record = {'id':None,'qty_wheels':4,'qty_tyres':4,'type_tyres':'knobbly','flag_color':'white','flag_color_secondary':'white','flag_pattern':'plain',
                'power_type':'petrol','power_units':1,'aux_power_type':'none','aux_power_units':0,'hamster_booster':0,'armour':'none','attack':'none',
                'qty_attacks':0,'fireproof':'false','insulated':'false','antibiotic':'false','banging':'false','algo':'steady'}
            #return f"{record['qty_wheels']}"
            return render_template("buggy-form.html",buggy=record, msg=msg)

    def calc_cost():
        cost = 0
        options = [power_type,aux_power_type,attack]
        cost_catalog = {'knobbly': 15,'slick': 10,'steelband': 20,'reactive': 40,'maglev': 50,'petrol': 4,'fusion': 400,'steam': 3,'bio': 5,
            'electric': 20,'rocket': 16,'hamster': 3,'thermo': 300,'solar': 40,'wind': 20,'none': 0,'wood': 40,'aluminium': 200,'thinsteel': 100,
            'thicksteel': 200,'titanium': 290,'spike': 5,'flame': 20,'charge': 28,'biohazard': 30}
        for option in options:
            cost += cost_catalog[option]
        if qty_wheels > 4:
            multiplier = (100+((qty_wheels-4)*10))/100
            cost += cost_catalog[armour]*multiplier
        else:
            cost += cost_catalog[armour]
        cost += cost_catalog[type_tyres] * qty_tyres
        if fireproof == 'true':
            cost += 70
        if insulated == 'true':
            cost += 100
        if antibiotic == 'true':
            cost += 90
        if banging == 'true':
            cost += 42
        return cost

    if request.method == 'GET':
        buggy_form()
    elif request.method == 'POST':
        non_consumable = ['fusion','thermo','solar','wind']
        buggy_id = request.form['buggy_id']
        qty_wheels = int(request.form['qty_wheels'])
        qty_tyres = int(request.form['qty_tyres'])
        type_tyres = request.form['type_tyres']
        flag_color = request.form['flag_color']
        flag_color_secondary = request.form['flag_color_secondary']
        flag_pattern = request.form['flag_pattern']
        power_type = request.form['power_type']
        power_units = int(request.form['power_units'])
        aux_power_type = request.form['aux_power_type']
        aux_power_units = int(request.form['aux_power_units'])
        hamster_booster = int(request.form['hamster_booster'])
        armour = request.form['armour']
        attack = request.form['attack']
        qty_attacks = int(request.form['qty_attacks'])
        fireproof = request.form['fireproof']
        insulated = request.form['insulated']
        antibiotic = request.form['antibiotic']
        banging = request.form['banging']
        algo = request.form['algo']
        total_cost = calc_cost()
        #2-Valid
        if qty_wheels >= 4:
            if qty_wheels % 2 == 0:
                if flag_pattern == 'plain' or flag_color != flag_color_secondary:
                    if qty_tyres >= qty_wheels:
                        if power_units >=1:
                            if aux_power_units >=0:
                                if qty_attacks >=0:
                                    if hamster_booster >=0:
                                        if hamster_booster >= 0 and power_type == 'hamster' or hamster_booster >= 0 and aux_power_type == 'hamster' or hamster_booster == 0 and power_type != 'hamster' or hamster_booster == 0 and aux_power_type != 'hamster':
                                            if power_type in non_consumable and aux_power_type in non_consumable:
                                                msg = "You can only have one unit of non-consumable power per motive force!"
                                                return buggy_form()
                                        else:
                                            msg = "Hamster booster is only effective with hamster power type!"
                                            return buggy_form()
                                    else:
                                        msg = "Hamster booster can't be negative!"
                                        return buggy_form()
                                else:
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
                if buggy_id:
                    cur.execute(
                        "UPDATE buggies set qty_wheels=?, qty_tyres=?, type_tyres=?, power_type=?, power_units=?, aux_power_type=?, aux_power_units=?, hamster_booster=?, armour=?, attack=?, qty_attacks=?, fireproof=?, insulated=?, antibiotic=?, banging=?, algo=?, flag_color=?, flag_color_secondary=?, flag_pattern=?, total_cost=? WHERE id=?",
                        (qty_wheels, qty_tyres, type_tyres, power_type, power_units, aux_power_type, aux_power_units, hamster_booster, armour, attack, qty_attacks, fireproof, insulated, antibiotic, banging, algo, flag_color, flag_color_secondary, flag_pattern, total_cost, buggy_id)
                    )
                else:
                    cur.execute(
                        "INSERT INTO buggies(qty_wheels, qty_tyres, type_tyres, power_type, power_units, aux_power_type, aux_power_units, hamster_booster, armour, attack, qty_attacks, fireproof, insulated, antibiotic, banging, algo, flag_color, flag_color_secondary, flag_pattern, total_cost) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                        (qty_wheels, qty_tyres, type_tyres, power_type, power_units, aux_power_type, aux_power_units, hamster_booster, armour, attack, qty_attacks, fireproof, insulated, antibiotic, banging, algo, flag_color, flag_color_secondary, flag_pattern, total_cost)
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
    records = cur.fetchall(); 
    return render_template("buggy.html", buggies = records)

#------------------------------------------------------------
# a placeholder page for editing the buggy: you'll need
# to change this when you tackle task 2-EDIT
#------------------------------------------------------------
@app.route('/edit/<buggy_id>')
def edit_buggy(buggy_id):
    print(f"FIXME I want to edit buggy #{buggy_id}")
    con = sql.connect(DATABASE_FILE)
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM buggies WHERE id=?", (buggy_id,))
    record = cur.fetchone();
    return render_template("buggy-form.html", buggy=record)

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
