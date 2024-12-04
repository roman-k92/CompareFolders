import os
import settings
import traceback

sTEMPLATEFILE = ''
sPATHCOMPARE = ''

def CandidateDelFiles(setToDelete):
    try:
        sPathOutCsv = r'C:\Users\Name\Desktop\to_del.csv'
        objCsv = open(sPathOutCsv, 'w', encoding = 'utf-8')

        for sPath in setToDelete:
            listPath = sPath.split(';')
            sPathToDel = 'D:\\' + listPath[0]
            sPathToDel = sPathToDel.replace('\"', '')

            objCsv.write(sPathToDel + '\n')

        objCsv.close()

    except:
        traceback.print_exc()


def CompareFiles():
    if not (sTEMPLATEFILE and sPATHCOMPARE):
        print('EMPTY VALUES')
        exit(0)

    setTemplateData = set()
    setCompareData = set()

    with open(sTEMPLATEFILE, 'r', encoding='utf8') as objTemplateCSV:
        for sLine in objTemplateCSV:
            setTemplateData.add(sLine)

    with open(sPATHCOMPARE, 'r', encoding='utf8') as objCompareCSV:
        for sLine in objCompareCSV:
            setCompareData.add(sLine)


    setDiff = setCompareData.difference(setTemplateData)
    CandidateDelFiles(setDiff)



def print_text():
    print(sTEMPLATEFILE)
    print(sPATHCOMPARE)
    #val = 0
    #sCsv = r'C:\Users\Name\Desktop\to_del.csv'
    #objFile = open(sCsv, encoding = 'utf-8')
    #for sRow in objFile:
     #   outRow = sRow.replace('\n', '')
      #  print(outRow)
       # os.remove(outRow)
       # val = val + 1
    #objFile.close()
    #print(val)


