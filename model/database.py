import sqlite3

def createTablesIfNotExists(db):
    cursor = db.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS graphs(id INTEGER PRIMARY KEY, mass INTEGER,
                       color TEXT, position INTEGER, UNIQUE (mass))
        ''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS calculated(id INTEGER PRIMARY KEY, experiment_id INTEGER,
                       step INTEGER, value INTEGER, max_value INTEGER, graph_id INTEGER)
        ''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS mipsdata(id INTEGER PRIMARY KEY, experiment_id INTEGER,
                       step INTEGER, value INTEGER, channel INTEGER)
        ''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS experiments(id INTEGER PRIMARY KEY, folder TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS speedTest(id INTEGER PRIMARY KEY, operation TEXT, date timestamp)''')
    db.commit()
    
def insertMipsData(db, step, value, channel):
    try:
        with db:
            db.execute('''INSERT INTO mipsdata(experiment_id, step, value, channel)
                      VALUES(?,?,?,?)''', (0, step, value, channel))
    except sqlite3.IntegrityError:
        print('Record already exists')

def getMipsData(db, maxStep):
    cursor = db.cursor()
    cursor.execute('''SELECT step, value, channel FROM mipsdata WHERE step < ?''', (maxStep,))

    all_rows = cursor.fetchall()
    return all_rows

def getGraphs(db):
    cursor = db.cursor()
    cursor.execute('''SELECT id, mass, color, position FROM graphs''')

    all_rows = cursor.fetchall()
    return all_rows

def insertCalculatedData(cursor, step, peakInt, peakMax, index):
    try:
        cursor.execute('''INSERT INTO calculated(experiment_id, step, value, max_value, graph_id)
                      VALUES(?,?,?,?,?)''', (0, step, peakInt.item(), peakMax.item(), index))
    except sqlite3.IntegrityError:
        print('Record already exists')

def insertGraph(db, mass, color, position):
    try:
        with db:
            db.execute('''INSERT INTO graphs(mass, color, position)
                      VALUES(?,?,?)''', (mass, color, position))
    except sqlite3.IntegrityError:
        print('Record already exists')

def updateGraph(db, mass, color, position, index):
    cursor = db.cursor()
    cursor.execute('''SELECT id, mass, color, position FROM graphs WHERE id=?''', (index,))

    gr = cursor.fetchone()
    if gr[1] == mass:
        cursor.execute('''UPDATE graphs SET color = ?, position = ? WHERE id=?''', (color, position, index,))
        db.commit()
    else:
        cursor.execute('''UPDATE graphs SET mass = ?, color = ?, position = ? WHERE id=?''', (mass, color, position, index,))
        cursor.execute('''DELETE FROM calculated WHERE graph_id=?''', (index,))
        db.commit()

def deleteGraph(db, index):
    cursor = db.cursor()
    cursor.execute('''DELETE FROM graphs WHERE id=?''', (index,))
    cursor.execute('''DELETE FROM calculated WHERE graph_id=?''', (index,))
    db.commit()

def getUncalculatedDataIndex(db, gr_index):
    cursor = db.cursor()
    cursor.execute('''SELECT MAX(step) FROM calculated WHERE graph_id=?''', (gr_index,))
    maxVal = cursor.fetchone()
    if maxVal[0] is None:
        return 0
    return maxVal[0] + 1

def getCalculatedDataIndex(db, gr_index):
    cursor = db.cursor()
    cursor.execute('''SELECT step, value FROM calculated WHERE graph_id=? ORDER BY step ASC''', (gr_index,))
    all_rows = cursor.fetchall()
    arr = []
    for row in all_rows:
        arr.append(row[1])
    return arr


def remove(db):
    cursor = db.cursor()
    cursor.execute('''DELETE FROM graphs''')
    cursor.execute('''DELETE FROM calculated''')
    cursor.execute('''DELETE FROM mipsdata''')
    cursor.execute('''DELETE FROM experiments''')
    db.commit()