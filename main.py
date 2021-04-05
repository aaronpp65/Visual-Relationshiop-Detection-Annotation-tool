
import xml.etree.ElementTree as ET

from numpy.core.fromnumeric import size
import PySimpleGUI as sg
import pandas as pd

import cv2
import csv

import os
import json
import itertools

def nextBtn():
    return sg.Button("Next Image")


def prevBtn():
    return sg.Button("Previous")
    
def nextAnnBtn():
    return sg.Button("Next Ann")


def prevAnnBtn():
    return sg.Button("Previous Ann")

def get_annotation(ann_path):

    in_file = open(ann_path)
    tree=ET.parse(in_file)
    root = tree.getroot()
    anns={}

    for obj in root.iter('object'):
        cls = obj.find('name').text
        bbox = obj.find('bndbox')
        if(bbox):
            xmin=bbox.find('xmin').text
            ymin=bbox.find('ymin').text
            xmax=bbox.find('xmax').text
            ymax=bbox.find('ymax').text    
            anns[str([int(xmin),int(ymin),int(xmax),int(ymax)])]=cls
    return anns

def img(frame,window,ann_pairs,anns,j,df):
    frame_copy = frame.copy()
    x1,y1,x2,y2 = json.loads(ann_pairs[j][0])
    window['-label1-'].update(anns[ann_pairs[j][0]])
    cv2.rectangle(frame_copy, (x1, y1),(x2, y2), (255,0,0), 2)
    x1,y1,x2,y2 = json.loads(ann_pairs[j][1])
    window['-label2-'].update(anns[ann_pairs[j][1]])
    cv2.rectangle(frame_copy, (x1, y1),(x2, y2), (255,0,0), 2)

    label1 = df[(df["label1"] == anns[ann_pairs[j][0]]) ]
    label2 = label1.loc[label1["label2"] ==anns[ann_pairs[j][1]], "predicate"]
    try:
        window['-predicate-'].update(label2.values[0])
    except:
        window['-predicate-'].update("nil")
    resized_image = cv2.resize(frame_copy, (650,450))
    imgbytes = cv2.imencode('.png', resized_image)[1].tobytes()
    return imgbytes


def write_csv(response,df,anns,ann_pairs,vrd_filename,img_files,i,writer,j):
        predicate = response["Answer"]
        if(predicate):
            label1 = df[(df["label1"] == anns[ann_pairs[j-1][0]]) ]
            label2 = label1.loc[label1["label2"] ==anns[ann_pairs[j-1][1]], "predicate"]
            try:
                df.loc[label2.index[0],'predicate']=predicate
                df.to_csv(vrd_filename+"/"+img_files[i-1][:-4]+".csv", index=False)
            except:
                writer.writerow([anns[ann_pairs[j-1][0]],ann_pairs[j-1][0], predicate, anns[ann_pairs[j-1][1]], ann_pairs[j-1][1]])

def ann_pairs_list(ann_pairs,anns,df,window):
    ann_pairs_list=[]
    for ann_pair in ann_pairs:
        label1 = df[(df["label1"] == anns[ann_pair[0]]) ]
        label2 = label1.loc[label1["label2"] ==anns[ann_pair[1]], "predicate"]
        try:
            ann_pairs_list.append(anns[ann_pair[0]]+"   "+label2.values[0]+"    "+anns[ann_pair[1]])
        except:
            ann_pairs_list.append(anns[ann_pair[0]]+"   nil   "+anns[ann_pair[1]])
        
        window.Element('-LISTBOXAnn-').Update(ann_pairs_list)

def update_predicate(df,anns,ann_pairs,window,j):
    label1 = df[(df["label1"] == anns[ann_pairs[j][0]]) ]
    label2 = label1.loc[label1["label2"] ==anns[ann_pairs[j][1]], "predicate"]
    try:
        window['-predicate-'].update(label2.values[0])
    except:
        window['-predicate-'].update("nil")

def main():

    filename = sg.popup_get_folder('Filename with Imgs and Anns')
    if filename is None:
        return
    imgs_filename = filename+'/JPEGImages'
    anns_filename = filename+'/Annotations'
    vrd_filename = filename+'/vrd'
    
    img_files = os.listdir(imgs_filename)

    block_4 = [[sg.Text('Images', font='Any 20')],
            [sg.Listbox(img_files, size=(20, 30),default_values=[img_files[0],], bind_return_key=True, key='-LISTBOX-')]]
    block_5 = [[sg.Text('Ann Pairs', font='Any 20')],
            [sg.Listbox([], size=(30, 30), bind_return_key=True, key='-LISTBOXAnn-')]]
    layout = [
        [sg.Column([[sg.Image(filename='', key='image')], [sg.Text(size=(10,1), key='-label1-'),sg.Text(size=(10,1), key='-predicate-'),sg.Text(size=(10,1), key='-label2-')],[sg.InputText(key="Answer", do_not_clear=False)],
                [ nextAnnBtn()],[ nextBtn()]]),
                    sg.Column(block_4),sg.Column(block_5)]]
    window = sg.Window('VRD Application ', layout, location=(800, 400),resizable=True)

    i=0
    while window(timeout=20)[0] is not None:
        response = {}
        event, response = window.Read()
        print(event)


        if event =="-LISTBOX-":
            i= img_files.index(response["-LISTBOX-"][0])
            j=0

            vidFile = cv2.VideoCapture(imgs_filename+"/"+img_files[i])
            anns = get_annotation(anns_filename+"/"+img_files[i][:-4]+".xml")
            
            if(os.path.isfile(vrd_filename+"/"+img_files[i][:-4]+".csv")) :
                file = open(vrd_filename+"/"+img_files[i][:-4]+".csv", 'a')
                writer = csv.writer(file)
            else:
                file = open(vrd_filename+"/"+img_files[i][:-4]+".csv", 'w')
                writer = csv.writer(file)
                writer.writerow(["label1", "ann1", "predicate", "label2", "ann2"])
                file.close()
                file = open(vrd_filename+"/"+img_files[i][:-4]+".csv", 'a')
                writer = csv.writer(file)

            df = pd.read_csv(vrd_filename+"/"+img_files[i][:-4]+".csv")

            i+=1
            ret, frame = vidFile.read()

            ann_pairs = (list(itertools.combinations(anns.keys(), 2)))
            ann_pairs_list(ann_pairs,anns,df,window)
            # for ann_pair in ann_pairs:
            #     label1 = df[(df["label1"] == anns[ann_pair[0]]) ]
            #     label2 = label1.loc[label1["label2"] ==anns[ann_pair[1]], "predicate"]
            #     try:
            #         ann_pairs_list.append(anns[ann_pair[0]]+"   "+label2.values[0]+"    "+anns[ann_pair[1]])
            #     except:
            #         ann_pairs_list.append(anns[ann_pair[0]]+"   nil   "+anns[ann_pair[1]])

            # window.Element('-LISTBOXAnn-').Update(ann_pairs_list)

            imgbytes = img(frame,window,ann_pairs,anns,j,df)

            # label1 = df[(df["label1"] == anns[ann_pairs[j][0]]) ]
            # label2 = label1.loc[label1["label2"] ==anns[ann_pairs[j][1]], "predicate"]
            # try:
            #     window['-predicate-'].update(label2.values[0])
            # except:
            #     window['-predicate-'].update("nil")
            update_predicate(df,anns,ann_pairs,window,j)
            j+=1


        if event == "Next Image" and i!=len(img_files):
            j=0
            window.Element('-LISTBOX-').Update(set_to_index=i) 

            vidFile = cv2.VideoCapture(imgs_filename+"/"+img_files[i])
            anns = get_annotation(anns_filename+"/"+img_files[i][:-4]+".xml")

            if(os.path.isfile(vrd_filename+"/"+img_files[i][:-4]+".csv")) :
                file = open(vrd_filename+"/"+img_files[i][:-4]+".csv", 'a')
                writer = csv.writer(file)
            else:
                file = open(vrd_filename+"/"+img_files[i][:-4]+".csv", 'w')
                writer = csv.writer(file)
                writer.writerow(["label1", "ann1", "predicate", "label2", "ann2"])
                file.close()
                file = open(vrd_filename+"/"+img_files[i][:-4]+".csv", 'a')
                writer = csv.writer(file)

            df = pd.read_csv(vrd_filename+"/"+img_files[i][:-4]+".csv")

            i+=1
            ret, frame = vidFile.read()

            ann_pairs = (list(itertools.combinations(anns.keys(), 2)))
            ann_pairs_list(ann_pairs,anns,df,window)
            # for ann_pair in ann_pairs:
            #     label1 = df[(df["label1"] == anns[ann_pair[0]]) ]
            #     label2 = label1.loc[label1["label2"] ==anns[ann_pair[1]], "predicate"]
            #     try:
            #         ann_pairs_list.append(anns[ann_pair[0]]+"   "+label2.values[0]+"    "+anns[ann_pair[1]])
            #     except:
            #         ann_pairs_list.append(anns[ann_pair[0]]+"   nil   "+anns[ann_pair[1]])

            # window.Element('-LISTBOXAnn-').Update(ann_pairs_list)

            # label1 = df[(df["label1"] == anns[ann_pairs[j][0]]) ]
            # label2 = label1.loc[label1["label2"] ==anns[ann_pairs[j][1]], "predicate"]
            # try:
            #     window['-predicate-'].update(label2.values[0])
            # except:
            #     window['-predicate-'].update("nil")
            update_predicate(df,anns,ann_pairs,window,j)

            imgbytes = img(frame,window,ann_pairs,anns,j,df)
            j+=1

        
        if event == "-LISTBOXAnn-":
            print(ann_pairs_list.index(response["-LISTBOXAnn-"][0]))
            j=ann_pairs_list.index(response["-LISTBOXAnn-"][0])
            imgbytes = img(frame,window,ann_pairs,anns,j,df)


            # label1 = df[(df["label1"] == anns[ann_pairs[j][0]]) ]
            # label2 = label1.loc[label1["label2"] ==anns[ann_pairs[j][1]], "predicate"]
            # try:
            #     window['-predicate-'].update(label2.values[0])
            # except:
            #     window['-predicate-'].update("nil")
            update_predicate(df,anns,ann_pairs,window,j)
            
            write_csv(response,df,anns,ann_pairs,vrd_filename,img_files,i,writer,j)
            j+=1


        if(event=="Next Ann") and j!=len(ann_pairs):
            window.Element('-LISTBOXAnn-').Update(set_to_index=j) 


            imgbytes = img(frame,window,ann_pairs,anns,j,df)


            # label1 = df[(df["label1"] == anns[ann_pairs[j][0]]) ]
            # label2 = label1.loc[label1["label2"] ==anns[ann_pairs[j][1]], "predicate"]
            # try:
            #     window['-predicate-'].update(label2.values[0])
            # except:
            #     window['-predicate-'].update("nil")
            update_predicate(df,anns,ann_pairs,window,j)

            write_csv(response,df,anns,ann_pairs,vrd_filename,img_files,i,writer,j)
            j+=1
            
        if(j==len(ann_pairs)):
            write_csv(response,df,anns,ann_pairs,vrd_filename,img_files,i,writer,j)
            j=0

        window['image'](data=imgbytes)



main()