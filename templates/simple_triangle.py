import numpy as np,colorsys,math
from PIL import Image,ImageDraw
def draw_frame(t,data,w,h,stroke,colors,spec_color='multi',key=None):
	try:
		img=Image.new('RGB',(w,h),colors[0]);draw=ImageDraw.Draw(img);n=len(data);X,W,rad,rh=8,18,80,192
		sl,bh,bs,da=346,8,4,9;cx,cy=w/2,h/2;r_mid=sl*math.sqrt(3)/6;R_tri=sl*math.sqrt(3)/3;bars=[]
		v_pts=[(cx+sl/2,cy+r_mid),(cx,cy-R_tri),(cx-sl/2,cy+r_mid)]
		for i,v_d in enumerate(data):
			sec,li=i//22,i%22;nb=int(v_d*rh/12)
			clr=(int(rgb[0]*255),int(rgb[1]*255),int(rgb[2]*255)) if spec_color=='multi' and (rgb:=colorsys.hsv_to_rgb(i/n,0.8,1.0)) else (int(spec_color[1:3],16),int(spec_color[3:5],16),int(spec_color[5:7],16))
			if li<14:
				pos=(li-6.5)*24.7;an=math.radians([90,330,210][sec]);nx,ny=math.cos(an),math.sin(an);tx,ty=ny,-nx
				bx,by=cx+(r_mid+rad)*nx+pos*tx,cy+(r_mid+rad)*ny+pos*ty;bars.append(('s',nb,clr,(bx,by,nx,ny,tx,ty)))
			else:
				ci,ab=v_pts[sec],[90,330,210][sec];ang=math.radians(ab-(li-14+0.5)*15);bars.append(('c',nb,clr,(ci,ang)))
		for typ,nb,clr,p in bars:
			for j in range(nb+1):
				ri,ro=j*12,j*12+8
				if typ=='s':
					bx,by,nx,ny,tx,ty=p;d,r1,r2=da+stroke,ri-stroke,ro+stroke
					pts=[(bx+r1*nx-d*tx,by+r1*ny-d*ty),(bx+r1*nx+d*tx,by+r1*ny+d*ty),(bx+r2*nx+d*tx,by+r2*ny+d*ty),(bx+r2*nx-d*tx,by+r2*ny-d*ty)]
					draw.polygon(pts,fill=colors[1])
				else:
					(acx,acy),ang=p;r_i,r_o=rad+ri,rad+ro;d=(r_i*math.radians(15)-X)/(2*max(1,r_i));dd=d+stroke/max(1,r_i)
					a1,a2=ang-dd,ang+dd;draw.polygon([(acx+(r_i-stroke)*math.cos(a1),acy+(r_i-stroke)*math.sin(a1)),(acx+(r_i-stroke)*math.cos(a2),acy+(r_i-stroke)*math.sin(a2)),(acx+(r_o+stroke)*math.cos(a2),acy+(r_o+stroke)*math.sin(a2)),(acx+(r_o+stroke)*math.cos(a1),acy+(r_o+stroke)*math.sin(a1))],fill=colors[1])
		for typ,nb,clr,p in bars:
			for j in range(nb+1):
				ri,ro=j*12,j*12+8
				if typ=='s':
					bx,by,nx,ny,tx,ty=p;pts=[(bx+ri*nx-da*tx,by+ri*ny-da*ty),(bx+ri*nx+da*tx,by+ri*ny+da*ty),(bx+ro*nx+da*tx,by+ro*ny+da*ty),(bx+ro*nx-da*tx,by+ro*ny-da*ty)]
					draw.polygon(pts,fill=clr)
				else:
					(acx,acy),ang=p;r_i,r_o=rad+ri,rad+ro;d=(r_i*math.radians(15)-X)/(2*max(1,r_i));a1,a2=ang-d,ang+d
					draw.polygon([(acx+r_i*math.cos(a1),acy+r_i*math.sin(a1)),(acx+r_i*math.cos(a2),acy+r_i*math.sin(a2)),(acx+r_o*math.cos(a2),acy+r_o*math.sin(a2)),(acx+r_o*math.cos(a1),acy+r_o*math.sin(a1))],fill=clr)
		return img
	except Exception as e:print(f"Error: {e}");return Image.new('RGB',(w,h),colors[0])
def draw_svg(t,data,w,h,stroke,colors,spec_color='multi'):
	n=len(data);X,W,rad,rh=8,18,80,192;sl,bh,bs,da=346,8,4,9;cx,cy=w/2,h/2;r_mid=sl*math.sqrt(3)/6;R_tri=sl*math.sqrt(3)/3;els=[];pts=[]
	v_pts=[(cx+sl/2,cy+r_mid),(cx,cy-R_tri),(cx-sl/2,cy+r_mid)]
	for i,v_d in enumerate(data):
		sec,li=i//22,i%22;nb=int(v_d*rh/12)
		clr=f'rgb({",".join(map(str,[int(c*255) for c in colorsys.hsv_to_rgb(i/n,0.8,1.0)]))})' if spec_color=='multi' else spec_color
		if li<14:
			pos=(li-6.5)*24.7;an=math.radians([90,330,210][sec]);nx,ny=math.cos(an),math.sin(an);tx,ty=ny,-nx
			bx,by=cx+(r_mid+rad)*nx+pos*tx,cy+(r_mid+rad)*ny+pos*ty
			for r1_o,r2_o,d_o,f_o in [(0,nb*12+8,da+stroke,colors[1]),(0,nb*12+8,da,None)]:
				if f_o==colors[1] and stroke<=0:continue
				for j in range(nb+1):
					ri,ro,fc,d=j*12,j*12+8,f_o if f_o else clr,d_o;r1,r2=(ri-stroke,ro+stroke) if f_o else (ri,ro)
					p1x,p1y,p2x,p2y,p3x,p3y,p4x,p4y=bx+r1*nx-d*tx,by+r1*ny-d*ty,bx+r1*nx+d*tx,by+r1*ny+d*ty,bx+r2*nx+d*tx,by+r2*ny+d*ty,bx+r2*nx-d*tx,by+r2*ny-d*ty
					p=[(p1x,p1y),(p2x,p2y),(p3x,p3y),(p4x,p4y)];els.append(('p',p,fc));pts.extend(p)
		else:
			ci,ab=v_pts[sec],[90,330,210][sec];ang=math.radians(ab-(li-14+0.5)*15)
			for f_o in [colors[1],None]:
				if f_o==colors[1] and stroke<=0:continue
				for j in range(nb+1):
					ri,ro,fc=j*12,j*12+8,f_o if f_o else clr;r_i,r_o=rad+ri,rad+ro;d=(r_i*math.radians(15)-X)/(2*max(1,r_i))
					R1,R2,dd=(r_i-stroke,r_o+stroke,d+stroke/max(1,r_i)) if f_o else (r_i,r_o,d)
					a1,a2=ang-dd,ang+dd;p=[(ci[0]+R1*math.cos(a1),ci[1]+R1*math.sin(a1)),(ci[0]+R1*math.cos(a2),ci[1]+R1*math.sin(a2)),(ci[0]+R2*math.cos(a2),ci[1]+R2*math.sin(a2)),(ci[0]+R2*math.cos(a1),ci[1]+R2*math.sin(a1))]
					els.append(('p',p,fc));pts.extend(p)
	x_mi,y_mi,x_ma,y_ma=min(p[0] for p in pts),min(p[1] for p in pts),max(p[0] for p in pts),max(p[1] for p in pts)
	sw,sh=x_ma-x_mi,y_ma-y_mi;sd=max(sw,sh);ox,oy=(sd-sw)/2-x_mi,0-y_mi
	res=[f'<svg width="{sd:.1f}" height="{sd:.1f}" viewBox="0 0 {sd:.1f} {sd:.1f}" xmlns="http://www.w3.org/2000/svg">']
	for e in els:
		p=e[1];res.append(f'<path d="M{p[0][0]+ox:.1f} {p[0][1]+oy:.1f} L{p[1][0]+ox:.1f} {p[1][1]+oy:.1f} L{p[2][0]+ox:.1f} {p[2][1]+oy:.1f} L{p[3][0]+ox:.1f} {p[3][1]+oy:.1f} Z" fill="{e[2]}"/>')
	res.append('</svg>');return "".join(res)