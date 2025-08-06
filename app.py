from flask import Flask, render_template, request, send_file
import pandas as pd
from scraper import scrape_google_maps, scrape_yelp
import os
from datetime import datetime

app = Flask(__name__)

uk_counties = [
    "Bedfordshire", "Berkshire", "Bristol", "Buckinghamshire", "Cambridgeshire", "Cheshire", "City of London",
    "Cornwall", "County Durham", "Cumbria", "Derbyshire", "Devon", "Dorset", "East Riding of Yorkshire",
    "East Sussex", "Essex", "Gloucestershire", "Greater London", "Greater Manchester", "Hampshire", "Herefordshire",
    "Hertfordshire", "Isle of Wight", "Kent", "Lancashire", "Leicestershire", "Lincolnshire", "Merseyside",
    "Norfolk", "North Yorkshire", "Northamptonshire", "Northumberland", "Nottinghamshire", "Oxfordshire",
    "Rutland", "Shropshire", "Somerset", "South Yorkshire", "Staffordshire", "Suffolk", "Surrey", "Tyne and Wear",
    "Warwickshire", "West Midlands", "West Sussex", "West Yorkshire", "Wiltshire", "Worcestershire"
]

@app.route('/', methods=['GET', 'POST'])
def index():
    error = None
    results = []

    if request.method == 'POST':
        keywords = request.form['keyword'].split(',')
        county = request.form['county']
        export_format = request.form['export_format']

        all_results = []

        try:
            for keyword in keywords:
                keyword = keyword.strip()
                print(f"🔎 Searching: {keyword} in {county}")
                google_data = scrape_google_maps(keyword, county)
                yelp_data = scrape_yelp(keyword, county)

                combined = google_data + yelp_data
                print(f"✅ Results for '{keyword}': {len(combined)}")

                # Retry once if no data
                if not combined:
                    print("🔁 Retrying...")
                    google_data = scrape_google_maps(keyword, county)
                    yelp_data = scrape_yelp(keyword, county)
                    combined = google_data + yelp_data

                all_results += combined

            if not all_results:
                error = "No data found. Try different keywords or counties."
                return render_template("index.html", counties=uk_counties, error=error)

            # Export
            df = pd.DataFrame(all_results)
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"results_{timestamp}"

            if export_format == 'csv':
                filepath = f"{filename}.csv"
                df.to_csv(filepath, index=False)
            else:
                filepath = f"{filename}.xlsx"
                df.to_excel(filepath, index=False)

            return send_file(filepath, as_attachment=True)

        except Exception as e:
            print(f"❌ Error: {e}")
            error = f"An error occurred: {str(e)}"
            return render_template("index.html", counties=uk_counties, error=error)

    return render_template("index.html", counties=uk_counties)
