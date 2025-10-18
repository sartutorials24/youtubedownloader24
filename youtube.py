import os
import json
from io import BytesIO
from datetime import timedelta

import streamlit as st
from pytube import YouTube
import humanize

# App Config
st.set_page_config(
    page_title="🎬 YouTube Advanced Downloader",
    page_icon="📥",
    layout="centered",
)

# Custom CSS for better UI
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
        .css-1d391kg p {
            color: white !important;
        }
    </style>
""", unsafe_allow_html=True)

# ---- INTERNAL PYTUBE API ----
def pytube_api(url: str):
    """
    Acts like a lightweight internal YouTube API using pytube.
    Fetches metadata, available streams, and stats.
    """
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


# ---- STREAMLIT UI ----
st.title("🎬 YouTube Advanced Downloader")
st.markdown("**Download YouTube Videos or Audio in High Quality — Instantly!**")

url = st.text_input("🔗 Enter YouTube Video URL:")

if url:
    api_data = pytube_api(url)

    if "error" in api_data:
        st.error(f"❌ Error: {api_data['error']}")
    else:
        # Show thumbnail preview
        st.image(api_data["thumbnail"], use_container_width=True)

        # Show video info
        st.subheader("📊 Video Information")
        st.write(f"**🎬 Title:** {api_data['title']}")
        st.write(f"**📺 Channel:** {api_data['author']}")
        st.write(f"**👁 Views:** {humanize.intcomma(api_data['views'])}")
        st.write(f"**⏱ Duration:** {timedelta(seconds=api_data['length'])}")
        st.write(f"**📅 Published:** {api_data['publish_date']}")
        st.markdown("---")

        # Select mode
        mode = st.radio("⚙️ Choose download type:", ["🎥 Video", "🎵 Audio Only"])

        # Handle selection
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

        # Download button
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
                    label="⬇️ Click here to save file",
                    data=buffer,
                    file_name=file_name,
                    mime="video/mp4"
                    if mode == "🎥 Video"
                    else "audio/mp3",
                )
            except Exception as e:
                st.error(f"❌ Download failed: {e}")

else:
    st.info("👆 Paste a YouTube URL to begin.")
