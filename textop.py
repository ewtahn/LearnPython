class CopyAddmacro:
    def __init__(self,binarysw,tag01,unitNum=16,ReplaceDict = {'_U01':'_U', '单元01':'单元', '链路01':'链路'}):
        self.para=self.readFile('Cfg.txt')
        self.MacroFileLoc=self.readpara(self.para,'<MacroFileLoc')
        if(binarysw!=None):
            bWriteMacro=1
            self.binarysw=binarysw
        else:
            bWriteMacro=0




        self.tag01=tag01
        self.unitNum=unitNum
        self.ReplaceDict=ReplaceDict

        if(bWriteMacro==1):
            self.writeMacro()
    def readFile(self,fileName):
        file = open(fileName,'r')                  #打开文件
        if(file==-1):
            return
        content=file.read()                    #将文件读进内存
        file.close()                               #关闭文件
        return content

    def findend(self,string,endtag):               #找到strtag所在行的换行符位置
        pos=0
        move=string.find(endtag)                   #找到待复制的尾
        pos+=move 
        move=string[pos:].find('\n')               #找行结尾  
        pos+=move
        return pos

    def replacedict(self,string,tempNo):           #根据字典替换
        stringnew=string         
        for template,value in self.ReplaceDict.items():
            stringnew=stringnew.replace(template,value+tempNo)    #替换内容
        return stringnew

    def findBound(self,content,template,bound,endtag='',chnlist=[0]*100):
        posmax=0
        posmin=len(content)

        for i in range(1, 99+1):
            tempNo=str(i)
            tempNo=tempNo.zfill(2)
            tag=self.replacedict(template,tempNo)
            #print(template)
            pos=content.find(tag)
            if(pos!=-1):
                chnlist[i]=1
                if(pos>posmax):
                    posmax=pos
                if(pos<posmin):
                    posmin=pos

        head=content[:posmin].rfind('\n')        
        head+=1
        move=content[posmax:].find(endtag)      
        move=self.findend(content[posmax:],endtag)
        end=posmax+move+1
        bound['end']=end
        bound['head']=head  
        if (posmax<posmin): 
            return -1


    def readpara(self,content,para):
        content=content.replace(' ', '')
        head=content.find(para)
        move=content[head:].find("=")
        head+=move
        head+=1
        end=content[head:].find("\n")
        end=head+end
        return content[head:end]

    def biuldUnitMacro(self,content):                     #根据binarysw填宏定义
        bound = {'head':0,'end':0}
        chnlist=[0]*100
        self.findBound(content,self.tag01,bound,'',chnlist)
        template=self.readpara(self.para,'<MacroUnitEnaTemp')
        state=self.findBound(content,template,bound,'',chnlist)
        print('单元开关情况,注意与组件开关对比是否匹配，因为单元开关只增不减:')
        print(chnlist[1:self.unitNum+1])
        if (state==-1):                                   #当模版项不存在时(只对宏定义开关有用)
            taghead=self.readpara(self.para,'<MacroSW_UnitEna')
            #tagtail=self.readpara(self.para,'<MacroSW_tagtail')    
            head=content.find(taghead)               #找到待复制的头
            if(head==-1):
                print('写入位置标签(<MacroSW)或模版项不存在，请添加.file unchanged')
                return
            move=content[head:].find('\n')           # 
            head+=move+1
            end=head
            print(template+'类宏定义开关不存在，重新生成')
            bound['end']=end
            bound['head']=head  

        addstring=''
        for i in range(1, self.unitNum+1):
            tempNo=str(i)
            tempNo=tempNo.zfill(2)
            temp='#define '+template 
            temp=self.replacedict(temp,tempNo)
            if(chnlist[i]):
                addstring+=temp+'\n'

        #print('生成MacroUnitEna，注意是根据binarysw生成，但只增不减')
        newstring=content[:bound['head']]+addstring+content[bound['end']:]     #

        file = open(self.MacroFileLoc,'w')
        file.write(newstring)
        file.close()

    def biuldMacroSW(self,content):                     #根据binarysw填宏定义
        bound = {'head':0,'end':0}
        state=self.findBound(content,self.tag01,bound)

        if (state==-1):                         #当模版项不存在时(只对宏定义开关有用)
            taghead=self.readpara(self.para,'<MacroSW_taghead')
            #tagtail=self.readpara(self.para,'<MacroSW_tagtail')    
            head=content.find(taghead)               #找到待复制的头
            if(head==-1):
                print('写入位置标签(<MacroSW)或模版项不存在，请添加.file unchanged')
                return
            move=content[head:].find('\n')           # 
            head+=move+1
            end=head
            print(self.tag01+'类宏定义开关不存在，重新生成')
            bound['end']=end
            bound['head']=head  

        addstring=''
        for i in range(1, self.unitNum+1):
            tempNo=str(i)
            tempNo=tempNo.zfill(2)
            temp='#define '+self.tag01 
            temp=self.replacedict(temp,tempNo)
            if(self.binarysw&(1<<(i-1))):
                addstring+=temp+'\n'
        print(self.tag01+'类组件宏开关:\n'+addstring)
        newstring=content[:bound['head']]+addstring+content[bound['end']:]     #

        file = open(self.MacroFileLoc,'w')
        file.write(newstring)
        file.close()

    def copyaddFullDef(self,contentorg,fileName,lastpos):
        content=contentorg[lastpos['end']:]                 #这次只处理上次没处理到的部分

        bodyhead=content.find(self.tag01)                   #找到待复制的头
        bodyhead=content[:bodyhead].rfind('#ifdef')         #找到待复制的头ifdef位置
        bodyend=self.findend(content[bodyhead:],'#endif')   #找到待复制的尾endif\n的下一个位置
        tag01body=content[bodyhead:bodyhead+bodyend+1]      #

        bound = {'head':0,'end':0}
        state=self.findBound(content,self.tag01,bound,'#endif')
        if(state==-1):
            return
        addstring=''
        for i in range(1, self.unitNum+1):
            tempNo=str(i)
            tempNo=tempNo.zfill(2)
            insrtbody=self.replacedict(tag01body,tempNo)    #替换文本
            addstring+=insrtbody                            #新的插入内容

        newstring=contentorg[:lastpos['end']]+content[:bound['head']]+addstring+content[bound['end']:]     #
        lastpos['end']=len(contentorg[:lastpos['end']]+content[:bound['head']]+addstring)
        #print(content[bound['end']:])
        file = open(fileName,'w')
        file.write(newstring)
        file.close()    

    def writeMacro(self):
        content=self.readFile(self.MacroFileLoc)
        self.biuldMacroSW(content)
        content=self.readFile(self.MacroFileLoc)
        self.biuldUnitMacro(content)

    def writeFile(self,fileName):
        lastpos={'end':0}
        ProDir=self.readpara(self.para,'<ProDir')
        fileName=ProDir+fileName
        content=self.readFile(fileName)
        multiTimes=content.count(self.tag01)
        for i in range(1,multiTimes+1):         #一个文件中有多处需要替换
            content=self.readFile(fileName)
            self.copyaddFullDef(content,fileName,lastpos)
        #content=self.readFile(fileName+'.h')
        #self.copyaddFullDef(content,fileName+'.h')
