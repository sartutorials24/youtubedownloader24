import os
import json
from io import BytesIO
from datetime import timedelta

import streamlit as st
from pytube import YouTube
import humanize

# -------------------------------
# STREAMLIT CONFIG
# -------------------------------
st.set_page_config(
    page_title="🎬 YouTube Advanced Downloader",
    page_icon="📥",
    layout="centered",
)

# -------------------------------
# CUSTOM CSS
# -------------------------------
st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
            color: white;
        }
        h1, h2, h3 {
            color: #00ffff !important;
            text-align: center;
        }
        .stButton>button {
            background: #00adb5;
            color: white;
            border-radius: 8px;
            border: none;
            padding: 10px 20px;
            transition: 0.3s;
        }
        .stButton>button:hover {
            background: #00ffff;
            color: black;
        }
        .stRadio > div {
            flex-direction: row;
        }
        .css-1d391kg p {
            color: white !important;
        }
        .api-box {
            background-color: #0f3057;
            padding: 10px;
            border-radius: 10px;
            margin-top: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# -------------------------------
# INTERNAL PYTUBE API WRAPPER
# -------------------------------
def pytube_api(url: str):
    """Lightweight internal YouTube API using pytube."""
    try:
        yt = YouTube(url)
        data = {
            "title": yt.title,
            "author": yt.author,
            "views": yt.views,
            "length": yt.length,
            "publish_date": yt.publish_date.strftime('%Y-%m-%d'),
            "thumbnail": yt.thumbnail_url,
            "video_streams": [
                {
                    "itag": s.itag,
                    "resolution": s.resolution,
                    "mime_type": s.mime_type,
                    "size": round(s.filesize / 1024 / 1024, 2)
                }
                for s in yt.streams.filter(progressive=True, file_extension='mp4').order_by("resolution").desc()
            ],
            "audio_streams": [
                {
                    "itag": s.itag,
                    "abr": s.abr,
                    "mime_type": s.mime_type,
                    "size": round(s.filesize / 1024 / 1024, 2)
                }
                for s in yt.streams.filter(only_audio=True)
            ]
        }
        return data
    except Exception as e:
        return {"error": str(e)}


# -------------------------------
# SIMPLE REST API ENDPOINT (local)
# -------------------------------
# You can hit this from a browser or bot:
# e.g. http://localhost:8501/api/video-info?url=https://youtube.com/watch?v=xxxx
query_params = st.query_params
if "api/video-info" in query_params.get("path", "") or st.query_params.get("api") == "video-info":
    url = query_params.get("url", "")
    if not url:
        st.json({"error": "Missing YouTube URL parameter (?url=...)"})
    else:
        st.json(pytube_api(url))
    st.stop()

# -------------------------------
# STREAMLIT UI
# -------------------------------
st.title("🎬 YouTube Advanced Downloader")
st.markdown("**Download YouTube Videos or Audio in High Quality — Instantly!**")

url = st.text_input("🔗 Enter YouTube Video URL:")

if url:
    api_data = pytube_api(url)

    if "error" in api_data:
        st.error(f"❌ Error: {api_data['error']}")
    else:
        # Show video preview & info
        st.image(api_data["thumbnail"], use_container_width=True)

        st.subheader("📊 Video Information")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**🎬 Title:** {api_data['title']}")
            st.write(f"**📺 Channel:** {api_data['author']}")
        with col2:
            st.write(f"**👁 Views:** {humanize.intcomma(api_data['views'])}")
            st.write(f"**📅 Published:** {api_data['publish_date']}")

        st.write(f"**⏱ Duration:** {timedelta(seconds=api_data['length'])}")
        st.markdown("---")

        # Mode selection
        mode = st.radio("⚙️ Choose download type:", ["🎥 Video", "🎵 Audio Only"], horizontal=True)

        if mode == "🎥 Video":
            options = [
                f"{s['resolution']} - {s['size']} MB"
                for s in api_data["video_streams"]
            ]
            selected = st.selectbox("Select video quality:", options)
            selected_stream = api_data["video_streams"][options.index(selected)]
        else:
            options = [
                f"{s['abr']} - {s['size']} MB"
                for s in api_data["audio_streams"]
            ]
            selected = st.selectbox("Select audio quality:", options)
            selected_stream = api_data["audio_streams"][options.index(selected)]

        # Download section
        if st.button("📥 Download Now"):
            try:
                yt = YouTube(url)
                stream = yt.streams.get_by_itag(selected_stream["itag"])
                buffer = BytesIO()
                stream.stream_to_buffer(buffer)
                buffer.seek(0)

                file_name = (
                    f"{api_data['title'][:50]}.mp4"
                    if mode == "🎥 Video"
                    else f"{api_data['title'][:50]}.mp3"
                )

                st.success("✅ Download complete!")
                st.download_button(
                    label="⬇️ Click to save file",
                    data=buffer,
                    file_name=file_name,
                    mime="video/mp4" if mode == "🎥 Video" else "audio/mp3",
                )
            except Exception as e:
                st.error(f"❌ Download failed: {e}")

        # REST API info display
        st.markdown("---")
        st.markdown("### 🧠 Local API Endpoint")
        st.markdown("You can fetch video info using this internal endpoint:")
        st.code(
            f"http://localhost:8501/api/video-info?url={url}",
            language="bash",
        )

else:
    st.info("👆 Paste a YouTube URL to begin.")
