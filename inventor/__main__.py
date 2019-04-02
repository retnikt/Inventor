from inventor import app, init

if __name__ == "__main__":
    init(debug=True)
    app.run("127.0.0.1", 5000, debug=True)
