import sqlite3

import sqlalchemy
from flask import Flask, render_template, redirect, url_for, request, current_app, flash

from data import db_session
from data.oil import Oil
from data.users import User
import requests
import os
from contextlib import contextmanager
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)


app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

siberianoil = ['Самотлорское', 'Салымское', 'Приобское', 'Красноленинское', 'Ванкорское']
volgauraloil = ['Ромашкинское', 'Бавлинское', 'Новоольховско-Домоскинское', 'Арланское', 'Туймазинское', 'Ярино-Каменное']
n1 = len(siberianoil)
n2 = len(volgauraloil)


@app.route('/main')
def index():
    return render_template('index.html')


@contextmanager
def create_db_session():
    db_session.global_init("db/oil.db")
    db_sess = db_session.create_session()
    try:
        yield db_sess
        db_sess.commit()
    except Exception as e:
        db_sess.rollback()
        raise e
    finally:
        db_sess.close()


@app.route('/oil', methods=['GET', 'POST'])
def oil():
    image_url = url_for('static', filename='img/1.png')
    if request.method == 'POST':
        selected_image = request.form["image"]
        print(selected_image)
        try:
            con = sqlite3.connect('db/oil.db')
            cur = con.cursor()
            end_img = cur.execute(
                f"""SELECT o.img FROM oil AS o WHERE o.title='{selected_image}'""").fetchall()
            con.close()

            if end_img:
                print(1111, end_img)
                image_url = f'static/img/{end_img[0][0]}'
                print(222, image_url)
            else:
                print(f"Не найдено изображение для {selected_image}")
        except sqlite3.Error as e:
            print(f"Ошибка при работе с базой данных: {e}")
    try:
        with create_db_session() as db_sess:
            con = sqlite3.connect('db/oil.db')
            cur = con.cursor()
            for i, oil_title in enumerate(siberianoil + volgauraloil):

                resulttitle = cur.execute(
                    f"""SELECT o.placed FROM oil AS o WHERE o.title='{oil_title}'""").fetchall()  # f-string

                if not resulttitle:
                    oil = Oil()
                    oil.title = oil_title
                    if oil_title in siberianoil:
                        oil.placed = "Западная-Сибирь"
                    else:
                        oil.placed = "Волго-Уральская область"
                    db_sess.add(oil)

            server_address = 'https://static-maps.yandex.ru/v1?'
            api_key = 'f3a0fe3a-b07e-4840-a1da-06f18b2ddf13'

            for c, oil_title in enumerate(siberianoil):
                resultcoo = cur.execute(
                    f"""SELECT o.coo FROM oil AS o WHERE o.title='{oil_title}'""").fetchall()

                if resultcoo:
                    resultcoo = resultcoo[0][0]
                    print(resultcoo)
                    ll_spn = f"ll={resultcoo}&spn=0.2,0.2&l=map&z=16"
                    map_request = f"{server_address}{ll_spn}&apikey={api_key}"

                    try:
                        response = requests.get(map_request)
                        response.raise_for_status()

                        filename = f"map{c}.png"
                        map_file = os.path.join(current_app.root_path, "static", "img", filename)

                        os.makedirs(os.path.dirname(map_file), exist_ok=True)

                        with open(map_file, "wb") as file:
                            file.write(response.content)

                        oil_record = db_sess.query(Oil).filter(Oil.title == oil_title).first()
                        if oil_record:
                            oil_record.img = filename
                        else:
                            print(f"Не найдено месторождение с названием '{oil_title}'")

                    except requests.exceptions.RequestException as e:
                        print(f"Ошибка при запросе к API Яндекс.Карт: {e}")
                    except Exception as e:
                        print(f"Ошибка при сохранении изображения: {e}")

            con.close()

    except sqlalchemy.exc.PendingRollbackError as e:
        print(f"Ошибка PendingRollbackError: {e}")
    except sqlalchemy.exc.IntegrityError as e:
        print(f"Ошибка IntegrityError: {e}")
    except Exception as e:
        print(f"Общая ошибка: {e}")
    print(image_url)
    return render_template('oil.html', place1=siberianoil, place2=volgauraloil, n1=n1, n2=n2, image_url=image_url)


@app.route('/')
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login = request.form["login"]
        passw = request.form["password"]

        db_session.global_init("db/user.db")
        db_sess = db_session.create_session()

        user = db_sess.query(User).filter(User.login == login).first()

        if user and check_password_hash(user.password, passw):
            users = db_sess.query(User).all()
            db_sess.close()
            return render_template("index.html", users=users)
        else:
            db_sess.close()
            flash("Неправильный логин или пароль", "error")
            return render_template("mainwindow.html")

    return render_template("mainwindow.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        uname = request.form["username"]
        login = request.form["login"]
        passw = request.form["password"]
        confirmedpassw = request.form["confirm_password"]

        if passw != confirmedpassw:
            flash("Пароли не совпадают", "error")
            return render_template("register.html")

        db_session.global_init("db/user.db")
        db_sess = db_session.create_session()

        existing_user = db_sess.query(User).filter(User.login == login).first()
        if existing_user:
            flash("Пользователь с таким логином уже существует", "error")
            return render_template("register.html")

        hashed_password = generate_password_hash(passw)

        user = User()
        user.name = uname
        user.login = login
        user.password = hashed_password

        db_sess.add(user)
        db_sess.commit()
        db_sess.close()

        flash("Регистрация прошла успешно! Теперь войдите.", "success")
        return redirect(url_for("index"))

    return render_template("register.html")

if __name__ == '__main__':
    app.run(port=8000, host='127.0.0.1')
