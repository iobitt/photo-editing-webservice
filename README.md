# photo-editing-webservice
Онлайн-сервис для редактирования изображений

## Инициализация

Создаём виртуальное окружение

`python3 -m venv venv`

Активируем виртуальное окружение

`source venv/bin/activate` (linux)

Устанавливаем зависимости

`pip install -r requirements.txt`

## Использование

Запустить сервер

`bash run.sh` (linux)

Открыть swagger

`http://localhost:8000/docs`

Отправить изображение на обработку. На данный момент доступно 2 метода

По параметру new_file_name запрашивать статус операции через равные интервалы времени (5-10 секунд)

Когда "ready" будет равен true, скачать изображение по ссылке

http://localhost:8000/downloadable_files/{new_file_name}


wget https://pjreddie.com/media/files/yolov3.weights
