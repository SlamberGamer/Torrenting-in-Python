import asyncio
import urllib.parse
import base64
import aiohttp
import libtorrent as lt
import time

def parse_magnet_link(magnet_uri):
    parsed = urllib.parse.urlparse(magnet_uri)
    query = urllib.parse.parse_qs(parsed.query)

    info_hash_raw = query["xt"][0][9:]  # Extract infohash and remove "urn:btih:"
    if len(info_hash_raw) == 32:  # base32-encoded infohash
        info_hash = base64.b32decode(info_hash_raw).hex()
    else:
        info_hash = info_hash_raw

    trackers = query.get("tr", [])

    return info_hash, trackers

async def display_seed_leech(magnet_uri):
    info_hash, trackers = parse_magnet_link(magnet_uri)
    async with aiohttp.ClientSession() as session:
        for tracker in trackers:
            try:
                seeders, leechers = await get_seed_leech(session, info_hash, tracker)
                print(f"Tracker: {tracker}")
                print(f"Seeders: {seeders}, Leechers: {leechers}")
            except Exception as e:
                print(f"Failed to fetch seed and leech count from {tracker}: {e}")

async def get_seed_leech(session, info_hash, tracker):
    url = f"{tracker}announce?info_hash={info_hash}&peer_id=ABCDEFGHIJKLMNOPQRST&left=0"
    async with session.get(url) as response:
        if response.status != 200:
            raise Exception(f"HTTP error: {response.status}")

        content = await response.text()
        seeders = content.count("seeder")
        leechers = content.count("leecher")

        return seeders, leechers

def download_torrent(magnet_link, save_path='./'):
    ses = lt.session()
    info = lt.parse_magnet_uri(magnet_link)
    info["save_path"] = save_path
    h = ses.add_torrent(info)

    print("Starting download...")
    while not h.is_seed():
        s = h.status()
        progress = s.progress * 100
        print(f"Progress: {progress:.2f}%")
        time.sleep(1)

    print("Download complete!")

magnet_link = "_magnet link"
save_path = "path/to/save/files"

# Display seeders and leechers count
asyncio.run(display_seed_leech(magnet_link))

# Download the torrent
download_torrent(magnet_link, save_path)
