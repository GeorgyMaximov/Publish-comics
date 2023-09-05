import requests
import os
from random import randint
from dotenv import load_dotenv


def check_response(response):
    if "error" in response:
        message = response["error"]["error_msg"]
        error_code = response["error"]["error_code"]
        raise requests.HTTPError(error_code, message)


def get_wall_upload_url(group_id, access_token):
    url = f"https://api.vk.com/method/photos.getWallUploadServer"
    params = {
        "group_id": group_id,
        "access_token": access_token,
        "v": 5.131
    }
    response = requests.get(url, params)
    response.raise_for_status()
    check_response(response)
    response = response.json()
    return response["response"]["upload_url"]


def upload_photo(wall_upload_url):
    with open("comic.png", "rb") as photo:
        files = {
            "photo": photo
        }
        response = requests.post(wall_upload_url, files=files)
    response.raise_for_status()
    check_response(response)
    return response.json()


def save_wall_photos(group_id, access_token, server, photo, hash):
    params = {
        "server": server,
        "photo": photo,
        "hash": hash,
        "group_id": group_id,
        "access_token": access_token,
        "v": 5.131
    }
    url = f"https://api.vk.com/method/photos.saveWallPhoto"
    response = requests.post(url, params)
    response.raise_for_status()
    check_response(response)
    response = response.json()
    response = response["response"][0]
    return response


def post_comic(group_id, access_token, comment, photo_id, owner_id):
    params = {
        "owner_id": -group_id,
        "from_group": 1,
        "attachments": f"photo{owner_id}_{photo_id}",
        "message": comment,
        "group_id": group_id,
        "access_token": access_token,
        "v": 5.131
    }
    url = f"https://api.vk.com/method/wall.post"
    response = requests.post(url, params)
    response.raise_for_status()
    check_response(response)
    response = response.json()


def get_random_comic():
    response = requests.get("https://xkcd.com/info.0.json")
    response.raise_for_status()
    comics_number = response.json()["num"]
    url = f"https://xkcd.com/{randint(1, comics_number)}/info.0.json"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def download_comic(url):
    response = requests.get(url)
    response.raise_for_status()
    with open("comic.png", 'wb') as file:
        file.write(response.content)


def main():
    load_dotenv()
    access_token = os.environ["VK_ACCESS_TOKEN"]
    group_id = int(os.environ["VK_GROUP_ID"])
    comic = get_random_comic()
    download_comic(comic["img"])
    try:
        wall_upload_url = get_wall_upload_url(group_id, access_token)
        wall_upload_server = upload_photo(wall_upload_url)
        photo = save_wall_photos(group_id, access_token, wall_upload_server["server"], wall_upload_server["photo"], wall_upload_server["hash"])
        post_comic(group_id, access_token, comic["alt"], photo["id"], photo["owner_id"])
    finally:
        os.remove("comic.png")


if __name__ == "__main__":
    main()