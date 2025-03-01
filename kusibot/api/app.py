from flask import Flask, render_template
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__, template_folder='frontend/templates', static_folder='frontend/static')
csrf = CSRFProtect()
csrf.init_app(app)

@app.route('/')
def home():
    return render_template('index.html')

def main():
    """Main entry point for running the app."""
    app.run(host="0.0.0.0", port=5000, debug=True)


if __name__ == '__main__':
  main()  