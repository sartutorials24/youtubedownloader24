import os
import pytube
import streamlit as st
from pytube import YouTube
from datetime import timedelta
import humanize
from io import BytesIO

# App Config
st.set_page_config(page_title="🎬 YouTube Advanced Downloader", page_icon="📥", layout="centered")

# Custom CSS for UI polish
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

# Header
st.title("🎬 YouTube Advanced Downloader")
st.markdown("**Download YouTube Videos or Audio in High Quality — Instantly!**")

# Input field
url = st.text_input("🔗 Enter YouTube Video URL:")

if url:
    try:
        yt = YouTube(url)
        st.video(url)

        st.subheader("📊 Video Information")
        st.write(f"**🎬 Title:** {yt.title}")
        st.write(f"**📺 Channel:** {yt.author}")
        st.write(f"**👁 Views:** {humanize.intcomma(yt.views)}")
        st.write(f"**⏱ Duration:** {timedelta(seconds=yt.length)}")
        st.write(f"**📅 Published:** {yt.publish_date.strftime('%Y-%m-%d')}")

        st.markdown("---")
        st.subheader("⚙️ Choose Download Options")

        download_type = st.radio("Select download type:", ["🎥 Video", "🎵 Audio Only"])
        
        if download_type == "🎥 Video":
            streams = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc()
            resolutions = [f"{s.resolution} - {round(s.filesize / 1024 / 1024, 2)} MB" for s in streams]
            selected = st.selectbox("Select resolution:", resolutions)
            stream = streams[resolutions.index(selected)]
        else:
            streams = yt.streams.filter(only_audio=True)
            audio_streams = [f"{round(s.filesize / 1024 / 1024, 2)} MB (Audio)" for s in streams]
            selected = st.selectbox("Select audio quality:", audio_streams)
            stream = streams[audio_streams.index(selected)]

        st.markdown("---")

        if st.button("📥 Download Now"):
            with st.spinner("Downloading... Please wait ⏳"):
                buffer = BytesIO()
                stream.stream_to_buffer(buffer)
                buffer.seek(0)
                file_extension = "mp4" if download_type == "🎥 Video" else "mp3"
                file_name = f"{yt.title[:50]}.{file_extension}"

                st.success("✅ Download Complete!")
                st.download_button(
                    label="⬇️ Click here to save file",
                    data=buffer,
                    file_name=file_name,
                    mime="video/mp4" if download_type == "🎥 Video" else "audio/mp3"
                )

    except Exception as e:
        st.error(f"❌ Error: {e}")

else:
    st.info("👆 Paste a YouTube URL to begin.")
