# Language-dependent paths. VIDEO_LANG=ru|en (default ru).
import os
LANG=os.environ.get("VIDEO_LANG","ru")
if LANG not in ("ru","en"): raise SystemExit("VIDEO_LANG must be ru or en")
TMP="/tmp/badm-video" if LANG=="ru" else "/tmp/badm-video-en"
VIDEO_DIR="/Users/rommil/KATE/бадминтон-приложуха/video"
OUT=VIDEO_DIR+("/kak-polzovatsya.mp4" if LANG=="ru" else "/how-to-use-en.mp4")
