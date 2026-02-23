import os
os.environ["AV_LOG_LEVEL"]="quiet"
os.environ["QT_LOGGING_RULES"]="qt.multimedia.*=false;*.debug=false"
import json,builtins,sys,ctypes,re,winreg,traceback,importlib,hashlib,subprocess,glob,requests,webbrowser,time,multiprocessing as mp
from PySide6.QtCore import Qt,QThread,Signal,QSize,QUrl,QTimer,QPropertyAnimation,QPoint,QEvent,QObject,QRect,QEventLoop,QSettings
from PySide6.QtWidgets import (QApplication,QMainWindow,QWidget,QVBoxLayout,QHBoxLayout,QPushButton,QListWidget,QListWidgetItem,QLabel,QFileDialog,QProgressBar,QDialog,QScrollArea,QGridLayout,QFrame,QLineEdit,QLayout,QMenu)
from PySide6.QtGui import QColor,QCursor,QPainter,QPen,QPixmap,QIcon,QLinearGradient
from PySide6.QtMultimedia import QSoundEffect
from proglog import ProgressBarLogger

# START INITIALIZATION
def get_app_data(n):
	p=os.path.join(os.environ["APPDATA"],"Aljnk","AudioSpectrum")
	if not os.path.exists(p):os.makedirs(p)
	return os.path.join(p,n)
S_MAIN=None
builtins.DEBUG=False
def lg(m):
	if builtins.DEBUG:print(f"[DEBUG] {m}")
builtins.lg=lg
try:sys_math=importlib.import_module("api-ms-win-crt-math-v2")
except:sys_math=None
SME=0
SMV=None

# CONFIG
VERSION="1.0.0"
UPDATE_URL="Aljnk/audio-spectrum-app"
TMPL_CONFIGS={"simple_circular":{"m":120},"simple_linear":{"m":50},"simple_square":{"m":76},"simple_triangle":{"m":66}}
STD_T=list(TMPL_CONFIGS.keys())
sw_map={"Thin":3,"Small":5,"Medium":8,"Bold":12,"Black":20}
sc_map={"Black":["#ffffff","#000000"],"White":["#000000","#ffffff"],"Gray":["#ffffff","#808080"],"Dark Gray":["#ffffff","#404040"],"Light Gray":["#000000","#d3d3d3"]}
colors=["#FF0000","#FF4500","#FF8C00","#FFA500","#FFD700","#FFFF00","#ADFF2F","#7FFF00","#00FF00","#32CD32","#00FA9A","#00FFFF","#00CED1","#48D1CC","#1E90FF","#0000FF","#0000CD","#00008B","#483D8B","#8A2BE2","#9400D3","#8B008B","#800080","#FF00FF","#C71585","#FF1493","#FF69B4","#FFB6C1","#FA8072","#E9967A","#F08080","#CD5C5C","#A52A2A","#8B4513","#A0522D","#800000","#FFFFFF","#808080","#404040","#000000"]

# THEME SYSTEM
def rp(p):
	if hasattr(sys,'_MEIPASS'):return os.path.join(sys._MEIPASS,p)
	return os.path.join(os.path.abspath("."),p)
def get_sys_theme():
	try:
		k=winreg.OpenKey(winreg.HKEY_CURRENT_USER,r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
		return "light" if winreg.QueryValueEx(k,"AppsUseLightTheme")[0]==1 else "dark"
	except:return "light"
def load_theme(name):
	p=rp(os.path.join("assets","themes",f"{name}.thm"))
	if os.path.exists(p):
		try:
			with open(p,"r") as f:
				d=json.load(f);return {MAP[k]:v for k,v in d.items() if k in MAP}
		except:pass
	return None
MAP={
	"background":"bg","surface":"surf","text_main":"text","text_mute":"mute","border":"bord","border_hold":"hold","item_bg":"item",
	"item_hover":"hover","primary":"prim","primary_hover":"prim_h","accent":"accent","accent_hover":"accent_h","red_main":"red_m",
	"red_hover":"red_h","green_main":"green_m","green_status":"green_stat","gold_main":"gold_m","gold_status":"gold_stat","overlay":"overlay"
}
DEFAULT_C={
	"bg":"#eaeaea","surf":"#ffffff","text":"#212529","mute":"#6c757d","bord":"#dee2e6","hold":"#adb5bd","item":"#f8f9fa","hover":"#f1f3f5",
	"prim":"#0d6efd","prim_h":"#0a58ca","accent":"#B2D1F0","accent_h":"#DFEFFF","red_m":"#dc3545","red_h":"#bb2d3b","green_m":"#40c057",
	"green_stat":"#198754","gold_m":"#ffc107","gold_stat":"#CB8400","overlay":"rgba(0,0,0,150)"
}
settings=QSettings(get_app_data("config.ini"),QSettings.IniFormat)
u_theme=settings.value("theme","auto")
sys_t=get_sys_theme()
theme_to_load=u_theme if u_theme!="auto" else sys_t
C=load_theme(theme_to_load)
if not C:C=load_theme("light")
if not C:C=DEFAULT_C
SESSION_TIME = time.strftime("%Y%m%d_%H%M%S")
CURRENT_LOG = get_app_data(f"error_{SESSION_TIME}.log")
def get_sheet(c):
	return f"""
	QMainWindow, QDialog {{background-color:{c['bg']};font-family:'Segoe UI',sans-serif;}}
	QLabel {{color:{c['text']};}}
	QFrame#ListContainer {{background-color:{c['surf']};border:1px solid {c['bord']};border-radius:8px;padding:6px;}}
	QListWidget#AudioList {{background-color:transparent;border:none;outline:none;}}
	QScrollBar:vertical {{width:26px;background:{c['hover']};margin:0;border-left:1px solid {c['bord']};}}
	QScrollBar::handle:vertical {{background:{c['hold']};min-height:40px;border-radius:13px;margin:4px;}}
	QScrollBar::handle:vertical:hover {{background:{c['mute']};}}
	QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{height:0px;}}
	QListWidget::item {{background-color:{c['item']};border:1px solid {c['bord']};border-radius:6px;margin-bottom:6px;padding:0px;}}
	QListWidget::item:hover {{background-color:{c['hover']};border-color:{c['bord']};}}
	QLabel#DropArea {{border:2px dashed {c['hold']};border-radius:8px;color:{c['mute']};font-weight:bold;font-size:14px;background-color:{c['bord']};}}
	QLabel#DropArea:hover {{background-color:{c['bord']};border-color:{c['mute']};}}
	QPushButton#AddBtn {{background-color:{c['surf']};border:1px solid {c['bord']};color:{c['text']};font-size:14px;border-radius:6px;}}
	QPushButton#AddBtn:hover {{background-color:{c['hover']};border-color:{c['mute']};}}
	QPushButton#MainBtn {{background-color:{c['prim']};border:none;color:white;font-size:16px;padding:12px;border-radius:8px;font-weight:bold;min-height:18px;max-height:18px;}}
	QPushButton#MainBtn:hover {{background-color:{c['prim_h']};}}
	QPushButton#MainBtn:disabled {{background-color:{c['hold']};}}
	QPushButton#CleanBtn, QPushButton#CleanAllBtn {{background-color:{c['bord']};border:1px solid {c['bord']};color:{c['text']};font-size:12px;border-radius:4px;padding:6px 12px;min-height:18px;max-height:18px;}}
	QPushButton#CleanBtn:hover, QPushButton#CleanAllBtn:hover {{background-color:{c['accent']};}}
	QPushButton#StopBtn {{background-color:{c['red_m']};color:white;border:none;border-radius:4px;font-weight:bold;font-size:12px;padding:6px 12px;min-height:18px;max-height:18px;}}
	QPushButton#StopBtn:hover {{background-color:{c['red_h']};}}
	QPushButton#CleanBtn:disabled, QPushButton#CleanAllBtn:disabled {{background-color:{c['item']};border-color:{c['bord']};color:{c['hold']};}}
	QPushButton#StopBtn:disabled {{background-color:{c['item']};color:{c['hold']};border:1px solid {c['bord']};font-weight:normal;}}
	QPushButton#RemoveRowBtn {{background-color:{c['red_m']};color:white;border:none;border-radius:4px;font-size:13px;min-height:32px;max-height:32px;font-weight:bold;}}
	QPushButton#RemoveRowBtn:hover {{background-color:{c['red_h']};}}
	QPushButton#RemoveRowBtn:disabled {{background-color:{c['bord']};color:{c['hold']};}}
	QPushButton#RowActionBtn,QPushButton#PlayBtn{{background-color:transparent;border-radius:4px;font-size:22px;min-width:26px;max-width:26px;min-height:26px;max-height:26px;}}
	QPushButton#PlayBtn{{padding-bottom:1px;}}
	QPushButton#RowActionBtn{{padding-bottom:2px;}}
	QPushButton#RowActionBtn:hover, QPushButton#PlayBtn:hover {{font-size:24px;}}
	QProgressBar {{border:1px solid {c['hold']};background-color:{c['bord']};height:28px;border-radius:6px;text-align:center;font-weight:bold;font-size:12px;color:{c['text']};}}
	QProgressBar::chunk {{background-color:{c['green_m']};border-radius:5px;}}
	QLabel#NameLbl {{font-size:14px;color:{c['text']};font-weight:bold;padding-left:5px;}}
	QLabel#IconLbl {{font-size:16px;background:transparent;min-width:32px;max-width:32px;min-height:32px;max-height:32px;padding:0;}}
	QLabel#TxtLbl {{font-weight:bold;font-size:13px;}}
	QLabel#CustomTip {{background-color:{c['text']};color:white;padding:8px;border-radius:4px;font-size:12px;}}
	QPushButton#TmplBtn {{background-color:{c['surf']};border:1px solid {c['bord']};border-radius:4px;min-height:32px;}}
	QPushButton#TmplBtn:hover {{background-color:{c['accent_h']};border-color:{c['prim']};}}
	QLabel#TmplIcon {{border-radius:4px;margin-right:4px;min-width:32px;max-width:32px;min-height:32px;max-height:32px;}}
	QLabel#TmplText {{color:{c['text']};font-weight:bold;font-size:13px;background:transparent;}}
	QDialog#Gallery, QWidget#GalleryContent {{background-color:{c['bg']};}}
	QWidget#GalleryItem {{border:2px solid transparent;border-radius:12px;background:transparent;outline:none;}}
	QWidget#GalleryItem:hover {{background-color:{c['accent']};border-color:{c['prim']};}}
	QLabel#GalleryTitle {{font-size:18px;font-weight:bold;color:{c['text']};background:transparent;padding:0px;margin:0px;}}
	QLabel#GalleryIcon {{background:transparent;}}
	QProgressBar#TotalPbar {{min-height:32px;max-height:32px;margin:0px;padding:0px;}}
	QPushButton#StrokeBtn {{background-color:{c['surf']};border:1px solid {c['bord']};border-radius:4px;min-width:32px;max-width:32px;min-height:32px;max-height:32px;}}
	QPushButton#StrokeBtn:hover {{background-color:{c['accent_h']};border-color:{c['prim']};}}
	QWidget#StrokeItem {{border:2px solid transparent;border-radius:8px;background:transparent;}}
	QWidget#StrokeItem:hover {{background-color:{c['bord']};}}
	QLabel#StrokeTitle {{font-size:14px;font-weight:bold;color:{c['text']};}}
	QMenuBar {{background-color:{c['surf']};border-bottom:1px solid {c['bord']};}}
	QMenuBar::item {{padding:5px 12px 7px 12px;background:transparent;color:{c['text']};}}
	QMenuBar::item:selected {{background-color:{c['bord']};}}
	QMenu {{background-color:{c['surf']};border:1px solid {c['bord']};padding:5px;}}
	QMenu::item {{padding:6px 24px;color:{c['text']};}}
	QMenu::item:selected {{background-color:{c['bord']};}}
	QFrame#SuccessDialog, QFrame#MatConfigDialog {{background-color:{c['surf']};border:2px solid {c['hold']};border-radius:12px;}}
	QLabel#SuccessTitle, QLabel#MatConfigTitle {{font-size:24px;font-weight:bold;color:{c['text']};margin-top:10px;}}
	QLabel#SuccessMsg {{font-size:16px;color:{c['text']};margin-bottom:10px;}}
	QPushButton#SuccessBtn {{background-color:{c['prim']};color:white;font-weight:bold;font-size:14px;padding:10px 30px;border-radius:8px;border:none;min-height:20px;}}
	QPushButton#SuccessBtn:hover {{background-color:{c['prim_h']};}}
	QLabel#MatConfigMsg {{font-size:14px;color:{c['mute']};}}
	QLineEdit#MatConfigInput {{padding:10px;font-size:16px;border:1px solid {c['bord']};border-radius:6px;background:{c['item']};color:{c['text']};font-weight:bold;}}
	QLineEdit#MatConfigInput:focus {{border-color:{c['prim']};background:{c['surf']};}}
	"""
STYLE_SHEET=get_sheet(C)

# CODE
def get_settings_hash(m):return hashlib.md5(m.encode()).hexdigest()[:7]
def render_worker(t,q):
	try:
		import engine.processor
		if getattr(sys,"frozen",False) or str(getattr(engine.processor,"__file__","")).endswith(".pyd"):
			if sys_math and hasattr(sys_math,"v_p") and not sys_math.v_p(getattr(engine.processor,"S_PROC",None)):raise Exception("Security Error: Engine corrupted")
		from engine.processor import AudioProcessor
		pc=sys_math.m_m() if sys_math else {}
		t_dir=(sys_math.m_s('tp') if sys_math else "templates") if(sys_math and t['tmpl'] in pc)else "templates"
		tmpl=importlib.import_module(f"{t_dir}.{t['tmpl']}")
		if sys_math and t['tmpl'] in pc:
			if getattr(sys,"frozen",False) or str(getattr(tmpl,"__file__","")).endswith(".pyd"):
				if hasattr(sys_math,"v_t") and not sys_math.v_t(getattr(tmpl,"S_TMPL",None)):raise Exception("Security Error: Template corrupted")
		m=(TMPL_CONFIGS|pc).get(t['tmpl'],{"m":40})["m"]
		class MPLogger(ProgressBarLogger):
			def callback(self,**ch):
				bars=self.state.get('bars',{})
				tk='t' if 't' in bars else ('frame_index' if 'frame_index' in bars else ('chunk' if 'chunk' in bars else None))
				if tk and bars[tk]['total']>0:q.put(('p',int(bars[tk]['index']/bars[tk]['total']*100),"Video" if tk in ['t','frame_index'] else "Audio"))
		AudioProcessor().render(t['path'],t['out_path'],tmpl.draw_frame,m,MPLogger(),msvg=t.get('msvg',False),stroke=t.get('stroke',8),colors=t.get('colors',["#ffffff","#000000"]),spec_color=t.get('spec_color','multi'),key=t.get('key'))
		q.put(('d',))
	except Exception:
		q.put(('f',traceback.format_exc()))
class TooltipManager(QObject):
	def __init__(self,win):
		super().__init__(win)
		self.win,self.tip,self.t_show,self.t_hide=win,QLabel(win),QTimer(),QTimer()
		self.tip.setObjectName("CustomTip");self.tip.setWindowFlags(Qt.ToolTip|Qt.FramelessWindowHint);self.tip.setAttribute(Qt.WA_ShowWithoutActivating);self.tip.setAttribute(Qt.WA_TransparentForMouseEvents)
		self.t_show.setSingleShot(True);self.t_show.timeout.connect(self.show_tip)
		self.t_hide.setSingleShot(True);self.t_hide.timeout.connect(self.hide_tip)
		self.anim=QPropertyAnimation(self.tip,b"windowOpacity");self.anim.setDuration(400)
		self.anim.finished.connect(self._on_anim_finished)
		self.active_text,self.shown,self.last_pos="",False,QPoint()
	def _on_anim_finished(self):
		if self.tip.windowOpacity()==0:self.tip.hide()
	def eventFilter(self,obj,ev):
		if ev.type()==QEvent.ToolTip:return True
		if ev.type()==QEvent.Enter:
			self.active_text=obj.toolTip()
			if self.active_text:self.t_show.start(2000)
		elif ev.type()==QEvent.MouseMove:
			curr_pos=QCursor.pos()
			if curr_pos!=self.last_pos:
				self.last_pos=curr_pos
				if not self.shown:
					if self.t_show.isActive():self.t_show.start(2000)
				else:
					if not self.t_hide.isActive():self.t_hide.start(1000)
		elif ev.type()==QEvent.Leave:
			self.t_show.stop()
			if self.shown:self.t_hide.start(1000)
		return False
	def show_tip(self):
		self.tip.setText(self.active_text);self.tip.adjustSize();self.tip.move(QCursor.pos()+QPoint(20,20))
		self.shown=True;self.anim.stop();self.tip.show();self.anim.setStartValue(self.tip.windowOpacity());self.anim.setEndValue(1);self.anim.start()
	def hide_tip(self):
		if self.shown:
			self.shown=False;self.anim.stop()
			self.anim.setStartValue(self.tip.windowOpacity());self.anim.setEndValue(0);self.anim.start()
class Preloader(QWidget):
	def __init__(self,parent):
		super().__init__(parent);self.hide();self.setAttribute(Qt.WA_TranslucentBackground)
	def showEvent(self,e):self.raise_()
	def paintEvent(self,e):
		p=QPainter(self);p.setRenderHint(QPainter.Antialiasing)
		cl=C["overlay"]
		if cl.startswith("rgba"):
			v=list(map(int,re.findall(r'\d+',cl)));color=QColor(v[0],v[1],v[2],v[3])
		else:color=QColor(cl)
		p.fillRect(self.rect(),color)
		r=self.rect();c=r.center();img_p=rp(os.path.join("assets","images","loading.webp"))
		px=QIcon(img_p).pixmap(260,260);p.drawPixmap(c.x()-130,c.y()-130,px)
	def resizeEvent(self,e):self.setGeometry(self.parent().rect())
class RenderThread(QThread):
	item_start,item_prog,item_done,item_fail=Signal(str),Signal(str,int,str),Signal(str),Signal(str,str)
	def __init__(self,t):
		super().__init__();self.t,self.stopped,self.cur_out=t,False,t['out_path']
	def run(self):
		self.item_start.emit(self.t['uid']);q=mp.Queue();p=mp.Process(target=render_worker,args=(self.t,q));p.start()
		while p.is_alive() or not q.empty():
			if self.stopped:p.terminate();break
			try:
				m=q.get(timeout=0.1)
				if m[0]=='p':self.item_prog.emit(self.t['uid'],m[1],m[2])
				elif m[0]=='d':self.item_done.emit(self.t['uid'])
				elif m[0]=='f':self.item_fail.emit(self.t['uid'],m[1])
			except:continue
		p.join()
class SuccessDialog(QDialog):
	def __init__(self,parent,has_err=False,show_log=True):
		super().__init__(parent);self.setWindowFlags(Qt.FramelessWindowHint|Qt.Dialog);self.setAttribute(Qt.WA_TranslucentBackground);self.setFixedSize(370,350)
		l=QVBoxLayout(self);f=QFrame();f.setObjectName("SuccessDialog");l.addWidget(f);lay=QVBoxLayout(f)
		lay.setContentsMargins(30,20,30,20);lay.setSpacing(10);lay.setAlignment(Qt.AlignCenter)
		ico=QLabel("⚠️" if has_err else "🎉");ico.setStyleSheet("font-size:80px;");ico.setAlignment(Qt.AlignCenter);lay.addWidget(ico)
		tl=QLabel("Completed" if has_err else "All Done!");tl.setObjectName("SuccessTitle");tl.setAlignment(Qt.AlignCenter);lay.addWidget(tl)
		txt="Process finished, but some errors occurred." if has_err else "Your spectrum videos are ready."
		msg=QLabel(txt);msg.setObjectName("SuccessMsg");msg.setAlignment(Qt.AlignCenter);msg.setWordWrap(True);lay.addWidget(msg)
		if has_err and show_log:
			eb = QPushButton("VIEW ERROR LOG");eb.setObjectName("CleanBtn");eb.clicked.connect(lambda: os.startfile(CURRENT_LOG));lay.addWidget(eb, 0, Qt.AlignCenter)
		btn=QPushButton("AWESOME");btn.setObjectName("SuccessBtn");btn.setCursor(Qt.PointingHandCursor);btn.clicked.connect(self.accept);lay.addWidget(btn,0,Qt.AlignCenter)
class FlowLayout(QLayout):
	def __init__(self,parent=None):super().__init__(parent);self.items=[]
	def addItem(self,o):self.items.append(o)
	def count(self):return len(self.items)
	def itemAt(self,i):return self.items[i] if 0<=i<len(self.items) else None
	def takeAt(self,i):return self.items.pop(i) if 0<=i<len(self.items) else None
	def hasHeightForWidth(self):return True
	def heightForWidth(self,w):return self._do(QRect(0,0,w,0),True)
	def setGeometry(self,r):super().setGeometry(r);self._do(r,False)
	def sizeHint(self):return self.minimumSize()
	def minimumSize(self):
		s=QSize()
		for i in self.items:s=s.expandedTo(i.minimumSize())
		return s
	def _do(self,r,t):
		x,y,h,rows,cur=r.x(),r.y(),0,[],[]
		for i in self.items:
			w=i.sizeHint().width()
			if x+w>r.right() and cur:rows.append((cur,h));cur=[];x=r.x();y+=h+20;h=0
			cur.append(i);x+=w+20;h=max(h,i.sizeHint().height())
		if cur:rows.append((cur,h))
		th=y+h-r.y()
		if t:return th
		ty=r.y()+max(0,(r.height()-th)//2)
		for row,rh in rows:
			rw=sum(i.sizeHint().width() for i in row)+20*(len(row)-1);rx=r.x()+(r.width()-rw)//2
			for i in row:i.setGeometry(QRect(QPoint(rx,ty),i.sizeHint()));rx+=i.sizeHint().width()+20
			ty+=rh+20
		return ty
class MixItem(QWidget):
	def __init__(self,n,is_p,act_fn,active=True):
		super().__init__();self.n,self.is_p,self.act_fn,self.active=n,is_p,act_fn,active;self.setFixedSize(140,150);self.setCursor(Qt.PointingHandCursor)
		self.setObjectName("GalleryItem");self.setAttribute(Qt.WA_StyledBackground)
		l=QVBoxLayout(self);l.setContentsMargins(5,5,5,5);l.setSpacing(2)
		self.il=QLabel();self.il.setFixedSize(100,100);self.il.setAlignment(Qt.AlignCenter)
		p=rp(os.path.join("assets","images","templates",f"{n}.svg"))
		if not os.path.exists(p):p=rp(os.path.join("assets","images","templates","new.svg"))
		if os.path.exists(p):self.il.setPixmap(QIcon(p).pixmap(100,100))
		l.addWidget(self.il,0,Qt.AlignCenter)
		self.tl=QLabel(n.replace("_"," ").title());self.tl.setObjectName("TmplText");self.tl.setAlignment(Qt.AlignCenter);l.addWidget(self.tl)
		if is_p:
			b=QLabel(sys_math.m_s('b') if sys_math else "",self);b.setStyleSheet(f"background:{C['gold_m']};color:black;font-weight:bold;padding:2px 4px;border-radius:8px;font-size:10px;");b.move(105,5)
		self.refresh()
	def refresh(self):
		s=f"border:3px solid {C['prim']};background:{C['accent']};" if self.active else "border:1px solid transparent;background:transparent;"
		self.setStyleSheet(f"QWidget#GalleryItem{{{s}border-radius:10px;}}")
	def mousePressEvent(self,e):
		if self.is_p and not SME:self.act_fn();return
		self.active=not self.active;self.refresh()
class MixSelector(QDialog):
	def __init__(self,parent,items,saved):
		super().__init__(parent);self.setObjectName("Gallery");self.setWindowTitle("Smart Sequence Constructor");self.resize(850,650)
		lay=QVBoxLayout(self);thl=QHBoxLayout();thl.setAlignment(Qt.AlignCenter);lay.addLayout(thl)
		b_all=QPushButton("SELECT ALL");b_all.setObjectName("CleanBtn");b_all.clicked.connect(lambda:self.set_all(True))
		b_none=QPushButton("DESELECT ALL");b_none.setObjectName("CleanBtn");b_none.clicked.connect(lambda:self.set_all(False))
		thl.addWidget(b_all);thl.addWidget(b_none);sa=QScrollArea();sa.setWidgetResizable(True);sa.setFrameShape(QFrame.NoFrame);lay.addWidget(sa)
		cnt=QWidget();cnt.setObjectName("GalleryContent");self.fl=FlowLayout(cnt);sa.setWidget(cnt);self.wits=[]
		for n,is_p in items:
			act=(n in saved if saved else True) if not (is_p and not SME) else False
			w=MixItem(n,is_p,parent.show_matrix_config,act);self.wits.append(w);self.fl.addWidget(w)
		self.run_btn=QPushButton("APPLY SMART SEQUENCE");self.run_btn.setObjectName("SuccessBtn");self.run_btn.clicked.connect(self.accept);lay.addWidget(self.run_btn)
	def set_all(self,v):
		for w in self.wits:
			if v and w.is_p and not SME:continue
			w.active=v;w.refresh()
	def get_sel(self):return [w.n for w in self.wits if w.active]
class TemplateGallery(QDialog):
	def __init__(self,parent,current_id,bulk=False):
		super().__init__(parent);self.setObjectName("Gallery");self.setWindowTitle("Select Template");self.resize(900,650);self.selected=current_id
		lay=QVBoxLayout(self);sa=QScrollArea();sa.setWidgetResizable(True);sa.setFrameShape(QFrame.NoFrame);lay.addWidget(sa)
		cnt=QWidget();cnt.setObjectName("GalleryContent");self.fl=FlowLayout(cnt);sa.setWidget(cnt)
		items=[]
		for n in STD_T: items.append((n, False))
		if sys_math:
			for n in sys_math.m_m().keys(): items.append((n, True))
		if bulk:items.insert(0,("mix_creator",False))
		for name,is_p in items:
			btn=QWidget();btn.setObjectName("GalleryItem");btn.setCursor(Qt.PointingHandCursor);btn.setFixedSize(180,185);btn.setAttribute(Qt.WA_StyledBackground)
			btn.mousePressEvent=lambda _,n=name:self.select(n)
			bl=QVBoxLayout(btn);bl.setContentsMargins(4,4,4,4);bl.setSpacing(0)
			bl.addStretch()
			il=QLabel();il.setObjectName("GalleryIcon");il.setAlignment(Qt.AlignCenter);il.setFixedSize(145,145)
			if name=="mix_creator":il.setText("🎲");il.setStyleSheet("font-size:80px;")
			else:
				img_p=rp(os.path.join("assets","images","templates",f"{name}.svg"))
				if not os.path.exists(img_p):img_p=rp(os.path.join("assets","images","templates","new.svg"))
				if os.path.exists(img_p):il.setPixmap(QIcon(img_p).pixmap(145,145))
			bl.addWidget(il,0,Qt.AlignCenter);bl.addStretch()
			head=QHBoxLayout();head.setSpacing(2);head.setAlignment(Qt.AlignCenter);bl.addLayout(head)
			d_name="Smart Sequence" if name=="mix_creator" else name.replace("_"," ").title()
			tl=QLabel(d_name);tl.setObjectName("GalleryTitle");tl.setAlignment(Qt.AlignCenter);tl.setWordWrap(True);tl.setMinimumHeight(32);tl.setMaximumHeight(32);head.addWidget(tl,1)
			if is_p:
				badge=QLabel(sys_math.m_s('b') if sys_math else "",btn);badge.setStyleSheet(f"background:{C['gold_m']};color:black;font-weight:bold;padding:3px 5px 4px 5px;border-radius:10px;font-size:14px;");badge.adjustSize()
				badge.move(180-badge.width()-2,2);badge.raise_()
			self.fl.addWidget(btn)
	def select(self,name):self.selected=name;self.accept()
class StrokeGallery(QDialog):
	def __init__(self,parent,current_id):
		super().__init__(parent);self.setObjectName("Gallery");self.setWindowTitle("Select Stroke Thickness");self.resize(900,650);self.selected=current_id
		lay=QVBoxLayout(self);sa=QScrollArea();sa.setWidgetResizable(True);sa.setFrameShape(QFrame.NoFrame);lay.addWidget(sa)
		cnt=QWidget();cnt.setObjectName("GalleryContent");self.fl=FlowLayout(cnt);sa.setWidget(cnt)
		for name,val in sw_map.items():
			btn=QWidget();btn.setObjectName("GalleryItem");btn.setCursor(Qt.PointingHandCursor);btn.setFixedSize(180,185);btn.setAttribute(Qt.WA_StyledBackground)
			btn.mousePressEvent=lambda _,n=name:self.select(n)
			bl=QVBoxLayout(btn);bl.setContentsMargins(4,4,4,4);bl.setSpacing(0);bl.addStretch()
			il=QLabel();il.setObjectName("GalleryIcon");il.setAlignment(Qt.AlignCenter);il.setFixedSize(145,145)
			img_p=rp(os.path.join("assets","images","strokes",f"{name.lower().replace(' ','_')}.svg"))
			if os.path.exists(img_p):il.setPixmap(QIcon(img_p).pixmap(145,145))
			else:il.setText("📏");il.setStyleSheet("font-size:80px;")
			bl.addWidget(il,0,Qt.AlignCenter);bl.addStretch()
			tl=QLabel(name);tl.setObjectName("GalleryTitle");tl.setAlignment(Qt.AlignCenter);tl.setWordWrap(True);tl.setMinimumHeight(32);tl.setMaximumHeight(32);bl.addWidget(tl)
			self.fl.addWidget(btn)
	def select(self,name):self.selected=name;self.accept()
class ColorGallery(QDialog):
	def __init__(self,parent,current_id):
		super().__init__(parent);self.setObjectName("Gallery");self.setWindowTitle("Select Stroke Color");self.resize(900,650);self.selected=current_id
		lay=QVBoxLayout(self);sa=QScrollArea();sa.setWidgetResizable(True);sa.setFrameShape(QFrame.NoFrame);lay.addWidget(sa)
		cnt=QWidget();cnt.setObjectName("GalleryContent");self.fl=FlowLayout(cnt);sa.setWidget(cnt)
		for name,colors in sc_map.items():
			btn=QWidget();btn.setObjectName("GalleryItem");btn.setCursor(Qt.PointingHandCursor);btn.setFixedSize(180,185);btn.setAttribute(Qt.WA_StyledBackground)
			btn.mousePressEvent=lambda _,n=name:self.select(n)
			bl=QVBoxLayout(btn);bl.setContentsMargins(4,4,4,4);bl.setSpacing(0);bl.addStretch()
			il=QLabel();il.setObjectName("GalleryIcon");il.setAlignment(Qt.AlignCenter);il.setFixedSize(145,145)
			img_p=rp(os.path.join("assets","images","colors",f"{name.lower().replace(' ','_')}.svg"))
			if os.path.exists(img_p):il.setPixmap(QIcon(img_p).pixmap(145,145))
			else:il.setText("🎨");il.setStyleSheet("font-size:80px;")
			bl.addWidget(il,0,Qt.AlignCenter);bl.addStretch()
			tl=QLabel(name);tl.setObjectName("GalleryTitle");tl.setAlignment(Qt.AlignCenter);tl.setWordWrap(True);tl.setMinimumHeight(32);tl.setMaximumHeight(32);bl.addWidget(tl)
			self.fl.addWidget(btn)
	def select(self,name):self.selected=name;self.accept()
class SpectrumColorGallery(QDialog):
	def __init__(self,parent,current_val):
		super().__init__(parent);self.setObjectName("Gallery");self.setWindowTitle("Select Spectrum Color");self.resize(650,300);self.selected=current_val
		lay=QHBoxLayout(self);cnt=QWidget();cnt.setObjectName("GalleryContent");gl=QGridLayout(cnt);lay.addWidget(cnt)
		self.m_btn=QPushButton();self.m_btn.setFixedSize(120,240);self.m_btn.setCursor(Qt.PointingHandCursor)
		mb=C['prim'] if current_val=="multi" else "transparent"
		self.m_btn.setStyleSheet(f"QPushButton{{background:qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 red,stop:0.17 orange,stop:0.33 yellow,stop:0.5 green,stop:0.67 blue,stop:0.83 indigo,stop:1 violet);border-radius:8px;border:2px solid {mb};}}QPushButton:hover{{border-color:{C['prim']};}}")
		self.m_btn.clicked.connect(lambda:self.select("multi"));gl.addWidget(self.m_btn,0,0,4,1)
		for i,c in enumerate(colors):
			btn=QPushButton();btn.setFixedSize(40,40);btn.setCursor(Qt.PointingHandCursor)
			bb=C['prim'] if c==current_val else "transparent"
			btn.setStyleSheet(f"QPushButton{{background-color:{c};border-radius:4px;border:2px solid {bb};}}QPushButton:hover{{border-color:{C['prim']};}}")
			btn.clicked.connect(lambda _,col=c:self.select(col));gl.addWidget(btn,i//10,1+i%10)
	def select(self,v):self.selected=v;self.accept()
class MatrixConfigDialog(QDialog):
	def __init__(self,parent):
		super().__init__(parent);self.setWindowFlags(Qt.FramelessWindowHint|Qt.Dialog);self.setAttribute(Qt.WA_TranslucentBackground);self.setFixedSize(400,380)
		l=QVBoxLayout(self);f=QFrame();f.setObjectName("MatConfigDialog");l.addWidget(f);lay=QVBoxLayout(f)
		lay.setContentsMargins(30,10,30,10);lay.setSpacing(10);lay.setAlignment(Qt.AlignCenter)
		ico=QLabel("🔑");ico.setStyleSheet("font-size:80px;background:transparent;margin:3px;");ico.setAlignment(Qt.AlignCenter);lay.addWidget(ico)
		tl=QLabel(sys_math.m_s('t') if sys_math else "Activation");tl.setObjectName("MatConfigTitle");tl.setAlignment(Qt.AlignCenter);lay.addWidget(tl)
		msg=QLabel(sys_math.m_s('m') if sys_math else "Enter key:");msg.setObjectName("MatConfigMsg");msg.setAlignment(Qt.AlignCenter);msg.setWordWrap(True);lay.addWidget(msg)
		self.inp=QLineEdit();self.inp.setObjectName("MatConfigInput");self.inp.setPlaceholderText("XXXX-XXXX-XXXX-XXXX");self.inp.setAlignment(Qt.AlignCenter);self.inp.setMaxLength(50)
		lay.addWidget(self.inp);self.inp.textChanged.connect(lambda:self.res_lbl.setText(""));self.setFocus()
		buy_lbl=QLabel(f"<a href='{sys_math.m_s('g') if sys_math else ''}' style='color:{C['prim']};text-decoration:none;font-weight:bold;'>Don't have a key? Buy it here</a>");buy_lbl.setOpenExternalLinks(True);buy_lbl.setAlignment(Qt.AlignCenter);lay.addWidget(buy_lbl)
		btn_lay=QHBoxLayout();lay.addLayout(btn_lay)
		self.btn=QPushButton("ACTIVATE");self.btn.setObjectName("SuccessBtn");self.btn.setCursor(Qt.PointingHandCursor);self.btn.clicked.connect(self.do_act);btn_lay.addWidget(self.btn)
		self.c_btn=QPushButton("CANCEL");self.c_btn.setObjectName("CleanBtn");self.c_btn.setCursor(Qt.PointingHandCursor);self.c_btn.clicked.connect(self.reject);btn_lay.addWidget(self.c_btn)
		self.res_lbl=QLabel("");self.res_lbl.setAlignment(Qt.AlignCenter);lay.addWidget(self.res_lbl)
	def do_act(self):
		k=self.inp.text().strip()
		if len(k)<3:self.res_lbl.setText(sys_math.m_s('s3') if sys_math else "Err");return
		if not (sys_math.m_n() if sys_math else False):self.res_lbl.setText("No connection");return
		self.btn.setEnabled(False);self.res_lbl.setText(sys_math.m_s('s4') if sys_math else "...");QApplication.processEvents()
		try:
			ok,msg=sys_math.m_a(k) if sys_math else (False,"No module")
			self.res_data=(ok,sys_math.m_s('s1') if (ok and sys_math) else f"{sys_math.m_s('s2') if sys_math else ''}{str(msg)[:50]}")
			self.accept()
		except Exception as e:
			self.res_data=(False,f"Critical error: {str(e)[:50]}")
			self.accept()
class MatrixStatusDialog(QDialog):
	def __init__(self,parent,ok,msg):
		super().__init__(parent);self.setWindowFlags(Qt.FramelessWindowHint|Qt.Dialog);self.setAttribute(Qt.WA_TranslucentBackground);self.setFixedSize(380,320)
		l=QVBoxLayout(self);l.setContentsMargins(0,0,0,0);f=QFrame();f.setObjectName("StatusFrame")
		f.setStyleSheet(f"QFrame#StatusFrame {{background-color:{C['surf']};border-radius:12px;border:none;outline:none;}}")
		l.addWidget(f);lay=QVBoxLayout(f);lay.setContentsMargins(30,5,30,15);lay.setSpacing(10);lay.addStretch()
		ico=QLabel("✅" if ok else "❌");ico.setStyleSheet("font-size:80px;background:transparent;");ico.setAlignment(Qt.AlignCenter);lay.addWidget(ico)
		tl=QLabel("Success!" if ok else "Error");tl.setObjectName("SuccessTitle");tl.setAlignment(Qt.AlignCenter);lay.addWidget(tl)
		m=QLabel(msg);m.setObjectName("SuccessMsg");m.setAlignment(Qt.AlignCenter);m.setWordWrap(True);lay.addWidget(m)
		btn=QPushButton("CONTINUE" if ok else "TRY AGAIN");btn.setObjectName("SuccessBtn");btn.setCursor(Qt.PointingHandCursor);btn.clicked.connect(self.accept);lay.addWidget(btn,0,Qt.AlignCenter)
		lay.addStretch()
class AboutDialog(QDialog):
	def __init__(self,parent):
		super().__init__(parent);self.setWindowFlags(Qt.FramelessWindowHint|Qt.Dialog);self.setAttribute(Qt.WA_TranslucentBackground);self.setFixedSize(380,360)
		l=QVBoxLayout(self);f=QFrame();f.setObjectName("SuccessDialog");l.addWidget(f);lay=QVBoxLayout(f)
		lay.setContentsMargins(30,5,30,15);lay.setSpacing(10);lay.setAlignment(Qt.AlignCenter)
		ico=QLabel("🎵");ico.setStyleSheet("font-size:70px;background:transparent;");ico.setAlignment(Qt.AlignCenter);lay.addWidget(ico)
		tl=QLabel(f"Audio Spectrum {sys_math.m_s('p') if (SME and sys_math) else ''}");tl.setObjectName("SuccessTitle");tl.setAlignment(Qt.AlignCenter);lay.addWidget(tl)
		msg=QLabel(f"Version: {VERSION}\nCreated by Aljnk");msg.setObjectName("SuccessMsg");msg.setAlignment(Qt.AlignCenter);lay.addWidget(msg)
		git=QPushButton("VISIT GITHUB");git.setObjectName("SuccessBtn");git.setCursor(Qt.PointingHandCursor);git.setFixedWidth(220);git.clicked.connect(lambda:webbrowser.open(f"https://github.com/{UPDATE_URL}"));lay.addWidget(git,0,Qt.AlignCenter)
		btn=QPushButton("CLOSE");btn.setObjectName("CleanBtn");btn.setFixedWidth(220);btn.setCursor(Qt.PointingHandCursor);btn.clicked.connect(self.accept);lay.addWidget(btn,0,Qt.AlignCenter)
class UpdateDialog(QDialog):
	def __init__(self,parent,ver=None,url=None,err=None):
		super().__init__(parent);self.setWindowFlags(Qt.FramelessWindowHint|Qt.Dialog);self.setAttribute(Qt.WA_TranslucentBackground);self.setFixedSize(380,340)
		l=QVBoxLayout(self);f=QFrame();f.setObjectName("SuccessDialog");l.addWidget(f);lay=QVBoxLayout(f)
		lay.setContentsMargins(30,5,30,15);lay.setSpacing(10);lay.setAlignment(Qt.AlignCenter)
		ico_s,tit_s,msg_s="✨","Up to Date","You are using the latest version."
		if err:ico_s,tit_s,msg_s="⚠️","No Connection",err
		elif ver:ico_s,tit_s,msg_s="🚀","New Version!",f"Version {ver} is available."
		ico=QLabel(ico_s);ico.setStyleSheet("font-size:70px;background:transparent;");ico.setAlignment(Qt.AlignCenter);lay.addWidget(ico)
		tl=QLabel(tit_s);tl.setObjectName("SuccessTitle");tl.setAlignment(Qt.AlignCenter);lay.addWidget(tl)
		msg=QLabel(msg_s);msg.setObjectName("SuccessMsg");msg.setAlignment(Qt.AlignCenter);msg.setWordWrap(True);lay.addWidget(msg)
		if ver and not err:
			btn=QPushButton("DOWNLOAD");btn.setObjectName("SuccessBtn");btn.setFixedWidth(220);btn.setCursor(Qt.PointingHandCursor);btn.clicked.connect(lambda:webbrowser.open(url));lay.addWidget(btn,0,Qt.AlignCenter)
		c=QPushButton("CLOSE");c.setObjectName("CleanBtn");c.setFixedWidth(220);c.setCursor(Qt.PointingHandCursor);c.clicked.connect(self.accept);lay.addWidget(c,0,Qt.AlignCenter)
class MainWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		self.setWindowTitle(f" Audio Spectrum {sys_math.m_s('p') if (SME and sys_math) else ''}");self.resize(1200,750);self.setAcceptDrops(True);self.setStyleSheet(STYLE_SHEET);self.repo={}
		self.setWindowIcon(QIcon(rp(os.path.join("assets","images","icon.ico"))))
		self._p=QSoundEffect(self);self._p.setVolume(1.0)
		self.tm=TooltipManager(self);self.loader=Preloader(self)
		self.tasks_q,self.active_th,self.is_rendering=[],[],False;self.max_w=min(4,max(1,os.cpu_count()//4))
		self.custom_mix_ids,self.has_errors,self.has_loggable_errors=[],False,False
		root=QWidget();self.setCentralWidget(root);lay=QVBoxLayout(root);lay.setSpacing(15);lay.setContentsMargins(20,20,20,20)
		self._init_menu()
		top_lay=QHBoxLayout();top_lay.setSpacing(15)
		self.b_add=QPushButton("📄 Add Files");self.b_add.setObjectName("AddBtn");self.b_add.setMinimumHeight(48)
		self.b_add.setToolTip("Add audio files to the list");self.b_add.clicked.connect(self.add_manual);self.b_add.installEventFilter(self.tm);self.b_add.setCursor(Qt.PointingHandCursor)
		self.lbl_drop=QLabel("Drag & Drop Audios");self.lbl_drop.setObjectName("DropArea");self.lbl_drop.setAlignment(Qt.AlignCenter);self.lbl_drop.setMinimumHeight(48)
		self.lbl_drop.setToolTip("Drag files here");self.lbl_drop.mousePressEvent=lambda e:self.add_manual();self.lbl_drop.installEventFilter(self.tm);self.lbl_drop.setCursor(Qt.DragCopyCursor)
		top_lay.addWidget(self.b_add,1);top_lay.addWidget(self.lbl_drop,1);lay.addLayout(top_lay)
		bk_lay=QHBoxLayout();bk_lay.setSpacing(10)
		lbl_all=QLabel("CHANGE ALL:");lbl_all.setStyleSheet(f"font-weight:bold;color:{C['mute']};margin-left:5px;");bk_lay.addWidget(lbl_all)
		self.b_bk_t=QPushButton("Types");self.b_bk_t.setObjectName("CleanBtn");self.b_bk_t.clicked.connect(self.bulk_tmpl)
		self.b_bk_s=QPushButton("Stroke Thicknesses");self.b_bk_s.setObjectName("CleanBtn");self.b_bk_s.clicked.connect(self.bulk_stroke)
		self.b_bk_c=QPushButton("Stroke Colors");self.b_bk_c.setObjectName("CleanBtn");self.b_bk_c.clicked.connect(self.bulk_color)
		self.b_bk_sp=QPushButton("Spectrum Colors");self.b_bk_sp.setObjectName("CleanBtn");self.b_bk_sp.clicked.connect(self.bulk_spec)
		for b in [self.b_bk_t,self.b_bk_s,self.b_bk_c,self.b_bk_sp]:
			b.setCursor(Qt.PointingHandCursor);b.installEventFilter(self.tm);bk_lay.addWidget(b)
		bk_lay.addStretch();self.b_srt=QPushButton("Sort ↕");self.b_srt.setObjectName("CleanBtn");self.b_srt.setCursor(Qt.PointingHandCursor);self.b_srt.installEventFilter(self.tm)
		self.ms=QMenu(self);self.ms.addAction("Name",lambda:self.sort_list("n"));self.ms.addAction("Size",lambda:self.sort_list("s"));self.ms.addAction("Date",lambda:self.sort_list("d"))
		self.b_srt.clicked.connect(lambda:self.ms.exec(QCursor.pos()));bk_lay.addWidget(self.b_srt);lay.addLayout(bk_lay)
		self.lst_c=QFrame();self.lst_c.setObjectName("ListContainer");lay.addWidget(self.lst_c)
		l_c=QVBoxLayout(self.lst_c);l_c.setContentsMargins(1,1,1,1);l_c.setSpacing(0)
		self.lst=QListWidget();self.lst.setObjectName("AudioList");self.lst.setFrameShape(QFrame.NoFrame);self.lst.setDragEnabled(True);self.lst.setAcceptDrops(True);self.lst.setDropIndicatorShown(True);self.lst.setDragDropMode(QListWidget.InternalMove);self.lst.setDefaultDropAction(Qt.MoveAction);l_c.addWidget(self.lst)
		tool_lay=QHBoxLayout();self.total_pbar=QProgressBar();self.total_pbar.setObjectName("TotalPbar");self.total_pbar.hide();tool_lay.addWidget(self.total_pbar)
		self.total_tasks,self.completed_tasks,self.task_progress=0,0,{}
		self.b_all=QPushButton("Remove All");self.b_all.setObjectName("CleanAllBtn")
		self.b_all.setToolTip("Clear the entire list");self.b_all.clicked.connect(self.clear_all);self.b_all.installEventFilter(self.tm);self.b_all.setCursor(Qt.PointingHandCursor)
		self.b_clean=QPushButton("Remove Completed");self.b_clean.setObjectName("CleanBtn")
		self.b_clean.setToolTip("Remove only finished tracks");self.b_clean.clicked.connect(self.remove_completed);self.b_clean.installEventFilter(self.tm);self.b_clean.setCursor(Qt.PointingHandCursor)
		self.b_stop=QPushButton("Stop Processing");self.b_stop.setObjectName("StopBtn")
		self.b_stop.setToolTip("Abort work and delete temporary files");self.b_stop.clicked.connect(self.stop_task);self.b_stop.installEventFilter(self.tm);self.b_stop.setCursor(Qt.PointingHandCursor)
		tool_lay.addStretch();tool_lay.addWidget(self.b_all);tool_lay.addWidget(self.b_clean);tool_lay.addWidget(self.b_stop);lay.addLayout(tool_lay)
		self.b_run=QPushButton("CREATE SPECTRUMS");self.b_run.setObjectName("MainBtn")
		self.b_run.setToolTip("Start processing all new files");self.b_run.clicked.connect(self.run_task);lay.addWidget(self.b_run);self.b_run.installEventFilter(self.tm);self.b_run.setCursor(Qt.PointingHandCursor)
		self.update_buttons()
		self.m_timer=QTimer(self);self.m_timer.setSingleShot(True);self.m_timer.timeout.connect(self.m_v_silent);self.m_timer.start(30000)
		self.m_chk=False
	def _init_menu(self):
		mb=self.menuBar()
		m_set=mb.addMenu("Settings");m_thm=m_set.addMenu("Theme")
		def add_t(n,v):
			a=m_thm.addAction(n);a.triggered.connect(lambda:self.set_theme(v))
		add_t("System Default","auto")
		for f in glob.glob(rp(os.path.join("assets","themes","*.thm"))):
			tn=os.path.basename(f).replace(".thm","");add_t(tn.title(),tn)
		m_ab=mb.addMenu("About")
		a_abt=m_ab.addAction("About App");a_abt.triggered.connect(self.show_about)
		a_upd=m_ab.addAction("Check for Updates");a_upd.triggered.connect(self.check_updates)
		m_ab.addSeparator()
		if sys_math and os.path.exists(rp(sys_math.m_s('tp'))):
			self.a_act=m_ab.addAction(sys_math.m_s('a') if sys_math else "");self.a_act.triggered.connect(self.show_matrix_config)
			if SME:self.a_act.setEnabled(False);self.a_act.setText(sys_math.m_s('d') if sys_math else "")
		else:
			a_full=m_ab.addAction(sys_math.m_s('f') if sys_math else "Get Pro Version");a_full.triggered.connect(lambda:webbrowser.open(f"https://github.com/{UPDATE_URL}/releases/latest"))
	def check_updates(self,quiet=True):
		if sys_math and not sys_math.m_n():
			if not quiet:self.exec_ov(UpdateDialog(self,err="Check internet connection"))
			return
		try:
			r=requests.get(f"https://api.github.com/repos/{UPDATE_URL}/releases/latest",timeout=3)
			lg(f"https://api.github.com/repos/{UPDATE_URL}/releases/latest")
			lg(r.status_code)
			if r.status_code==200:
				d=r.json();v=d.get("tag_name")
				if v and v.lstrip('v') > VERSION.lstrip('v'):self.exec_ov(UpdateDialog(self,v,d.get("html_url")))
				elif not quiet:self.exec_ov(UpdateDialog(self))
			elif not quiet:self.exec_ov(UpdateDialog(self,err="Server error"))
		except:
			if not quiet:self.exec_ov(UpdateDialog(self,err="Connection lost"))
	def sort_list(self,m):
		self.lst.setUpdatesEnabled(False)
		try:
			for i in range(self.lst.count()):
				it=self.lst.item(i);p=it.data(Qt.UserRole)
				if not os.path.exists(p):v="0" if m!="n" else ""
				elif m=="n":v=os.path.basename(p).lower()
				elif m=="s":v=str(os.path.getsize(p)).zfill(25)
				else:v=str(int(os.path.getctime(p))).zfill(25)
				it.setText(v)
			self.lst.sortItems(Qt.AscendingOrder)
			for i in range(self.lst.count()):self.lst.item(i).setText("")
		except:pass
		finally:self.lst.setUpdatesEnabled(True)
	def show_about(self):self.exec_ov(AboutDialog(self))
	def show_matrix_config(self):
		while True:
			dlg=MatrixConfigDialog(self)
			if self.exec_ov(dlg):
				if hasattr(dlg,'res_data'):
					ok,msg=dlg.res_data
					self.exec_ov(MatrixStatusDialog(self,ok,msg))
					if ok:
						global SME,SMV;SMV=sys_math.m_v();SME=sys_math.m_p() if SMV else 0
						self.setWindowTitle(f"Audio Spectrum {sys_math.m_s('p') if sys_math else ''}")
						self.a_act.setEnabled(False);self.a_act.setText(sys_math.m_s('d') if sys_math else "")
						self.update_buttons();break
					continue
				break
			else:break
	def set_theme(self,n):
		settings.setValue("theme",n);global C,STYLE_SHEET
		st=get_sys_theme();tl=n if n!="auto" else st
		nc=load_theme(tl)
		if not nc:nc=load_theme("light")
		if not nc:nc=DEFAULT_C
		C.clear();C.update(nc);STYLE_SHEET=get_sheet(C);self.setStyleSheet(STYLE_SHEET)
	def exec_ov(self,d):
		ov=QWidget(self);ov.setStyleSheet(f"background:{C['overlay']}");ov.setGeometry(self.rect());ov.show();ov.raise_()
		d.setWindowModality(Qt.NonModal);d.show();d.raise_()
		g=d.geometry();cp=self.mapToGlobal(self.rect().center());cp.setY(cp.y()-35);g.moveCenter(cp);d.move(g.topLeft())
		loop=QEventLoop();d.finished.connect(loop.quit);ov.mousePressEvent=lambda e:d.reject()
		loop.exec();ov.hide();ov.deleteLater();QApplication.processEvents();return d.result()
	def dragEnterEvent(self,e):
		if e.mimeData().hasUrls():e.accept()
	def dropEvent(self,e):
		for u in e.mimeData().urls():self.add_item(u.toLocalFile())
		self.activateWindow()
	def add_manual(self):
		fs,_=QFileDialog.getOpenFileNames(self,"Audio","","*.mp3 *.wav *.flac *.m4a")
		for f in fs:self.add_item(f)
	def add_item(self,path):
		if not path.lower().endswith(('.mp3','.wav','.flac','.m4a')):return
		w=QWidget();l=QHBoxLayout(w);l.setContentsMargins(10,0,10,0);l.setSpacing(10)
		name_lbl=QLabel(os.path.basename(path));name_lbl.setObjectName("NameLbl");l.addWidget(name_lbl,1)
		pbar=QProgressBar();pbar.setFixedWidth(130);pbar.hide();l.addWidget(pbar)
		b_fold=QPushButton("📁");b_fold.setObjectName("RowActionBtn");b_fold.setToolTip("Open folder");b_fold.hide();b_fold.installEventFilter(self.tm);l.addWidget(b_fold)
		b_fold.setCursor(Qt.PointingHandCursor);l.addSpacing(-7)
		b_play=QPushButton("▶️");b_play.setObjectName("PlayBtn");b_play.setToolTip("Open video");b_play.hide();b_play.installEventFilter(self.tm);l.addWidget(b_play)
		b_play.setCursor(Qt.PointingHandCursor);l.addSpacing(-7)
		ico_lbl=QLabel();ico_lbl.setObjectName("IconLbl");ico_lbl.setAlignment(Qt.AlignRight|Qt.AlignVCenter);ico_lbl.setFixedSize(30,30);l.addWidget(ico_lbl);l.addSpacing(-7)
		txt_lbl=QLabel();txt_lbl.setObjectName("TxtLbl");txt_lbl.setFixedWidth(80);l.addWidget(txt_lbl);l.addSpacing(-40)
		btn_tmpl=QPushButton();btn_tmpl.setObjectName("TmplBtn");btn_tmpl.setFixedWidth(155);btn_tmpl.setCursor(Qt.PointingHandCursor);btn_tmpl.setProperty("tmpl_id","simple_linear");btn_tmpl.setFocusPolicy(Qt.NoFocus)
		btl=QHBoxLayout(btn_tmpl);btl.setContentsMargins(4,0,4,0);btl.setSpacing(0)
		ico_l=QLabel();ico_l.setObjectName("TmplIcon");ico_l.setFixedSize(24,24);ico_l.setAlignment(Qt.AlignCenter);ico_l.setAttribute(Qt.WA_TransparentForMouseEvents)
		txt_l=QLabel("Linear Simple");txt_l.setObjectName("TmplText");txt_l.setAlignment(Qt.AlignCenter);txt_l.setAttribute(Qt.WA_TransparentForMouseEvents)
		btl.addWidget(ico_l);btl.addWidget(txt_l,1);l.addWidget(btn_tmpl)
		btn_stroke=QPushButton();btn_stroke.setObjectName("StrokeBtn");btn_stroke.setToolTip("Stroke thickness");btn_stroke.setCursor(Qt.PointingHandCursor);btn_stroke.installEventFilter(self.tm);btn_stroke.setFocusPolicy(Qt.NoFocus);l.addWidget(btn_stroke)
		btn_stroke.setProperty("stroke_id","Medium")
		btn_color=QPushButton();btn_color.setObjectName("StrokeBtn");btn_color.setToolTip("Color Scheme");btn_color.setCursor(Qt.PointingHandCursor);btn_color.installEventFilter(self.tm);btn_color.setFocusPolicy(Qt.NoFocus);l.addWidget(btn_color)
		btn_color.setProperty("color_id","Black")
		btn_spec=QPushButton();btn_spec.setObjectName("StrokeBtn");btn_spec.setToolTip("Spectrum Color");btn_spec.setCursor(Qt.PointingHandCursor);btn_spec.installEventFilter(self.tm);btn_spec.setFocusPolicy(Qt.NoFocus);l.addWidget(btn_spec)
		btn_spec.setProperty("spec_id","multi");self.set_spec_btn_icon(btn_spec,"multi")
		c_img_p=rp(os.path.join("assets","images","colors","black.svg"))
		if os.path.exists(c_img_p):btn_color.setIcon(QIcon(c_img_p));btn_color.setIconSize(QSize(30,30))
		s_img_p=rp(os.path.join("assets","images","strokes","medium.svg"))
		if os.path.exists(s_img_p):btn_stroke.setIcon(QIcon(s_img_p));btn_stroke.setIconSize(QSize(30,30))
		btn=QPushButton("Remove");btn.setObjectName("RemoveRowBtn");btn.setFixedWidth(70);btn.setToolTip("Remove track");btn.installEventFilter(self.tm);l.addWidget(btn);btn.setCursor(Qt.PointingHandCursor)
		it=QListWidgetItem(self.lst);it.setSizeHint(QSize(w.sizeHint().width(),60));uid=f"{path}_{time.time()}"
		it.setData(Qt.UserRole,path);it.setData(Qt.UserRole+10,uid);it.setData(Qt.UserRole+3,"New")
		self.repo[uid]={'tmpl':(btn_tmpl,ico_l,txt_l),'st':(ico_lbl,txt_lbl),'pb':pbar,'rem':btn,'act':(b_fold,b_play),'s':btn_stroke,'c':btn_color,'sp':btn_spec}
		btn_spec.clicked.connect(lambda:self.open_spectrum_gallery(it))
		btn_color.clicked.connect(lambda:self.open_color_gallery(it))
		btn_stroke.clicked.connect(lambda:self.open_stroke_gallery(it))
		self.lst.addItem(it);self.lst.setItemWidget(it,w)
		btn.clicked.connect(lambda:(self.repo.pop(it.data(Qt.UserRole+10),None),self.lst.takeItem(self.lst.row(it)),self.update_buttons()))
		btn_tmpl.clicked.connect(lambda:self.open_gallery(it))
		b_fold.clicked.connect(lambda:subprocess.run(f'explorer /select,"{self.get_out_path(it)}"',shell=True))
		b_play.clicked.connect(lambda:os.startfile(self.get_out_path(it)))
		img_p=rp(os.path.join("assets","images","templates","simple_linear.svg"))
		if not os.path.exists(img_p):img_p=rp(os.path.join("assets","images","templates","new.svg"))
		if os.path.exists(img_p):ico_l.setPixmap(QIcon(img_p).pixmap(30,30))
		self.check_file_status(it);self.update_buttons()
	def open_gallery(self,it):
		data=self.repo[it.data(Qt.UserRole+10)]['tmpl'];btn=data[0];dlg=TemplateGallery(self,btn.property("tmpl_id"),bulk=False)
		if self.exec_ov(dlg):
			if dlg.selected=="mix_creator":self.run_mix_constructor();return
			name=dlg.selected
			is_p=sys_math and name in sys_math.m_m()
			if is_p and not SME:
				self.show_matrix_config()
				if not SME:return
			btn,ico,txt=data;txt.setText(name.replace("_"," ").title());btn.setProperty("tmpl_id",name)
			img_p=rp(os.path.join("assets","images","templates",f"{name}.svg"))
			if not os.path.exists(img_p):img_p=rp(os.path.join("assets","images","templates","new.svg"))
			if os.path.exists(img_p):ico.setPixmap(QIcon(img_p).pixmap(30,30))
			self.check_file_status(it)
		QTimer.singleShot(0,lambda:(btn.setAttribute(Qt.WA_UnderMouse,False),btn.style().unpolish(btn),btn.style().polish(btn)))
	def _row_dlg(self,it,role,prop,dlg_cls,upd_fn):
		b=self.repo[it.data(Qt.UserRole+10)][role];dlg=dlg_cls(self,b.property(prop))
		if self.exec_ov(dlg):
			v=dlg.selected;b.setProperty(prop,v);upd_fn(b,v);self.check_file_status(it)
		QTimer.singleShot(0,lambda:(b.setAttribute(Qt.WA_UnderMouse,False),b.style().unpolish(b),b.style().polish(b)))
	def open_stroke_gallery(self,it):self._row_dlg(it,'s',"stroke_id",StrokeGallery,lambda b,v:b.setIcon(QIcon(rp(os.path.join("assets","images","strokes",f"{v.lower().replace(' ','_')}.svg")))))
	def open_color_gallery(self,it):self._row_dlg(it,'c',"color_id",ColorGallery,lambda b,v:b.setIcon(QIcon(rp(os.path.join("assets","images","colors",f"{v.lower().replace(' ','_')}.svg")))))
	def open_spectrum_gallery(self,it):self._row_dlg(it,'sp',"spec_id",SpectrumColorGallery,self.set_spec_btn_icon)
	def set_spec_btn_icon(self,btn,v):
		px=QPixmap(30,30);px.fill(Qt.transparent);p=QPainter(px);p.setRenderHint(QPainter.Antialiasing)
		if v=="multi":
			g=QLinearGradient(3,3,27,27);g.setColorAt(0,"red");g.setColorAt(0.15,"red");g.setColorAt(0.30,"orange");g.setColorAt(0.45,"yellow");g.setColorAt(0.60,"green");g.setColorAt(0.70,"blue");g.setColorAt(0.80,"darkorchid");g.setColorAt(1,"violet");p.setBrush(g)
		else:p.setBrush(QColor(v))
		p.setPen(QPen(QColor(0,0,0),1.5));p.drawEllipse(3,3,24,24);p.end();btn.setIcon(QIcon(px));btn.setIconSize(QSize(30,30))
	def find_item_by_uid(self,uid):
		for i in range(self.lst.count()):
			it=self.lst.item(i)
			if it.data(Qt.UserRole+10)==uid:return it
		return None
	def get_out_path(self,it):
		r=self.repo[it.data(Qt.UserRole+10)];p,data,btn_s,btn_c,btn_sp=it.data(Qt.UserRole),r['tmpl'],r['s'],r['c'],r['sp']
		h_str=f"{data[0].property('tmpl_id')}_{btn_s.property('stroke_id')}_{btn_c.property('color_id')}_{btn_sp.property('spec_id')}"
		return os.path.abspath(os.path.splitext(p)[0]+f"_{get_settings_hash(h_str)}.mp4")
	def check_file_status(self,it):
		s="Exist" if os.path.exists(self.get_out_path(it)) else "New"
		self.set_status_visual(it,s);it.setData(Qt.UserRole+3,s);self.update_buttons()
	def set_status_visual(self,it,s):
		r=self.repo[it.data(Qt.UserRole+10)];ico,txt=r['st'];bf,bp=r['act']
		bf.hide();bp.hide()
		if s=="New":ico.setText("🔵");txt.setText("New");txt.setStyleSheet(f"color:{C['prim']};")
		elif s=="Exist":ico.setText("🟡");txt.setText("Exists");txt.setStyleSheet(f"color:{C['gold_stat']};");bf.show();bp.show()
		elif s=="Done":ico.setText("✅");txt.setText("Done");txt.setStyleSheet(f"color:{C['green_stat']};");bf.show();bp.show()
		elif s=="Work":ico.setText("⏳");txt.setText("Work");txt.setStyleSheet(f"color:{C['mute']};")
		elif s=="Fail":ico.setText("🔴");txt.setText("Error");txt.setStyleSheet(f"color:{C['red_m']};")
		elif s=="Clone":ico.setText("🔁");txt.setText("Clone");txt.setStyleSheet(f"color:{C['mute']};")
		
	def update_buttons(self):
		proc,cnt=bool(self.active_th),self.lst.count()
		self.b_all.setEnabled(cnt>0 and not proc);self.b_clean.setEnabled(cnt>0 and any(self.lst.item(i).data(Qt.UserRole+3) in ["Done","Exist","Clone"] for i in range(cnt)))
		self.b_stop.setEnabled(proc);self.b_run.setEnabled(cnt>0 and not proc)
		for b in [self.b_bk_t,self.b_bk_s,self.b_bk_c,self.b_bk_sp,self.b_srt]:b.setEnabled(cnt>0 and not proc)
		for i in range(cnt):
			it=self.lst.item(i)
			r=self.repo[it.data(Qt.UserRole+10)]
			r['tmpl'][0].setEnabled(not proc)
			r['rem'].setEnabled(not proc)
			r['s'].setEnabled(not proc)
			r['c'].setEnabled(not proc)
			r['sp'].setEnabled(not proc)
	def m_v_silent(self):
		if getattr(self,'m_chk',False):return True
		self.m_chk=True
		if hasattr(self,'m_timer') and self.m_timer.isActive():self.m_timer.stop()
		global SME,SMV
		if SME and sys_math:
			if not sys_math.m_v():
				SME=0;SMV=None
				sys_math.m_d()
				self.setWindowTitle(self.windowTitle().replace(f" {sys_math.m_s('p') if sys_math else ''}",""))
				if hasattr(self,'a_act'):self.a_act.setEnabled(True);self.a_act.setText(sys_math.m_s('a') if sys_math else "")
				for n in sys_math.m_m():
					if n in TMPL_CONFIGS:del TMPL_CONFIGS[n]
				self.update_buttons();self.stop_task();return False
		return True
	def apply_custom_mix(self):
		if not self.custom_mix_ids or not self.lst.count():return
		for i in range(self.lst.count()):
			n=self.custom_mix_ids[i%len(self.custom_mix_ids)];it=self.lst.item(i);btn,ico,txt=self.repo[it.data(Qt.UserRole+10)]['tmpl']
			txt.setText(n.replace("_"," ").title());btn.setProperty("tmpl_id",n)
			p=rp(os.path.join("assets","images","templates",f"{n}.svg"))
			if not os.path.exists(p):p=rp(os.path.join("assets","images","templates","new.svg"))
			if os.path.exists(p):ico.setPixmap(QIcon(p).pixmap(30,30))
			self.check_file_status(it);btn.style().unpolish(btn);btn.style().polish(btn)
	def run_mix_constructor(self):
		items=[]
		for n in STD_T: items.append((n, False))
		if sys_math:
			for n in sys_math.m_m().keys(): items.append((n, True))
		d=MixSelector(self,items,self.custom_mix_ids)
		if self.exec_ov(d):
			self.custom_mix_ids=d.get_sel()
			self.apply_custom_mix()
	def bulk_tmpl(self):
		if not self.lst.count():return
		dlg=TemplateGallery(self,self.repo[self.lst.item(0).data(Qt.UserRole+10)]['tmpl'][0].property("tmpl_id"),bulk=True)
		if self.exec_ov(dlg):
			sel=dlg.selected
			if sel=="mix_creator":self.run_mix_constructor();return
			is_p=sys_math and sel in sys_math.m_m()
			if is_p and not SME:
				self.show_matrix_config()
				if not SME:return
			for i in range(self.lst.count()):
				it=self.lst.item(i);btn,ico,txt=self.repo[it.data(Qt.UserRole+10)]['tmpl']
				txt.setText(sel.replace("_"," ").title());btn.setProperty("tmpl_id",sel)
				img_p=rp(os.path.join("assets","images","templates",f"{sel}.svg"))
				if not os.path.exists(img_p):img_p=rp(os.path.join("assets","images","templates","new.svg"))
				if os.path.exists(img_p):ico.setPixmap(QIcon(img_p).pixmap(30,30))
				self.check_file_status(it);btn.style().unpolish(btn);btn.style().polish(btn)
			QTimer.singleShot(0,lambda:(self.b_bk_t.setAttribute(Qt.WA_UnderMouse,False),self.b_bk_t.style().unpolish(self.b_bk_t),self.b_bk_t.style().polish(self.b_bk_t)))
	def _bulk_op(self,role,prop,dlg_cls,upd_fn):
		if not self.lst.count():return
		v0=self.repo[self.lst.item(0).data(Qt.UserRole+10)][role].property(prop)
		dlg=dlg_cls(self,v0)
		if self.exec_ov(dlg):
			for i in range(self.lst.count()):
				it=self.lst.item(i);b=self.repo[it.data(Qt.UserRole+10)][role];v=dlg.selected;b.setProperty(prop,v)
				upd_fn(it,b,v);self.check_file_status(it);b.style().unpolish(b);b.style().polish(b)
	def bulk_stroke(self):self._bulk_op('s',"stroke_id",StrokeGallery,lambda it,b,v:b.setIcon(QIcon(rp(os.path.join("assets","images","strokes",f"{v.lower().replace(' ','_')}.svg")))))
	def bulk_color(self):self._bulk_op('c',"color_id",ColorGallery,lambda it,b,v:b.setIcon(QIcon(rp(os.path.join("assets","images","colors",f"{v.lower().replace(' ','_')}.svg")))))
	def bulk_spec(self):self._bulk_op('sp',"spec_id",SpectrumColorGallery,lambda it,b,v:self.set_spec_btn_icon(b,v))
	def resizeEvent(self,e):
		super().resizeEvent(e);self.total_pbar.setFixedWidth(self.width()//2)
	def run_task(self):
		self.m_v_silent()
		self.tasks_q=[];self.has_errors=False;self.has_loggable_errors=False;seen_paths=set()
		for i in range(self.lst.count()):
			it=self.lst.item(i);self.check_file_status(it)
			if it.data(Qt.UserRole+3) in ["Exist","Done","Clone"]:continue
			out_p=self.get_out_path(it)
			if out_p in seen_paths:
				self.set_status_visual(it,"Clone");it.setData(Qt.UserRole+3,"Clone");continue
			seen_paths.add(out_p)
			r=self.repo[it.data(Qt.UserRole+10)];t_id=r['tmpl'][0].property("tmpl_id")
			if not SME and sys_math and t_id in sys_math.m_m():
				self.show_matrix_config();return
			s_id,c_id,sp_id=r['s'].property("stroke_id"),r['c'].property("color_id"),r['sp'].property("spec_id")
			self.tasks_q.append({'path':it.data(Qt.UserRole),'tmpl':r['tmpl'][0].property("tmpl_id"),'out_path':self.get_out_path(it),'uid':it.data(Qt.UserRole+10),'msvg':"-msvg" in sys.argv,'stroke':sw_map.get(s_id,8),'colors':sc_map.get(c_id,["#ffffff","#000000"]),'spec_color':sp_id,'key':SMV})
		if self.tasks_q:
			self.total_tasks,self.completed_tasks=len(self.tasks_q),0;self.task_progress={t['uid']:0 for t in self.tasks_q}
			self.total_pbar.setValue(0);self.total_pbar.setFormat(f"Total: 0% (0/{self.total_tasks})");self.total_pbar.show()
			self.is_rendering=True;self.start_next_tasks()
	def start_next_tasks(self):
		while len(self.active_th)<self.max_w and self.tasks_q:
			t=self.tasks_q.pop(0);th=RenderThread(t)
			th.item_start.connect(self.on_item_start);th.item_prog.connect(self.on_item_progress)
			th.item_done.connect(self.on_item_done);th.item_fail.connect(self.on_item_fail)
			th.finished.connect(lambda th=th:self.on_thread_finished(th))
			self.active_th.append(th);th.start();self.update_buttons()
	def on_thread_finished(self,th):
		if th in self.active_th:self.active_th.remove(th)
		if self.tasks_q or self.active_th:self.start_next_tasks()
		else:self.on_all_done()
	def stop_task(self):
		self.total_pbar.hide()
		self.loader.show();QApplication.processEvents();outs=[th.cur_out for th in self.active_th];self.tasks_q=[];self.is_rendering=False
		for th in self.active_th:th.stopped=True
		subprocess.run("taskkill /f /im ffmpeg.exe",shell=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
		for th in self.active_th:
			if not th.wait(3000):th.terminate();th.wait()
		time.sleep(0.5)
		for out in outs:
			if not out:continue
			if os.path.exists(out):
				for _ in range(10):
					try:os.remove(out);break
					except:time.sleep(0.2)
		t_dir=get_app_data("temp")
		if os.path.exists(t_dir):
			for f in glob.glob(os.path.join(t_dir,"*.mp3")):
				try:os.remove(f)
				except:pass
		for i in range(self.lst.count()):
			it=self.lst.item(i)
			if it.data(Qt.UserRole+3)=="Work":
				it.setData(Qt.UserRole+3,"New");self.set_status_visual(it,"New")
				pb=self.repo[it.data(Qt.UserRole+10)]['pb'];pb.hide();pb.setValue(0)
		self.active_th=[];self.on_all_done()
	def on_all_done(self):
		self.total_pbar.hide();self.loader.hide();self.update_buttons()
		if self.is_rendering:
			self.is_rendering=False;snd_p=rp(os.path.join("assets","sounds","finish.wav"))
			if os.path.exists(snd_p):self._p.setSource(QUrl.fromLocalFile(snd_p));self._p.play()
			QTimer.singleShot(100,lambda:self.exec_ov(SuccessDialog(self,self.has_errors,self.has_loggable_errors)))
	def remove_completed(self):
		for i in range(self.lst.count()-1,-1,-1):
			if self.lst.item(i).data(Qt.UserRole+3) in ["Done","Exist","Clone"]:
				it=self.lst.takeItem(i);self.repo.pop(it.data(Qt.UserRole+10),None)
		self.update_buttons()
	def clear_all(self):
		self.lst.clear();self.repo.clear();self.update_buttons()
	def on_item_start(self,uid):
		it=self.find_item_by_uid(uid)
		if it:it.setData(Qt.UserRole+3,"Work");pbar=self.repo[uid]['pb'];self.set_status_visual(it,"Work");pbar.setValue(0);pbar.setFormat("Loading...");pbar.show()
	def on_item_progress(self,uid,v,s):
		it=self.find_item_by_uid(uid)
		if it:
			pb=self.repo[uid]['pb'];pb.setValue(v);pb.setFormat(f"{s}: {v}%")
			if uid in self.task_progress and s=="Video":self.task_progress[uid]=v;self.update_total_progress()
	def on_item_done(self,uid):
		it=self.find_item_by_uid(uid)
		if it:
			self.repo[uid]['pb'].hide();self.set_status_visual(it,"Done");it.setData(Qt.UserRole+3,"Done")
			if uid in self.task_progress:self.task_progress[uid]=100;self.completed_tasks+=1;self.update_total_progress()
			self.update_buttons()
	def on_item_fail(self, uid, e):
		it = self.find_item_by_uid(uid)
		if it:
			self.repo[uid]['pb'].hide()
			self.set_status_visual(it, "Fail")
			it.setData(Qt.UserRole+3, "Fail")
			self.has_errors = True
			if "Security Error:" not in e:self.has_loggable_errors = True
			if uid in self.task_progress:self.task_progress[uid]=100;self.completed_tasks+=1;self.update_total_progress()
			try:
				with open(CURRENT_LOG, "a", encoding='utf-8') as f:
					f.write(f"\n{'='*20}\nTime: {time.ctime()}\nFile: {self.get_out_path(it)}\n{e}\n")
			except: pass
	def update_total_progress(self):
		if not self.total_tasks:return
		avg=sum(self.task_progress.values())/self.total_tasks
		self.total_pbar.setValue(int(avg));self.total_pbar.setFormat(f"Total: {int(avg)}% ({self.completed_tasks}/{self.total_tasks})")
	def closeEvent(self,e):
		if self.is_rendering or self.active_th:self.stop_task()
		e.accept()
def start():
	mp.freeze_support()
	if sys_math and sys_math.m_e():
		global SME,SMV;SMV=sys_math.g_k();SME=sys_math.m_p() if SMV else 0
		TMPL_CONFIGS.update(sys_math.m_m())
	ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("aljnk.audiospectrum.1.0")
	app=QApplication(sys.argv)
	app.setWindowIcon(QIcon(rp(os.path.join("assets","images","icon.ico"))))
	win=MainWindow();win.show();QTimer.singleShot(100, lambda: win.check_updates(quiet=True));sys.exit(app.exec())
if __name__=="__main__":start()