from flask import Flask, render_template, request, json, g, session
import re
import sqlite3

app = Flask(__name__)
app.secret_key = "super secret key"
def get_db():
    """
    Establish connection to database and store results in sqlite3.Row
    since these are iterable and an easier data structure to use
    """
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect("nutrition.db")
    db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    #Close connection
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

@app.route("/")
def homepage():
    #Load homepage
    return render_template('homepage.html')

def loginQuery(query, args=(), one=False):
    #Execute query for login and make sure credentials match in DB
    cur = get_db().cursor().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    #Return none if no result found; otherwise, return results (sqlite3 Rows)
    return (rv[0] if rv else None) if one else rv

@app.route('/loginCheck', methods=['POST'])
def loginUser():
    #Extract form information for employee ID and password
    employeeId = request.form['empId']
    empPassword = request.form['password']

    #Use Regex to check if employee ID is 5 digits and not empty
    if re.match("^[0-9]{5}$", employeeId) is None:
        return json.dumps({'status':"BAD", 'user':"Employee ID must contain 5 digits."})

    #Check if employee ID exists in database
    res = loginQuery("SELECT employeeId FROM user WHERE employeeId = ?",
                      [employeeId])
    if res is None or len(res)==0:
        return json.dumps({"status": "BAD", "user": "Incorrect employee ID."})

    #Check if password matches employee ID. If all above conditions are met, login user
    res2 = loginQuery("SELECT employeeId, empPassword FROM user WHERE employeeId = ? AND empPassword = ?",
                      [employeeId, empPassword])
    if res2 is None or len(res2)==0:
        return json.dumps({"status": "BAD", "user": "Incorrect password."})
    else:
        session["empId"] = employeeId
        return json.dumps({"status": "OK", "user": "Logging in."})

def transQuery(query, args=(), one=False):
    #Execute query to extract all transaction history for current user
    cur = get_db().cursor().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    #Return none if no result
    return (rv[0] if rv else None) if one else rv

@app.route("/main-page")
def mainPage():
   res = transQuery("SELECT sum(calories) as calories, sum(protein) as protein, sum(carb) as carb, sum(fat) as fat, dateTrans FROM items JOIN transactions on items.itemId=transactions.itemId WHERE employeeID=? GROUP BY dateTrans;",
               [session["empId"]])
   fields = ["calories", "protein", "carb", "fat"]
   i = 0
   for res in res:
        if i==0:
            statsDict = {field: res[field] for field in fields}
        i+=1
   return render_template("main-page.html", stats = statsDict)



@app.route("/vizAgg")
def vizAgg():
    #Get all raw transaction history for current user
    res = transQuery("SELECT * FROM transactions JOIN items ON transactions.itemId=items.itemId WHERE employeeId = ?;",
                [session["empId"]])
    purchaseHist = []
    fields = ["dateTrans", "itemName", "calories", "protein",
              "fat", "carb", "fiber", "sugar", "calcium",
              "iron", "phosphorous", "sodium", "vitaminA",
              "vitaminC", "cholesterol", "isMeal"]
    for row in res:
        purchaseHist.append({field: row[field] for field in fields})

    fields.remove("itemName")

    #Get transaction history for current user grouped by date (daily aggregates)
    resAgg = transQuery("SELECT dateTrans, isMeal, sum(calories) AS calories, sum(protein) AS protein, sum(fat) AS fat, sum(carb) AS carb, sum(fiber) AS fiber, sum(sugar) AS sugar, sum(calcium) AS calcium, sum(iron) AS iron, sum(phosphorous) AS phosphorous, sum(sodium) AS sodium, sum(vitaminA) AS vitaminA, sum(vitaminC) AS vitaminC, sum(cholesterol) AS cholesterol, sum(isMeal) AS isMeal FROM transactions JOIN items ON transactions.itemId=items.itemId WHERE employeeId = ? GROUP BY dateTrans, isMeal;",
                [session["empId"]])
    snackList = []
    mealList = []
    for row in resAgg:
        if row["isMeal"]==1:
            mealList.append({field: row[field] for field in fields})
        else:
            snackList.append({field: row[field] for field in fields})
    resAgg = transQuery("SELECT dateTrans, sum(calories) AS calories, sum(protein) AS protein, sum(fat) AS fat, sum(carb) AS carb, sum(fiber) AS fiber, sum(sugar) AS sugar, sum(calcium) AS calcium, sum(iron) AS iron, sum(phosphorous) AS phosphorous, sum(sodium) AS sodium, sum(vitaminA) AS vitaminA, sum(vitaminC) AS vitaminC, sum(cholesterol) AS cholesterol, sum(isMeal) AS isMeal FROM transactions JOIN items ON transactions.itemId=items.itemId WHERE employeeId = ? GROUP BY dateTrans",
                [session["empId"]])
    aggList = []
    for row in resAgg:
        aggList.append({field: row[field] for field in fields})
    return render_template("vizAgg.html", hist = purchaseHist, histAgg = [mealList, snackList], histAggDaily = aggList)

@app.route("/transactions")
def transactionHistory():
    fields = ["dateTrans", "itemName", "calories", "protein",
              "fat", "carb", "fiber", "sugar", "calcium",
              "iron", "phosphorous", "sodium", "vitaminA",
              "vitaminC", "cholesterol"]
    res = transQuery(
        "SELECT dateTrans, itemName, calories, protein, fat, carb, fiber, sugar, calcium, iron, phosphorous, sodium, vitaminA, vitaminC, cholesterol FROM transactions JOIN items ON transactions.itemId=items.itemId WHERE employeeId = ?",
        [session["empId"]])
    transactionList = []
    for row in res:
        transactionList.append({field: row[field] for field in fields})
    foodData = []
    foodDataRow = []
    for row in transactionList:
        for field in fields:
            foodDataRow.append(row[field])
            if field == "cholesterol":
                foodData.append(foodDataRow)
                foodDataRow = []
    formattedFields = ["Date of Transaction", "Item Name", "Calories", "Protein",
              "Fat", "Carbohydrates", "Fiber", "Sugar", "Calcium",
              "Iron", "Phosphorous", "Sodium", "Vitamin A",
              "Vitamin C", "Cholesterol"]
    return render_template("displayData.html", header = formattedFields, data = foodData)

if __name__ == "__main__":
    app.run()
