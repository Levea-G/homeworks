import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import filedialog,messagebox
import matplotlib.pyplot as plt
#高明源20002530
data=pd.read_csv('data.csv')#read the whole data
class console():
    def __init__(self):
        def modify(x):#modifies the input data x, changes an index to a column name
            x=x.strip()
            if x in data.columns:return x
            else:
                try:return data.columns[int(x)]
                except:return 'nan'
        def checkup():#modifies the data before showing them
            cont=check.get()
            if cont=='*':indx=data.columns
            else:indx=list(map(modify,cont.split(',')))
            if 'nan' in indx:messagebox.showinfo('error','wrong index')
            else:datas(indx).main.transient()
        def draws():#draws the plots of selected datas
            indx=list(map(modify,draw.get().split(',')))
            if 'nan' in indx:messagebox.showinfo('error','wrong index')
            elif len(indx)==2:#draw scatter
                plt.scatter(data[indx[0]],data[indx[1]])
                plt.xlabel(indx[0])
                plt.ylabel(indx[1])
            elif len(indx)==1:#draw line chart
                plt.plot(data['date'],data[indx[0]])
                plt.xticks(['2010-02','2014-01','2018-01','2021-12'])
                plt.xlabel('date')
                plt.ylabel(indx[0])
            else:messagebox.showinfo('error','too many indexers')
            plt.show()
        def calc():#modifies the data before calculating
            cont=cal.get()
            if cont=='*':indx=data.columns[1:]
            else:indx=list(map(modify,cont.split(',')))
            if 'nan' in indx:messagebox.showinfo('error','wrong index')
            else:cals(indx).main.transient()
        self.main=tk.Tk()
        self.main.title('上证行业指数历史收益率')
        self.main.geometry('600x450+300+200')
        self.main.resizable(0,0)
        tk.Label(self.main,font=('times',12),text='请输入要查看的列名或列号,用逗号隔开',anchor='w').place(x=50,y=70,width=300,height=30)
        check=tk.Entry(self.main,font=('times',14))
        check.place(x=50,y=100,width=400,height=30)
        tk.Button(self.main,font=('times',14),text='查看',command=checkup).place(x=460,y=100,width=100,height=30)
        tk.Label(self.main,font=('times',12),text='请输入要绘制的图像的数据列',anchor='w').place(x=50,y=150,width=300,height=30)
        draw=tk.Entry(self.main,font=('times',14))
        draw.place(x=50,y=180,width=400,height=30)
        tk.Button(self.main,font=('times',14),text='绘制',command=draws).place(x=460,y=180,width=100,height=30)
        tk.Label(self.main,font=('times',12),text='请输入参与计算协方差矩阵的数据列',anchor='w').place(x=50,y=230,width=300,height=30)
        cal=tk.Entry(self.main,font=('times',14))
        cal.place(x=50,y=260,width=400,height=30)
        tk.Button(self.main,font=('times',14),text='计算',command=calc).place(x=460,y=260,width=100,height=30)
class datas():#a window showing the selected data
    def __init__(self,indx):
        self.main=tk.Toplevel()
        self.main.title('查看数据')
        self.main.geometry('600x480+350+250')
        self.main.resizable(0,0)
        show=tk.Listbox(self.main,font=('consolas',12))#displaying data in listbox
        show.place(x=0,y=0,width=600,height=480)
        indv=data[indx]
        show.insert('end',' '*5+''.join(map(lambda x:'%15s'%x,indx)))
        for i in range(143):
            col='%5s'%str(i)
            for item in indv.loc[i]:
                try:col+='%15lf'%item
                except:col+='%15s'%item#in case the 'date' column can't be converted to %lf
            show.insert('end',col+' '*10)
        scx=tk.Scrollbar(show,command=show.xview,orient='horizontal')#scrollbar setups
        scx.pack(side='bottom',fill='x')
        scy=tk.Scrollbar(show,command=show.yview)
        scy.pack(side='right',fill='y')
        show.config(xscrollcommand=scx.set,yscrollcommand=scy.set)
class cals():#a window showing the calculation outcomes
    def __init__(self,indx):
        def sav():
            xx=open(filedialog.asksaveasfilename(),'w+')#convenient interactive file-saving window
            xx.write(show.get('1.0','end'))
            xx.close()
        self.main=tk.Toplevel()
        self.main.title('协方差-方差矩阵')
        self.main.geometry('600x480+350+250')
        self.main.resizable(0,0)
        show=tk.Text(self.main,font=('consolas',12),wrap='none')
        show.place(x=0,y=0,relwidth=1,relheight=0.8)
        indv=np.cov(data[indx].T)#core calculation module
        try:len(indv)
        except:indv=np.array([[indv]])#in case there's only one column selected
        show.insert('end',' '*10+''.join(map(lambda x:'%15s'%x,indx))+'\n')
        for i in range(len(indx)):
            show.insert('end','%10s'%indx[i]+''.join(map(lambda x:'%15lf'%x,indv[i]))+' '*10+'\n')
        scx=tk.Scrollbar(show,command=show.xview,orient='horizontal')
        scx.pack(side='bottom',fill='x')
        scy=tk.Scrollbar(show,command=show.yview)
        scy.pack(side='right',fill='y')
        show.config(state='disabled',xscrollcommand=scx.set,yscrollcommand=scy.set)
        tk.Button(self.main,font=('times',16),text='保存到文件',command=sav).place(x=240,y=400,width=120,height=50)
console().main.mainloop()