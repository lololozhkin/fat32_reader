import requests
from urllib.parse import urlencode
from progress.bar import IncrementalBar
from to_download import FILES
import os


API_URL = 'https://cloud-api.yandex.net/v1/disk/public/resources/download?'


def download_file(public_key, file_path):
    final_url = API_URL + urlencode({'public_key': public_key})
    response = requests.get(final_url)
    download_url = response.json()['href']

    with open(file_path, 'wb') as f:
        download_response = requests.get(download_url, stream=True)
        length = int(download_response.headers.get('Content-length'))
        bar = IncrementalBar('Progress', max=length)

        for data in download_response.iter_content(chunk_size=4096):
            f.write(data)
            bar.next(len(data))

        bar.finish()


def main():
    try:
        os.mkdir('test_files')
    except FileExistsError:
        pass

    for href, file in FILES:
        print(f'Downloading {file}')
        download_file(href, os.path.join('test_files', file))

    print('Done')


if __name__ == '__main__':
    main()
