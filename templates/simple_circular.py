import math,colorsys,numpy as np
from PIL import Image,ImageDraw
g_rad=5
def draw_frame(t,data,w,h,stroke,colors,spec_color='multi',key=None):
	img=Image.new('RGB',(w,h),colors[0])
	draw=ImageDraw.Draw(img)
	c=(w//2,h//2);v_data=data;n=len(v_data);pts=[]
	for i,vol in enumerate(v_data):
		ang=(i/n)*2*math.pi-math.pi/2
		if spec_color=='multi':
			rgb=colorsys.hsv_to_rgb(i/n,0.8,1.0);clr=(int(rgb[0]*255),int(rgb[1]*255),int(rgb[2]*255))
		else:
			clr=(int(spec_color[1:3],16),int(spec_color[3:5],16),int(spec_color[5:7],16))
		for j in range(int(vol*20)+1):
			r=250+(j*12);pts.append((c[0]+r*math.cos(ang),c[1]+r*math.sin(ang),clr))
	for p in pts:draw.ellipse([p[0]-(g_rad+stroke),p[1]-(g_rad+stroke),p[0]+(g_rad+stroke),p[1]+(g_rad+stroke)],fill=colors[1])
	for p in pts:draw.ellipse([p[0]-g_rad,p[1]-g_rad,p[0]+g_rad,p[1]+g_rad],fill=p[2])
	return img
def draw_svg(t,data,w,h,stroke,colors,spec_color='multi'):
	c,pts=(w//2,h//2),[];v_data=data;n=len(v_data)
	for i,vol in enumerate(v_data):
		ang=(i/n)*2*math.pi-math.pi/2
		if spec_color=='multi':
			rgb=colorsys.hsv_to_rgb(i/n,0.8,1.0);clr=f'rgb({int(rgb[0]*255)},{int(rgb[1]*255)},{int(rgb[2]*255)})'
		else:
			clr=spec_color
		for j in range(int(vol*20)+1):
			r=250+(j*12);pts.append((c[0]+r*math.cos(ang),c[1]+r*math.sin(ang),clr))
	x_min,x_max=min(p[0] for p in pts)-(g_rad+stroke),max(p[0] for p in pts)+(g_rad+stroke)
	y_min,y_max=min(p[1] for p in pts)-(g_rad+stroke),max(p[1] for p in pts)+(g_rad+stroke);rw,rh=x_max-x_min,y_max-y_min
	side=max(rw,rh);ox,oy=(side-rw)/2-x_min,(side-rh)/2-y_min
	res=[f'<svg width="{side}" height="{side}" viewBox="0 0 {side} {side}" xmlns="http://www.w3.org/2000/svg">']
	for p in pts:res.append(f'<circle cx="{p[0]+ox}" cy="{p[1]+oy}" r="{g_rad+stroke}" fill="{colors[1]}"/>')
	for p in pts:res.append(f'<circle cx="{p[0]+ox}" cy="{p[1]+oy}" r="{g_rad}" fill="{p[2]}"/>')
	res.append('</svg>');return "".join(res)