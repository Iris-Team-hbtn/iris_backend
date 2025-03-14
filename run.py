from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True, ssl_context=(
        '/etc/letsencrypt/live/34.44.177.109.nip.io/fullchain.pem',
        '/etc/letsencrypt/live/34.44.177.109.nip.io/privkey.pem'
    ))