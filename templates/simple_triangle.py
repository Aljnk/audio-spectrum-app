import numpy as np,colorsys,math,skia,time,os,sys
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
	n,out_w=len(data),stroke
	ck=(n,spec_color,w,h,out_w,colors[0],colors[1],stroke_style)
	if ck not in _c:
		bg_c=int(colors[0][1:],16)|0xFF000000
		bd_c=int(colors[1][1:],16)|0xFF000000
		buf=np.zeros((h,w,4),dtype=np.uint8)
		info=skia.ImageInfo.Make(w,h,skia.kRGBA_8888_ColorType,skia.kPremul_AlphaType)
		surf=skia.Surface.MakeRasterDirect(info,buf)
		if spec_color=='multi':
			fps=[skia.Paint(Color=skia.Color(int(r*255),int(g*255),int(b*255)),AntiAlias=True,Style=skia.Paint.kFill_Style) for r,g,b in [colorsys.hsv_to_rgb(i/n,0.8,1.0) for i in range(n)]]
		else:
			fps=skia.Paint(Color=int(spec_color[1:],16)|0xFF000000,AntiAlias=True,Style=skia.Paint.kFill_Style)
		bp=None;k_size=0
		if out_w>0:
			bp=skia.Paint(Color=bd_c,Style=skia.Paint.kStrokeAndFill_Style,StrokeWidth=out_w*2,StrokeJoin=skia.Paint.kRound_Join,AntiAlias=True)
			if stroke_style=='gradient':
				k_size=int(out_w*3)|1
				if k_size<3:k_size=3
		_c[ck]={'buf':buf,'surf':surf,'bg_c':bg_c,'fps':fps,'bp':bp,'k_size':k_size}
	cv=_c[ck]
	buf,surf,bg_c,fps,bp,k_size=cv['buf'],cv['surf'],cv['bg_c'],cv['fps'],cv['bp'],cv['k_size']
	if _do_prof:t1=time.perf_counter()
	X,W,rad,rh=8,18,80,192;sl,bh,bs,da=346,8,4,9;cx,cy=w/2,h/2;r_mid=sl*math.sqrt(3)/6;R_tri=sl*math.sqrt(3)/3
	v_pts=[(cx+sl/2,cy+r_mid),(cx,cy-R_tri),(cx-sl/2,cy+r_mid)]
	fill_paths=[skia.Path() for _ in range(n)] if type(fps) is list else skia.Path()
	for i,v in enumerate(data):
		sec,li=i//22,i%22;nb=int(v*rh/12)
		fp=fill_paths[i] if type(fps) is list else fill_paths
		if li<14:
			pos=(li-6.5)*24.7;an=math.radians([90,330,210][sec]);nx,ny=math.cos(an),math.sin(an);tx,ty=ny,-nx
			bx,by=cx+(r_mid+rad)*nx+pos*tx,cy+(r_mid+rad)*ny+pos*ty
			for j in range(nb+1):
				ri,ro=j*12,j*12+8
				pts=[(bx+ri*nx-da*tx,by+ri*ny-da*ty),(bx+ri*nx+da*tx,by+ri*ny+da*ty),(bx+ro*nx+da*tx,by+ro*ny+da*ty),(bx+ro*nx-da*tx,by+ro*ny-da*ty)]
				fp.moveTo(pts[0][0],pts[0][1]);fp.lineTo(pts[1][0],pts[1][1]);fp.lineTo(pts[2][0],pts[2][1]);fp.lineTo(pts[3][0],pts[3][1]);fp.close()
		else:
			ci,ab=v_pts[sec],[90,330,210][sec];ang=math.radians(ab-(li-14+0.5)*15)
			for j in range(nb+1):
				ri,ro=j*12,j*12+8;r_i,r_o=rad+ri,rad+ro;d=(r_i*math.radians(15)-X)/(2*max(1,r_i));a1,a2=ang-d,ang+d
				pts=[(ci[0]+r_i*math.cos(a1),ci[1]+r_i*math.sin(a1)),(ci[0]+r_i*math.cos(a2),ci[1]+r_i*math.sin(a2)),(ci[0]+r_o*math.cos(a2),ci[1]+r_o*math.sin(a2)),(ci[0]+r_o*math.cos(a1),ci[1]+r_o*math.sin(a1))]
				fp.moveTo(pts[0][0],pts[0][1]);fp.lineTo(pts[1][0],pts[1][1]);fp.lineTo(pts[2][0],pts[2][1]);fp.lineTo(pts[3][0],pts[3][1]);fp.close()
	if _do_prof:t2=time.perf_counter()
	with surf as canvas:
		canvas.clear(bg_c)
		if bp:
			if type(fps) is list:
				for i in range(n):canvas.drawPath(fill_paths[i],bp)
			else:
				canvas.drawPath(fill_paths,bp)
			canvas.flush()
		if _do_prof:t3=time.perf_counter()
		if bp and k_size>0 and stroke_style=='gradient' and 'cv2' in sys.modules:
			cv2.GaussianBlur(buf,(k_size,k_size),0,dst=buf)
		if _do_prof:t4=time.perf_counter()
		if type(fps) is list:
			for i in range(n):canvas.drawPath(fill_paths[i],fps[i])
		else:
			canvas.drawPath(fill_paths,fps)
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
	n=len(data);X,W,rad,rh=8,18,80,192;sl,bh,bs,da=346,8,4,9;cx,cy=w/2,h/2;r_mid=sl*math.sqrt(3)/6;R_tri=sl*math.sqrt(3)/3;els=[];pts=[]
	v_pts=[(cx+sl/2,cy+r_mid),(cx,cy-R_tri),(cx-sl/2,cy+r_mid)]
	for i,v in enumerate(data):
		sec,li=i//22,i%22;nb=int(v*rh/12)
		clr=f'rgb({",".join(map(str,[int(c*255) for c in colorsys.hsv_to_rgb(i/n,0.8,1.0)]))})' if spec_color=='multi' else spec_color
		if li<14:
			pos=(li-6.5)*24.7;an=math.radians([90,330,210][sec]);nx,ny=math.cos(an),math.sin(an);tx,ty=ny,-nx
			bx,by=cx+(r_mid+rad)*nx+pos*tx,cy+(r_mid+rad)*ny+pos*ty
			for j in range(nb+1):
				ri,ro=j*12,j*12+8
				p1x,p1y,p2x,p2y,p3x,p3y,p4x,p4y=bx+ri*nx-da*tx,by+ri*ny-da*ty,bx+ri*nx+da*tx,by+ri*ny+da*ty,bx+ro*nx+da*tx,by+ro*ny+da*ty,bx+ro*nx-da*tx,by+ro*ny-da*ty
				p=[(p1x,p1y),(p2x,p2y),(p3x,p3y),(p4x,p4y)];els.append(('p',p,clr));pts.extend(p)
		else:
			ci,ab=v_pts[sec],[90,330,210][sec];ang=math.radians(ab-(li-14+0.5)*15)
			for j in range(nb+1):
				ri,ro=j*12,j*12+8;r_i,r_o=rad+ri,rad+ro;d=(r_i*math.radians(15)-X)/(2*max(1,r_i))
				a1,a2=ang-d,ang+d
				p=[(ci[0]+r_i*math.cos(a1),ci[1]+r_i*math.sin(a1)),(ci[0]+r_i*math.cos(a2),ci[1]+r_i*math.sin(a2)),(ci[0]+r_o*math.cos(a2),ci[1]+r_o*math.sin(a2)),(ci[0]+r_o*math.cos(a1),ci[1]+r_o*math.sin(a1))]
				els.append(('p',p,clr));pts.extend(p)
	x_mi,y_mi=min(p[0] for p in pts)-stroke,min(p[1] for p in pts)-stroke
	x_ma,y_ma=max(p[0] for p in pts)+stroke,max(p[1] for p in pts)+stroke
	sw,sh=x_ma-x_mi,y_ma-y_mi;sd=max(sw,sh);ox,oy=(sd-sw)/2-x_mi,(sd-sh)/2-y_mi
	res=[f'<svg width="{sd:.1f}" height="{sd:.1f}" viewBox="0 0 {sd:.1f} {sd:.1f}" xmlns="http://www.w3.org/2000/svg">']
	if stroke>0 and stroke_style=='gradient':
		res.append(f'<defs><filter id="blur"><feGaussianBlur stdDeviation="{max(1,stroke/3)}"/></filter></defs>')
	if stroke>0:
		filt=' filter="url(#blur)"' if stroke_style=='gradient' else ''
		for e in els:
			p=e[1];res.append(f'<path d="M{p[0][0]+ox:.1f} {p[0][1]+oy:.1f} L{p[1][0]+ox:.1f} {p[1][1]+oy:.1f} L{p[2][0]+ox:.1f} {p[2][1]+oy:.1f} L{p[3][0]+ox:.1f} {p[3][1]+oy:.1f} Z" fill="{colors[1]}" stroke="{colors[1]}" stroke-width="{stroke*2}" stroke-linejoin="round"{filt}/>')
	for e in els:
		p=e[1];res.append(f'<path d="M{p[0][0]+ox:.1f} {p[0][1]+oy:.1f} L{p[1][0]+ox:.1f} {p[1][1]+oy:.1f} L{p[2][0]+ox:.1f} {p[2][1]+oy:.1f} L{p[3][0]+ox:.1f} {p[3][1]+oy:.1f} Z" fill="{e[2]}"/>')
	res.append('</svg>');return "".join(res)