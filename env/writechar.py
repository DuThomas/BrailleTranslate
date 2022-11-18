import cv2
import brailleTable
def write(img,tlcorner,char):
    print(tlcorner)
    color=[255,255,255]
    m = ""
    for cle,val in brailleTable.brailleTable.items():
        if (val == char):
            m=cle
    x=0
    y=0
    # for j in range(5):

    #     if (j==3):
    #         x+=2
    #         y=0
    #     if (m[j]=='1'):
    #         img[tlcorner[0]+y][tlcorner[1]+x]=color
    #     y+=2
            
    for i in range(len(m)):
        if(m[i]=='1'):
            img[tlcorner[0]+i%3 * 2,tlcorner[1] + i//3 * 2]=color

    # img[tlcorner[]+2,tlcorner[1]]=color
    # img[tlcorner[0]+2,tlcorner[1]]=color
    # img[tlcorner[0]+2,tlcorner[1]+2]=color
    # img[tlcorner[0],tlcorner[1]+2]=color
    # img[tlcorner[0],tlcorner[1]+4]=color

def write2(img,tlcorner,height,width,char):
    for lignes in range(0,height,6):
        for colonnes in range(0,width,4):
            write3(img,(tlcorner[0]+lignes,tlcorner[1]+colonnes))

def write3(img,tlcorner):
    print(tlcorner)
    color=[255,255,255]
    m = ""
    char = input()
    for cle,val in brailleTable.brailleTable.items():
        if (val == char):
            m=cle
    x=0
    y=0
    # for j in range(5):

    #     if (j==3):
    #         x+=2
    #         y=0
    #     if (m[j]=='1'):
    #         img[tlcorner[0]+y][tlcorner[1]+x]=color
    #     y+=2
            
    for i in range(len(m)):
        if(m[i]=='1'):
            img[tlcorner[0]+i%3 * 2,tlcorner[1] + i//3 * 2]=color