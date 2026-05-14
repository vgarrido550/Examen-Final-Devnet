from flask import Flask
from flask_bcrypt import Bcrypt
import sqlite3

app = Flask(__name__)
bcrypt = Bcrypt(app)

conexion = sqlite3.connect("usuarios.db")
cursor = conexion.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT NOT NULL,
    password TEXT NOT NULL
)
""")

usuarios = [
    ("Victor Garrido", "clave123"),
    ("admin", "admin123")
]

for usuario, clave in usuarios:
    hash_password = bcrypt.generate_password_hash(clave).decode('utf-8')

    cursor.execute(
        "INSERT INTO usuarios (usuario, password) VALUES (?, ?)",
        (usuario, hash_password)
    )

conexion.commit()

print("Usuarios almacenados correctamente con hash.")

usuario_login = input("Ingrese usuario: ")
password_login = input("Ingrese contraseña: ")

cursor.execute(
    "SELECT password FROM usuarios WHERE usuario=?",
    (usuario_login,)
)

resultado = cursor.fetchone()

if resultado:
    hash_guardado = resultado[0]

    if bcrypt.check_password_hash(hash_guardado, password_login):
        print("Autenticación exitosa")
    else:
        print("Contraseña incorrecta")
else:
    print("Usuario no encontrado")

conexion.close()

@app.route('/')
def inicio():
    return "Servidor Flask funcionando en puerto 5800"

if __name__ == '__main__':
    app.run(port=5800)