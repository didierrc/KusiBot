from flask import Flask, render_template

app = Flask(__name__, template_folder='frontend/templates', static_folder='frontend/static')

@app.route('/')
def home():
    return render_template('index.html')

def main():
    """Main entry point for running the app."""
    app.run(host="0.0.0.0", port=5000, debug=True)


if __name__ == '__main__':
  main()  