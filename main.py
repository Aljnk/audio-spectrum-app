import os
os.environ["AV_LOG_LEVEL"]="quiet"
os.environ["QT_LOGGING_RULES"]="qt.multimedia.*=false;*.debug=false"
import json,builtins,sys,ctypes,re,winreg,traceback,importlib,hashlib,subprocess,glob,requests,webbrowser,time,multiprocessing as mp
from PySide6.QtCore import Qt,QThread,Signal,QSize,QUrl,QTimer,QPropertyAnimation,QPoint,QEvent,QObject,QRect,QEventLoop,QSettings
from PySide6.QtWidgets import (QApplication,QMainWindow,QWidget,QVBoxLayout,QHBoxLayout,QPushButton,QListWidget,QListWidgetItem,QLabel,QFileDialog,QProgressBar,QDialog,QScrollArea,QGridLayout,QFrame,QLineEdit,QLayout,QMenu,QStackedWidget)
from PySide6.QtGui import QColor,QCursor,QPainter,QPen,QPixmap,QIcon,QLinearGradient
from PySide6.QtMultimedia import QSoundEffect

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
VERSION="2.0.0"
CACHE_TTL_SEC=7*24*60*60
UPDATE_URL="Aljnk/audio-spectrum-app"
TMPL_CONFIGS={"simple_circular":{"m":120},"simple_linear":{"m":50},"simple_square":{"m":76},"simple_triangle":{"m":66}}
STD_T=list(TMPL_CONFIGS.keys())
sw_map={"None":0,"Thin":3,"Small":5,"Medium":8,"Bold":12,"Black":20}
sc_map={"Black":["#ffffff","#000000"],"White":["#000000","#ffffff"],"Gray":["#ffffff","#808080"],"Dark Gray":["#ffffff","#404040"],"Light Gray":["#000000","#d3d3d3"],"Borderless":["#000000","#000000"]}
ss_map={"Solid":"solid","Gradient":"gradient"}
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
	QPushButton#MainBtn {{background-color:{c['prim']};border:none;color:{c['surf']};font-size:16px;padding:12px;border-radius:8px;font-weight:bold;min-height:18px;max-height:18px;}}
	QPushButton#MainBtn:hover {{background-color:{c['prim_h']};}}
	QPushButton#MainBtn:disabled {{background-color:{c['hold']};}}
	QPushButton#CleanBtn, QPushButton#CleanAllBtn {{background-color:{c['bord']};border:1px solid {c['bord']};color:{c['text']};font-size:12px;border-radius:4px;padding:6px 12px;min-height:18px;max-height:18px;}}
	QPushButton#CleanBtn:hover, QPushButton#CleanAllBtn:hover {{background-color:{c['accent']};}}
	QPushButton#StopBtn {{background-color:{c['red_m']};color:{c['surf']};border:none;border-radius:4px;font-weight:bold;font-size:12px;padding:6px 12px;min-height:18px;max-height:18px;}}
	QPushButton#StopBtn:hover {{background-color:{c['red_h']};}}
	QPushButton#CleanBtn:disabled, QPushButton#CleanAllBtn:disabled {{background-color:{c['item']};border-color:{c['bord']};color:{c['hold']};}}
	QPushButton#StopBtn:disabled {{background-color:{c['item']};color:{c['hold']};border:1px solid {c['bord']};font-weight:normal;}}
	QPushButton#RemoveRowBtn {{background-color:{c['red_m']};color:{c['surf']};border:none;border-radius:4px;font-size:13px;min-height:32px;max-height:32px;font-weight:bold;}}
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
	QLabel#CustomTip {{background-color:{c['text']};color:{c['surf']};padding:8px;border-radius:4px;font-size:12px;}}
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
	QMenu {{background-color:{c['surf']};border:1px solid {c['bord']};padding:5px;border-radius:7px;margin:4px;}}
	QMenu::item {{padding:6px 24px;color:{c['text']};}}
	QMenu::item:selected {{background-color:{c['bord']};}}
	QFrame#SuccessDialog, QFrame#MatConfigDialog {{background-color:{c['surf']};border:2px solid {c['hold']};border-radius:12px;}}
	QLabel#SuccessTitle, QLabel#MatConfigTitle {{font-size:24px;font-weight:bold;color:{c['text']};margin-top:10px;}}
	QLabel#SuccessMsg {{font-size:16px;color:{c['text']};margin-bottom:10px;}}
	QPushButton#SuccessBtn {{background-color:{c['prim']};color:{c['surf']};font-weight:bold;font-size:14px;padding:10px 30px;border-radius:8px;border:none;min-height:20px;}}
	QPushButton#SuccessBtn:hover {{background-color:{c['prim_h']};}}
	QLabel#MatConfigMsg {{font-size:14px;color:{c['mute']};}}
	QLineEdit#MatConfigInput {{padding:10px;font-size:16px;border:1px solid {c['bord']};border-radius:6px;background:{c['item']};color:{c['text']};font-weight:bold;}}
	QLineEdit#MatConfigInput:focus {{border-color:{c['prim']};background:{c['surf']};}}
	"""
STYLE_SHEET=get_sheet(C)

# CODE
def get_settings_hash(m):return hashlib.md5(m.encode()).hexdigest()[:7]
def render_worker(in_q, out_q):
	import engine.processor
	from engine.processor import AudioProcessor
	while True:
		t=in_q.get()
		if t is None:break
		try:
			if getattr(sys,"frozen",False) or str(getattr(engine.processor,"__file__","")).endswith(".pyd"):
				if sys_math and hasattr(sys_math,"v_p") and not sys_math.v_p(getattr(engine.processor,"S_PROC",None)):raise Exception("Security Error: Engine corrupted")
			pc=sys_math.m_m() if sys_math else {}
			t_dir=(sys_math.m_s('tp') if sys_math else "templates") if(sys_math and t['tmpl'] in pc)else "templates"
			tmpl=importlib.import_module(f"{t_dir}.{t['tmpl']}")
			if sys_math and t['tmpl'] in pc:
				if getattr(sys,"frozen",False) or str(getattr(tmpl,"__file__","")).endswith(".pyd"):
					if hasattr(sys_math,"v_t") and not sys_math.v_t(getattr(tmpl,"S_TMPL",None)):raise Exception("Security Error: Template corrupted")
			m=(TMPL_CONFIGS|pc).get(t['tmpl'],{"m":40})["m"]
			def prog_cb(curr,total):
				if total>0 and curr%5==0:out_q.put(('p',t['uid'],int(curr/total*100),"Video"))
			out_q.put(('s',t['uid']))
			AudioProcessor().render(t['path'],t['out_path'],tmpl.draw_frame,m,prog_cb,msvg=t.get('msvg',False),stroke=t.get('stroke',8),colors=t.get('colors',["#ffffff","#000000"]),spec_color=t.get('spec_color','multi'),key=t.get('key'),stroke_style=t.get('stroke_style','solid'))
			out_q.put(('d',t['uid']))
		except Exception:
			out_q.put(('f',t['uid'],traceback.format_exc()))
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
class PoolManagerThread(QThread):
	item_start,item_prog,item_done,item_fail=Signal(str),Signal(str,int,str),Signal(str),Signal(str,str)
	all_done=Signal()
	def __init__(self,tasks,max_w):
		super().__init__();self.tasks,self.max_w,self.stopped=tasks,max_w,False
	def run(self):
		self.in_q,self.out_q=mp.Queue(),mp.Queue();self.workers=[]
		for _ in range(self.max_w):
			p=mp.Process(target=render_worker,args=(self.in_q,self.out_q));p.start();self.workers.append(p)
		for t in self.tasks:self.in_q.put(t)
		active_tasks=len(self.tasks)
		while active_tasks>0 and not self.stopped:
			try:
				m=self.out_q.get(timeout=0.1)
				if m[0]=='s':self.item_start.emit(m[1])
				elif m[0]=='p':self.item_prog.emit(m[1],m[2],m[3])
				elif m[0]=='d':self.item_done.emit(m[1]);active_tasks-=1
				elif m[0]=='f':self.item_fail.emit(m[1],m[2]);active_tasks-=1
			except:continue
		for _ in self.workers:self.in_q.put(None)
		for p in self.workers:
			if self.stopped:p.terminate()
			p.join()
		self.all_done.emit()
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
			eb = QPushButton("VIEW ERROR LOG");eb.setObjectName("CleanBtn");eb.clicked.connect(lambda _=False: os.startfile(CURRENT_LOG));lay.addWidget(eb, 0, Qt.AlignCenter)
		btn=QPushButton("AWESOME");btn.setObjectName("SuccessBtn");btn.setCursor(Qt.PointingHandCursor);btn.clicked.connect(lambda _=False: self.accept());lay.addWidget(btn,0,Qt.AlignCenter)
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
	def __init__(self,parent,items,saved,has_dups=False,dup_only=False):
		super().__init__(parent);self.setObjectName("Gallery");self.setWindowTitle("Smart Sequence Constructor");self.resize(850,650)
		lay=QVBoxLayout(self);thl=QHBoxLayout();thl.setAlignment(Qt.AlignCenter);lay.addLayout(thl)
		b_all=QPushButton("SELECT ALL");b_all.setObjectName("CleanBtn");b_all.clicked.connect(lambda _=False:self.set_all(True))
		b_none=QPushButton("DESELECT ALL");b_none.setObjectName("CleanBtn");b_none.clicked.connect(lambda _=False:self.set_all(False))
		thl.addWidget(b_all);thl.addWidget(b_none)
		self.cb_dup=None
		if has_dups:
			from PySide6.QtWidgets import QCheckBox
			self.cb_dup=QCheckBox("Apply to duplicates only");self.cb_dup.setStyleSheet(f"QCheckBox{{color:{C['text']};margin-left:10px;padding:2px;}}");self.cb_dup.setMinimumHeight(26);self.cb_dup.setChecked(dup_only);thl.addWidget(self.cb_dup)
		sa=QScrollArea();sa.setWidgetResizable(True);sa.setFrameShape(QFrame.NoFrame);lay.addWidget(sa)
		cnt=QWidget();cnt.setObjectName("GalleryContent");self.fl=FlowLayout(cnt);sa.setWidget(cnt);self.wits=[]
		for n,is_p in items:
			act=(n in saved if saved else True) if not (is_p and not SME) else False
			w=MixItem(n,is_p,parent.show_matrix_config,act);self.wits.append(w);self.fl.addWidget(w)
		self.run_btn=QPushButton("APPLY SMART SEQUENCE");self.run_btn.setObjectName("SuccessBtn");self.run_btn.clicked.connect(lambda _=False: self.accept());lay.addWidget(self.run_btn)
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
		self.m_btn.clicked.connect(lambda _=False:self.select("multi"));gl.addWidget(self.m_btn,0,0,4,1)
		for i,c in enumerate(colors):
			btn=QPushButton();btn.setFixedSize(40,40);btn.setCursor(Qt.PointingHandCursor)
			bb=C['prim'] if c==current_val else "transparent"
			btn.setStyleSheet(f"QPushButton{{background-color:{c};border-radius:4px;border:2px solid {bb};}}QPushButton:hover{{border-color:{C['prim']};}}")
			btn.clicked.connect(lambda _=False,col=c:self.select(col));gl.addWidget(btn,i//10,1+i%10)
	def select(self,v):self.selected=v;self.accept()
class StrokeStyleGallery(QDialog):
	def __init__(self,parent,current_id):
		super().__init__(parent);self.setObjectName("Gallery");self.setWindowTitle("Select Stroke Style");self.resize(500,300);self.selected=current_id
		lay=QVBoxLayout(self);sa=QScrollArea();sa.setWidgetResizable(True);sa.setFrameShape(QFrame.NoFrame);lay.addWidget(sa)
		cnt=QWidget();cnt.setObjectName("GalleryContent");self.fl=FlowLayout(cnt);sa.setWidget(cnt)
		for name in ss_map.keys():
			btn=QWidget();btn.setObjectName("GalleryItem");btn.setCursor(Qt.PointingHandCursor);btn.setFixedSize(160,160);btn.setAttribute(Qt.WA_StyledBackground)
			btn.mousePressEvent=lambda _,n=name:self.select(n)
			bl=QVBoxLayout(btn);bl.setContentsMargins(4,4,4,4);bl.setSpacing(0);bl.addStretch()
			il=QLabel();il.setObjectName("GalleryIcon");il.setAlignment(Qt.AlignCenter);il.setFixedSize(120,120)
			px=QPixmap()
			if name=="Gradient":
				px.loadFromData(f'<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg"><defs><filter id="b" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="6"/></filter></defs><rect x="25" y="25" width="70" height="70" rx="12" fill="none" stroke="{C["text"]}" stroke-width="12" filter="url(#b)"/><rect x="25" y="25" width="70" height="70" rx="12" fill="none" stroke="{C["text"]}" stroke-width="2"/></svg>'.encode())
			else:
				px.loadFromData(f'<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg"><rect x="25" y="25" width="70" height="70" rx="12" fill="none" stroke="{C["text"]}" stroke-width="12"/></svg>'.encode())
			il.setPixmap(px)
			bl.addWidget(il,0,Qt.AlignCenter);bl.addStretch()
			tl=QLabel(name);tl.setObjectName("GalleryTitle");tl.setAlignment(Qt.AlignCenter);tl.setWordWrap(True);bl.addWidget(tl)
			self.fl.addWidget(btn)
	def select(self,name):self.selected=name;self.accept()
class MatrixConfigDialog(QDialog):
	def __init__(self,parent):
		super().__init__(parent);self.setWindowFlags(Qt.FramelessWindowHint|Qt.Dialog);self.setAttribute(Qt.WA_TranslucentBackground);self.setFixedSize(400,380)
		l=QVBoxLayout(self);f=QFrame();f.setObjectName("MatConfigDialog");l.addWidget(f);lay=QVBoxLayout(f)
		lay.setContentsMargins(30,10,30,10);lay.setSpacing(10);lay.setAlignment(Qt.AlignCenter)
		ico=QLabel("🔑");ico.setStyleSheet("font-size:80px;background:transparent;margin:3px;");ico.setAlignment(Qt.AlignCenter);lay.addWidget(ico)
		tl=QLabel(sys_math.m_s('t') if sys_math else "Activation");tl.setObjectName("MatConfigTitle");tl.setAlignment(Qt.AlignCenter);lay.addWidget(tl)
		msg=QLabel(sys_math.m_s('m') if sys_math else "Enter key:");msg.setObjectName("MatConfigMsg");msg.setAlignment(Qt.AlignCenter);msg.setWordWrap(True);lay.addWidget(msg)
		self.inp=QLineEdit();self.inp.setObjectName("MatConfigInput");self.inp.setPlaceholderText("XXXX-XXXX-XXXX-XXXX");self.inp.setAlignment(Qt.AlignCenter);self.inp.setMaxLength(50)
		lay.addWidget(self.inp);self.inp.textChanged.connect(lambda _="":self.res_lbl.setText(""));self.setFocus()
		buy_lbl=QLabel(f"<a href='{sys_math.m_s('g') if sys_math else ''}' style='color:{C['prim']};text-decoration:none;font-weight:bold;'>Don't have a key? Buy it here</a>");buy_lbl.setOpenExternalLinks(True);buy_lbl.setAlignment(Qt.AlignCenter);lay.addWidget(buy_lbl)
		btn_lay=QHBoxLayout();lay.addLayout(btn_lay)
		self.btn=QPushButton("ACTIVATE");self.btn.setObjectName("SuccessBtn");self.btn.setCursor(Qt.PointingHandCursor);self.btn.clicked.connect(lambda _=False: self.do_act());btn_lay.addWidget(self.btn)
		self.c_btn=QPushButton("CANCEL");self.c_btn.setObjectName("CleanBtn");self.c_btn.setCursor(Qt.PointingHandCursor);self.c_btn.clicked.connect(lambda _=False: self.reject());btn_lay.addWidget(self.c_btn)
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
		btn=QPushButton("CONTINUE" if ok else "TRY AGAIN");btn.setObjectName("SuccessBtn");btn.setCursor(Qt.PointingHandCursor);btn.clicked.connect(lambda _=False: self.accept());lay.addWidget(btn,0,Qt.AlignCenter)
		lay.addStretch()
class AboutDialog(QDialog):
	def __init__(self,parent):
		super().__init__(parent);self.setWindowFlags(Qt.FramelessWindowHint|Qt.Dialog);self.setAttribute(Qt.WA_TranslucentBackground);self.setFixedSize(380,360)
		l=QVBoxLayout(self);f=QFrame();f.setObjectName("SuccessDialog");l.addWidget(f);lay=QVBoxLayout(f)
		lay.setContentsMargins(30,5,30,15);lay.setSpacing(10);lay.setAlignment(Qt.AlignCenter)
		ico=QLabel("🎵");ico.setStyleSheet("font-size:70px;background:transparent;");ico.setAlignment(Qt.AlignCenter);lay.addWidget(ico)
		tl=QLabel(f"Audio Spectrum {sys_math.m_s('p') if (SME and sys_math) else ''}");tl.setObjectName("SuccessTitle");tl.setAlignment(Qt.AlignCenter);lay.addWidget(tl)
		msg=QLabel(f"Version: {VERSION}\nCreated by Aljnk");msg.setObjectName("SuccessMsg");msg.setAlignment(Qt.AlignCenter);lay.addWidget(msg)
		git=QPushButton("VISIT GITHUB");git.setObjectName("SuccessBtn");git.setCursor(Qt.PointingHandCursor);git.setFixedWidth(220);git.clicked.connect(lambda _=False:webbrowser.open(f"https://github.com/{UPDATE_URL}"));lay.addWidget(git,0,Qt.AlignCenter)
		btn=QPushButton("CLOSE");btn.setObjectName("CleanBtn");btn.setFixedWidth(220);btn.setCursor(Qt.PointingHandCursor);btn.clicked.connect(lambda _=False: self.accept());lay.addWidget(btn,0,Qt.AlignCenter)
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
			btn=QPushButton("DOWNLOAD");btn.setObjectName("SuccessBtn");btn.setFixedWidth(220);btn.setCursor(Qt.PointingHandCursor);btn.clicked.connect(lambda _=False:webbrowser.open(url));lay.addWidget(btn,0,Qt.AlignCenter)
		c=QPushButton("CLOSE");c.setObjectName("CleanBtn");c.setFixedWidth(220);c.setCursor(Qt.PointingHandCursor);c.clicked.connect(lambda _=False: self.accept());lay.addWidget(c,0,Qt.AlignCenter)

class SettingsDialog(QDialog):
	def __init__(self,parent):
		super().__init__(parent);self.setObjectName("Gallery");self.setWindowTitle("Settings");self.resize(950,600)
		ml=QVBoxLayout(self);hl=QHBoxLayout();ml.addLayout(hl)
		self.sb=QListWidget();self.sb.setFixedWidth(220);self.sb.setObjectName("AudioList")
		self.sb.addItem("🎨 Theme");self.sb.addItem("Finish Sound");hl.addWidget(self.sb)
		self.stack=QStackedWidget();hl.addWidget(self.stack)
		p_t=QWidget();l_t=QVBoxLayout(p_t);l_t.addWidget(QLabel("Select Application Theme:"))
		self.t_list=QListWidget();self.t_list.setObjectName("AudioList");l_t.addWidget(self.t_list);self.stack.addWidget(p_t)
		t_vals=[("System Default","auto")]
		for f in glob.glob(rp(os.path.join("assets","themes","*.thm"))):
			tn=os.path.basename(f).replace(".thm","");t_vals.append((tn.title(),tn))
		c_t=settings.value("theme","auto")
		for i,(n,v) in enumerate(t_vals):
			it=QListWidgetItem(n);it.setData(Qt.UserRole,v);self.t_list.addItem(it)
			if v==c_t:self.t_list.setCurrentItem(it)
		p_s=QWidget();l_s=QVBoxLayout(p_s);l_s.addWidget(QLabel("Select Finish Sound:"))
		self.s_list=QListWidget();self.s_list.setObjectName("AudioList");l_s.addWidget(self.s_list);self.stack.addWidget(p_s)
		s_vals=[("None","none")]
		sd=rp(os.path.join("assets","sounds"))
		if not os.path.exists(sd):sd=os.path.join(os.path.abspath("."),"assets","sounds")
		if os.path.exists(sd):
			for f in sorted(os.listdir(sd)):
				if f.lower().startswith("finish") and f.lower().endswith(".wav"):
					parts=f[:-4].split("_");sn=" ".join(parts[2:]).title() if len(parts)>2 else f[:-4]
					s_vals.append((sn,f))
		c_s=settings.value("finish_sound","default")
		if c_s=="":c_s="none"
		for i,(n,v) in enumerate(s_vals):
			it=QListWidgetItem();it.setData(Qt.UserRole,v);it.setSizeHint(QSize(0,42));self.s_list.addItem(it)
			row_w=QWidget();row_l=QHBoxLayout(row_w);row_l.setContentsMargins(5,0,15,0);row_l.setSpacing(10)
			btn_sel=QPushButton(n);btn_sel.setObjectName("SoundSelectBtn");btn_sel.setCursor(Qt.PointingHandCursor)
			btn_sel.clicked.connect(lambda _=False,curr_it=it:self.s_list.setCurrentItem(curr_it))
			row_l.addWidget(btn_sel,1)
			if v and v!="none":
				btn_p=QPushButton();btn_p.setObjectName("PreviewBtn");btn_p.setFixedSize(30,30);btn_p.setCursor(Qt.PointingHandCursor)
				btn_p.setToolTip("Preview sound");btn_p.clicked.connect(lambda _=False,f=v:self.preview_sound(f));row_l.addWidget(btn_p)
			self.s_list.setItemWidget(it,row_w)
			if v==c_s:self.s_list.setCurrentItem(it)
		self.sb.currentRowChanged.connect(self.stack.setCurrentIndex);self.sb.setCurrentRow(0)
		self.t_list.itemSelectionChanged.connect(self.apply_theme);self.s_list.itemSelectionChanged.connect(self.apply_sound)
		bl=QHBoxLayout();bl.addStretch()
		b_c=QPushButton("CLOSE");b_c.setObjectName("CleanBtn");b_c.setCursor(Qt.PointingHandCursor)
		b_c.clicked.connect(self.accept);bl.addWidget(b_c);ml.addLayout(bl);self.refresh_styles()
	def refresh_styles(self):
		self.setStyleSheet(get_sheet(C))
		self.sb.setStyleSheet(f"QListWidget{{font-weight:bold;font-size:16px;}}QListWidget::item{{padding:6px 10px;color:{C['mute']};border:none;background:transparent;}} QListWidget::item:hover{{color:{C['text']};background-color:{C['hover']};}} QListWidget::item:selected{{background-color:{C['prim']};color:{C['surf']};border-radius:8px;}}")
		ls=f"QListWidget::item{{padding:5px 15px;margin-bottom:4px;color:{C['text']};background-color:{C['item']};border:1px solid {C['bord']};border-radius:6px;font-size:14px;}} QListWidget::item:hover{{background-color:{C['hover']};}} QListWidget::item:selected{{border:2px solid {C['prim']};background-color:{C['accent']};}}"
		self.t_list.setStyleSheet(ls)
		self.s_list.setStyleSheet("QListWidget::item{background:transparent;border:none;} QListWidget::item:selected{background:transparent;border:none;}")
		spk=f'<svg viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg"><defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="10%" stop-color="{C["prim"]}"/><stop offset="100%" stop-color="{C["gold_m"]}"/></linearGradient></defs><path d="M13 9L7 13H3V19H7L13 23V9Z" fill="url(#g)" stroke="{C["text"]}" stroke-width="1.5" stroke-linejoin="round"/><path d="M17 11A6 6 0 0 1 17 21M21 7A11 11 0 0 1 21 25" fill="none" stroke="url(#g)" stroke-width="2.5" stroke-linecap="round"/></svg>'.encode()
		px=QPixmap();px.loadFromData(spk);ic=QIcon(px)
		self.sb.item(1).setIcon(ic);self.sb.setIconSize(QSize(22,22))
		for i in range(self.s_list.count()):
			w=self.s_list.itemWidget(self.s_list.item(i))
			if w:
				b=w.findChild(QPushButton,"PreviewBtn")
				if b:b.setIcon(ic);b.setIconSize(QSize(20,20));b.setStyleSheet(f"QPushButton{{background:transparent;border:none;border-radius:15px;}}QPushButton:hover{{background:{C['accent']};}}")
		self.update_sound_list_styles()
	def update_sound_list_styles(self):
		sel_it=self.s_list.currentItem()
		for i in range(self.s_list.count()):
			it=self.s_list.item(i);w=self.s_list.itemWidget(it)
			if w:
				btn_sel=w.findChild(QPushButton,"SoundSelectBtn")
				if btn_sel:
					if it==sel_it:btn_sel.setStyleSheet(f"QPushButton{{text-align:left;padding:8px 15px;color:{C['text']};border:2px solid {C['prim']};background-color:{C['accent']};border-radius:6px;font-size:14px;}}")
					else:btn_sel.setStyleSheet(f"QPushButton{{text-align:left;padding:8px 15px;color:{C['text']};background-color:{C['item']};border:1px solid {C['bord']};border-radius:6px;font-size:14px;}} QPushButton:hover{{background-color:{C['hover']};}}")
	def apply_theme(self):
		it=self.t_list.currentItem()
		if it:
			tv=it.data(Qt.UserRole);settings.setValue("theme",tv);self.parent().set_theme(tv);self.refresh_styles()
	def apply_sound(self):
		it=self.s_list.currentItem()
		if it:sv=it.data(Qt.UserRole);settings.setValue("finish_sound",sv)
		self.update_sound_list_styles()
	def preview_sound(self,f):
		if not f:return
		s_p=rp(os.path.join("assets","sounds",f))
		if not os.path.exists(s_p):s_p=os.path.join(os.path.abspath("."),"assets","sounds",f)
		if os.path.exists(s_p):self.parent()._p.setSource(QUrl.fromLocalFile(s_p));self.parent()._p.play()

class MainWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		self.setWindowTitle(f" Audio Spectrum {sys_math.m_s('p') if (SME and sys_math) else ''}");self.setAcceptDrops(True);self.setStyleSheet(STYLE_SHEET);self.repo={}
		sg=QApplication.primaryScreen().availableGeometry();fix_h=295;track_h=60
		track_cnt_max=max(1,(sg.height()-80-fix_h)//track_h)
		w,h=min(1200,sg.width()-80),fix_h+track_h*track_cnt_max
		self.resize(w,h);self.move(sg.x()+(sg.width()-w)//2,max(sg.y(),sg.y()+(sg.height()-h)//2-16))
		self.setWindowIcon(QIcon(rp(os.path.join("assets","images","icon.ico"))))
		self._p=QSoundEffect(self);self._p.setVolume(1.0)
		self.tm=TooltipManager(self);self.loader=Preloader(self)
		self.tasks_q,self.active_th,self.is_rendering=[],[],False;self.max_w=min(4,max(1,os.cpu_count()//4))
		self.custom_mix_ids,self.has_errors,self.has_loggable_errors=[],False,False
		root=QWidget();self.setCentralWidget(root);lay=QVBoxLayout(root);lay.setSpacing(15);lay.setContentsMargins(20,20,20,20)
		self._init_menu()
		top_lay=QHBoxLayout();top_lay.setSpacing(15)
		self.b_add=QPushButton("📄 Add Files");self.b_add.setObjectName("AddBtn");self.b_add.setMinimumHeight(48)
		self.b_add.setToolTip("Add audio files to the list");self.b_add.clicked.connect(lambda _=False: self.add_manual());self.b_add.installEventFilter(self.tm);self.b_add.setCursor(Qt.PointingHandCursor)
		self.lbl_drop=QLabel("Drag & Drop Audios");self.lbl_drop.setObjectName("DropArea");self.lbl_drop.setAlignment(Qt.AlignCenter);self.lbl_drop.setMinimumHeight(48)
		self.lbl_drop.setToolTip("Drag files here");self.lbl_drop.mousePressEvent=lambda e: self.add_manual();self.lbl_drop.installEventFilter(self.tm);self.lbl_drop.setCursor(Qt.DragCopyCursor)
		top_lay.addWidget(self.b_add,1);top_lay.addWidget(self.lbl_drop,1);lay.addLayout(top_lay)
		bk_lay=QHBoxLayout();bk_lay.setSpacing(10)
		lbl_all=QLabel("CHANGE ALL:");lbl_all.setStyleSheet(f"font-weight:bold;color:{C['mute']};margin-left:5px;");bk_lay.addWidget(lbl_all)
		self.b_bk_t=QPushButton("Types");self.b_bk_t.setObjectName("CleanBtn");self.b_bk_t.setToolTip("Change type for all tracks");self.b_bk_t.clicked.connect(lambda _=False: self.bulk_tmpl())
		self.b_bk_s=QPushButton("Stroke Thicknesses");self.b_bk_s.setObjectName("CleanBtn");self.b_bk_s.setToolTip("Change stroke thickness for all tracks");self.b_bk_s.clicked.connect(lambda _=False: self.bulk_stroke())
		self.b_bk_c=QPushButton("Stroke Colors");self.b_bk_c.setObjectName("CleanBtn");self.b_bk_c.setToolTip("Change stroke color for all tracks");self.b_bk_c.clicked.connect(lambda _=False: self.bulk_color())
		self.b_bk_ss=QPushButton("Stroke Styles");self.b_bk_ss.setObjectName("CleanBtn");self.b_bk_ss.setToolTip("Change stroke style for all tracks");self.b_bk_ss.clicked.connect(lambda _=False: self.bulk_style())
		self.b_bk_sp=QPushButton("Spectrum Colors");self.b_bk_sp.setObjectName("CleanBtn");self.b_bk_sp.setToolTip("Change spectrum color for all tracks");self.b_bk_sp.clicked.connect(lambda _=False: self.bulk_spec())
		self.b_bk_dup=QPushButton("Duplicate All");self.b_bk_dup.setObjectName("CleanBtn");self.b_bk_dup.setToolTip("Duplicate all tracks");self.b_bk_dup.clicked.connect(lambda _=False:self.duplicate_all())
		for b in [self.b_bk_t,self.b_bk_s,self.b_bk_c,self.b_bk_ss,self.b_bk_sp,self.b_bk_dup]:
			b.setCursor(Qt.PointingHandCursor);b.installEventFilter(self.tm);bk_lay.addWidget(b)
		bk_lay.addStretch();self.b_srt=QPushButton("Sort ↕");self.b_srt.setObjectName("CleanBtn");self.b_srt.setToolTip("Sort list");self.b_srt.setCursor(Qt.PointingHandCursor);self.b_srt.installEventFilter(self.tm)
		self.ms=QMenu(self);self.ms.setWindowFlags(Qt.Popup|Qt.FramelessWindowHint|Qt.NoDropShadowWindowHint);self.ms.setAttribute(Qt.WA_TranslucentBackground);self.ms.addAction("Name",lambda _=False:self.sort_list("n"));self.ms.addAction("Size",lambda _=False:self.sort_list("s"));self.ms.addAction("Date",lambda _=False:self.sort_list("d"))
		self.ms.aboutToHide.connect(lambda:setattr(self,"_ms_last",time.time()));self.b_srt.clicked.connect(lambda _=False:self.ms.exec(self.b_srt.mapToGlobal(QPoint(self.b_srt.width()-self.ms.sizeHint().width(),self.b_srt.height()))) if time.time()-getattr(self,"_ms_last",0)>0.3 else None);bk_lay.addWidget(self.b_srt);lay.addLayout(bk_lay)
		self.lst_c=QFrame();self.lst_c.setObjectName("ListContainer");lay.addWidget(self.lst_c)
		l_c=QVBoxLayout(self.lst_c);l_c.setContentsMargins(1,1,1,1);l_c.setSpacing(0)
		self.lst=QListWidget();self.lst.setObjectName("AudioList");self.lst.setFrameShape(QFrame.NoFrame);self.lst.setDragEnabled(True);self.lst.setAcceptDrops(True);self.lst.setDropIndicatorShown(True);self.lst.setDragDropMode(QListWidget.InternalMove);self.lst.setDefaultDropAction(Qt.MoveAction);l_c.addWidget(self.lst)
		tool_lay=QHBoxLayout();self.total_pbar=QProgressBar();self.total_pbar.setObjectName("TotalPbar");self.total_pbar.hide();tool_lay.addWidget(self.total_pbar)
		self.total_tasks,self.completed_tasks,self.task_progress=0,0,{}
		self.b_all=QPushButton("Remove All");self.b_all.setObjectName("CleanAllBtn")
		self.b_all.setToolTip("Clear the entire list");self.b_all.clicked.connect(lambda _=False: self.clear_all());self.b_all.installEventFilter(self.tm);self.b_all.setCursor(Qt.PointingHandCursor)
		self.b_all=QPushButton("Remove All");self.b_all.setObjectName("CleanAllBtn")
		self.b_all.setToolTip("Clear the entire list");self.b_all.clicked.connect(lambda _=False: self.clear_all());self.b_all.installEventFilter(self.tm);self.b_all.setCursor(Qt.PointingHandCursor)
		self.b_clean=QPushButton("Remove Completed");self.b_clean.setObjectName("CleanBtn")
		self.b_clean.setToolTip("Remove only finished tracks");self.b_clean.clicked.connect(lambda _=False: self.remove_completed());self.b_clean.installEventFilter(self.tm);self.b_clean.setCursor(Qt.PointingHandCursor)
		self.b_rem_dup=QPushButton("Remove Duplicates");self.b_rem_dup.setObjectName("CleanBtn")
		self.b_rem_dup.setToolTip("Remove duplicate tracks");self.b_rem_dup.clicked.connect(lambda _=False: self.remove_duplicates());self.b_rem_dup.installEventFilter(self.tm);self.b_rem_dup.setCursor(Qt.PointingHandCursor)
		self.b_stop=QPushButton("Stop Processing");self.b_stop.setObjectName("StopBtn")
		self.b_stop.setToolTip("Abort work and delete temporary files");self.b_stop.clicked.connect(lambda _=False: self.stop_task());self.b_stop.installEventFilter(self.tm);self.b_stop.setCursor(Qt.PointingHandCursor)
		tool_lay.addStretch();tool_lay.addWidget(self.b_all);tool_lay.addWidget(self.b_clean);tool_lay.addWidget(self.b_rem_dup);tool_lay.addWidget(self.b_stop);lay.addLayout(tool_lay)
		self.b_run=QPushButton("CREATE SPECTRUMS");self.b_run.setObjectName("MainBtn")
		self.b_run.setToolTip("Start processing all new files");self.b_run.clicked.connect(lambda _=False: self.run_task());lay.addWidget(self.b_run);self.b_run.installEventFilter(self.tm);self.b_run.setCursor(Qt.PointingHandCursor)
		self.update_buttons()
		self.m_timer=QTimer(self);self.m_timer.setSingleShot(True);self.m_timer.timeout.connect(self.m_v_silent);self.m_timer.start(30000)
		self.m_chk=False
	def _init_menu(self):
		mb=self.menuBar()
		a_set=mb.addAction("Settings");a_set.triggered.connect(lambda _=False: self.show_settings())
		m_ab=mb.addMenu("About")
		a_abt=m_ab.addAction("About App");a_abt.triggered.connect(lambda _=False: self.show_about())
		a_upd=m_ab.addAction("Check for Updates");a_upd.triggered.connect(lambda _=False: self.check_updates(quiet=False))
		m_ab.addSeparator()
		if sys_math and os.path.exists(rp(sys_math.m_s('tp'))):
			self.a_act=m_ab.addAction(sys_math.m_s('a') if sys_math else "");self.a_act.triggered.connect(lambda _=False: self.show_matrix_config())
			if SME:self.a_act.setEnabled(False);self.a_act.setText(sys_math.m_s('d') if sys_math else "")
		else:
			a_full=m_ab.addAction(sys_math.m_s('f') if sys_math else "Get Pro Version");a_full.triggered.connect(lambda _=False:webbrowser.open(f"https://github.com/{UPDATE_URL}/releases/latest"))
	def show_settings(self):
		self.exec_ov(SettingsDialog(self))
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
		for uid,r in self.repo.items():
			self.set_style_btn_icon(r['ss'],r['ss'].property("style_id"))
			px_dup=QPixmap();px_dup.loadFromData(f'<svg viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg"><path d="M16 7 L16 25 M7 16 L25 16" stroke="{C["text"]}" stroke-width="4.5" stroke-linecap="round"/></svg>'.encode());r['dup'].setIcon(QIcon(px_dup))
			px_rem=QPixmap();px_rem.loadFromData(f'<svg viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg"><path d="M7 7 L25 25 M25 7 L7 25" stroke="{C["surf"]}" stroke-width="4.8" stroke-linecap="round"/></svg>'.encode());r['rem'].setIcon(QIcon(px_rem))
	def exec_ov(self,d):
		if self.isMinimized():self.showNormal()
		self.activateWindow()
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
		if self.active_th:return
		dp=settings.value("last_dir","")
		if not dp or not os.path.exists(dp):
			try:k=winreg.OpenKey(winreg.HKEY_CURRENT_USER,r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders");dp=winreg.QueryValueEx(k,"Desktop")[0]
			except:dp=""
		fs,_=QFileDialog.getOpenFileNames(self,"Audio",dp,"*.mp3 *.wav *.flac *.m4a")
		if fs:settings.setValue("last_dir",os.path.dirname(fs[0]))
		for f in fs:self.add_item(f)
	def add_item(self,path,copy_uid=None):
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
		txt_l=QLabel("Simple Linear");txt_l.setObjectName("TmplText");txt_l.setAlignment(Qt.AlignCenter);txt_l.setAttribute(Qt.WA_TransparentForMouseEvents)
		btl.addWidget(ico_l);btl.addWidget(txt_l,1);l.addWidget(btn_tmpl)
		btn_stroke=QPushButton();btn_stroke.setObjectName("StrokeBtn");btn_stroke.setToolTip("Stroke Thickness");btn_stroke.setCursor(Qt.PointingHandCursor);btn_stroke.installEventFilter(self.tm);btn_stroke.setFocusPolicy(Qt.NoFocus);l.addWidget(btn_stroke)
		btn_stroke.setProperty("stroke_id","Medium")
		btn_color=QPushButton();btn_color.setObjectName("StrokeBtn");btn_color.setToolTip("Stroke Color");btn_color.setCursor(Qt.PointingHandCursor);btn_color.installEventFilter(self.tm);btn_color.setFocusPolicy(Qt.NoFocus);l.addWidget(btn_color)
		btn_color.setProperty("color_id","Black")
		btn_style=QPushButton();btn_style.setObjectName("StrokeBtn");btn_style.setToolTip("Stroke Style");btn_style.setCursor(Qt.PointingHandCursor);btn_style.installEventFilter(self.tm);btn_style.setFocusPolicy(Qt.NoFocus);l.addWidget(btn_style)
		btn_style.setProperty("style_id","Solid");self.set_style_btn_icon(btn_style,"Solid")
		btn_spec=QPushButton();btn_spec.setObjectName("StrokeBtn");btn_spec.setToolTip("Spectrum Color");btn_spec.setCursor(Qt.PointingHandCursor);btn_spec.installEventFilter(self.tm);btn_spec.setFocusPolicy(Qt.NoFocus);l.addWidget(btn_spec)
		btn_spec.setProperty("spec_id","multi");self.set_spec_btn_icon(btn_spec,"multi")
		c_img_p=rp(os.path.join("assets","images","colors","black.svg"))
		if os.path.exists(c_img_p):btn_color.setIcon(QIcon(c_img_p));btn_color.setIconSize(QSize(30,30))
		s_img_p=rp(os.path.join("assets","images","strokes","medium.svg"))
		if os.path.exists(s_img_p):btn_stroke.setIcon(QIcon(s_img_p));btn_stroke.setIconSize(QSize(30,30))
		b_dup=QPushButton();b_dup.setObjectName("StrokeBtn");b_dup.setToolTip("Duplicate track");b_dup.installEventFilter(self.tm);l.addWidget(b_dup);b_dup.setCursor(Qt.PointingHandCursor)
		px_dup=QPixmap();px_dup.loadFromData(f'<svg viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg"><path d="M16 7 L16 25 M7 16 L25 16" stroke="{C["text"]}" stroke-width="4.5" stroke-linecap="round"/></svg>'.encode())
		b_dup.setIcon(QIcon(px_dup));b_dup.setIconSize(QSize(22,22))
		btn=QPushButton();btn.setObjectName("RemoveRowBtn");btn.setFixedWidth(32);btn.setToolTip("Remove track");btn.installEventFilter(self.tm);l.addWidget(btn);btn.setCursor(Qt.PointingHandCursor)
		px=QPixmap();px.loadFromData(f'<svg viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg"><path d="M7 7 L25 25 M25 7 L7 25" stroke="{C["surf"]}" stroke-width="4.8" stroke-linecap="round"/></svg>'.encode());btn.setIcon(QIcon(px));btn.setIconSize(QSize(20,20))
		it=QListWidgetItem(self.lst);it.setSizeHint(QSize(w.sizeHint().width(),60));uid=f"{path}_{time.time()}"
		b_dup.clicked.connect(lambda _=False, p=path, cuid=uid:self.add_item(p,copy_uid=cuid))
		it.setData(Qt.UserRole,path);it.setData(Qt.UserRole+10,uid);it.setData(Qt.UserRole+3,"New")
		self.repo[uid]={'tmpl':(btn_tmpl,ico_l,txt_l),'st':(ico_lbl,txt_lbl),'pb':pbar,'rem':btn,'act':(b_fold,b_play),'s':btn_stroke,'c':btn_color,'ss':btn_style,'sp':btn_spec,'dup':b_dup}
		btn_spec.clicked.connect(lambda _=False:self.open_spectrum_gallery(it))
		btn_stroke.clicked.connect(lambda _=False:self.open_stroke_gallery(it))
		btn_style.clicked.connect(lambda _=False:self.open_style_gallery(it))
		btn_color.clicked.connect(lambda _=False:self.open_color_gallery(it))
		self.lst.addItem(it);self.lst.setItemWidget(it,w)
		btn.clicked.connect(lambda _=False:(self.repo.pop(it.data(Qt.UserRole+10),None),self.lst.takeItem(self.lst.row(it)),self.update_buttons()))
		btn_tmpl.clicked.connect(lambda _=False:self.open_gallery(it))
		b_fold.clicked.connect(lambda _=False:subprocess.run(f'explorer /select,"{self.get_out_path(it)}"',shell=True))
		b_play.clicked.connect(lambda _=False:os.startfile(self.get_out_path(it)))
		img_p=rp(os.path.join("assets","images","templates","simple_linear.svg"))
		if not os.path.exists(img_p):img_p=rp(os.path.join("assets","images","templates","new.svg"))
		if os.path.exists(img_p):ico_l.setPixmap(QIcon(img_p).pixmap(30,30))
		if copy_uid and copy_uid in self.repo:
			cr=self.repo[copy_uid]
			c_tmpl=cr['tmpl'][0].property("tmpl_id");txt_l.setText(c_tmpl.replace("_"," ").title());btn_tmpl.setProperty("tmpl_id",c_tmpl)
			img_p=rp(os.path.join("assets","images","templates",f"{c_tmpl}.svg"))
			if not os.path.exists(img_p):img_p=rp(os.path.join("assets","images","templates","new.svg"))
			if os.path.exists(img_p):ico_l.setPixmap(QIcon(img_p).pixmap(30,30))
			c_s=cr['s'].property("stroke_id");btn_stroke.setProperty("stroke_id",c_s);btn_stroke.setIcon(QIcon(rp(os.path.join("assets","images","strokes",f"{c_s.lower().replace(' ','_')}.svg"))))
			c_c=cr['c'].property("color_id");btn_color.setProperty("color_id",c_c);btn_color.setIcon(QIcon(rp(os.path.join("assets","images","colors",f"{c_c.lower().replace(' ','_')}.svg"))))
			c_ss=cr['ss'].property("style_id");btn_style.setProperty("style_id",c_ss);self.set_style_btn_icon(btn_style,c_ss)
			c_sp=cr['sp'].property("spec_id");btn_spec.setProperty("spec_id",c_sp);self.set_spec_btn_icon(btn_spec,c_sp)
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
	def open_style_gallery(self,it):self._row_dlg(it,'ss',"style_id",StrokeStyleGallery,self.set_style_btn_icon)
	def set_style_btn_icon(self,btn,v):
		px=QPixmap()
		if v=="Gradient":
			px.loadFromData(f'<svg viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg"><defs><filter id="b" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2"/></filter></defs><rect x="6" y="6" width="20" height="20" rx="4" fill="none" stroke="{C["text"]}" stroke-width="5" filter="url(#b)"/><rect x="6" y="6" width="20" height="20" rx="4" fill="none" stroke="{C["text"]}" stroke-width="1"/></svg>'.encode())
		else:
			px.loadFromData(f'<svg viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg"><rect x="6" y="6" width="20" height="20" rx="4" fill="none" stroke="{C["text"]}" stroke-width="4"/></svg>'.encode())
		btn.setIcon(QIcon(px));btn.setIconSize(QSize(30,30));btn.setText("");btn.setStyleSheet("")
	def find_item_by_uid(self,uid):
		for i in range(self.lst.count()):
			it=self.lst.item(i)
			if it.data(Qt.UserRole+10)==uid:return it
		return None
	def get_out_path(self,it):
		r=self.repo[it.data(Qt.UserRole+10)];p,data,btn_s,btn_c,btn_sp,btn_ss=it.data(Qt.UserRole),r['tmpl'],r['s'],r['c'],r['sp'],r['ss']
		t=data[0].property('tmpl_id').lower();s=btn_s.property('stroke_id').lower();c=btn_c.property('color_id').replace(' ','').lower();sp=btn_sp.property('spec_id').replace('#','').lower()
		ss=btn_ss.property('style_id').lower()
		return os.path.abspath(os.path.splitext(p)[0]+f"_{t}_{s}_{c}_{ss}_{sp}.mp4")
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
		elif s=="Clone":ico.setText("💤");txt.setText("Clone");txt.setStyleSheet(f"color:{C['mute']};")
		elif s=="Wait":ico.setText("⏱️");txt.setText("Wait");txt.setStyleSheet(f"color:{C['mute']};")
		
	def update_buttons(self):
		proc,cnt=bool(self.active_th),self.lst.count()
		seen=set();has_dup=False
		for i in range(cnt):
			it=self.lst.item(i);uid=it.data(Qt.UserRole+10);r=self.repo.get(uid)
			if not r:continue
			sig=(it.data(Qt.UserRole),r['tmpl'][0].property("tmpl_id"),r['s'].property("stroke_id"),r['c'].property("color_id"),r['ss'].property("style_id"),r['sp'].property("spec_id"))
			cur_st=it.data(Qt.UserRole+3)
			if sig in seen:
				if cur_st not in ["Work","Done","Exist","Fail"]:
					it.setData(Qt.UserRole+3,"Clone");self.set_status_visual(it,"Clone")
				has_dup=True
			else:
				seen.add(sig)
				if cur_st=="Clone":it.setData(Qt.UserRole+3,"New");self.set_status_visual(it,"New")
			r['tmpl'][0].setEnabled(not proc);r['rem'].setEnabled(not proc);r['s'].setEnabled(not proc)
			r['c'].setEnabled(not proc);r['ss'].setEnabled(not proc);r['sp'].setEnabled(not proc);r['dup'].setEnabled(not proc)
		self.b_all.setEnabled(cnt>0 and not proc);self.b_clean.setEnabled(cnt>0 and any(self.lst.item(i).data(Qt.UserRole+3) in ["Done","Exist"] for i in range(cnt)))
		self.b_rem_dup.setEnabled(has_dup and not proc);self.b_stop.setEnabled(proc);self.b_run.setEnabled(cnt>0 and not proc)
		self.b_add.setEnabled(not proc);self.lbl_drop.setEnabled(not proc);self.setAcceptDrops(not proc)
		self.lst.setDragDropMode(QListWidget.NoDragDrop if proc else QListWidget.InternalMove)
		for b in [self.b_bk_t,self.b_bk_s,self.b_bk_c,self.b_bk_ss,self.b_bk_sp,self.b_srt,self.b_bk_dup]:b.setEnabled(cnt>0 and not proc)
	def duplicate_all(self):
		for i in range(self.lst.count()):
			it=self.lst.item(i);self.add_item(it.data(Qt.UserRole),copy_uid=it.data(Qt.UserRole+10))
	def remove_duplicates(self):
		seen=set()
		for i in range(self.lst.count()):
			it=self.lst.item(i);uid=it.data(Qt.UserRole+10);r=self.repo.get(uid)
			if not r:continue
			sig=(it.data(Qt.UserRole),r['tmpl'][0].property("tmpl_id"),r['s'].property("stroke_id"),r['c'].property("color_id"),r['ss'].property("style_id"),r['sp'].property("spec_id"))
			if sig in seen:
				it.setData(Qt.UserRole+99,True)
			else:seen.add(sig)
		for i in range(self.lst.count()-1,-1,-1):
			it=self.lst.item(i)
			if it.data(Qt.UserRole+99):
				self.repo.pop(it.data(Qt.UserRole+10),None);self.lst.takeItem(i)
		self.update_buttons()
	def clear_all(self):
		self.lst.clear();self.repo.clear();self.update_buttons()
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
	def apply_custom_mix(self, dup_only=False):
		if not self.custom_mix_ids or not self.lst.count():return
		seen=set()
		for i in range(self.lst.count()):
			it=self.lst.item(i);uid=it.data(Qt.UserRole+10);r=self.repo[uid]
			if dup_only and it.data(Qt.UserRole+3)=="Clone":continue
			seen.add((it.data(Qt.UserRole),r['tmpl'][0].property("tmpl_id"),r['s'].property("stroke_id"),r['c'].property("color_id"),r['ss'].property("style_id"),r['sp'].property("spec_id")))
		mix_idx=0
		for i in range(self.lst.count()):
			it=self.lst.item(i);uid=it.data(Qt.UserRole+10)
			if dup_only and it.data(Qt.UserRole+3)!="Clone":continue
			r=self.repo[uid];btn,ico,txt=r['tmpl']
			s_id,c_id,ss_id,sp_id=r['s'].property("stroke_id"),r['c'].property("color_id"),r['ss'].property("style_id"),r['sp'].property("spec_id")
			attempts=0;n=self.custom_mix_ids[0]
			while attempts<=len(self.custom_mix_ids):
				n=self.custom_mix_ids[mix_idx%len(self.custom_mix_ids)];mix_idx+=1;attempts+=1
				sig=(it.data(Qt.UserRole),n,s_id,c_id,ss_id,sp_id)
				if sig not in seen:
					seen.add(sig);break
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
		has_dups=any(self.lst.item(i).data(Qt.UserRole+3)=="Clone" for i in range(self.lst.count()))
		d=MixSelector(self,items,self.custom_mix_ids,has_dups,getattr(self,'custom_mix_dup_only',False))
		if self.exec_ov(d):
			self.custom_mix_ids=d.get_sel()
			dup_only=d.cb_dup.isChecked() if getattr(d, 'cb_dup', None) else False
			self.custom_mix_dup_only=dup_only
			self.apply_custom_mix(dup_only)
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
	def _bulk_op(self,btn_src,role,prop,dlg_cls,upd_fn):
		if not self.lst.count():return
		v0=self.repo[self.lst.item(0).data(Qt.UserRole+10)][role].property(prop)
		dlg=dlg_cls(self,v0)
		if self.exec_ov(dlg):
			for i in range(self.lst.count()):
				it=self.lst.item(i);b=self.repo[it.data(Qt.UserRole+10)][role];v=dlg.selected;b.setProperty(prop,v)
				upd_fn(it,b,v);self.check_file_status(it);b.style().unpolish(b);b.style().polish(b)
		QTimer.singleShot(0,lambda:(btn_src.setAttribute(Qt.WA_UnderMouse,False),btn_src.style().unpolish(btn_src),btn_src.style().polish(btn_src)))
	def bulk_stroke(self):self._bulk_op(self.b_bk_s,'s',"stroke_id",StrokeGallery,lambda it,b,v:b.setIcon(QIcon(rp(os.path.join("assets","images","strokes",f"{v.lower().replace(' ','_')}.svg")))))
	def bulk_color(self):self._bulk_op(self.b_bk_c,'c',"color_id",ColorGallery,lambda it,b,v:b.setIcon(QIcon(rp(os.path.join("assets","images","colors",f"{v.lower().replace(' ','_')}.svg")))))
	def bulk_spec(self):self._bulk_op(self.b_bk_sp,'sp',"spec_id",SpectrumColorGallery,lambda it,b,v:self.set_spec_btn_icon(b,v))
	def bulk_style(self):self._bulk_op(self.b_bk_ss,'ss',"style_id",StrokeStyleGallery,lambda it,b,v:self.set_style_btn_icon(b,v))
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
			s_id,c_id,sp_id,ss_id=r['s'].property("stroke_id"),r['c'].property("color_id"),r['sp'].property("spec_id"),r['ss'].property("style_id")
			self.tasks_q.append({'path':it.data(Qt.UserRole),'tmpl':r['tmpl'][0].property("tmpl_id"),'out_path':self.get_out_path(it),'uid':it.data(Qt.UserRole+10),'msvg':"-msvg" in sys.argv,'stroke':sw_map.get(s_id,8),'colors':sc_map.get(c_id,["#ffffff","#000000"]),'spec_color':sp_id,'stroke_style':ss_map.get(ss_id,'solid'),'key':SMV})
		if self.tasks_q:
			self.total_tasks,self.completed_tasks=len(self.tasks_q),0;self.task_progress={t['uid']:0 for t in self.tasks_q}
			self.total_pbar.setValue(0);self.total_pbar.setFormat(f"Total: 0% (0/{self.total_tasks})");self.total_pbar.show()
			for t in self.tasks_q[:self.max_w]:
				it=self.find_item_by_uid(t['uid'])
				if it:it.setData(Qt.UserRole+3,"Work");self.set_status_visual(it,"Work");pb=self.repo[t['uid']]['pb'];pb.setValue(0);pb.setFormat("Initializing...");pb.show()
			for t in self.tasks_q[self.max_w:]:
				it=self.find_item_by_uid(t['uid'])
				if it:it.setData(Qt.UserRole+3,"Wait");self.set_status_visual(it,"Wait")
			QApplication.processEvents()
			self.is_rendering=True;self.start_pool_tasks()
	def start_pool_tasks(self):
		self.pool_th=PoolManagerThread(self.tasks_q,self.max_w)
		self.pool_th.item_start.connect(self.on_item_start);self.pool_th.item_prog.connect(self.on_item_progress)
		self.pool_th.item_done.connect(self.on_item_done);self.pool_th.item_fail.connect(self.on_item_fail)
		self.pool_th.all_done.connect(lambda:(self.active_th.clear(),self.on_all_done()))
		self.active_th=[self.pool_th];self.pool_th.start();self.update_buttons()
	def stop_task(self):
		self.total_pbar.hide()
		self.loader.show();QApplication.processEvents();outs=[t['out_path'] for t in getattr(self.pool_th,'tasks',[])] if hasattr(self,'pool_th') else [];self.tasks_q=[];self.is_rendering=False
		if hasattr(self,'pool_th'):self.pool_th.stopped=True
		subprocess.run("taskkill /f /im ffmpeg.exe",shell=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
		if hasattr(self,'pool_th'):
			if not self.pool_th.wait(3000):self.pool_th.terminate();self.pool_th.wait()
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
			if it.data(Qt.UserRole+3) in ["Work","Wait"]:
				it.setData(Qt.UserRole+3,"New");self.set_status_visual(it,"New")
				pb=self.repo[it.data(Qt.UserRole+10)]['pb'];pb.hide();pb.setValue(0)
		self.active_th=[];self.on_all_done()
	def on_all_done(self):
		self.total_pbar.hide();self.loader.hide();self.update_buttons()
		if self.is_rendering:
			self.is_rendering=False;snd_file=settings.value("finish_sound","default")
			if snd_file!="none" and snd_file!="":
				s_dir=rp(os.path.join("assets","sounds"))
				if not os.path.exists(s_dir): s_dir=os.path.join(os.path.abspath("."),"assets","sounds")
				snd_p=os.path.join(s_dir,snd_file) if snd_file and snd_file!="default" else ""
				if not snd_p or not os.path.exists(snd_p):
					snd_p=""
					if os.path.exists(s_dir):
						s_files=sorted([f for f in os.listdir(s_dir) if f.lower().startswith("finish") and f.lower().endswith(".wav")])
						if s_files:snd_p=os.path.join(s_dir,s_files[0])
				if snd_p and os.path.exists(snd_p):
					self._p.setSource(QUrl.fromLocalFile(snd_p));self._p.play()
			QTimer.singleShot(100,lambda:self.exec_ov(SuccessDialog(self,self.has_errors,self.has_loggable_errors)))
	def remove_completed(self):
		for i in range(self.lst.count()-1,-1,-1):
			if self.lst.item(i).data(Qt.UserRole+3) in ["Done","Exist","Clone"]:
				it=self.lst.takeItem(i);self.repo.pop(it.data(Qt.UserRole+10),None)
		self.update_buttons()
	def duplicate_all(self):
		cnt=self.lst.count()
		for i in range(cnt):
			it=self.lst.item(i);self.add_item(it.data(Qt.UserRole),copy_uid=it.data(Qt.UserRole+10))
	def remove_duplicates(self):
		seen=set()
		for i in range(self.lst.count()-1,-1,-1):
			it=self.lst.item(i);uid=it.data(Qt.UserRole+10)
			if uid not in self.repo:continue
			r=self.repo[uid]
			sig=(it.data(Qt.UserRole),r['tmpl'][0].property("tmpl_id"),r['s'].property("stroke_id"),r['c'].property("color_id"),r['ss'].property("style_id"),r['sp'].property("spec_id"))
			if sig in seen:
				self.repo.pop(uid,None);self.lst.takeItem(i)
			else:seen.add(sig)
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
		t_dir=get_app_data("temp")
		if os.path.exists(t_dir):
			ct=time.time()
			for f in glob.glob(os.path.join(t_dir,"*")):
				try:
					if f.endswith(".npz"):
						if ct-os.path.getmtime(f)>CACHE_TTL_SEC:os.remove(f)
					else:os.remove(f)
				except:pass
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