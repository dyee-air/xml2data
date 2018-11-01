import csv

def writeData(xml_codebook, out_file, out_fields):
    
    if out_file[-4:].lower() != ".csv":
        out_file += ".csv"

    