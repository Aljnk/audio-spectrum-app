import numpy as np,colorsys
from PIL import Image,ImageDraw
def draw_frame(t,data,w,h,stroke,colors,spec_color='multi',key=None):
	img=Image.new('RGB',(w,h),colors[0])
	draw=ImageDraw.Draw(img)
	n,rw,rh,out_w=len(data),w*0.9,h*0.7,stroke;bw,sx,cy=rw/n,(w-rw)/2,h/2;lines=[]
	for i,v in enumerate(data):
		if spec_color=='multi':
			hue,bh=i/n,max(2,v*rh);rgb=colorsys.hsv_to_rgb(hue,0.9,1.0);c=(int(rgb[0]*255),int(rgb[1]*255),int(rgb[2]*255))
		else:
			bh=max(2,v*rh);c=(int(spec_color[1:3],16),int(spec_color[3:5],16),int(spec_color[5:7],16))
		x,lw=sx+i*bw,max(1,int(bw*0.7));lines.append((x,cy-bh/2,x,cy+bh/2,c,lw))
	for l in lines:draw.line([l[0],l[1]-out_w,l[2],l[3]+out_w],fill=colors[1],width=l[5]+out_w*2)
	for l in lines:draw.line([l[0],l[1],l[2],l[3]],fill=l[4],width=l[5])
	return img
def draw_svg(t,data,w,h,stroke,colors,spec_color='multi'):
	n,rw,rh,out_w=len(data),w*0.9,h*0.7,stroke;bw,sx,cy=rw/n,(w-rw)/2,h/2;ls=[]
	for i,v in enumerate(data):
		if spec_color=='multi':
			hue,bh=i/n,max(2,v*rh);rgb=colorsys.hsv_to_rgb(hue,0.9,1.0);c=f'rgb({int(rgb[0]*255)},{int(rgb[1]*255)},{int(rgb[2]*255)})'
		else:
			bh=max(2,v*rh);c=spec_color
		x,lw=sx+i*bw,max(1,int(bw*0.7));ls.append((x,cy-bh/2,x,cy+bh/2,c,lw))
	x_min,x_max=min(l[0]-l[5]/2-out_w for l in ls),max(l[0]+l[5]/2+out_w for l in ls)
	y_min,y_max=min(l[1]-out_w for l in ls),max(l[3]+out_w for l in ls)
	sw,sh=x_max-x_min,y_max-y_min;side=max(sw,sh);ox,oy=(side-sw)/2-x_min,(side-sh)/2-y_min
	res=[f'<svg width="{side}" height="{side}" viewBox="0 0 {side} {side}" xmlns="http://www.w3.org/2000/svg">']
	for l in ls:res.append(f'<line x1="{l[0]+ox}" y1="{l[1]-out_w+oy}" x2="{l[2]+ox}" y2="{l[3]+out_w+oy}" stroke="{colors[1]}" stroke-width="{l[5]+out_w*2}"/>')
	for l in ls:res.append(f'<line x1="{l[0]+ox}" y1="{l[1]+oy}" x2="{l[2]+ox}" y2="{l[3]+oy}" stroke="{l[4]}" stroke-width="{l[5]}"/>')
	res.append('</svg>');return "".join(res)