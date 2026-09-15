import os
import time
import threading
import requests
import yt_dlp
import re

DOWNLOAD_MUSIC = "/storage/emulated/0/Download/tool/musicvd"
DOWNLOAD_VIDEO = "/storage/emulated/0/Download/tool/vds"
DOWNLOAD_FACEBOOK_VIDEO = "/storage/emulated/0/Download/tool/fbvds"
DOWNLOAD_FACEBOOK_PICTURE = "/storage/emulated/0/Download/tool/fbpicture"
DOWNLOAD_TIKTOK_PICTURE = "/storage/emulated/0/Download/tool/ttpicture"

BLUE = "\033[94m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

RAINBOW = [
    "\033[91m",
    "\033[93m",
    "\033[92m",
    "\033[96m",
    "\033[94m",
    "\033[95m",
    "\033[97m"
]

def blue(text):
    return f"{BLUE}{text}{RESET}"

def yellow(text):
    return f"{YELLOW}{text}{RESET}"

def red(text):
    return f"{RED}{text}{RESET}"

def ask(text):
    value = input(red(text)).strip()

    if value.lower() == "off":
        print()
        print(yellow("🛑 Đã nhận lệnh OFF!"))
        print(yellow("🛑 Dừng tool như Ctrl + C..."))
        raise KeyboardInterrupt

    return value

def rainbow_loading(text, stop_event):
    i = 0

    while not stop_event.is_set():
        print(
            f"\r{RAINBOW[i]}{text}{RESET}",
            end="",
            flush=True
        )

        i = (i + 1) % len(RAINBOW)
        time.sleep(0.12)

    print(
        "\r" + " " * (len(text) + 10),
        end="\r",
        flush=True
    )

def start_loading(text):
    stop_event = threading.Event()

    thread = threading.Thread(
        target=rainbow_loading,
        args=(text, stop_event),
        daemon=True
    )

    thread.start()

    return stop_event, thread

def stop_loading(stop_event, thread):
    stop_event.set()
    thread.join()

def download_file(url, filename, folder):
    os.makedirs(folder, exist_ok=True)

    response = requests.get(
        url,
        timeout=60,
        stream=True
    )

    response.raise_for_status()

    path = os.path.join(folder, filename)

    with open(path, "wb") as f:
        for chunk in response.iter_content(1024 * 64):
            if chunk:
                f.write(chunk)

    return path

def download_tiktok(url, mode):
    api_url = "https://www.tikwm.com/api/?url=" + url

    response = requests.get(
        api_url,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    if data.get("code") != 0:
        raise Exception("Không lấy được dữ liệu TikTok!")

    video_url = data["data"].get("play")
    music_url = data["data"].get("music")

    if mode == "video":
        if not video_url:
            raise Exception("Không tìm thấy video TikTok!")

        download_file(
            video_url,
            "tiktok_video.mp4",
            DOWNLOAD_MUSIC
        )

    else:
        if not music_url:
            raise Exception("Không tìm thấy nhạc TikTok!")

        download_file(
            music_url,
            "tiktok_music.mp3",
            DOWNLOAD_MUSIC
        )

def download_facebook(url, mode):
    os.makedirs(
        DOWNLOAD_MUSIC if mode == "music"
        else DOWNLOAD_FACEBOOK_VIDEO,
        exist_ok=True
    )

    if mode == "music":
        options = {
            "format": "bestaudio/best",
            "outtmpl": os.path.join(
                DOWNLOAD_MUSIC,
                "%(title).80s-%(id)s.%(ext)s"
            ),
            "noplaylist": True,
            "continuedl": True,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192"
                }
            ]
        }

    else:
        options = {
            "format": (
                "bestvideo[ext=mp4]+bestaudio[ext=m4a]"
                "/best[ext=mp4]/best"
            ),
            "outtmpl": os.path.join(
                DOWNLOAD_FACEBOOK_VIDEO,
                "%(title).80s-%(id)s.%(ext)s"
            ),
            "merge_output_format": "mp4",
            "noplaylist": True,
            "continuedl": True
        }

    with yt_dlp.YoutubeDL(options) as ydl:
        ydl.download([url])

def download_youtube(url, mode):
    if mode == "music":
        options = {
            "format": "bestaudio/best",
            "outtmpl": os.path.join(
                DOWNLOAD_MUSIC,
                "%(title)s.%(ext)s"
            ),
            "noplaylist": True,
            "continuedl": True,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192"
                }
            ]
        }

    else:
        options = {
            "format": (
                "bestvideo[ext=mp4]+bestaudio[ext=m4a]"
                "/best[ext=mp4]/best"
            ),
            "outtmpl": os.path.join(
                DOWNLOAD_VIDEO,
                "%(title)s.%(ext)s"
            ),
            "merge_output_format": "mp4",
            "noplaylist": True,
            "continuedl": True
        }

    os.makedirs(
        DOWNLOAD_MUSIC if mode == "music"
        else DOWNLOAD_VIDEO,
        exist_ok=True
    )

    with yt_dlp.YoutubeDL(options) as ydl:
        ydl.download([url])

def youtube_music_video():
    os.system("clear")

    print(blue("=" * 48))
    print(blue("     TẢI NHẠC + HÌNH ẢNH YOUTUBE"))
    print(blue("=" * 48))
    print()

    url = ask("🔗 Nhập link YouTube: ")

    if (
        "youtube.com" not in url.lower()
        and "youtu.be" not in url.lower()
    ):
        print(yellow(
            "❌ Chức năng này chỉ dành cho YouTube!"
        ))
        time.sleep(2)
        return

    os.makedirs(
        DOWNLOAD_VIDEO,
        exist_ok=True
    )

    options = {
        "format": (
            "bestvideo[ext=mp4]+bestaudio[ext=m4a]"
            "/best[ext=mp4]/best"
        ),
        "outtmpl": os.path.join(
            DOWNLOAD_VIDEO,
            "%(title)s.%(ext)s"
        ),
        "merge_output_format": "mp4",
        "noplaylist": True,
        "continuedl": True,
        "quiet": True,
        "no_warnings": True
    }

    stop_event, thread = start_loading(
        "❄️ Đang tải nhạc + hình ảnh YouTube..."
    )

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([url])

    except KeyboardInterrupt:
        stop_loading(
            stop_event,
            thread
        )
        raise

    except Exception as e:
        stop_loading(
            stop_event,
            thread
        )

        print(yellow(
            f"❌ Có lỗi xảy ra: {e}"
        ))

        time.sleep(3)
        return

    stop_loading(
        stop_event,
        thread
    )

    print(yellow(
        "❄️ Tải nhạc + hình ảnh hoàn thành!"
    ))

    print(yellow(
        "📁 Download/tool/vds"
    ))

    time.sleep(3)

def download_tiktok_image(image_url, image_number):
    os.makedirs(
        DOWNLOAD_TIKTOK_PICTURE,
        exist_ok=True
    )

    filename = os.path.join(
        DOWNLOAD_TIKTOK_PICTURE,
        f"tiktok_{image_number}.jpg"
    )

    response = requests.get(
        image_url,
        timeout=30
    )

    response.raise_for_status()

    with open(filename, "wb") as f:
        f.write(response.content)

    return filename

def show_image_termux(image_url, image_number):
    temp_dir = "/data/data/com.termux/files/usr/tmp"

    os.makedirs(
        temp_dir,
        exist_ok=True
    )

    temp_file = os.path.join(
        temp_dir,
        f"tiktok_{image_number}.jpg"
    )

    try:
        response = requests.get(
            image_url,
            timeout=30
        )

        response.raise_for_status()

        with open(temp_file, "wb") as f:
            f.write(response.content)

        os.system(
            f'chafa --format symbols --colors 256 '
            f'--size 50x25 "{temp_file}"'
        )

    except Exception as e:
        print(yellow(
            f"❌ Không thể hiển thị ảnh: {e}"
        ))

    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

def tiktok_picture():
    os.system("clear")

    print(blue("=" * 48))
    print(blue("       TẢI ẢNH TIKTOK"))
    print(blue("=" * 48))
    print()

    url = ask("🔗 Nhập link TikTok: ")

    if "tiktok.com" not in url.lower():
        print(yellow(
            "❌ Chức năng này chỉ dành cho TikTok!"
        ))
        time.sleep(2)
        return

    stop_event, thread = start_loading(
        "❄️ Đang lấy ảnh TikTok..."
    )

    try:
        api_url = "https://www.tikwm.com/api/?url=" + url

        response = requests.get(
            api_url,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        if data.get("code") != 0:
            stop_loading(
                stop_event,
                thread
            )

            print(yellow(
                "❌ Không lấy được dữ liệu TikTok!"
            ))

            time.sleep(3)
            return

        images = data["data"].get(
            "images",
            []
        )

        stop_loading(
            stop_event,
            thread
        )

        if not images:
            print(yellow(
                "❌ Video TikTok này không có ảnh!"
            ))

            time.sleep(3)
            return

        total = len(images)

        print(yellow(
            f"Video có {total} ảnh"
        ))

        print()

        choice = ask(
            "Bạn có muốn xem ảnh kh? (Yes/No): "
        ).lower()

        if choice == "no":
            return

        if choice != "yes":
            print(yellow(
                "❌ Vui lòng nhập Yes hoặc No!"
            ))

            time.sleep(2)
            return

        if total < 5:
            for i, image_url in enumerate(
                images,
                1
            ):
                print(yellow(
                    f"❄️ Đang tải ảnh {i}/{total}..."
                ))

                download_tiktok_image(
                    image_url,
                    i
                )

                show_image_termux(
                    image_url,
                    i
                )

            print()
            print(yellow(
                "❄️ Tải ảnh TikTok hoàn thành!"
            ))

            print(yellow(
                "📁 Download/tool/ttpicture"
            ))

            time.sleep(3)
            return

        print(yellow(
            "Do quá 5 ảnh nên hãy chọn ảnh để xem :"
        ))

        while True:
            number = ask(
                f"Nhập số ảnh (1-{total}): "
            )

            try:
                number = int(number)

            except ValueError:
                print(yellow(
                    "❌ Hãy nhập số!"
                ))
                continue

            if number < 1 or number > total:
                print(yellow(
                    f"Không tồn tại ảnh số {number}, "
                    f"tối đa: {total}"
                ))
                continue

            break

        image_url = images[number - 1]

        print(yellow(
            f"❄️ Đang tải ảnh {number}..."
        ))

        download_tiktok_image(
            image_url,
            number
        )

        show_image_termux(
            image_url,
            number
        )

        print()
        print(yellow(
            "❄️ Tải ảnh hoàn thành!"
        ))

        print(yellow(
            "📁 Download/tool/ttpicture"
        ))

        time.sleep(3)

    except KeyboardInterrupt:
        stop_loading(
            stop_event,
            thread
        )
        raise

    except Exception as e:
        stop_loading(
            stop_event,
            thread
        )

        print(yellow(
            f"❌ Có lỗi xảy ra: {e}"
        ))

        time.sleep(3)

def download_facebook_picture(url):
    os.system("clear")

    print(blue("=" * 48))
    print(blue("     TẢI ẢNH FACEBOOK"))
    print(blue("=" * 48))
    print()

    if not (
        "facebook.com" in url.lower()
        or "fb.com" in url.lower()
        or "fb.watch" in url.lower()
    ):
        print(yellow(
            "❌ Chức năng này chỉ dành cho Facebook!"
        ))

        time.sleep(2)
        return

    os.makedirs(
        DOWNLOAD_FACEBOOK_PICTURE,
        exist_ok=True
    )

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Linux; Android 14; SM-A725F) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/140.0.0.0 Mobile Safari/537.36"
        ),
        "Accept": (
            "text/html,application/xhtml+xml,"
            "application/xml;q=0.9,"
            "image/avif,image/webp,*/*;q=0.8"
        ),
        "Accept-Language": (
            "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7"
        ),
        "Referer": "https://www.facebook.com/"
    }

    session = requests.Session()
    session.headers.update(headers)

    urls = [
        url,
        url.replace(
            "https://www.facebook.com/",
            "https://m.facebook.com/"
        ),
        url.replace(
            "https://facebook.com/",
            "https://m.facebook.com/"
        )
    ]

    image_url = None

    stop_event, thread = start_loading(
        "❄️ Đang lấy ảnh Facebook..."
    )

    try:
        for target_url in urls:
            try:
                response = session.get(
                    target_url,
                    timeout=30,
                    allow_redirects=True
                )

                if response.status_code != 200:
                    continue

                html = response.text

                patterns = [
                    r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']',
                    r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']',
                    r'<meta[^>]+property=["\']og:image:url["\'][^>]+content=["\']([^"\']+)["\']',
                    r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image:url["\']',
                    r'"image"\s*:\s*"([^"]+)"',
                    r'"thumbnailUrl"\s*:\s*"([^"]+)"',
                    r'"src"\s*:\s*"(https:\\/\\/[^"]+)"'
                ]

                for pattern in patterns:
                    match = re.search(
                        pattern,
                        html,
                        re.IGNORECASE
                    )

                    if match:
                        image_url = match.group(1)
                        break

                if image_url:
                    break

            except requests.RequestException:
                continue

        if not image_url:
            stop_loading(
                stop_event,
                thread
            )

            print(yellow(
                "❌ Không tìm thấy ảnh Facebook!"
            ))

            print()

            print(yellow(
                "Có thể do:"
            ))

            print(yellow(
                "- Link /share/p/ yêu cầu đăng nhập"
            ))

            print(yellow(
                "- Bài viết không công khai"
            ))

            print(yellow(
                "- Facebook đã thay đổi cấu trúc trang"
            ))

            print(yellow(
                "- Facebook chặn yêu cầu từ Termux"
            ))

            time.sleep(4)
            return

        image_url = image_url.replace(
            "\\/",
            "/"
        )

        image_url = image_url.replace(
            "\\u0025",
            "%"
        )

        image_url = image_url.replace(
            "\\u003A",
            ":"
        )

        image_url = image_url.replace(
            "\\u002F",
            "/"
        )

        image_url = image_url.replace(
            "&amp;",
            "&"
        )

        image_response = session.get(
            image_url,
            timeout=30,
            allow_redirects=True
        )

        if image_response.status_code != 200:
            stop_loading(
                stop_event,
                thread
            )

            print(yellow(
                "❌ Không tải được ảnh!"
            ))

            print(yellow(
                f"HTTP {image_response.status_code}"
            ))

            time.sleep(3)
            return

        content_type = image_response.headers.get(
            "Content-Type",
            ""
        ).lower()

        extension = ".jpg"

        if "png" in content_type:
            extension = ".png"

        elif "webp" in content_type:
            extension = ".webp"

        elif "gif" in content_type:
            extension = ".gif"

        elif (
            "jpeg" in content_type
            or "jpg" in content_type
        ):
            extension = ".jpg"

        filename = os.path.join(
            DOWNLOAD_FACEBOOK_PICTURE,
            f"facebook_{int(time.time())}{extension}"
        )

        with open(filename, "wb") as f:
            f.write(image_response.content)

    except KeyboardInterrupt:
        stop_loading(
            stop_event,
            thread
        )
        raise

    except Exception as e:
        stop_loading(
            stop_event,
            thread
        )

        print(yellow(
            f"❌ Có lỗi xảy ra: {e}"
        ))

        time.sleep(3)
        return

    stop_loading(
        stop_event,
        thread
    )

    print(yellow(
        "❄️ Tải ảnh Facebook hoàn thành!"
    ))

    print()

    print(yellow(
        "🖼️ Ảnh đã lưu tại:"
    ))

    print(yellow(
        "Download/tool/fbpicture"
    ))

    print(yellow(
        f"📁 File: {os.path.basename(filename)}"
    ))

    time.sleep(3)

def youtube_tiktok_facebook_video():
    os.system("clear")

    print(blue("=" * 48))
    print(blue("       TẢI VIDEO"))
    print(blue("=" * 48))
    print()

    url = ask("🔗 Nhập link: ")

    if (
        "youtube.com" in url.lower()
        or "youtu.be" in url.lower()
    ):
        stop_event, thread = start_loading(
            "❄️ Đang tải video YouTube..."
        )

        try:
            download_youtube(
                url,
                "video"
            )

        except KeyboardInterrupt:
            stop_loading(
                stop_event,
                thread
            )
            raise

        except Exception as e:
            stop_loading(
                stop_event,
                thread
            )

            print(yellow(
                f"❌ Có lỗi xảy ra: {e}"
            ))

            time.sleep(3)
            return

        stop_loading(
            stop_event,
            thread
        )

        print(yellow(
            "❄️ Tải video YouTube hoàn thành!"
        ))

        print(yellow(
            "📁 Download/tool/vds"
        ))

        time.sleep(3)
        return

    if "tiktok.com" in url.lower():
        stop_event, thread = start_loading(
            "❄️ Đang tải video TikTok..."
        )

        try:
            download_tiktok(
                url,
                "video"
            )

        except KeyboardInterrupt:
            stop_loading(
                stop_event,
                thread
            )
            raise

        except Exception as e:
            stop_loading(
                stop_event,
                thread
            )

            print(yellow(
                f"❌ Có lỗi xảy ra: {e}"
            ))

            time.sleep(3)
            return

        stop_loading(
            stop_event,
            thread
        )

        print(yellow(
            "❄️ Tải video TikTok hoàn thành!"
        ))

        print(yellow(
            "📁 Download/tool/musicvd"
        ))

        time.sleep(3)
        return

    if (
        "facebook.com" in url.lower()
        or "fb.watch" in url.lower()
        or "fb.com" in url.lower()
    ):
        stop_event, thread = start_loading(
            "❄️ Đang tải video Facebook..."
        )

        try:
            download_facebook(
                url,
                "video"
            )

        except KeyboardInterrupt:
            stop_loading(
                stop_event,
                thread
            )
            raise

        except Exception as e:
            stop_loading(
                stop_event,
                thread
            )

            print(yellow(
                f"❌ Có lỗi xảy ra: {e}"
            ))

            time.sleep(3)
            return

        stop_loading(
            stop_event,
            thread
        )

        print(yellow(
            "❄️ Tải video Facebook hoàn thành!"
        ))

        print(yellow(
            "📁 Download/tool/fbvds"
        ))

        time.sleep(3)
        return

    print(yellow(
        "❌ Link không được hỗ trợ!"
    ))

    time.sleep(2)

def youtube_tiktok_facebook_music():
    os.system("clear")

    print(blue("=" * 48))
    print(blue("       TẢI NHẠC"))
    print(blue("=" * 48))
    print()

    url = ask("🔗 Nhập link: ")

    if (
        "youtube.com" in url.lower()
        or "youtu.be" in url.lower()
    ):
        stop_event, thread = start_loading(
            "❄️ Đang tải nhạc YouTube..."
        )

        try:
            download_youtube(
                url,
                "music"
            )

        except KeyboardInterrupt:
            stop_loading(
                stop_event,
                thread
            )
            raise

        except Exception as e:
            stop_loading(
                stop_event,
                thread
            )

            print(yellow(
                f"❌ Có lỗi xảy ra: {e}"
            ))

            time.sleep(3)
            return

        stop_loading(
            stop_event,
            thread
        )

        print(yellow(
            "❄️ Tải nhạc YouTube hoàn thành!"
        ))

        print(yellow(
            "📁 Download/tool/musicvd"
        ))

        time.sleep(3)
        return

    if "tiktok.com" in url.lower():
        stop_event, thread = start_loading(
            "❄️ Đang tải nhạc TikTok..."
        )

        try:
            download_tiktok(
                url,
                "music"
            )

        except KeyboardInterrupt:
            stop_loading(
                stop_event,
                thread
            )
            raise

        except Exception as e:
            stop_loading(
                stop_event,
                thread
            )

            print(yellow(
                f"❌ Có lỗi xảy ra: {e}"
            ))

            time.sleep(3)
            return

        stop_loading(
            stop_event,
            thread
        )

        print(yellow(
            "❄️ Tải nhạc TikTok hoàn thành!"
        ))

        print(yellow(
            "📁 Download/tool/musicvd"
        ))

        time.sleep(3)
        return

    if (
        "facebook.com" in url.lower()
        or "fb.watch" in url.lower()
        or "fb.com" in url.lower()
    ):
        stop_event, thread = start_loading(
            "❄️ Đang tải nhạc Facebook..."
        )

        try:
            download_facebook(
                url,
                "music"
            )

        except KeyboardInterrupt:
            stop_loading(
                stop_event,
                thread
            )
            raise

        except Exception as e:
            stop_loading(
                stop_event,
                thread
            )

            print(yellow(
                f"❌ Có lỗi xảy ra: {e}"
            ))

            time.sleep(3)
            return

        stop_loading(
            stop_event,
            thread
        )

        print(yellow(
            "❄️ Tải nhạc Facebook hoàn thành!"
        ))

        print(yellow(
            "📁 Download/tool/musicvd"
        ))

        time.sleep(3)
        return

    print(yellow(
        "❌ Link không được hỗ trợ!"
    ))

    time.sleep(2)

def menu():
    while True:
        os.system("clear")

        print(blue("=" * 55))
        print(blue("     🥶HBACH TOOL - SNAP YTB , TIKTOK , FACEBOOK🥶"))
        print(blue("=" * 55))
        print()

        print(blue(
            "1. 📜Tải video Youtube , Tiktok , Facebook📜"
        ))

        print(blue(
            "2. 📜Tải nhạc Youtube , Tiktok , Facebook 📜"
        ))

        print(blue(
            "3. 🎵 Tải nhạc + hình ảnh Youtube 🎬"
        ))

        print(blue(
            "4. 🖼️ Tải ảnh Facebook 🖼️"
        ))

        print(blue(
            "5. 🖼️ Tải ảnh TikTok 🖼️"
        ))

        print(blue(
            "6. ❌️Thoát❌️"
        ))

        print()

        print(yellow(
            'Ghi "off" để dừng tool'
        ))

        print()

        choice = ask(
            "👉 Chọn chức năng: "
        )

        if choice == "1":
            youtube_tiktok_facebook_video()

        elif choice == "2":
            youtube_tiktok_facebook_music()

        elif choice == "3":
            youtube_music_video()

        elif choice == "4":
            os.system("clear")

            print(blue("=" * 48))
            print(blue("     TẢI ẢNH FACEBOOK"))
            print(blue("=" * 48))
            print()

            url = ask(
                "🔗 Nhập link Facebook ảnh: "
            )

            download_facebook_picture(url)

        elif choice == "5":
            tiktok_picture()

        elif choice == "6":
            os.system("clear")

            print(yellow(
                "👋 Đã thoát!"
            ))

            break

        else:
            print(yellow(
                "❌ Lựa chọn không hợp lệ!"
            ))

            time.sleep(2)

if __name__ == "__main__":
    try:
        menu()

    except KeyboardInterrupt:
        print()
        print(yellow(
            "🛑 Tool đã dừng!"
        ))
        print(yellow(
            "👋 Đã thoát bằng Ctrl + C / OFF."
        ))