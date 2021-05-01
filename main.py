
import xml.etree.ElementTree as ET

from numpy.core.fromnumeric import size
import PySimpleGUI as sg
import pandas as pd

import cv2
import csv

import os
import json
import itertools

# todo : change writer to df

def nextBtn():
    return sg.Button("Next Image",size=(10,3))

    
def nextAnnBtn():
    return sg.Button("Next Ann",size=(7,2))


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
    window['-subject-'].update(anns[ann_pairs[j][0]])
    cv2.rectangle(frame_copy, (x1, y1),(x2, y2), (255,0,0), 2)
    x1,y1,x2,y2 = json.loads(ann_pairs[j][1])
    window['-object-'].update(anns[ann_pairs[j][1]])
    cv2.rectangle(frame_copy, (x1, y1),(x2, y2), (255,0,0), 2)

    subject = df[(df["subject"] == anns[ann_pairs[j][0]]) ]
    object = subject.loc[subject["object"] ==anns[ann_pairs[j][1]], "predicate"]
    try:
        window['-predicate-'].update(object.values[0])
    except:
        window['-predicate-'].update("nil")
    resized_image = cv2.resize(frame_copy, (650,450))
    imgbytes = cv2.imencode('.png', resized_image)[1].tobytes()
    return imgbytes


def write_csv(response,df,anns,ann_pairs,vrd_filename,img_files,i,writer,j):
        predicate = response["-predicateList-"]
        if(predicate):
            subject = df[(df["subjectAnn"] == ann_pairs[j-1][0]) ]
            object = subject.loc[subject["objectAnn"] ==ann_pairs[j-1][1], "predicate"]
            try:
                df.loc[object.index[0],'predicate']=predicate
                df.to_csv(vrd_filename+"/"+img_files[i-1][:-4]+".csv", index=False)
            except:
                # writer.writerow([anns[ann_pairs[j-1][0]],ann_pairs[j-1][0], predicate, anns[ann_pairs[j-1][1]], ann_pairs[j-1][1]])
                df.loc[len(df.index)] = [anns[ann_pairs[j-1][0]],ann_pairs[j-1][0], predicate, anns[ann_pairs[j-1][1]], ann_pairs[j-1][1]] 
                df.to_csv(vrd_filename+"/"+img_files[i-1][:-4]+".csv", index=False)



def get_list(ann_pairs,anns,df):
    ann_pairs_list=[]
    for ann_pair in ann_pairs:
        subject = df[(df["subjectAnn"] == ann_pair[0]) ]
        object = subject.loc[subject["objectAnn"] == ann_pair[1], "predicate"]
        try:
            ann_pairs_list.append(anns[ann_pair[0]]+"   "+object.values[0]+"    "+anns[ann_pair[1]])
        except:
            ann_pairs_list.append(anns[ann_pair[0]]+"   nil   "+anns[ann_pair[1]])
    return ann_pairs_list
        

def update_predicate(df,anns,ann_pairs,window,j):
    subject = df[(df["subjectAnn"] == ann_pairs[j][0]) ]
    object = subject.loc[subject["objectAnn"] ==ann_pairs[j][1], "predicate"]
    try:
        window['-predicate-'].update(object.values[0])
    except:
        window['-predicate-'].update("nil")

def main():

    # filename = sg.popup_get_folder('Filename with Imgs and Anns')
    filename = "/home/phi/code/Neuroplex/vrd_gui/demo/airport-data"
    print(filename)
    if filename is None:
        return
    imgs_filename = filename+'/JPEGImages'
    anns_filename = filename+'/Annotations'
    vrd_filename = filename+'/vrd'
    
    img_files = os.listdir(imgs_filename)

    predicatesfile = open("/home/phi/code/Neuroplex/vrd_gui/predicates.txt", 'r')
    predicates_list = [line.rstrip() for line in predicatesfile.readlines()]
    predicates_list=list(set(predicates_list))
    predicates_list.sort()


    block_1 = [[sg.Image(filename='', key='image')], [sg.Text(size=(10,1), key='-subject-',font='Any 20'),sg.Text(size=(10,1), key='-predicate-',font='Any 20', text_color='#66CDAA'),sg.Text(size=(10,1), key='-object-',font='Any 20')],
                [sg.Text('Predicate :',font='Any 20'), sg.Combo(predicates_list, size=(22,30), key='-predicateList-')],[ nextAnnBtn()],[ nextBtn()]]

    block_3 = [[sg.Text('Images', font='Any 20')],
            [sg.Listbox(img_files, size=(20, 30),default_values=[img_files[0],], bind_return_key=True, key='-LISTBOXImg-')]]

    block_2 = [[sg.Text('Relationships', font='Any 20')],
            [sg.Listbox([], size=(30, 30), bind_return_key=True, key='-LISTBOXAnn-')]]

    layout = [[sg.Column(block_1),sg.Column(block_2),sg.Column(block_3)]]

    window = sg.Window('VRD Application ', layout, location=(800, 400),resizable=True)

    i=0
    while window(timeout=20)[0] is not None:
        response = {}
        event, response = window.Read()
        print(event)


        if event =="-LISTBOXImg-":
            window.Element('-predicateList-').update(value='', values=predicates_list)
            i= img_files.index(response["-LISTBOXImg-"][0])
            j=0

            vidFile = cv2.VideoCapture(imgs_filename+"/"+img_files[i])
            anns = get_annotation(anns_filename+"/"+img_files[i][:-4]+".xml")
            
            if(os.path.isfile(vrd_filename+"/"+img_files[i][:-4]+".csv")) :
                file = open(vrd_filename+"/"+img_files[i][:-4]+".csv", 'a')
                writer = csv.writer(file)
            else:
                file = open(vrd_filename+"/"+img_files[i][:-4]+".csv", 'w')
                writer = csv.writer(file)
                writer.writerow(["subject", "subjectAnn", "predicate", "object", "objectAnn"])
                file.close()
                file = open(vrd_filename+"/"+img_files[i][:-4]+".csv", 'a')
                writer = csv.writer(file)

            df = pd.read_csv(vrd_filename+"/"+img_files[i][:-4]+".csv")

            i+=1
            ret, frame = vidFile.read()
            #
            anns_keys=[]
            for key, value in anns.items():
                anns_keys.append(key)

            ann_pairs=[]
            for k in range(0,len(anns)):
                for l in range(0,len(anns)):
                    if(k!=l and anns[anns_keys[l]]=="aeroplane"):
                        ann_pairs.append((anns_keys[k],anns_keys[l]))
            #

            # ann_pairs = (list(itertools.combinations(anns.keys(), 2)))
            ann_pairs_list=[]
            ann_pairs_list=get_list(ann_pairs,anns,df)
            window.Element('-LISTBOXAnn-').Update(ann_pairs_list)

            imgbytes = img(frame,window,ann_pairs,anns,j,df)

            update_predicate(df,anns,ann_pairs,window,j)
            j+=1


        if event == "Next Image" and i!=len(img_files):
            j=0
            window.Element('-LISTBOXImg-').Update(set_to_index=i) 
            # window.Element('-LISTBOXAnn-').Update(set_to_index=0) 
            window.Element('-predicateList-').update(value='', values=predicates_list)

            vidFile = cv2.VideoCapture(imgs_filename+"/"+img_files[i])
            anns = get_annotation(anns_filename+"/"+img_files[i][:-4]+".xml")

            if(os.path.isfile(vrd_filename+"/"+img_files[i][:-4]+".csv")) :
                file = open(vrd_filename+"/"+img_files[i][:-4]+".csv", 'a')
                writer = csv.writer(file)
            else:
                file = open(vrd_filename+"/"+img_files[i][:-4]+".csv", 'w')
                writer = csv.writer(file)
                writer.writerow(["subject", "subjectAnn", "predicate", "object", "objectAnn"])
                file.close()
                file = open(vrd_filename+"/"+img_files[i][:-4]+".csv", 'a')
                writer = csv.writer(file)

            df = pd.read_csv(vrd_filename+"/"+img_files[i][:-4]+".csv")

            i+=1
            ret, frame = vidFile.read()
            #
            anns_keys=[]
            for key, value in anns.items():
                anns_keys.append(key)

            ann_pairs=[]
            for k in range(0,len(anns)):
                for l in range(0,len(anns)):
                    if(k!=l and anns[anns_keys[l]]=="aeroplane"):
                        ann_pairs.append((anns_keys[k],anns_keys[l]))
            #
            # ann_pairs = (list(itertools.combinations(anns.keys(), 2)))
            ann_pairs_list=[]
            ann_pairs_list=get_list(ann_pairs,anns,df)
            window.Element('-LISTBOXAnn-').Update(ann_pairs_list)

            update_predicate(df,anns,ann_pairs,window,j)

            imgbytes = img(frame,window,ann_pairs,anns,j,df)
            j+=1

        
        if event == "-LISTBOXAnn-":
            window.Element('-predicateList-').update(value='', values=predicates_list)
            # j=ann_pairs_list.index(response["-LISTBOXAnn-"][0])
            j=window[event].GetIndexes()[0]
            print(window[event].GetIndexes()[0])
            imgbytes = img(frame,window,ann_pairs,anns,j,df)

            update_predicate(df,anns,ann_pairs,window,j)
            
            write_csv(response,df,anns,ann_pairs,vrd_filename,img_files,i,writer,j)
            j+=1


        if(event=="Next Ann") and j!=len(ann_pairs):
            # #updating the list in window
            # ann_pairs_list=[]
            # ann_pairs_list=get_list(ann_pairs,anns,df)
            # window.Element('-LISTBOXAnn-').Update(ann_pairs_list)

            # reseting the  predciates dropdown
            window.Element('-predicateList-').update(value='', values=predicates_list)


            imgbytes = img(frame,window,ann_pairs,anns,j,df)

            update_predicate(df,anns,ann_pairs,window,j)

            write_csv(response,df,anns,ann_pairs,vrd_filename,img_files,i,writer,j)
            print(ann_pairs,anns)
            #updating the list in window
            ann_pairs_list=[]
            ann_pairs_list=get_list(ann_pairs,anns,df)
            window.Element('-LISTBOXAnn-').Update(ann_pairs_list)  
            # updating the selected relationship
            window.Element('-LISTBOXAnn-').Update(set_to_index=j)          
            j+=1
            
        elif(j==len(ann_pairs)):
            write_csv(response,df,anns,ann_pairs,vrd_filename,img_files,i,writer,j)
            #updating the list in window
            ann_pairs_list=[]
            ann_pairs_list=get_list(ann_pairs,anns,df)
            window.Element('-LISTBOXAnn-').Update(ann_pairs_list)  
            # updating the selected relationship
            window.Element('-LISTBOXAnn-').Update(set_to_index=j) 
            j=0
    
        # if(event=="Submit"):
        #     write_csv(response,df,anns,ann_pairs,vrd_filename,img_files,i,writer,j)
        #     # reseting the  predciates dropdown
        #     window.Element('-predicateList-').update(value='', values=predicates_list)
        #     #updating the list in window
        #     ann_pairs_list=[]
        #     ann_pairs_list=get_list(ann_pairs,anns,df)
        #     window.Element('-LISTBOXAnn-').Update(ann_pairs_list)


        window['image'](data=imgbytes)



main()