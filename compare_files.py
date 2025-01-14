import os
import settings
import traceback

sDelimeter = settings.sDelimeter
sDISK = ''
sTEMPLATEFILE = ''
sPATHCOMPARE = ''

def copy_files(setCandidateToCopy):
    try:
        sOutFilePath = os.path.join(os.getcwd(), 'to_copy.txt')
        objOutTxt = open(sOutFilePath, "w", encoding = 'utf-8')
        for sPath in sorted(setCandidateToCopy):
            listPath = sPath.split(';')
            sPathToCopy = os.path.join(sDISK + ':\\', listPath[0])
            sPathToCopy = sPathToCopy.replace('\"', '')\

            objOutTxt.write(sPathToCopy + '\n')

        objOutTxt.close()
    except:
        objOutTxt.close()
        traceback.print_exc()


def create_line_log(sLine):

    listInfo = sLine.split(';')

    sOutLine = listInfo[0] + sDelimeter + listInfo[1] + sDelimeter + listInfo[3] # Name, size and hash

    return sOutLine

def start_compare():

    if not (sTEMPLATEFILE and sPATHCOMPARE and sDISK):
        print('EMPTY VALUES')
        exit(0)

    setTemplateData = set()
    setCompareData = set()

    with open(sTEMPLATEFILE, 'r', encoding='utf8') as objTemplateCSV:
        for sLine in objTemplateCSV:

            sOutLine = create_line_log(sLine)
            setTemplateData.add(sOutLine)

    with open(sPATHCOMPARE, 'r', encoding='utf8') as objCompareCSV:
        for sLine in objCompareCSV:

            sOutLine = create_line_log(sLine)
            setCompareData.add(sOutLine)


    setDiff = setTemplateData.difference(setCompareData)

    copy_files(setDiff)

