from tkinter import *
from tkinter import filedialog
from PIL import Image
from PIL import ImageTk
from tkinter import Tk, Label
import cv2
import tkinter as tk
import os
import imutils
import sqlite3 as sl

from models.common import DetectMultiBackend
from utils.torch_utils import select_device
from detect import run


#global variables
weights='models/best.pt'
device = select_device('')
model = DetectMultiBackend(weights, device=device, dnn=False, data='data/aracTip.yaml')
stride, names, pt = model.stride, model.names, model.pt
imgsz = [640, 640]  # inference size (height, width)
conf_thres = 0.35  # confidence threshold
iou_thres = 0.45  # NMS IOU threshold
max_det = 1000  # maximum detections per image
classes = None  # filter by class: --class 0, or --class 0 2 3
line_thickness = 3  # bounding box thickness (pixels)
detectionLine = 1.8
thickness = 8
####################################################
# Veritabanina baglanma ve data yolunu ve ismini orada bulunan roads tablena kaydetme
db = sl.connect("db.sqlite")
cs=None
ROAD_ID = None
#######stopdetection
stopVideo=False
# arac kordinatlari icin ve sayisi icin tanimlanan arrayler
aracKordinat = [[0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0]]
aracSayisi = [0, 0, 0, 0, 0, 0, 0, 0]

def video():
    global cs,ROAD_ID,db,Labels,labelIndicator,stopVideo
    global cap,model,names,device,aracKordinat,aracSayisi, conf_thres, iou_thres, max_det, classes, line_thickness, detectionLine,thickness
    ret, frame = cap.read()
    if ret == True:
        frame=run(model,names,frame,device,aracKordinat,aracSayisi, conf_thres, iou_thres, max_det, classes, line_thickness, detectionLine,cs,ROAD_ID,db,thickness)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        im = Image.fromarray(frame)
        im=im.resize((620, 337), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(image=im)
        IblVideo.configure(image=img)
        IblVideo.image = img
        labelIndicator=0
        for car in names:
            cs.execute('''select SUM(quantity) from road_car where car_id=? and road_id=?''',(labelIndicator,ROAD_ID))
            sayi=cs.fetchone()[0]
            if(sayi):
                if(yon.get()==2):
                    labelGelisSayi[labelIndicator]['text']=f"{sayi}"
                else:
                    labelGidisSayi[labelIndicator]['text'] = f"{sayi}"
            labelIndicator+=1
        if not stopVideo:
            IblVideo.after(1,video)

def stop():
    global stopVideo
    stopVideo=True
    btnStop_btn.grid_forget()
    IblVideo.grid_forget()
    logo_label.grid(column=0, row=0,columnspan=7,rowspan=3)
    btnbrowse_btn.grid(column=4,columnspan=2,row=2)

#video secme fonksiyonu
def browse():
    global cap,db,cs,ROAD_ID,stopVideo,detectionLine
    path_video = filedialog.askopenfilename(filetypes = [
        ("all video format", ".mp4"),
        ("all video format", ".avi")])
    if len(path_video) > 0:
        #eklenilen videodaki yolu veritabanina ekleme ve ROAD_ID degiskenine atama
        cs = db.cursor()
        cs.execute("insert into roads (name) values (?)", ([path_video]))
        db.commit()
        ROAD_ID=cs.lastrowid
        if(yon.get()==2):
            detectionLine=1.8
        else:
            detectionLine=2.8
        ###########################################################################
        logo_label.grid_forget()
        btnbrowse_btn.grid_forget()
        btnStop_btn.grid(column=4,columnspan=2,row=2)
        IblVideo.grid(column=0,row=0,rowspan=3,columnspan=7)
        stopVideo=False
        cap = cv2.VideoCapture(path_video)
        labelSayisifirlama()
        video()



#tasarim kodlari
#########################################################################
#baslangic penceresi tasarimi

root = Tk()
root.title("KARAYOLLARINDA ARAÇ TESPİTİ")
root.iconbitmap(r'data/icons/logo.ico')
screen_height=root.winfo_screenheight()
screen_width=root.winfo_screenwidth()
root.state("zoomed")
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

frmUst = Frame(root,bg='#2d4483',width=screen_width)
frmMiddle = Frame(root,bg="orangered",width=screen_width)
frmALt = Frame(root,width=screen_width)



frmUst.grid(row=0, column=0,columnspan=4,sticky="NESW")
frmUst.grid_rowconfigure(0, weight=2)
frmUst.grid_rowconfigure(1, weight=1)
frmUst.grid_rowconfigure(2, weight=1)
frmUst.grid_columnconfigure(0, weight=4)
frmUst.grid_columnconfigure(1, weight=2)
frmUst.grid_columnconfigure(2, weight=2)
frmUst.grid_columnconfigure(3, weight=2)
frmUst.grid_columnconfigure(4, weight=0)
frmUst.grid_columnconfigure(5, weight=0)
frmUst.grid_columnconfigure(6, weight=1)
#logo tasarimi
logo = Image.open('logo6.jpg')
logo=logo.resize((620, 337), Image.ANTIALIAS)
logo = ImageTk.PhotoImage(logo)
logo_label = tk.Label(frmUst,image=logo)
logo_label.image = logo
logo_label.grid(column=0,row=0,rowspan=3,columnspan=7)

######################################################################
yon=IntVar()
gidisCheck = Radiobutton(frmUst,bg='orange', text="Gidiş Yönü", variable=yon, value=1,height=2,padx=3,font=('Halvetica',10,'bold'))
gelisCheck = Radiobutton(frmUst,bg='orange', text='Geliş Yönü',variable=yon, value=2,height=2,padx=3,font=('Halvetica',10,'bold'))
gelisCheck.grid(column=4,row=1)
gidisCheck.grid(column=5,row=1)
#secme buttonu
btnbrowse_btn = Button(frmUst, text='Bir video seciniz', command=browse, bg="#222", fg="white", height=2, width=15,font=('Halvetica',13,'bold'),borderwidth=0)
btnbrowse_btn.grid(column=4,columnspan=2,row=2)
#Durdurma buttonu
btnStop_btn = Button(frmUst, text='Durdur', command=stop, bg="#a42020", fg="white", height=2, width=15,font=('Halvetica',13,'bold'),borderwidth=0)
#btnStop_btn.grid(column=4,columnspan=2,row=2)



##############################################################################

frmMiddle.grid(row=2, column=0,columnspan=2,sticky="NESW")
frmMiddle.grid_rowconfigure(0, weight=1)
frmMiddle.grid_columnconfigure(1, weight=1)
frmMiddle.grid_columnconfigure(0, weight=1)
#gelis yonu
gelis = Image.open('data/icons/gelis.png')
img1 = gelis.resize((35,30), Image.ANTIALIAS)
img1 = ImageTk.PhotoImage(img1)
gelisLabel = tk.Label(frmMiddle,text=" Geliş Yönü",font=('Halvetica',15,'bold'),bg="orangered",fg='white')
gelisLabel["compound"] = tk.LEFT
gelisLabel["image"] = img1
#gidis yonu
gidis = Image.open('data/icons/gidis.png')
img2 = gidis.resize((35,30), Image.ANTIALIAS)
img2 = ImageTk.PhotoImage(img2)
gidisLabel=tk.Label(frmMiddle,text=" Gidiş Yönü",font=('Halvetica',15,'bold'),bg="orangered",fg='white')
gidisLabel["compound"] = tk.LEFT
gidisLabel["image"] = img2
gelisLabel.grid(column=0,row=0)
gidisLabel.grid(column=1,row=0)



#araclar table
frmALt.grid(row=3, column=0,columnspan=4,sticky="NESW")
frmALt.grid_rowconfigure(0, weight=1)
frmALt.grid_columnconfigure(0, weight=1)
frmALt.grid_columnconfigure(1, weight=1)
frmALt.grid_columnconfigure(2, weight=1)
frmALt.grid_columnconfigure(3, weight=1)

labelIcons=['data/icons/ambulans.png',
            'data/icons/otobus.png',
            'data/icons/otomobil.png',
            'data/icons/motorsiklet.png',
            'data/icons/tank.png',
            'data/icons/taksi.png',
            'data/icons/kamyon.png',
            'data/icons/minibus.png',
            ]

labelGelis=[]
labelGelisSayi=[]
labelIndicator=0
labelGelisIcon=[]
def gelisLabelYazdirma():
    global labelGelis,labelGelisSayi,labelIndicator,labelGelisIcon
    labelIndicator=0
    for car in names:
        labelGelis.append(tk.Label(frmALt,text=f" {car}",font=('Comic Sans MS',15,'normal')))
        labelGelisSayi.append(tk.Label(frmALt,text="0",font=('Comic Sans MS',15,'normal'),fg="orangered"))
        imgIcon=Image.open(labelIcons[labelIndicator])
        imgIcon = imgIcon.resize((37, 25), Image.ANTIALIAS)
        imgIcon = ImageTk.PhotoImage(imgIcon)
        labelGelisIcon.append(imgIcon)
        labelGelis[labelIndicator]["compound"] = tk.LEFT
        labelGelis[labelIndicator]["image"]=labelGelisIcon[labelIndicator]
        labelGelis[labelIndicator].grid(column=0,row=labelIndicator,sticky="w",padx=80)
        labelGelisSayi[labelIndicator].grid(column=1,row=labelIndicator,sticky="w")
        labelIndicator+=1

labelsGidis=[]
labelGidisSayi=[]
def gidisLabelYazdirma():
    global labelIndicator,labelsGidis,labelGidisSayi
    labelIndicator=0
    for car in names:
        labelsGidis.append(tk.Label(frmALt,text=f" {car}",font=('Comic Sans MS',15,'normal')))
        labelGidisSayi.append(tk.Label(frmALt,text="0",font=('Comic Sans MS',15,'normal'),fg="orangered"))
        labelsGidis[labelIndicator]["compound"] = tk.LEFT
        labelsGidis[labelIndicator]["image"]=labelGelisIcon[labelIndicator]
        labelsGidis[labelIndicator].grid(column=2,row=labelIndicator,sticky="w",padx=80)
        labelGidisSayi[labelIndicator].grid(column=3,row=labelIndicator,sticky="w")
        labelIndicator+=1
gelisLabelYazdirma()
gidisLabelYazdirma()

def labelSayisifirlama():
    global labelGidisSayi,labelGelisSayi
    labelIndicator = 0
    for car in names:
        labelGelisSayi[labelIndicator]['text'] ="0"
        labelGidisSayi[labelIndicator]['text'] ="0"
        labelIndicator+=1
cap=None
IblVideo = Label(frmUst)

root.mainloop()