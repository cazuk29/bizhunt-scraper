from flask import Flask, render_template, request, send_file
from scraper import scrape_google_maps, scrape_yelp
import pandas as pd
import json
import uuid
import os

app = Flask(__name__)
HISTORY_FILE = "history.json"

UK_COUNTIES = [
    "Bedfordshire", "Berkshire", "Bristol", "Buckinghamshire", "Cambridgeshire", "Cheshire", "City of London",
    "Cornwall", "Cumbria", "Derbyshire", "Devon", "Dorset", "Durham", "East Riding of Yorkshire",
    "East Sussex", "Essex", "Gloucestershire", "Greater London", "Greater Manchester", "Hampshire",
    "Herefordshire", "Hertfordshire", "Isle of Wight", "Kent", "Lancashire", "Leicestershire", "Lincolnshire",
    "Merseyside", "Middlesbrough", "Norfolk", "North Yorkshire", "Northamptonshire", "Northumberland",
    "Nottinghamshire", "Oxfordshire", "Rutland", "Shropshire", "Somerset", "South Yorkshire", "Staffordshire",
    "Suffolk", "Surrey", "Tyne and Wear", "Warwickshire", "West Midlands", "West Sussex", "West Yorkshire",
    "Wiltshire", "Worcestershire", "Anglesey", "Blaenau Gwent", "Bridgend", "Caerphilly", "Cardiff",
    "Carmarthenshire", "Ceredigion", "Conwy", "Denbighshire", "Flintshire", "Gwynedd", "Merthyr Tydfil",
    "Monmouthshire", "Neath Port Talbot", "Newport", "Pembrokeshire", "Powys", "Rhondda Cynon Taf",
    "Swansea", "Torfaen", "Vale of Glamorgan", "Wrexham", "Aberdeen City", "Aberdeenshire", "Angus",
    "Argyll and Bute", "Clackmannanshire", "Dumfries and Galloway", "Dundee City", "East Ayrshire",
    "East Dunbartonshire", "East Lothian", "East Renfrewshire", "Edinburgh", "Falkirk", "Fife", "Glasgow",
    "Highland", "Inverclyde", "Midlothian", "Moray", "Na h-Eileanan Siar", "North Ayrshire", "North Lanarkshire",
    "Orkney Islands", "Perth and Kinross", "Renfrewshire", "Scottish Borders", "Shetland Islands",
    "South Ayrshire", "South Lanarkshire", "Stirling", "West Dunbartonshire", "West Lothian", "Antrim and Newtownabbey",
    "Ards and North Down", "Armagh City, Banbridge and Craigavon", "Belfast", "Causeway Coast and Glens",
    "Derry and Strabane", "Fermanagh and Omagh", "Lisburn and Castlereagh", "Mid and East Antrim",
    "Mid Ulster", "Newry, Mourne and Down"
]

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        keyword = request.form.get("keyword")
        selected_county = request.form.get("county")
        scrape_all = request.form.get("scrape_all")
        file_format = request.form.get("file_format")

        all_results = []

        counties_to_scrape = UK_COUNTIES if scrape_all else [selected_county]

        for idx, county in enumerate(counties_to_scrape, 1):
            print(f"🔍 Scraping {idx}/{len(counties_to_scrape)}: {keyword} in {county}")
            google_results = scrape_google_maps(keyword, county)
            yelp_results = scrape_yelp(keyword, county)
            for r in google_results + yelp_results:
                r["County"] = county
            all_results.extend(google_results + yelp_results)

        history_entry = {
            "keyword": keyword,
            "county": "All UK Counties" if scrape_all else selected_county,
            "results_count": len(all_results)
        }

        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r") as f:
                history = json.load(f)
        else:
            history = []

        history.insert(0, history_entry)
        with open(HISTORY_FILE, "w") as f:
            json.dump(history[:20], f)

        df = pd.DataFrame(all_results)
        uid = uuid.uuid4().hex
        if file_format == "xlsx":
            filename = f"{uid}_results.xlsx"
            df.to_excel(filename, index=False)
        else:
            filename = f"{uid}_results.csv"
            df.to_csv(filename, index=False)

        return send_file(filename, as_attachment=True)

    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            history = json.load(f)
    else:
        history = []

    return render_template("index.html", history=history, counties=UK_COUNTIES)

if __name__ == "__main__":
    app.run(debug=True)
