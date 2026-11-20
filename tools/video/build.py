# Сборка: webm + озвучка по таймлайну -> MP4 (H.264 + AAC, 30 к/с).
import json, subprocess, os, sys
TMP="/tmp/badm-video"; OUT="/Users/rommil/KATE/бадминтон-приложуха/video/kak-polzovatsya.mp4"
OFFSET=float(sys.argv[1]) if len(sys.argv)>1 else -0.2   # сдвиг звука относительно видео, сек
tl=json.load(open(TMP+"/timeline.json")); os.makedirs(os.path.dirname(OUT),exist_ok=True)
ins=[]; flt=[]
for i,t in enumerate(tl["timeline"]):
    ins+=["-i",f"{TMP}/audio/{t['n']:02d}.wav"]
    ms=int(max(0,(t["start"]+OFFSET))*1000)
    flt.append(f"[{i+1}:a]aresample=44100,aformat=channel_layouts=mono,adelay={ms}[a{i}]")
mix="".join(f"[a{i}]" for i in range(len(tl["timeline"])))
flt.append(f"{mix}amix=inputs={len(tl['timeline'])}:normalize=0,apad[aout]")
subprocess.run(["ffmpeg","-y","-loglevel","error","-i",TMP+"/raw/rec.webm",*ins,"-filter_complex",";".join(flt),
 "-map","0:v","-map","[aout]","-r","30","-c:v","libx264","-preset","medium","-crf","24","-pix_fmt","yuv420p",
 "-c:a","aac","-b:a","128k","-t","%.2f"%tl["total"],"-movflags","+faststart",OUT],check=True)
print(OUT, os.path.getsize(OUT)/1e6,"MB")
