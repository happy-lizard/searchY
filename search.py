import os
import time
import subprocess
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup

def extract_video_id(href):
    # Extract the video ID until the semicolon
    return href.split('=', 1)[-1].split('&', 1)[0]

def extract_playlist_id(href):
    # Extract the playlist ID after "list="
    return href.split('list=', 1)[-1]

def download_or_stream(url):
    choice = input("Would you like to download or stream? (dl/s): ").lower()

    if choice == 'dl':
        # Open a new terminal window and run "yt-dlp" with the corresponding URL
        subprocess.run(['gnome-terminal', '--', 'yt-dlp', url])
    elif choice == 's':
        # Open a new terminal window and run "mpv" with the corresponding URL
        subprocess.run(['gnome-terminal', '--', 'mpv', url])
    else:
        print("Invalid choice. Exiting...")

def search_and_display():
    # Replace spaces with +
    query = input("Enter search query: ").replace(" ", "+")

    # Set Firefox to run in headless mode
    firefox_options = Options()
    firefox_options.add_argument('--headless')

    # Open the URL with Firefox using Selenium
    driver = webdriver.Firefox(options=firefox_options)
    driver.get(f"https://www.youtube.com/results?search_query={query}")

    # Wait for a few seconds to load the page
    time.sleep(5)

    # Get the page source
    page_source = driver.page_source

    # Close the browser window
    driver.quit()

    # Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(page_source, 'html.parser')

    # Find all the video entries with the specified structure
    video_entries = soup.find_all('ytd-video-renderer', class_='style-scope ytd-item-section-renderer')

    # Display the title and channel name of each video entry
    for index, entry in enumerate(video_entries, start=1):
        title_element = entry.find('a', id='video-title', class_='yt-simple-endpoint style-scope ytd-video-renderer')
        channel_element = entry.find('div', id='channel-info').find('a', class_='yt-simple-endpoint style-scope yt-formatted-string')

        if title_element and channel_element:
            title = title_element.get('title', 'Title not found')
            channel_name = channel_element.text
            print(f"{index}. Video Title: {title} by {channel_name}")

    # Print a separator line
    print("\n--- Playlists ---\n")

    # Find all the playlist entries with the specified structure
    playlist_entries = soup.find_all('ytd-playlist-renderer', class_='style-scope ytd-item-section-renderer')

    # Display the title of each playlist entry (without channel name)
    for index, entry in enumerate(playlist_entries, start=len(video_entries) + 1):
        playlist_thumbnail = entry.find('ytd-playlist-thumbnail', class_='style-scope ytd-playlist-renderer')
        content_element = entry.find('div', id='content', class_='style-scope ytd-playlist-renderer')

        if playlist_thumbnail and content_element:
            playlist_thumbnail_href = playlist_thumbnail.find('a').get('href', '')
            title_element = content_element.find('h3', class_='style-scope ytd-playlist-renderer').find('span', id='video-title', class_='style-scope ytd-playlist-renderer')

            if title_element:
                title = title_element.text.strip()
                print(f"{index}. Playlist Title: {title}")

    # Allow the user to select an entry
    selected_index = int(input("Select an entry (enter the corresponding number): ")) - 1

    # Check if the selected entry is a video or a playlist
    if selected_index < len(video_entries):
        selected_entry = video_entries[selected_index]
        title_element = selected_entry.find('a', id='video-title', class_='yt-simple-endpoint style-scope ytd-video-renderer')
        href = title_element.get('href', '')

        # Extract the video ID from the selected video entry
        video_id = extract_video_id(href)

        # Combine with the YouTube URL
        youtube_url = f"https://www.youtube.com/watch?v={video_id}"
    else:
        selected_entry = playlist_entries[selected_index - len(video_entries)]
        playlist_thumbnail = selected_entry.find('ytd-playlist-thumbnail', class_='style-scope ytd-playlist-renderer')
        playlist_thumbnail_href = playlist_thumbnail.find('a').get('href', '')

        # Extract the playlist ID from the selected playlist entry
        playlist_id = extract_playlist_id(playlist_thumbnail_href)

        # Combine with the YouTube Playlist URL
        youtube_url = f"https://www.youtube.com/playlist?list={playlist_id}"

    # Download or stream the selected video/playlist
    download_or_stream(youtube_url)

if __name__ == "__main__":
    print("Scanning and displaying initial videos and playlists...")
    search_and_display()
