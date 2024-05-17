import socket
import os
import shutil
import threading
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
connection_log = logging.getLogger('connection')
authentication_log = logging.getLogger('authentication')
file_operation_log = logging.getLogger('file_operation')

# База данных пользователей (логины и пароли)
users = {
    "user1": "password1",
    "user2": "password2"
}

# База данных администраторов (логины и пароли)
admins = {
    "admin1": "adminpassword1",
    "admin2": "adminpassword2"
}

# Функция для аутентификации пользователя
def authenticate(conn):
    conn.send("Введите логин и пароль через пробел: ".encode())
    credentials = conn.recv(1024).decode().strip()
    print("Полученные учетные данные:", credentials)  # Добавим эту строку для отладки
    if ' ' not in credentials:
        conn.send("Неверный формат логина и пароля".encode())
        authentication_log.info("Invalid format of username and password")
        return None
    username, password = credentials.split(' ', 1)
    print("Попытка аутентификации с логином и паролем:", username, password)  # Добавим эту строку для отладки
    print("Содержимое словаря users:", users)  # Добавим эту строку для отладки
    print("Содержимое словаря admins:", admins)  # Добавим эту строку для отладки
    if username in users and users[username] == password:
        conn.send("OK user".encode())
        authentication_log.info(f"User {username} successfully authenticated")
        return "user"
    elif username in admins and admins[username] == password:
        conn.send("OK admin".encode())
        authentication_log.info(f"Admin {username} successfully authenticated")
        return "admin"
    else:
        conn.send("Неправильный логин или пароль".encode())
        authentication_log.info(f"Failed authentication attempt for user {username}")
        return None



# Функция для обработки команд от клиента
def handle_command(command, conn, user_type):
    command_parts = command.split()
    if not command_parts:
        conn.send("Invalid command".encode())
        return False
    if command_parts[0] == "list":
        files = os.listdir('.')
        conn.send(str(files).encode())
        file_operation_log.info("List of files and folders sent to client")
    elif command_parts[0] == "mkdir" and len(command_parts) > 1:
        try:
            os.mkdir(command_parts[1])
            conn.send("Папка успешно создана".encode())
            file_operation_log.info(f"Folder '{command_parts[1]}' created")
        except OSError as e:
            conn.send(f"Error: {e}".encode())
            file_operation_log.error(f"Error creating folder '{command_parts[1]}': {e}")
    elif command_parts[0] == "rmdir" and len(command_parts) > 1:
        try:
            shutil.rmtree(command_parts[1])
            conn.send("Папка успешно удалена".encode())
            file_operation_log.info(f"Folder '{command_parts[1]}' deleted")
        except OSError as e:
            conn.send(f"Error: {e}".encode())
            file_operation_log.error(f"Error deleting folder '{command_parts[1]}': {e}")
    elif command_parts[0] == "delete" and len(command_parts) > 1:
        try:
            os.remove(command_parts[1])
            conn.send("Файл успешно удален".encode())
            file_operation_log.info(f"File '{command_parts[1]}' deleted")
        except OSError as e:
            conn.send(f"Error: {e}".encode())
            file_operation_log.error(f"Error deleting file '{command_parts[1]}': {e}")
    elif command_parts[0] == "rename" and len(command_parts) > 2:
        try:
            os.rename(command_parts[1], command_parts[2])
            conn.send("Файл успешно переименован".encode())
            file_operation_log.info(f"File '{command_parts[1]}' renamed to '{command_parts[2]}'")
        except OSError as e:
            conn.send(f"Error: {e}".encode())
            file_operation_log.error(f"Error renaming file '{command_parts[1]}': {e}")
    elif command_parts[0] == "copy_to_server" and len(command_parts) > 2:
        try:
            with open(command_parts[1], 'rb') as f:
                with open(command_parts[2], 'wb') as new_f:
                    shutil.copyfileobj(f, new_f)
            conn.send("Файл успешно скопирован на сервер".encode())
            file_operation_log.info(f"File '{command_parts[1]}' copied to server as '{command_parts[2]}'")
        except OSError as e:
            conn.send(f"Error: {e}".encode())
            file_operation_log.error(f"Error copying file '{command_parts[1]}' to server: {e}")
    elif command_parts[0] == "copy_to_client" and len(command_parts) > 2:
        try:
            with open(command_parts[1], 'rb') as f:
                with open(command_parts[2], 'wb') as new_f:
                    shutil.copyfileobj(f, new_f)
            conn.send("Файл успешно скопирован клиенту".encode())
            file_operation_log.info(f"File '{command_parts[1]}' copied to client as '{command_parts[2]}'")
        except OSError as e:
            conn.send(f"Error: {e}".encode())
            file_operation_log.error(f"Error copying file '{command_parts[1]}' to client: {e}")
    elif command_parts[0] == "exit":
        conn.send("До свидания!".encode())
        conn.close()
        connection_log.info("Connection closed")
        return True
    else:
        conn.send("Invalid command".encode())
    return False

# Функция для обработки подключения клиента
def handle_client(conn, addr):
    connection_log.info(f"Connected to {addr}")

    user_type = authenticate(conn)
    if not user_type:
        conn.close()
        return

    while True:
        command = conn.recv(1024).decode()
        if not command:
            break
        if handle_command(command, conn, user_type):
            break

    connection_log.info(f"Disconnected from {addr}")

# Основная функция сервера
def main():
    host = '127.0.0.1'
    port = 12345

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)

    connection_log.info(f"Server listening on {host}:{port}")

    while True:
        conn, addr = server.accept()
        connection_log.info(f"Connected to {addr}")
        client_thread = threading.Thread(target=handle_client, args=(conn, addr))
        client_thread.start()

if __name__ == "__main__":
    main()
