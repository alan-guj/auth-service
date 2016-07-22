#!flask/bin/python


from apps import app


app.config.from_object('config')

if __name__ == '__main__':
    app.run(debug=True, threaded=True, host='0.0.0.0', port=9050)
