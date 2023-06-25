from live_tkwindow import *
dialog = tkdialog("test",("test1","test2"),("192.168.0.128","7777"))
out = dialog.input
del dialog
print(out)
# t1 = threading.Thread(target=quick)
# t1.start()
