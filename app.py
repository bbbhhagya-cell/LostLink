from flask import Flask, render_template, request, redirect
import psycopg2

app = Flask(__name__)

conn = psycopg2.connect(
    dbname="lostlink",
    user="bhagya-s",
    host="/tmp"
)

@app.route("/")
def home():
    return render_template("index.html")

# Report Lost Item
@app.route("/lost", methods=["GET", "POST"])
def lost():
    if request.method == "POST":

        item_name = request.form["item_name"]
        category = request.form["category"]
        location = request.form["location"]

        cur = conn.cursor()

        cur.execute("""
        INSERT INTO lost_items
        (item_name, category, location_lost, date_lost, reported_by)
        VALUES (%s,%s,%s,CURRENT_DATE,1)
        """,
        (item_name, category, location))

        conn.commit()
        cur.close()

        return redirect("/")

    return render_template("lost.html")


# Report Found Item
@app.route("/found", methods=["GET", "POST"])
def found():

    if request.method == "POST":

        item_name = request.form["item_name"]
        category = request.form["category"]
        location = request.form["location"]

        cur = conn.cursor()

        cur.execute("""
        INSERT INTO found_items
        (item_name, category, location_found, date_found, reported_by)
        VALUES (%s,%s,%s,CURRENT_DATE,1)
        """,
        (item_name, category, location))

        conn.commit()
        cur.close()

        return redirect("/")

    return render_template("found.html")


# View Lost Items
@app.route("/view_lost")
def view_lost():

    cur = conn.cursor()

    cur.execute("""
    SELECT item_id,item_name,category,location_lost
    FROM lost_items
    ORDER BY item_id DESC
    """)

    items = cur.fetchall()
    cur.close()

    return render_template("view_lost.html", items=items)


# View Found Items
@app.route("/view_found")
def view_found():

    cur = conn.cursor()

    cur.execute("""
    SELECT found_id,item_name,category,location_found
    FROM found_items
    ORDER BY found_id DESC
    """)

    items = cur.fetchall()
    cur.close()

    return render_template("view_found.html", items=items)


# Match Results
@app.route("/matches")
def matches():

    cur = conn.cursor()

    cur.execute("""
    SELECT *
    FROM (
        SELECT
            l.item_id AS lost_id,
            f.found_id AS found_id,
            l.item_name AS lost_item,
            f.item_name AS found_item,
            (
                CASE WHEN LOWER(l.item_name)=LOWER(f.item_name) THEN 40 ELSE 0 END +
                CASE WHEN l.category=f.category THEN 20 ELSE 0 END +
                CASE WHEN l.location_lost=f.location_found THEN 20 ELSE 0 END +
                CASE WHEN ABS(f.date_found-l.date_lost)<=3 THEN 20 ELSE 0 END
            ) AS match_score
        FROM lost_items l
        JOIN found_items f ON TRUE
    ) result
    WHERE match_score >= 50
    ORDER BY match_score DESC
    """)

    matches = cur.fetchall()
    cur.close()

    return render_template("matches.html", matches=matches)


if __name__ == "__main__":
    app.run(debug=True)
