import multiprocessing,sys,os
if sys.platform.startswith('win'):multiprocessing.freeze_support()
if __name__=='__main__':
	try:
		import main
		main.start()
	except Exception as e:
		import traceback;traceback.print_exc()
		import ctypes;ctypes.windll.user32.MessageBoxW(0,f"Error: {e}","Error",16)