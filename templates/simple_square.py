import numpy as np,colorsys,math
from PIL import Image,ImageDraw
def draw_frame(t,data,w,h,stroke,colors,spec_color='multi',key=None):
	try:
		img=Image.new('RGB',(w,h),colors[0]);draw=ImageDraw.Draw(img);n=len(data);X,W,rad,rh=8,18,80,192
		sl=346;cx,cy=w/2,h/2;bh,bs,da=8,4,W/2
		for i,v in enumerate(data):
			sec,li=i//19,i%19
			if spec_color=='multi':
				rgb=colorsys.hsv_to_rgb(i/n,0.8,1.0);clr=(int(rgb[0]*255),int(rgb[1]*255),int(rgb[2]*255))
			else:clr=(int(spec_color[1:3],16),int(spec_color[3:5],16),int(spec_color[5:7],16))
			nb=int(v*rh/(bh+bs))
			if li<13:
				pos=(li-6)*26.4
				if sec==0:bx,by,nx,ny,tx,ty=cx+pos,cy-sl/2-rad,0,-1,1,0
				elif sec==1:bx,by,nx,ny,tx,ty=cx+sl/2+rad,cy+pos,1,0,0,1
				elif sec==2:bx,by,nx,ny,tx,ty=cx-pos,cy+sl/2+rad,0,1,1,0
				else:bx,by,nx,ny,tx,ty=cx-sl/2-rad,cy-pos,-1,0,0,1
				for r1,r2,d,f in [(0,nb*(bh+bs)+bh,da+stroke,colors[1]),(0,nb*(bh+bs)+bh,da,None)]:
					for j in range(nb+1):
						ri,ro=j*(bh+bs),j*(bh+bs)+bh
						if f is None:
							p1,p2=(bx+ri*nx-da*tx,by+ri*ny-da*ty),(bx+ro*nx+da*tx,by+ro*ny+da*ty);draw.rectangle([min(p1[0],p2[0]),min(p1[1],p2[1]),max(p1[0],p2[0]),max(p1[1],p2[1])],fill=clr)
						else:
							p1,p2=(bx+(ri-stroke)*nx-d*tx,by+(ri-stroke)*ny-d*ty),(bx+(ro+stroke)*nx+d*tx,by+(ro+stroke)*ny+d*ty);draw.rectangle([min(p1[0],p2[0]),min(p1[1],p2[1]),max(p1[0],p2[0]),max(p1[1],p2[1])],fill=f)
			else:
				ci,(acx,acy)=li-13,[(cx+sl/2,cy-sl/2),(cx+sl/2,cy+sl/2),(cx-sl/2,cy+sl/2),(cx-sl/2,cy-sl/2)][sec]
				ang=math.radians([-90,0,90,180][sec]+(ci+0.5)*15)
				for f in [colors[1],clr]:
					for j in range(nb+1):
						ri,ro=rad+j*(bh+bs),rad+j*(bh+bs)+bh;d=(ri*math.radians(15)-X)/(2*max(1,ri))
						if f==colors[1]:
							r1,r2,dd=ri-stroke,ro+stroke,d+stroke/max(1,ri)
							a1,a2=ang-dd,ang+dd;pts=[(acx+r1*math.cos(a1),acy+r1*math.sin(a1)),(acx+r1*math.cos(a2),acy+r1*math.sin(a2)),(acx+r2*math.cos(a2),acy+r2*math.sin(a2)),(acx+r2*math.cos(a1),acy+r2*math.sin(a1))];draw.polygon(pts,fill=f)
						else:
							a1,a2=ang-d,ang+d;pts=[(acx+ri*math.cos(a1),acy+ri*math.sin(a1)),(acx+ri*math.cos(a2),acy+ri*math.sin(a2)),(acx+ro*math.cos(a2),acy+ro*math.sin(a2)),(acx+ro*math.cos(a1),acy+ro*math.sin(a1))];draw.polygon(pts,fill=f)
		return img
	except Exception as e:print(f"Error: {e}");return Image.new('RGB',(w,h),colors[0])
def draw_svg(t,data,w,h,stroke,colors,spec_color='multi'):
	n=len(data);X,W,rad,rh=8,18,80,192;sl=346;cx,cy=w/2,h/2;bh,bs,da=8,4,9;els=[];pts=[]
	for i,v in enumerate(data):
		sec,li=i//19,i%19;nb=int(v*rh/12)
		clr=f'rgb({",".join(map(str,[int(c*255) for c in colorsys.hsv_to_rgb(i/n,0.8,1.0)]))})' if spec_color=='multi' else spec_color
		if li<13:
			pos=(li-6)*26.4
			if sec==0:bx,by,nx,ny,tx,ty=cx+pos,cy-sl/2-rad,0,-1,1,0
			elif sec==1:bx,by,nx,ny,tx,ty=cx+sl/2+rad,cy+pos,1,0,0,1
			elif sec==2:bx,by,nx,ny,tx,ty=cx-pos,cy+sl/2+rad,0,1,1,0
			else:bx,by,nx,ny,tx,ty=cx-sl/2-rad,cy-pos,-1,0,0,1
			for r1_o,r2_o,d_o,f_o in [(0,nb*12+8,da+stroke,colors[1]),(0,nb*12+8,da,None)]:
				if f_o==colors[1] and stroke<=0:continue
				for j in range(nb+1):
					ri,ro,fc,d=j*12,j*12+8,f_o if f_o else clr,d_o;r1,r2=(ri-stroke,ro+stroke) if f_o else (ri,ro)
					px1,py1,px2,py2=bx+r1*nx-d*tx,by+r1*ny-d*ty,bx+r2*nx+d*tx,by+r2*ny+d*ty
					ex,ey,ew,eh=min(px1,px2),min(py1,py2),abs(px2-px1),abs(py2-py1)
					els.append(('r',ex,ey,ew,eh,fc));pts.extend([(ex,ey),(ex+ew,ey+eh)])
		else:
			ci,(acx,acy)=li-13,[(cx+sl/2,cy-sl/2),(cx+sl/2,cy+sl/2),(cx-sl/2,cy+sl/2),(cx-sl/2,cy-sl/2)][sec]
			ang=math.radians([-90,0,90,180][sec]+(ci+0.5)*15)
			for f_o in [colors[1],None]:
				if f_o==colors[1] and stroke<=0:continue
				for j in range(nb+1):
					ri,ro,fc=rad+j*12,rad+j*12+8,f_o if f_o else clr;d=(ri*math.radians(15)-X)/(2*max(1,ri))
					R1,R2,dd=(ri-stroke,ro+stroke,d+stroke/max(1,ri)) if f_o else (ri,ro,d)
					a1,a2=ang-dd,ang+dd;p=[(acx+R1*math.cos(a1),acy+R1*math.sin(a1)),(acx+R1*math.cos(a2),acy+R1*math.sin(a2)),(acx+R2*math.cos(a2),acy+R2*math.sin(a2)),(acx+R2*math.cos(a1),acy+R2*math.sin(a1))]
					els.append(('p',p,fc));pts.extend(p)
	x_mi,y_mi,x_ma,y_ma=min(p[0] for p in pts),min(p[1] for p in pts),max(p[0] for p in pts),max(p[1] for p in pts)
	sw,sh=x_ma-x_mi,y_ma-y_mi;sd=max(sw,sh);ox,oy=(sd-sw)/2-x_mi,(sd-sh)/2-y_mi
	res=[f'<svg width="{sd:.1f}" height="{sd:.1f}" viewBox="0 0 {sd:.1f} {sd:.1f}" xmlns="http://www.w3.org/2000/svg">']
	for e in els:
		if e[0]=='r':res.append(f'<rect x="{e[1]+ox:.1f}" y="{e[2]+oy:.1f}" width="{e[3]:.1f}" height="{e[4]:.1f}" fill="{e[5]}"/>')
		else:p=e[1];res.append(f'<path d="M{p[0][0]+ox:.1f} {p[0][1]+oy:.1f} L{p[1][0]+ox:.1f} {p[1][1]+oy:.1f} L{p[2][0]+ox:.1f} {p[2][1]+oy:.1f} L{p[3][0]+ox:.1f} {p[3][1]+oy:.1f} Z" fill="{e[2]}"/>')
	res.append('</svg>');return "".join(res)