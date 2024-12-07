import os
import hashlib
import time
from datetime import datetime
import settings
import compare_files


listExcludeFolders = settings.listExcludeFolders
sDelimeter = settings.sDelimeter

dictFiles = {}

def compute_md5(file_name):
    hash_md5 = hashlib.md5()
    with open(file_name, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def collect_files_info(sRootPath, sOutFilePath):
    try:

        objOutCSV = open(sOutFilePath, "w", encoding = 'utf-8')

        # Varibale to print info
        counter = 0

        objNow = datetime.now()
        sCurrentTime = objNow.strftime("%H:%M:%S")
        print( str(counter) + '\t' + sCurrentTime)

        objFileSystemInfo = os.walk(sRootPath)

        # Read every file
        for path, subdirs, files in objFileSystemInfo:

            # Do skip
            for skipDir in subdirs[:]: # Get copy of list https://stackoverflow.com/questions/14267722/python-list-remove-skips-next-element-in-list
                if skipDir in listExcludeFolders:
                    subdirs.remove(skipDir)

            # Get info about every file
            for name in files:

                # Get full path
                sFullPath = os.path.join(path, name)

                # Get path witout disk letter
                sRelFilePath = sFullPath[3:] # os.path.relpath(sFullPath, name)

                # Check path is file, not directory
                bIsFile = os.path.isfile(sFullPath)
                if bIsFile:

                    try:
                        # Calculate MD%
                        #sMd5 = sDelimeter + compute_md5(sFullPath)
                        sMd5 = ''
                    except:
                        print('Exception for ' + sFullPath)
                        sMd5 = sDelimeter + 'EMPTY'

                    # Get file size
                    nFileSize = os.path.getsize(sFullPath)

                    # Form out string to write
                    sStrToWrite = '"' + sRelFilePath + '"' + sDelimeter + str(nFileSize) + sMd5 + '\n'

                    # Write line
                    objOutCSV.write(sStrToWrite)

                    counter = counter + 1

                    # Additional info
                    if counter % 10000 == 0:

                        objNow = datetime.now()
                        sCurrentTime = objNow.strftime("%H:%M:%S")
                        print( str(counter) + '\t' + sCurrentTime)

        objOutCSV.close()

        # Get current time and print
        objNow = datetime.now()
        sCurrentTime = objNow.strftime("%H:%M:%S")
        print(str(counter) + '\t' + sCurrentTime)

    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")

        objOutCSV.close()

if __name__ == '__main__':

    listDrives = settings.listDiskToWalk

    sOutFilePath = settings.sOutFilePath


    objNow = datetime.now().date()
    sCurrentDate = objNow.strftime("%Y_%m_%d")

    for sDrive in listDrives:

        sRootPath = sDrive + ':\\'

        isExist = os.path.exists(sRootPath)

        if isExist:

            print('================ Scan ', sRootPath, ' ================')

            sFilePrefix = sDrive + '_'

            sOutFileName = '_' + sFilePrefix.lower() + 'disk_' + sCurrentDate + '.csv'
            sOutFile = sOutFilePath + sOutFileName

            collect_files_info(sRootPath, sOutFile)
            dictFiles[sDrive] = sOutFile



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


    print('### FINISH ###')
    time.sleep(3)