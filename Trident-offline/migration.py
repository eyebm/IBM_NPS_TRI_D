import openpyxl
import sys, os
def migration_objects(inpath, outpath):
    data = extract_arr(inpath)
    wb = openpyxl.load_workbook(filename=resource_path('MIGRATION_TEMPLATE.xlsx'))
    ws = wb.active
    for i in range(5):
        key = 'E'+str(7+i)
        ws[key] = data[i]
    wb = wb.save(filename=outpath+'Migration_Cost.xlsx')

def extract_arr(inpath):
    data = []
    with open(inpath+"nz_objects.csv") as file:
        lines = file.readlines()
        for line in lines:
            split = line.split()
            data.append(split[1])
    return data

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
