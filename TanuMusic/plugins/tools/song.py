import os
import requests
from pyrogram import Client, filters
from TanuMusic import app

# Function to search for the song on archive.org
def search_archive(song_name):
    query = song_name.replace(" ", "+")
    url = f"https://archive.org/advancedsearch.php?q={query}+AND+mediatype%3Aaudio&fl[]=identifier&fl[]=title&rows=1&output=json"
    response = requests.get(url)
    data = response.json()

    if data['response']['docs']:
        identifier = data['response']['docs'][0]['identifier']
        title = data['response']['docs'][0]['title']
        return identifier, title
    else:
        return None, None

# Function to download the audio file
def download_audio_from_archive(identifier, title):
    meta_url = f"https://archive.org/metadata/{identifier}"
    meta_response = requests.get(meta_url)
    meta_data = meta_response.json()

    for file in meta_data.get("files", []):
        if file.get("format") == "VBR MP3":  # Check for MP3 format
            audio_url = f"https://archive.org/download/{identifier}/{file['name']}"
            response = requests.get(audio_url, stream=True)
            filename = f"{title}.mp3"

            if response.status_code == 200:
                with open(filename, "wb") as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        f.write(chunk)
                return filename
            else:
                return None
    return None

# Handler for /song command
@app.on_message(filters.command("song"))
async def handle_song(client, message):
    # Get the song name after the /song command
    song_name = message.text.split(" ", 1)[1] if len(message.text.split(" ", 1)) > 1 else None

    if not song_name:
        await message.reply("Please provide a song name after the /song command. Example: /song Beethoven Symphony 5")
        return

    identifier, title = search_archive(song_name)

    if identifier:
        filename = download_audio_from_archive(identifier, title)
        if filename:
             # Placeholder for channel name

            # Custom caption
            caption = f"""❖ {title}\n\n● ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ ➥ {message.from_user.mention}\n❖ ᴘᴏᴡᴇʀᴇᴅ ʙʏ ➥ ˹ ᴛᴀɴᴜ ꭙ ᴍᴜsɪᴄ™"""
                
            # Send the audio file with custom caption
            with open(filename, "rb") as audio_file:
                await message.reply_audio(audio_file, caption=caption)
            
            os.remove(filename)  # Remove the file after sending it
        else:
            await message.reply(f"Sorry, I couldn't find a downloadable MP3 file for '{title}'.")
    else:
        await message.reply(f"Sorry, I couldn't find anything for '{song_name}'.")
