#!/usr/bin/env python3
from flask import Flask, render_template
import yangvoodoo
import logic

app = Flask(__name__, static_url_path='/static')


@app.route("/example")
def hello_world():
    session = yangvoodoo.DataAccess()
    session.connect("integrationtest")
    root = session.get_node()

    processed = {}
    (count, band) = logic.bandlogic.find_highest_count(root.web.bands)

    processed['highest_band_count'] = count
    processed['highest_band_name'] = band

    xpath = "/integrationtest:web/integrationtest:bands/integrationtest:gigs[integrationtest:year='2019']"
    gigs_this_year = session.gets_len(xpath)
    target = 24

    processed['gigs_this_year_vs_target'] = "%.2f" % ((gigs_this_year/target)*100)

    distri = logic.bandlogic.find_gig_piehcart(root.web.bands)

    return render_template('example.html', root=root, processed=processed, distri=distri)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
