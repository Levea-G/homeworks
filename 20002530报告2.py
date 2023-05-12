import requests as req
import re
import numpy as np
import pandas as pd
import pymssql as sql
import tkinter as tk
from tkinter import messagebox
import sklearn.linear_model as skl
#高明源20002530
class predict():
    def __init__(self):
        def getdt():#crawler part
            self.code=scode.get().strip()
            url='https://stock.quote.stockstar.com/stockinfo_finance/summary.aspx?code=%s&dt='%self.code
            html=req.get(
                url=url,
                headers={
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'
                }
            )
            self.data=pd.DataFrame([],columns=['eps','nvps','upps','crps','ocps','roe','npm','cr','at'],dtype=float)#store as dataframe
            dates=re.findall(re.compile('<option value="(.*?)">'),html.text)[:0:-1]#get all valid dates
            for date,i in zip(dates,range(len(dates))):
                html=req.get(
                    url=url+date,
                    headers={
                        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'
                    }
                )
                temp=re.findall(re.compile('thead_1.*?<td>(.*?)<'),html.text)#get the statistics
                temp=np.array(list(map(lambda x:float(x) if x!='-' else np.nan,temp[0:7]+temp[9:10]+[temp[12]])))#modify the data
                temp[5:]/=100
                self.data.loc[i]=temp
            self.data=pd.concat((pd.DataFrame(dates,columns=['date']),self.data),axis=1).dropna().reset_index(drop=True)
            if len(self.data)<36:messagebox.showinfo('error','too less samples to analyse(<36)')#in case the sample is too small
            else:showdt(self.data).main.transient()
        def dbsav():#store the data into database
            if len(self.data)<36:
                messagebox.showinfo('error','too less samples to analyse(<36)')
                return
            try:conn=sql.connect('127.0.0.1',database='info')#can only connect on my PC, sorry for that
            except:
                messagebox.showerror('','connection to database failed')
                return
            cur=conn.cursor()
            try:cur.execute('drop table sh%s'%self.code)#if exists a table with the same name, drop it
            except:pass
            try:cur.execute('create table sh%s(date char(10),eps float,nvps float,upps float,crps float,ocps float,roe float,npm float,cr float,at float)'%self.code)
            except:
                messagebox.showerror('','interrupted while creating table')
                conn.close()
                return
            for i in range(len(self.data)):
                try:cur.execute('insert into sh%s(date,eps,nvps,upps,crps,ocps,roe,npm,cr,at) values(\'%s\',%lf,%lf,%lf,%lf,%lf,%lf,%lf,%lf,%lf)'%(tuple([self.code])+tuple(self.data.loc[i])))
                except:
                    messagebox.showerror('','insert error')
                    conn.close()
                    return
            conn.commit()
            conn.close()
            self.data=pd.DataFrame()#clear the data
        def cal():
            self.code=pcode.get()
            try:conn=sql.connect('127.0.0.1',database='info')
            except:
                messagebox.showerror('','connection to database failed')
                return
            cur=conn.cursor()
            try:cur.execute('select * from sh%s'%self.code)#get data from database
            except:
                messagebox.showinfo('error','data not exist')
                conn.close()
                return
            data=pd.DataFrame(cur.fetchall(),columns=['date','eps','nvps','upps','crps','ocps','roe','npm','cr','at'])
            data['eps']=data['eps'].shift(1)
            data=data.dropna()
            reg=skl.LassoCV(random_state=0,cv=10,fit_intercept=True,precompute='auto',max_iter=1e9,tol=1e-6)#setup lasso model
            reg.fit(data.iloc[:,2:].values,data['eps'].values)#feed the model with history data sequence
            messagebox.showinfo('预测结果','未来一季度eps可能是%lf'%np.sum(reg.coef_*data[['nvps','upps','crps','ocps','roe','npm','cr','at']].iloc[len(data)-1].values+reg.intercept_))#make use of the model
            conn.close()
        self.main=tk.Tk()
        self.main.title('股票收益率预测')
        self.main.geometry('350x220+300+200')
        self.main.resizable(0,0)
        self.data=pd.DataFrame()#use a in-class global variable to record the current crawed data
        self.code=''#used for recording the last chose stock code
        tk.Label(self.main,font=('times',14),text='请输入要分析的上证股票代码',anchor='w').place(x=50,y=30,width=300,height=30)
        scode=tk.Entry(self.main,font=('times',12))
        scode.place(x=50,y=60,width=100,height=30)
        tk.Button(self.main,font=('times',12),text='获取数据',command=getdt).place(x=160,y=60,width=70,height=30)
        tk.Button(self.main,font=('times',12),text='将上次结果存入数据库',command=dbsav).place(x=50,y=100,width=200,height=30)
        pcode=tk.Entry(self.main,font=('times',12))
        pcode.place(x=50,y=140,width=100,height=30)
        tk.Button(self.main,font=('times',12),text='预测',command=cal).place(x=160,y=140,width=70,height=30)
class showdt():#showing the crawed data in listbox
    def __init__(self,data):
        self.main=tk.Toplevel()
        self.main.title('data')
        self.main.geometry('640x480+350+250')
        self.main.resizable(0,0)
        show=tk.Listbox(self.main,font=('consolas',12))
        show.place(x=0,y=0,relwidth=1,relheight=1)
        show.insert('end',' '*5+'%15s'%'date'+''.join(map(lambda x:'%15s'%x,data.columns[1:]))+' '*5)#the column names
        for i in range(len(data)):
            show.insert('end','%5d'%i+'%15s'%data.iloc[i,0]+''.join(map(lambda x:'%15lf'%x,data.iloc[i,1:])))#each line of data
        scx=tk.Scrollbar(show,command=show.xview,orient='horizontal')
        scx.pack(side='bottom',fill='x')
        scy=tk.Scrollbar(show,command=show.yview)
        scy.pack(side='right',fill='y')
        show.config(yscrollcommand=scy.set,xscrollcommand=scx.set,state='disabled')
predict().main.mainloop()