import numpy as np,colorsys,skia,time,os,sys
try:import cv2
except:pass
_c={}
_prof={'init':0,'loop':0,'stroke':0,'blur':0,'fill':0,'snap':0,'frames':0}
_do_prof='--profile' in sys.argv

def draw_frame(t,data,w,h,stroke,colors,spec_color='multi',key=None,stroke_style='solid'):
	global _prof
	if _do_prof:
		if t==0:_prof={k:0 for k in _prof}
		t0=time.perf_counter()
	n,rw,rh,out_w=len(data),w*0.9,h*0.7,stroke;bw,sx,cy=rw/n,(w-rw)/2,h/2
	ck=(n,spec_color,w,h,out_w,colors[0],colors[1],stroke_style)
	if ck not in _c:
		bg_c=int(colors[0][1:],16)|0xFF000000
		bd_c=int(colors[1][1:],16)|0xFF000000
		buf=np.zeros((h,w,4),dtype=np.uint8)
		info=skia.ImageInfo.Make(w,h,skia.kRGBA_8888_ColorType,skia.kPremul_AlphaType)
		surf=skia.Surface.MakeRasterDirect(info,buf)
		if spec_color=='multi':
			fps=[skia.Paint(Color=skia.Color(int(r*255),int(g*255),int(b*255)),AntiAlias=True,Style=skia.Paint.kFill_Style) for r,g,b in [colorsys.hsv_to_rgb(i/n,0.9,1.0) for i in range(n)]]
		else:
			fps=skia.Paint(Color=int(spec_color[1:],16)|0xFF000000,AntiAlias=True,Style=skia.Paint.kFill_Style)
		bp=None;k_size=0
		if out_w>0:
			if stroke_style=='gradient':
				bp=skia.Paint(Color=bd_c,Style=skia.Paint.kStrokeAndFill_Style,StrokeWidth=out_w*2,StrokeJoin=skia.Paint.kRound_Join,AntiAlias=True)
				k_size=int(out_w*3)|1
				if k_size<3:k_size=3
			else:
				bp=skia.Paint(Color=bd_c,Style=skia.Paint.kStroke_Style,StrokeWidth=out_w*2,AntiAlias=True)
		_c[ck]={'buf':buf,'surf':surf,'bg_c':bg_c,'fps':fps,'bp':bp,'k_size':k_size}
	cv=_c[ck]
	buf,surf,bg_c,fps,bp,k_size=cv['buf'],cv['surf'],cv['bg_c'],cv['fps'],cv['bp'],cv['k_size']
	if _do_prof:t1=time.perf_counter()
	with surf as canvas:
		canvas.clear(bg_c)
		path=skia.Path()
		rects=[]
		for i,v in enumerate(data):
			bh=max(2,v*rh);x=sx+i*bw;lw=max(1,int(bw*0.7))
			rr=skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(x-lw/2,cy-bh/2,x+lw/2,cy+bh/2),4,4)
			path.addRRect(rr)
			if type(fps) is list:rects.append((rr,i))
		if _do_prof:t2=time.perf_counter()
		if bp:
			canvas.drawPath(path,bp)
			canvas.flush()
		if _do_prof:t3=time.perf_counter()
		if bp and k_size>0 and stroke_style=='gradient' and 'cv2' in sys.modules:
			cv2.GaussianBlur(buf,(k_size,k_size),0,dst=buf)
		if _do_prof:t4=time.perf_counter()
		if type(fps) is list:
			for rr,i in rects:canvas.drawRRect(rr,fps[i])
		else:
			canvas.drawPath(path,fps)
		if _do_prof:t5=time.perf_counter()
	res=buf[:,:,:3]
	if _do_prof:
		t6=time.perf_counter()
		_prof['init']+=t1-t0;_prof['loop']+=t2-t1;_prof['stroke']+=t3-t2;_prof['blur']+=t4-t3;_prof['fill']+=t5-t4;_prof['snap']+=t6-t5;_prof['frames']+=1
		if _prof['frames']%20==0:
			try:
				tmpl_n=__name__.split('.')[-1];spec_c=str(spec_color).replace('#','')
				log_f=f"prof_{tmpl_n}_st{stroke}_{stroke_style}_{spec_c}.log"
				with open(os.path.join(os.environ.get("APPDATA",""),"Aljnk","AudioSpectrum","temp",log_f),"w") as f:
					f.write(f"DRAW PROFILING {tmpl_n} (Frames: {_prof['frames']})\n")
					for k,v in _prof.items():
						if k!='frames':f.write(f"{k}: {v:.4f}s (Avg: {v/_prof['frames']:.4f}s)\n")
			except:pass
	return res

def draw_svg(t,data,w,h,stroke,colors,spec_color='multi',stroke_style='gradient'):
	n,rw,rh,out_w=len(data),w*0.9,h*0.7,stroke;bw,sx,cy=rw/n,(w-rw)/2,h/2;ls=[]
	for i,v in enumerate(data):
		if spec_color=='multi':
			hue,bh=i/n,max(2,v*rh);rgb=colorsys.hsv_to_rgb(hue,0.9,1.0);c=f'rgb({int(rgb[0]*255)},{int(rgb[1]*255)},{int(rgb[2]*255)})'
		else:
			bh=max(2,v*rh);c=spec_color
		x,lw=sx+i*bw,max(1,int(bw*0.7));ls.append((x-lw/2,cy-bh/2,lw,bh,c))
	x_min=min(l[0]-out_w*2 for l in ls);x_max=max(l[0]+l[2]+out_w*2 for l in ls)
	y_min=min(l[1]-out_w*2 for l in ls);y_max=max(l[1]+l[3]+out_w*2 for l in ls)
	sw,sh=x_max-x_min,y_max-y_min;side=max(sw,sh);ox,oy=(side-sw)/2-x_min,(side-sh)/2-y_min
	res=[f'<svg width="{side}" height="{side}" viewBox="0 0 {side} {side}" xmlns="http://www.w3.org/2000/svg">']
	if out_w>0 and stroke_style=='gradient':
		res.append(f'<defs><filter id="blur"><feGaussianBlur stdDeviation="{max(1,out_w/3)}"/></filter></defs>')
	for l in ls:
		rx=4
		if out_w>0:
			if stroke_style=='gradient':res.append(f'<rect x="{l[0]+ox}" y="{l[1]+oy}" width="{l[2]}" height="{l[3]}" rx="{rx}" fill="{colors[1]}" stroke="{colors[1]}" stroke-width="{out_w*2}" filter="url(#blur)"/>')
			else:res.append(f'<rect x="{l[0]+ox}" y="{l[1]+oy}" width="{l[2]}" height="{l[3]}" rx="{rx}" fill="{colors[1]}" stroke="{colors[1]}" stroke-width="{out_w*2}"/>')
		res.append(f'<rect x="{l[0]+ox}" y="{l[1]+oy}" width="{l[2]}" height="{l[3]}" rx="{rx}" fill="{l[4]}"/>')
	res.append('</svg>');return "".join(res)