import socket  # Импортируем модуль socket для работы с сетью

def send_command(command, conn):  # Функция отправки команды на сервер
    conn.send(command.encode())  # Кодируем команду и отправляем на сервер
    response = conn.recv(1024).decode()  # Получаем и декодируем ответ от сервера
    print("Ответ сервера:", response)  # Выводим ответ сервера

def authenticate(conn):  # Функция аутентификации пользователя
    while True:  # Начинаем цикл для запроса логина и пароля
        username = input("Введите логин: ")  # Запрашиваем логин у пользователя
        password = input("Введите пароль: ")  # Запрашиваем пароль у пользователя
        credentials = f"{username} {password}"  # Составляем учетные данные
        conn.send(credentials.encode())  # Отправляем учетные данные на сервер
        response = conn.recv(1024).decode().strip().lower()  # Получаем ответ и приводим его к нижнему регистру
        if response == "ok user" or response == "ok admin":  # Проверяем ответ сервера
            print("Аутентификация успешна!")  # Выводим сообщение об успешной аутентификации
            return True  # Возвращаем True при успешной аутентификации
        else:
            print("Неправильный логин или пароль. Попробуйте снова.")  # Выводим сообщение об ошибке

def main():  # Основная функция клиента
    host = '127.0.0.1'  # Устанавливаем IP-адрес сервера
    port = 12345  # Устанавливаем порт сервера

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Создаем сокет клиента
    client.connect((host, port))  # Устанавливаем соединение с сервером

    print("Добро пожаловать в клиент файлового менеджера!")  # Приветственное сообщение

    if not authenticate(client):  # Проверяем аутентификацию
        print("Не удалось произвести аутентификацию. Завершение программы.")  # Выводим сообщение об ошибке
        client.close()  # Закрываем соединение
        return  # Завершаем выполнение программы

    print("Доступные команды:")  # Выводим список доступных команд
    print("list - Список файлов и папок в текущем каталоге")
    print("mkdir <folder_name> - Создать новую папку")
    print("rmdir <folder_name> - Удалить папку")
    print("delete <file_name> - Удалить файл")
    print("rename <old_name> <new_name> - Переименовать файл")
    print("copy_to_server <source_path> <destination_path> - Скопировать файл на сервер")
    print("copy_to_client <source_path> <destination_path> - Копируем файл с сервера")
    print("exit - Выйти из клиента")

    while True:  # Начинаем цикл ввода команд
        command = input("Введите команду: ")  # Запрашиваем команду у пользователя
        send_command(command, client)  # Отправляем команду на сервер
        if command.strip() == "exit":  # Проверяем команду на выход
            break  # Прерываем цикл

    client.close()  # Закрываем соединение при завершении программы

if __name__ == "__main__":  # Проверяем запуск скрипта как основной программы
    main()  # Вызываем основную функцию