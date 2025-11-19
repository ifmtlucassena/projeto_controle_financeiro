from app import criar_app

if __name__ == '__main__':
    app = criar_app()
    app.run(debug=True, host='127.0.0.1', port=5000)
