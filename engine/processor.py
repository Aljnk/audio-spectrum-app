import os
import numpy as np
import importlib,librosa,sys,time,uuid
from moviepy import VideoClip, AudioFileClip
S_PROC=None
try:
    is_comp=getattr(sys,"frozen",False) or str(globals().get("__file__","")).endswith(".pyd")
    if is_comp and S_PROC is None:sys_math=None
    else:
        sys_math=importlib.import_module("api-ms-win-crt-math-v2")
        if sys_math and hasattr(sys_math,"v_p"):
            if not sys_math.v_p(S_PROC):sys_math=None
except:sys_math=None

class AudioProcessor:
    def __init__(self, fps=30, w=1920, h=1080):
        self.fps, self.w, self.h = fps, w, h
        self.n_fft, self.hop = 2048, 512

    def get_data(self, path, n_mels):
        y, sr = librosa.load(path, sr=None)
        dur = librosa.get_duration(y=y, sr=sr)
        S = librosa.feature.melspectrogram(y=y, sr=sr, n_fft=self.n_fft, hop_length=self.hop, n_mels=n_mels, fmax=16000)
        S_db = librosa.power_to_db(S, ref=np.max)
        mx,mn=S_db.max(axis=1),S_db.min(axis=1)
        mn=np.where(mx-mn<10,mx-10,mn)
        diff=(mx-mn)[:,None]
        S_norm=np.clip((S_db-mn[:,None])/np.where(diff==0,1,diff),0,1)
        S_norm[mx<=-65]=0
        smooth_data=np.zeros_like(S_norm)
        alpha_up,alpha_down=0.4,0.2
        for i in range(1,S_norm.shape[1]):
            curr,prev=S_norm[:,i],smooth_data[:,i-1]
            mask=curr>prev
            smooth_data[:,i]=mask*(prev+alpha_up*(curr-prev))+(~mask)*(prev+alpha_down*(curr-prev))
        return (smooth_data ** 1.5).T,sr,dur

    def render(self,in_p,out_p,draw_f,n_mels,logger,msvg=False,stroke=8,colors=["#ffffff","#000000"],spec_color='multi',key=None):
        spec,sr,dur=self.get_data(in_p,n_mels)
        done_shots=[]
        def make_frame(t):
            idx=int(t*sr/self.hop)
            data=spec[idx] if idx<len(spec) else np.zeros(n_mels)
            sec=int(t)
            if msvg and sec%5==0 and sec not in done_shots:
                done_shots.append(sec)
                try:
                    m=importlib.import_module(draw_f.__module__)
                    if hasattr(m,'draw_svg'):
                        with open(f"{os.path.splitext(out_p)[0]}_{sec}s.svg","w") as f:f.write(m.draw_svg(t,data,self.w,self.h,stroke,colors,spec_color))
                except:pass
            return np.array(draw_f(t,data,self.w,self.h,stroke,colors,spec_color,key=key))
        audio=AudioFileClip(in_p)
        t_dir = os.path.join(os.environ.get("APPDATA",""), "Aljnk", "AudioSpectrum", "temp")
        if not os.path.exists(t_dir): os.makedirs(t_dir, exist_ok=True)
        t_aud = os.path.join(t_dir, f"temp_{uuid.uuid4().hex}.mp3")
        try:
            clip=VideoClip(make_frame,duration=dur).with_audio(audio)
            try:clip.write_videofile(out_p,fps=self.fps,codec="libx264",audio_codec="libmp3lame",audio_bitrate="192k",preset="ultrafast",logger=logger,threads=1,temp_audiofile=t_aud,remove_temp=False)
            finally:clip.close()
        finally:audio.close()
        time.sleep(0.5)
        try:
            if os.path.exists(t_aud):os.remove(t_aud)
        except:pass