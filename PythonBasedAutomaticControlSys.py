#============================================================#
#   Tipsuda Chaipiboonwong tchaipib@tu.ac.th
#   Department of Physics, Thammasat University
#   Klong Luang, Pathum Thani 12120
#   Thailand
#============================================================#
# Designed for the measurment of QTF's frequency response
# Wavform Generator: Rigol DG4062
# Oscilloscope: Rigol DG2010
#============================================================#
#                       Import Package                       #
#============================================================#
from tkinter import *
import time
import numpy as np
import pandas as pd
import csv
import matplotlib.pyplot as plt
import pyvisa as visa
from time import sleep
import matplotlib 
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from tkinter.ttk import *
#============================================================#
class Application(Frame):
    def __init__(self, master):
        self.master = master   
#==============================================#
#                MAIN WINDOW                   #
#===============================================#
#---------------USB CONNECTION -----------------#         
        rm=visa.ResourceManager()  
        while len(rm.list_resources())!= 2:
            error_usb(self)
        fgenaddress = rm.list_resources()[0]
        oscaddress = rm.list_resources()[1]
        global fgen,osc
        fgen=rm.open_resource(fgenaddress)
        osc=rm.open_resource(oscaddress)
        #---------------- Labels -------------------#
        self.label1 = tk.Label(master, text="Function Generator:", bg='bisque3').grid(column=1, row=1)
        self.label2 = tk.Label(master, text="Oscilloscope:", bg='bisque3').grid(column=1, row=2)
        self.label3 = tk.Label(master, text="No. of Data points:", bg='bisque3').grid(column=1, row=3)
        self.label4 = tk.Label(master, text="No.of Measurements:", bg='bisque3').grid(column=1, row=4)
        self.label5 = tk.Label(master, text="Intitial Frequency:", bg='bisque3').grid(column=1, row=5)
        self.label6 = tk.Label(master, text="Final Frequency:", bg='bisque3').grid(column=1, row=6)
        self.label7 = tk.Label(master, text="Input Voltage:", bg='bisque3').grid(column=1, row=7)
        self.label8 = tk.Label(master, text="Output File:", bg='bisque3').grid(column=1, row=8)
        self.label9 = tk.Label(master, text="Time delay:", bg='bisque3').grid(column=1, row=9)    
        #---------------- Entries -------------------#
        self.box3 = Entry(master, width=20)  ### No.of Data points ###
        self.box3.grid(column=2, row=3)
        self.box3.insert(0, "256")
        self.box4 = Entry(master, width=20)  ### No.of Measurements ###
        self.box4.grid(column=2, row=4)
        self.box4.insert(0, "1")
        self.box5 = Entry(master, width=20)   ### Intitial Frequency ###
        self.box5.grid(column=2, row=5)
        self.box5.insert(0, "32700")
        self.box6 = Entry(master, width=20)   ### Final Frequency ### 
        self.box6.grid(column=2, row=6)
        self.box6.insert(0, "32800")
        self.box7 = Entry(master, width=20)   ### Input Voltage ###
        self.box7.grid(column=2, row=7)
        self.box7.insert(0, "1")
        self.box8= Entry(master, width=20)    ### Output File Name) ###
        self.box8.grid(column=2, row=8)
        self.box8.insert(0, time.strftime("%y%m%d")+'data')
        self.box9 = Entry(master, width=20) ### Entry of Time delay ###
        self.box9.grid(column=2, row=9)
        self.box9.insert(0, "0.5")
        #---------------- Buttons -------------------#
        self.button1 = tk.Button(master, text="Browse", command=self.select_file, bg='orange3')
        self.button1.grid(column=3, row=8)        
        self.button2 = tk.Button(master, text="RUN", width = 12, command=self.run_data, bg='sienna2')
        self.button2.grid(column=2, row=11)
        self.button3 = tk.Button(master, text="Freq Res Graph", width = 13, command=self.plot_curve, bg='peach puff')
        self.button3.grid(column=3, row=11)
        self.button4 =tk. Button(master, text="Q-fac Cal",width = 13, command=self.calculate_Qfactor, bg='misty rose')
        self.button4.grid(column=3, row=12)
        self.button5 = tk.Button(master, text=" QUIT ",width = 12, command=self.quitwindows, bg='tomato3')
        self.button5.grid(column=2, row=12)
        #----------------Radio Buttons -------------------#
        global fgen_chnum
        fgen_chnum = IntVar()
        fgen_chnum.set(1)
        radio1 = tk.Radiobutton(master, text='Channel 1', variable=fgen_chnum, value=1, bg='bisque3').grid(column=2, row=1)
        radio2 = tk.Radiobutton(master, text='Channel 2', variable=fgen_chnum, value=2, bg='bisque3').grid(column=3, row=1)
        
        global osc_chnum
        osc_chnum = IntVar()
        osc_chnum.set(1)  # default channel
        radio3=tk.Radiobutton(master, text='Channel 1', variable=osc_chnum,value=1, bg='bisque3').grid(column=2, row=2)
        radio4=tk.Radiobutton(master, text='Channel 2', variable=osc_chnum,value=2, bg='bisque3').grid(column=3, row=2)
       
        global v_unit
        v_unit = IntVar()
        v_unit.set(1)  # default unit 
        radio5=tk.Radiobutton(master, text='Vpp', variable=v_unit,value=1, bg='bisque3').grid(column=3, row=7)
        radio6=tk.Radiobutton(master, text='Vrms', variable=v_unit,value=2, bg='bisque3').grid(column=4, row=7)

##################################################    
#    Subfuntion for Creating Error Msg Box       #
##################################################         
    global error_usb
    def error_usb(self):
        root = Tk()
        root.withdraw()
        messagebox.showerror("Error", "Check your USB connection with instruments!!!")
#---------------------------------------------------------------------------------------------------#       
    global error_vol
    def error_vol(self):
        root = Tk()
        root.withdraw()
        messagebox.showerror("Error", "Input voltage must be less than 5 V.")
#---------------------------------------------------------------------------------------------------#  
    global error_dcal 
    def error_dcal(self):
        root = Tk()
        root.withdraw()
        messagebox.showerror("Error", "No data to calculte Q-factor.")
#---------------------------------------------------------------------------------------------------# 
    global error_cal 
    def error_cal(self):
        root = Tk()
        root.withdraw()
        messagebox.showerror("Error", "Can not calculate Q-factor!")
#---------------------------------------------------------------------------------------------------# 
    global error_plot
    def error_plot(self):
        root = Tk()
        root.withdraw()
        messagebox.showerror("Error", "No data to plot a graph")
#---------------------------------------------------------------------------------------------------# 
#---------------------------------------------#
#              Graph Button               #
#---------------------------------------------#       
    global fig    
    def plot_curve(self):
        if 'fgenfreq'and 'Vo' not in globals():
            error_plot(self)
        else:
            fig=plt.figure(figsize=(7,5))
            a = fig.add_subplot(111)
            a.plot(fgenfreq,Vo)
            a.set_xlabel('Frequency (Hz)')
            a.set_ylabel(v_unit_graphtxt+' (V)')
#---------------------------------------------#
#              Q-fac Cal Button               #
#---------------------------------------------#  
    global FWHM,f0, Qfactor
    def calculate_Qfactor(self):
       if 'fgenfreq'and 'Vop' not in globals(): # in case users don't run the measurement previously
           error_dcal(self)
       else:
           Vmax=max(Vop) 
           Vmin=min(Vop)
           Vhalfmax=(Vmax-Vmin)/2
           ######################
           if Vhalfmax==0: # for the test constant data, no calculation of FWHM
              error_cal(self)
           else:
               f0=np.mean(fgenfreq[(Vop==Vmax)]) 
               highVhalfmax=np.where(Vop>Vhalfmax)
               indL=highVhalfmax[0][0]
               V1L=Vop[indL]-Vmin
               V2L=Vop[indL-1]-Vmin
               f1L=fgenfreq[indL]
               f2L=fgenfreq[indL-1]
               slopeL=(V1L-V2L)/(f1L-f2L)
               yintL=V1L-(slopeL*f1L)
               fL=(Vhalfmax-yintL)/slopeL
               
               indR=highVhalfmax[0][-1]
               V1R=Vop[indR]-Vmin
               V2R=Vop[indR+1]-Vmin
               f1R=fgenfreq[indR]
               f2R=fgenfreq[indR+1]
               slopeR=(V1R-V2R)/(f1R-f2R)
               yintR=V1R-(slopeR*f1R)
               fR=(Vhalfmax-yintR)/slopeR
               FWHM=fR-fL
               Qfactor=f0/FWHM
               root = Tk()
               root.title('Calculating Q-factor')
               root.geometry('250x150')
               Label(root, text="FWHM:").grid(row=1)
               Label(root, text="f0:").grid(row=2)
               Label(root, text="Q-factor:").grid(row=3)
               s1=Entry(root)
               s2=Entry(root)
               s3=Entry(root)
               s1.grid(row=1, column=1)
               s2.grid(row=2, column=1)
               s3.grid(row=3, column=1)
               s1.insert(0,FWHM)
               s2.insert(0,f0)
               s3.insert(0,Qfactor)
##-------------Append more info to the log file ---------------------------#                
               logfile= open(fname1+'.txt',"a")          
               logfile.write('FWHM (Hz): '+str(FWHM)+'\n')
               logfile.write('f0 (Hz): '+str(f0)+'\n')
               logfile.write('Q-factor: '+str(Qfactor))
               logfile.close()   
#---------------------------------------------#
#               Browse Button                 #
#---------------------------------------------#
    def select_file(self):
        master.filename =  filedialog.asksaveasfilename(initialdir = "/",title = "Select file",filetypes = (("CSV(comma delimited)","*.csv"),("all files","*.*")))
        print (master.filename)
#---------------------------------------------#
#               Quit Button                   #
#---------------------------------------------#
    def quitwindows(self):
        master.destroy()
        fgen.clear()
        osc.clear()
        plt.close('all')
        
#---------------------------------------------#
#               Run Button                   #
#---------------------------------------------#
    global num,v_unit_graphtxt,unit
    def run_data(self):
    #=====  Enable Func Gen's Output Channel 
        if fgen_chnum.get() == 1:
            f_chnum='1'
            fgen.write(':OUTPut1 ON')
        else:
            f_chnum='2'
            fgen.write(':OUTPut2 ON')
    #=====  Enable OSC' Input Channel 
        if osc_chnum.get() == 1:
            osc.write(':CHANnel1:DISPlay ON')
            o_chnum='1'
        else:
            osc.write(':CHANnel2:DISPlay ON')
            o_chnum='2'
#---------------------------------------------#
#    Get parameters from the control panel    #
#---------------------------------------------#                       
        num=int(self.box3.get())
        numread=int(self.box4.get())
        fi=float(self.box5.get())
        ff=float(self.box6.get())
        Vin=self.box7.get()
        if float(self.box7.get()) > 5:
            error_vol(self)
        elif v_unit.get() == 1:
            unit='VPP'
            v_unit_graphtxt='V$_{pp}$'
        else:
            v_unit.get() == 2
            unit='VRMS'
            v_unit_graphtxt='V$_{rms}$'
        fname1=self.box8.get()
        delay=float(self.box9.get())
#==========================================================#
#           Data Arrays and Frequency Sweep Loop           #
#==========================================================#
        global fgenfreq,Vop,fop
        step=((ff-fi))/((num-1))
        fgenfreq = np.zeros(num, dtype=float)
        Vop = np.zeros(num, dtype=float)
        fop = np.zeros(num, dtype=float)
        fread=np.zeros(numread, dtype=float)
        vread=np.zeros(numread, dtype=float)
        fgen.write(':SOURce'+f_chnum+':VOLTage:UNIT '+unit)
        fgen.write(':SOURce'+f_chnum+':VOLTage '+Vin)
        osc.write(':AUToscale')
        for j in range(0,num,1):
            fgenfreq[j] = fi+(step*j)
            fgen.write(':SOURce'+f_chnum+':FREQuency '+str(fgenfreq[j]))
            sleep(delay)
            for k in range(0,numread,1):
                fread[k]=osc.query(':MEASure:FREQuency? CHANnel'+o_chnum)
                while (fread[k]==9.9E+37):
                   osc.write(':AUToscale')
                   fread[k]=osc.query(':MEASure:FREQuency? CHANnel'+o_chnum)
                vread[k]=osc.query(':MEASure:'+unit+'? CHANnel'+o_chnum)
                while (vread[k]==9.9E+37):
                   osc.write(':AUToscale')
                   vread[k]=osc.query(':MEASure:'+unit+'? CHANnel'+o_chnum)                   
            fop[j] = np.mean(fread)
            Vop[j] = np.mean(vread)
#--------------------Export  Data file and Log File---------------------------#            
        data = np.transpose([fgenfreq,Vop,fop])
        df=pd.DataFrame(data,columns= ['Frequency','Vop','fop'])
        df.to_csv(fname1+'.csv',sep=',')
 
        logfile= open(fname1+'.txt',"w")
        logfile.write('Date: '+time.strftime("%d/%m/%y, %H:%M:%S")+'\n')
        logfile.write('Number of Data: '+str(num)+'\n')
        logfile.write('Number of Repeated Reading: '+str(numread)+'\n')
        logfile.write('Initial Frequency (Hz): '+str(fi)+'\n')
        logfile.write('Final Frequency (Hz): '+str(ff)+'\n')
        logfile.write('Input Voltage '+'('+unit+')'+': '+str(Vin)+'\n')
        logfile.write('Time delay (s): '+str(delay)+'\n')
        logfile.close()
################################################################
#                           Main Window                        #
#################################################################
if __name__=="__main__":    
    master = Tk()
    master.title("QTF Freq Response Measurent")
    master.geometry("450x350")
    master.configure(background='bisque3')
    app = Application(master)
    app.plot_curve
    master.mainloop()

                
 
 
        
        
 