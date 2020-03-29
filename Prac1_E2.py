from pydicom import dcmread
from pandastable import Table

import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
import pandas as pd
import numpy as np


def main():

    # Extracts main information from DICOM header
    def ExtractInfo():
        df = pd.DataFrame(columns = ['name','value'])

        df = df.append({'name' : 'Filename', 'value' : path},ignore_index=True)
        df = df.append({'name' : 'Storage type', 'value' : ds.SOPClassUID},ignore_index=True)

        pat_name = ds.PatientName
        display_name = pat_name.family_name + ", " + pat_name.given_name
        df = df.append({'name': "Patient's name", 'value': display_name},ignore_index=True)
        df = df.append({'name': "Patient id", 'value': ds.PatientID},ignore_index=True)
        df = df.append({'name': "Patient's Birth Date ", 'value': ds.PatientBirthDate},ignore_index=True)
        df = df.append({'name': "Patient's sex", 'value': ds.PatientSex},ignore_index=True)
        df = df.append({'name': "Modality", 'value': ds.Modality},ignore_index=True)
        df = df.append({'name': "Study Date", 'value': ds.StudyDate},ignore_index=True)
        df = df.append({'name': "Manufacturer", 'value': ds.Manufacturer},ignore_index=True)
        df = df.append({'name': "Manufacturer's Model Name", 'value': ds.ManufacturerModelName},ignore_index=True)
        df = df.append({'name': "Study Date", 'value': ds.StudyDate},ignore_index=True)

        if 'PixelData' in ds:
            rows = int(ds.Rows)
            cols = int(ds.Columns)
            df = df.append({'name': "Image size", 'value': "{rows:d} x {cols:d}, {size:d} bytes".format(
                rows=rows, cols=cols, size=len(ds.PixelData))},ignore_index=True)

            if 'PixelSpacing' in ds:
                df = df.append({'name': "Pixel spacing", 'value': ds.PixelSpacing},ignore_index=True)

            if 'SliceThickness' in ds:
                df = df.append({'name': "Slice Thickness", 'value': ds.SliceThickness},ignore_index=True)
            if 'SpacingBetweenSlices' in ds:
                df = df.append({'name': "Spacing Between Slices", 'value': ds.SpacingBetweenSlices},ignore_index=True)

        return df

    # Displays at the GUI the DICOM header info extracted from ExtractInfo()
    def HeaderInfo():
        window = tk.Toplevel(root)
        window.title("Header Information")
        window.resizable(True, True)
        header_info = Table(window, dataframe=data)
        header_info.autoResizeColumns()
        header_info.show()

    def update_contrast(self):
        if bottom_limit.get() < upper_limit.get():
            new_vmin.set(bottom_limit.get())
            new_vmax.set(upper_limit.get())

    def cmapcolor(*args):
        colormap.set(variable.get())

    def update_slice(self):
        pos = slice_selector.get()

        ax3.imshow(img[pos, :, :], cmap=plt.cm.get_cmap(colormap.get()), aspect=pixel_len_mm[0]/pixel_len_mm[1], vmin = new_vmin.get(), vmax=new_vmax.get())
        if pos < img.shape[1]:
            ax1.imshow(img[:, :, pos], cmap=plt.cm.get_cmap(colormap.get()), aspect=pixel_len_mm[2]/pixel_len_mm[0], vmin = new_vmin.get(), vmax=new_vmax.get())
            ax2.imshow(img[:, pos, :], cmap=plt.cm.get_cmap(colormap.get()), aspect=pixel_len_mm[0]/pixel_len_mm[1], vmin = new_vmin.get(), vmax=new_vmax.get())
        else:
            ax1.imshow(img[:, :, img.shape[2]-1], cmap=plt.cm.get_cmap(colormap.get()), aspect=pixel_len_mm[2]/pixel_len_mm[0], vmin = new_vmin.get(), vmax=new_vmax.get())
            ax2.imshow(img[:, img.shape[1]-1, :], cmap=plt.cm.get_cmap(colormap.get()), aspect=pixel_len_mm[0]/pixel_len_mm[1], vmin = new_vmin.get(), vmax=new_vmax.get())
        fig.canvas.draw_idle()
        slice_pos = "Nº Slice: " + str(pos)
        label_slice.config(text=slice_pos)

    def onclick(event):
        if event.inaxes == ax1:
            if (event.x and event.y) is not None:
                sli = img[:,:,pos]
                print(sli)
                pixel_val = str(sli[int(event.ydata),int(event.xdata)])
                l2.config(text=pixel_val)
        elif event.inaxes == ax2:
            if (event.x and event.y) is not None:
                sli = img[:,pos,:]
                pixel_val = str(sli[int(event.ydata), int(event.xdata)])
                l2.config(text=pixel_val)
        elif event.inaxes == ax3:
            if (event.x and event.y) is not None:
                sli = img[pos, :, :]

                pixel_val = str(sli[int(event.ydata), int(event.xdata)])
                l2.config(text=pixel_val)


    #Read DICOM image path from keyboard imput
    path = input("Insert your DICOM image path: ")
    ds = dcmread(path)

    print(ds)
    data = ExtractInfo()
    pixel_len_mm = [float(ds.SliceThickness), float(ds.PixelSpacing[0]), float(ds.PixelSpacing[1])]
    print()

    img = np.flip(ds.pixel_array, axis=0)

    # Main Frame
    root = tk.Tk()
    root.title("DICOM Image Display")
    topFrame = tk.Frame()
    rightFrame = tk.Frame()

    topFrame.pack(side="top", fill="both", expand=True)
    rightFrame.pack(side="right", fill="x", expand=True)

    minValueRep = ds[0x00409096][0].RealWorldValueFirstValueMapped
    maxValueRep = ds[0x00409096][0].RealWorldValueLastValueMapped

    # Selecting slices
    pos = 0
    slice_selector = tk.Scale(topFrame, label="Slice selector", from_=0, to=ds.pixel_array.shape[0] - 1,
                              orient=tk.HORIZONTAL, length=400,
                              command=update_slice,tickinterval=20)
    slice_selector.pack(side=tk.LEFT,anchor=tk.NW)

    # Header Information Button
    button1 = tk.Button(rightFrame, height=3, width=10, text="Header", command=HeaderInfo)
    button1.pack(side="left", fill="both",anchor=tk.W)

    label_contrast = tk.Label(topFrame)
    label_contrast.pack(side=tk.TOP, anchor=tk.NE)
    contrast = "CONTRAST SELECTOR"
    label_contrast.config(text=contrast)

    # Contrast & colormap selector
    bottom_limit = tk.Scale(topFrame, label="Bottom limit", from_=minValueRep, to=maxValueRep,
                            orient=tk.HORIZONTAL, length=800,command=update_contrast,tickinterval=10000, resolution=1)
    bottom_limit.pack(anchor=tk.NE)
    bottom_limit.set(minValueRep)

    upper_limit = tk.Scale(topFrame, label="Upper limit", from_=minValueRep, to=maxValueRep,
                           orient=tk.HORIZONTAL, length=800,command=update_contrast,tickinterval=10000, resolution=1)
    upper_limit.pack(anchor=tk.NE, before=bottom_limit)
    upper_limit.set(maxValueRep)

    label_colormap = tk.Label(topFrame)
    label_colormap.pack(side=tk.TOP, anchor=tk.NE)
    l_cmap = "COLORMAP SELECTOR"
    label_colormap.config(text=l_cmap)

    cmap_OptionList = ["autumn", "bone", "cool", "copper", "flag", "gray", "hot", "jet", "pink", "prism",
                       "spring", "summer", "winter"]

    variable = tk.StringVar(topFrame)
    variable.set(cmap_OptionList[1])
    opt = tk.OptionMenu(topFrame, variable, *cmap_OptionList)
    opt.pack(anchor=tk.NE,side="top")
    variable.trace("w", cmapcolor)

    #Displaying images
    fig = Figure(figsize=(15,6), dpi=100)
    ax1 = fig.add_subplot(131)
    ax2 = fig.add_subplot(132)
    ax3 = fig.add_subplot(133)
    colormap = tk.StringVar()
    colormap.set("bone")
    new_vmin = tk.IntVar()
    new_vmax = tk.IntVar()
    new_vmin.set(minValueRep)
    new_vmax.set(maxValueRep)

    ax1.imshow(img[:,:,0], cmap=plt.cm.get_cmap(colormap.get()), vmin = new_vmin.get(), vmax=new_vmax.get())
    ax2.imshow(img[:,0,:], cmap=plt.cm.get_cmap(colormap.get()), vmin = new_vmin.get(), vmax=new_vmax.get())
    ax3.imshow(img[0,:,:], cmap=plt.cm.get_cmap(colormap.get()), vmin = new_vmin.get(), vmax=new_vmax.get())

    canvas = FigureCanvasTkAgg(fig, master=root)  # A tk.DrawingArea.
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, expand=1)

    toolbar = NavigationToolbar2Tk(canvas, root)
    toolbar.update()
    canvas.get_tk_widget().pack(side=tk.TOP, expand=1)

    #Showing pixel numeric values on click
    l1 = tk.Label(topFrame, text="Pixel Numeric Value")
    l2 = tk.Label(topFrame, text="", width=40)
    l1.pack()
    l2.pack()
    cid = fig.canvas.mpl_connect('button_press_event', onclick)

    label_slice = tk.Label(topFrame)
    label_slice.pack(side=tk.TOP,anchor=tk.NW,before=slice_selector)
    slice_pos = "Nº Slice: " + str(pos)
    label_slice.config(text=slice_pos)

    root.mainloop()


if __name__ == '__main__':
    main()

