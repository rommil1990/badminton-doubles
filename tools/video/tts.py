# Озвучка: по одному wav на фразу -> /tmp/badm-video/audio/NN.wav + durations.json
import subprocess, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scenario import SCENES
OUT="/tmp/badm-video/audio"; os.makedirs(OUT,exist_ok=True)
durs={}; n=0
for sid,ph in SCENES:
    for text,act in ph:
        f=f"{OUT}/{n:02d}.wav"
        if not os.path.exists(f) or os.path.getmtime(f)<os.path.getmtime(os.path.join(os.path.dirname(os.path.abspath(__file__)),"scenario.py")):
            subprocess.run(["KATE","say",text,"-o",f],check=True,capture_output=True)
        durs[n]=float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f]).decode())
        n+=1
json.dump(durs,open("/tmp/badm-video/durations.json","w"))
print(n,"phrases, speech %.1f s"%sum(durs.values()))
