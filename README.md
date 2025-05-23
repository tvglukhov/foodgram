# Foodgram

## Описание проекта

Foodgram - сервис для хранения рецептов блюд. Создайте, загрузите свои рецепты, добавляйте их в избранное, в список покупок - делитесь рецептами с друзьями при помощи коротких ссылок, подписывайтесь на авторов рецептов.

## Инструкция по запуску

Проект предусматрвиает оркестрацию контейнерами (в том числе посредством CI/CD с помощью GitHub Actions).
- Workflow размещен в файле foodgram_workflow.yml. Отчет об успешном деплое высылается в tg;
- Инструкции Docker Compose для локального развертывания и для развертывания с помощью Docker Hub размещены в корне проекта;
- Необходимо создание файла .env с переменными: ключ, хосты, переменные PostgreSQL базы, режим дебага.

## Примеры запросов

Для просмотра документации API выполнить следующие действия:
Находясь в папке infra, выполните команду docker-compose up. При выполнении этой команды контейнер frontend, описанный в docker-compose.yml, подготовит файлы, необходимые для работы фронтенд-приложения, а затем прекратит свою работу.
По адресу http://localhost изучите фронтенд веб-приложения, а по адресу http://localhost/api/docs/ — спецификацию API.

## Использованные технологии
- Django
- Django Rest Framework
- Docker
- Docker Compose
- PostgreSQL
- GitHub Actions

## Информация об авторе
Тимофей Глухов, студент Яндекс.Практикум