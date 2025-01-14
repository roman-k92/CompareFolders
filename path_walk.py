import os
import sys
import time
import hashlib
import multiprocessing
import threading
from datetime import datetime
import settings
import compare_files


listExcludeFolders = settings.listExcludeFolders
sDelimeter = settings.sDelimeter

dictFiles = {}

nCounter = None

pool = None
objOutCSV = None


################################################################################
def counter_info():

    objNow = datetime.now()
    sCurrentTime = objNow.strftime("%H:%M:%S")

    global nCounter

    if settings.bCalculateHash:
        with nCounter.get_lock():
            nCounter.value += 1

            if nCounter.value % settings.nLine == 0:
                print(str(nCounter.value) + '\t' + sCurrentTime, flush=True)

    else:
        nCounter = nCounter + 1

        # Additional info
        if nCounter % settings.nLine == 0:
            print(str(nCounter) + '\t' + sCurrentTime, flush=True)

################################################################################
def init(nCnt):
    global nCounter
    nCounter = nCnt

################################################################################
def alive():

    while True:
        objNow = datetime.now()
        sCurrentTime = objNow.strftime("%H:%M:%S")
        print('I\'m alive', sCurrentTime, flush = True)

        time.sleep(settings.nTimeAlive)

################################################################################
def create_string_for_file(tplFileInfo):

    sStrToWrite = ''

    for sParam in tplFileInfo:

        if sParam:

            sStrToWrite = sStrToWrite + '"' + str(sParam) + '"' + sDelimeter


    sStrToWrite = sStrToWrite + '\n'

    return sStrToWrite

################################################################################
def compute_md5_async(sRootDir, listFiles):

    write_log('Start '  +  sRootDir + '; pid = ' + str(os.getpid()) + '\n')

    listRes = []

    for sFileName in listFiles:
        sFullPath = os.path.join(sRootDir, sFileName)

        # Check path is file, not directory
        bIsFile = os.path.isfile(sFullPath)
        if bIsFile:

            tplFileInfo = get_additional_info(sFullPath)

            sMd5 = compute_md5(sFullPath)

            tplFileInfo = tplFileInfo + (sMd5,)

            listRes.append(tplFileInfo)

    write_log('Finish '  +  sRootDir + '; pid = ' + str(os.getpid()) + '\n')

    return listRes

################################################################################
def write_log(sLine):
    with open('log.txt', 'a') as outfile:
        outfile.write(sLine)

################################################################################
def compute_md5(sFullPath):
    try:
        hash_md5 = hashlib.md5()
        with open(sFullPath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)

        sMd5 = hash_md5.hexdigest().upper()

        counter_info()

    except:
        sMd5 = '<No data>'
        print('Md5 exception for ' + sFullPath)

    return sMd5

################################################################################
def write_file_info(listRes):

    for tplFileInfo in listRes:

        sStrToWrite = create_string_for_file(tplFileInfo)

        # Write line
        objOutCSV.write(sStrToWrite)

################################################################################
# error callback function
def handler(error):
    print(f'Error handler: {error}', flush = True)


################################################################################
def get_additional_info(sFullPath):

    # Get path without disk letter
    sRelFilePath = sFullPath[3:] # os.path.relpath(sFullPath, name)

    # Get file size
    nFileSize = os.path.getsize(sFullPath)


    # File changed
    fFileTime = os.path.getmtime(sFullPath)
    sEditTime = datetime.fromtimestamp(fFileTime).strftime("%d.%m.%Y %H:%M:%S")

    return (sRelFilePath, nFileSize, sEditTime)

################################################################################
def collect_files_info(sRootPath):
    try:
        objFileSystemInfo = os.walk(sRootPath)

        # Read every file
        for path, subdirs, files in objFileSystemInfo:

            # Do skip
            for skipDir in subdirs[:]: # Get copy of list https://stackoverflow.com/questions/14267722/python-list-remove-skips-next-element-in-list
                if skipDir in listExcludeFolders:
                    subdirs.remove(skipDir)


            if settings.bCalculateHash:
                pool.apply_async(compute_md5_async, (path, files,), callback = write_file_info, error_callback = handler)

            else:
                # Get info about every file
                for name in files:

                    # Get full path
                    sFullPath = os.path.join(path, name)

                    # Check path is file, not directory
                    bIsFile = os.path.isfile(sFullPath)

                    sMd5 = ''

                    if bIsFile:

                        tplFileInfo = get_additional_info(sFullPath)

                        sMd5 = compute_md5(sFullPath)

                        if not sMd5:
                            counter_info()

                        tplFileInfo = tplFileInfo + (sMd5,)

                        sStrToWrite = create_string_for_file(tplFileInfo)
                        objOutCSV.write(sStrToWrite)

            #break

    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=} in collect_files_info")

################################################################################
def print_results(objStart, nCnt):

    objNow = datetime.now()

    sCurrentTime = objNow.strftime("%H:%M:%S")

    print('### FINISH at', sCurrentTime, '###', str((objNow - objStart).total_seconds() ) + '; Amount = ' + str(nCnt))


################################################################################
if __name__ == '__main__':

    try:

        nTotalCnt = 0

        process = multiprocessing.Process(target = alive)
        process.start()

        listCsv = []

        objNow = datetime.now()
        sCurrentTime = objNow.strftime("%H:%M:%S")


        listDrives = settings.listDiskToWalk

        sOutFilePath = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop') # Windows only


        objDate = objNow.date()
        sCurrentDate = objDate.strftime("%Y_%m_%d")

        for sDrive in listDrives:

            sRootPath = sDrive + ':\\'

            isExist = os.path.exists(sRootPath)

            if isExist:

                startDrive = datetime.now()
                sCurrentTime = startDrive.strftime("%H:%M:%S")

                print('================ Scan ', sRootPath, ' ================')

                sFilePrefix = sDrive + '_'

                sOutFileName = '_' + sFilePrefix.lower() + 'disk_' + sCurrentDate + '.csv'
                sOutFile = os.path.join(sOutFilePath, sOutFileName)

                objOutCSV = open(sOutFile, "w", encoding = 'utf-8')


                if settings.bCalculateHash:

                    nCounter = multiprocessing.Value('i', 0)

                    print(str(nCounter.value) + '\t' + sCurrentTime)

                    # количество ядер у процессора
                    n_proc = multiprocessing.cpu_count()

                    pool = multiprocessing.Pool(processes=n_proc, initializer = init, initargs = (nCounter,))

                    if pool:
                        pool.close()
                        pool.join()

                else:
                    nCounter = 0

                    print(str(nCounter) + '\t' + sCurrentTime)


                collect_files_info(sRootPath)
                dictFiles[sDrive] = sOutFile
                listCsv.append(objOutCSV)


                if settings.bCalculateHash:
                    print_results(startDrive, nCounter.value)

                    nTotalCnt = nTotalCnt + nCounter.value

                else:
                    print_results(startDrive, nCounter)

                    nTotalCnt = nTotalCnt + nCounter

        for objFile in listCsv:
            objFile.close()

        process.terminate() # alive logger

        print('\n##### List of files ####')
        for sKey in dictFiles:
            print(sKey + ':', dictFiles[sKey])

        print('')

        while(True):

            sDisk = (input("Choose one letter to set a template file: ")).upper()
            if sDisk in dictFiles:

                compare_files.sTEMPLATEFILE = dictFiles[sDisk]
                compare_files.sDISK = sDisk
                print('\nYou choose', compare_files.sTEMPLATEFILE)

                del dictFiles[sDisk]
                break


        for sKey in dictFiles:
            compare_files.sPATHCOMPARE = dictFiles[sKey]
            compare_files.start_compare()

        print_results(objNow, nTotalCnt)


        time.sleep(3)

    except:

        process.terminate()

        print_results(objNow, nTotalCnt)


        time.sleep(1)
