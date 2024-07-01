"""
@file     log_helper.py
@author   Anders Bandt
@date     April 2024
@brief    handle logging of application to output files
"""

# import needed modules
import logging
import csv
import os
from fpdf import FPDF
import subprocess
from matplotlib import pyplot as plt
from datetime import datetime


# import user created modules
import utils


#################################
#### pdf  #######################
#################################

def generate_summary_pdf(image_folder, output_pdf):
    # Create a PDF document
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Get the list of PNG files in the folder
    image_files = [f for f in os.listdir(image_folder) if f.endswith('.png')]

    # Add each PNG file as a page to the PDF document
    for image_file in image_files:
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=image_file, ln=True)

        # Add the PNG image to the PDF page
        pdf.image(os.path.join(image_folder, image_file), x=10, y=20, w=180)

    # Save the PDF document
    pdf.output(output_pdf)

    # start the PDF document
    pdf_filepath = f"{utils.BASEFILEPATH}/{output_pdf}"
    print(f"Starting .PDF at filepath: {pdf_filepath}")
    subprocess.Popen(pdf_filepath, shell=True)
