from bs4 import BeautifulSoup

# Load the saved HTML file
with open("../course_135.html", "r", encoding="utf-8") as f:
    html_content = f.read()

soup = BeautifulSoup(html_content, "html.parser")

# Look for video file links (e.g., MP4)
video_links = [a["href"] for a in soup.find_all("a", href=True) if ".mp4" in a["href"] or ".webm" in a["href"]]

# Look for embedded videos (iframe sources)
iframe_sources = [iframe["src"] for iframe in soup.find_all("iframe", src=True)]

# Print the extracted video links
print("Direct Video Links:", video_links)
print("Embedded Video Sources:", iframe_sources)
