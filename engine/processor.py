import os,time,numpy as np,importlib,librosa,sys,uuid,hashlib,subprocess
S_PROC=None
_do_prof='--profile-proc' in sys.argv
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
		if _do_prof:t0=time.perf_counter()
		t_dir=os.path.join(os.environ.get("APPDATA",""),"Aljnk","AudioSpectrum","temp")
		if not os.path.exists(t_dir):os.makedirs(t_dir,exist_ok=True)
		log_p=os.path.join(t_dir,"processor_profiling.log")
		c_p=os.path.join(t_dir,f"cache_{hashlib.md5(f'{path}_{n_mels}'.encode()).hexdigest()}.npz")
		l_p=f"{c_p}.lock"
		def _try_read():
			if not os.path.exists(c_p):return False
			try:
				with np.load(c_p) as d:return d['spec'],d['sr'].item(),d['dur'].item()
			except:return False
		data=_try_read()
		if data:
			if _do_prof:
				with open(log_p,"a") as f:f.write(f"CACHE LOAD [{os.path.basename(path)}]: {time.perf_counter()-t0:.4f}s\n")
			return data
		w=0
		while w<600:
			try:
				fd=os.open(l_p,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
				os.close(fd);break
			except:
				data=_try_read()
				if data:
					if _do_prof:
						with open(log_p,"a") as f:f.write(f"CACHE WAIT [{os.path.basename(path)}]: {time.perf_counter()-t0:.4f}s\n")
					return data
				time.sleep(0.1);w+=1
		try:
			if _do_prof:t1=time.perf_counter()
			y, sr = librosa.load(path, sr=None)
			dur = librosa.get_duration(y=y, sr=sr)
			if _do_prof:t2=time.perf_counter()
			S = librosa.feature.melspectrogram(y=y, sr=sr, n_fft=self.n_fft, hop_length=self.hop, n_mels=n_mels, fmax=16000)
			S_db = librosa.power_to_db(S, ref=np.max)
			if _do_prof:t3=time.perf_counter()
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
			res=(smooth_data ** 1.5).T
			if _do_prof:t4=time.perf_counter()
			t_c_p=f"{c_p}.{uuid.uuid4().hex}.tmp.npz"
			np.savez(t_c_p,spec=res,sr=sr,dur=dur)
			try:os.replace(t_c_p,c_p)
			except:pass
			if _do_prof:
				t5=time.perf_counter()
				with open(log_p,"a") as f:f.write(f"AUDIO PARSE [{os.path.basename(path)}]: Load={t2-t1:.4f}s, Mel={t3-t2:.4f}s, Math={t4-t3:.4f}s, Save={t5-t4:.4f}s, Total={t5-t0:.4f}s\n")
		finally:
			if os.path.exists(l_p):
				try:os.remove(l_p)
				except:pass
			if 't_c_p' in locals() and os.path.exists(t_c_p):
				try:os.remove(t_c_p)
				except:pass
		return res,sr,dur
	def render(self,in_p,out_p,draw_f,n_mels,logger,msvg=False,stroke=8,colors=["#ffffff","#000000"],spec_color='multi',key=None,stroke_style='solid'):
		if _do_prof:t0=time.perf_counter()
		spec,sr,dur=self.get_data(in_p,n_mels)
		if _do_prof:t1=time.perf_counter()
		done_shots=[]
		total_frames=int(dur*self.fps)
		f_p=os.path.join(os.path.dirname(os.path.abspath(__file__)),'ffmpeg.exe')
		cmd=[f_p,'-y','-f','rawvideo','-vcodec','rawvideo','-s',f'{self.w}x{self.h}','-pix_fmt','rgb24','-r',str(self.fps),'-i','-','-i',in_p,'-c:v','libx264','-preset','ultrafast','-c:a','libmp3lame','-b:a','192k','-map','0:v:0','-map','1:a:0','-shortest',out_p]
		proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.DEVNULL,stdout=subprocess.DEVNULL,creationflags=subprocess.CREATE_NO_WINDOW)
		if _do_prof:t2=time.perf_counter();tdraw,tpipe,tsvg=0,0,0
		try:
			for i in range(total_frames):
				t=i/self.fps
				idx=int(t*sr/self.hop)
				data=spec[idx] if idx<len(spec) else np.zeros(n_mels)
				sec=int(t)
				if msvg and sec%5==0 and sec not in done_shots:
					if _do_prof:ts1=time.perf_counter()
					done_shots.append(sec)
					try:
						m=importlib.import_module(draw_f.__module__)
						if hasattr(m,'draw_svg'):
							with open(f"{os.path.splitext(out_p)[0]}_{sec}s.svg","w") as f:f.write(m.draw_svg(t,data,self.w,self.h,stroke,colors,spec_color,stroke_style=stroke_style))
					except:pass
					if _do_prof:tsvg+=time.perf_counter()-ts1
				if _do_prof:td1=time.perf_counter()
				frame=np.array(draw_f(t,data,self.w,self.h,stroke,colors,spec_color,key=key,stroke_style=stroke_style))
				if _do_prof:td2=time.perf_counter()
				proc.stdin.write(frame.tobytes())
				if _do_prof:
					td3=time.perf_counter()
					tdraw+=(td2-td1);tpipe+=(td3-td2)
				if logger:logger(i,total_frames)
		finally:
			if _do_prof:t3=time.perf_counter()
			proc.stdin.close()
			proc.wait()
			if _do_prof:
				t4=time.perf_counter()
				t_dir=os.path.join(os.environ.get("APPDATA",""),"Aljnk","AudioSpectrum","temp")
				log_p=os.path.join(t_dir,"processor_profiling.log")
				with open(log_p,"a") as f:
					f.write(f"RENDER [{os.path.basename(out_p)}]: Total frames: {total_frames}\n")
					f.write(f"  Init/Data: {t1-t0:.4f}s\n")
					f.write(f"  FFmpeg Setup: {t2-t1:.4f}s\n")
					f.write(f"  Draw Total: {tdraw:.4f}s (Avg: {tdraw/total_frames if total_frames else 0:.4f}s/frame)\n")
					f.write(f"  Pipe Write Total: {tpipe:.4f}s (Avg: {tpipe/total_frames if total_frames else 0:.4f}s/frame)\n")
					if msvg:f.write(f"  SVG Total: {tsvg:.4f}s\n")
					f.write(f"  FFmpeg Finalize: {t4-t3:.4f}s\n")
					f.write(f"  TOTAL RENDER LOOP: {t4-t0:.4f}s\n--------------------------------\n")