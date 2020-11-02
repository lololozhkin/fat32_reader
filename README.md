# fat32_reader
### by Ложкин Александр
Простая утилита для просмотра листинга директорий образа fat32.
Так же имеется возможность "доставать" некоторые файлы из образа, пока только одиночные файлы, а не целые папки рекурсивно, но эта функция добавится в скором времени. Так же можно сканировать образ на некоторые проблемы в нем, такие как пересекающиеся цепочки кластеров и потерянные кластера.

## Как начать работу?

python3 main.py image_path \[options\]

## Как запустить тесты?
pytest-3

## Как скачать тестовые файлы?
python3 download_samples.py

## Какие команды доступны внутри утилиты?
Чтобы посмотреть список файлов и директорий наберите **ls**
По умолчанию команда ls не показывает скрытые файлы. Файл является скрытым, если он начинается на ".". Если же вы хотите посмотреть все файлы в данной директории, используйте флаг -a.
Если вы хотите посмотреть дополнительную информацию о файлах и директориях, используйте флаг -l.
Флаги можно комбинировать, например так: ls -la

Чтобы перейти в какую-то из директорий используйте команду **cd**.
Поддерживаются как абсолютная аддресация, так и относительная.
В каждой директории по умолчанию существует 2 папки: "." и "..", которые ссылаются на даную папку и на родительстую соответственно.

Если вы хотите узнать в какой директории вы сейчас находитесь, используйте команду **pwd**.

Если вам нужно "достать" файл из образа на свой диск, используйте команду **export**

Если вы хотите просканировать диск на некоторые проблемы, используйте **scan**. По умолчанию образ будет сканироваться и на потерянные кластера и на пересекающиеся цепочки, но вы можете управлять этим поведением используя флаги **-l -i -a**

Чтобы завершить работу приложения используйте команду **exit**

Каждая команда кроме **exit** содержит справку, которую можно посмотреть добавив флаг **--help**.
