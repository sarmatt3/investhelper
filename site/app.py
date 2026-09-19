from flask import Flask, render_template, request
from werkzeug.middleware.proxy_fix import ProxyFix
import invest_helper_funcs
app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto = 1, x_host = 1)
@app.route("/")
def home():
    key_rate = invest_helper_funcs.key_rate_today()
    more_key_rates = invest_helper_funcs.show_key_rate()
    currency = invest_helper_funcs.get_currency(True)
    return render_template("index.html", datas=[key_rate, more_key_rates, currency])

@app.route("/get_active", methods=["POST"])
def get_active():
    ticker = request.form["ticker"].upper()
    from_ = request.form["from_"]
    to = request.form["to"]

    return render_template("price.html", datas=invest_helper_funcs.return_active_price(ticker, from_, to)
)

@app.route("/birge")
def birge():
    popular = ["T", "SBER", "GAZP"]
    result = []
    for i in popular:
        result.append(invest_helper_funcs.get_active_price_last(i))
    return render_template("birge.html", datas = result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
