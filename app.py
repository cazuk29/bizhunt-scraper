from flask import Flask, render_template, request, send_file
from scraper import scrape_google_search
import pandas as pd
import uuid
import os

app = Flask(__name__)
EXPORT_FOLDER = "exports"
os.makedirs(EXPORT_FOLDER, exist_ok=True)


@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    exported_file = None
    error = None

    if request.method == "POST":
        keyword = request.form.get("keyword")
        county = request.form.get("county")
        file_format = request.form.get("file_format")

        if not keyword or not county:
            error = "Please enter both keyword and county."
        else:
            try:
                results = scrape_google_search(keyword, county)

                if not results:
                    error = "No UK results found. Try another keyword or county."
                else:
                    df = pd.DataFrame(results)
                    filename = f"{uuid.uuid4().hex}_results.{ 'xlsx' if file_format == 'xlsx' else 'csv' }"
                    filepath = os.path.join(EXPORT_FOLDER, filename)

                    if file_format == "xlsx":
                        df.to_excel(filepath, index=False)
                    else:
                        df.to_csv(filepath, index=False)

                    exported_file = filepath

            except Exception as e:
                error = f"An error occurred: {e}"

    return render_template("index.html", results=results, exported_file=exported_file, error=error)


@app.route("/download")
def download_file():
    filepath = request.args.get("file")
    if filepath and os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    return "File not found", 404


if __name__ == "__main__":
    app.run(debug=True)
