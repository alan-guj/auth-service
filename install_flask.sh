#Flask环境部署
packages=(Flask flask-sqlalchemy sqlalchemy-migrate requests PyMySQL flask-login flask-wtf requests \
    flask-oauthlib flask-session qrcode image flask-cors)
#packages=(Flask)
for p in ${packages[@]};do
    echo -----------------install $p-----------------------------
    ./flask/bin/pip install $p
done
