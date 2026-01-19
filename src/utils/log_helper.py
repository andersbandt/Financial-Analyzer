"""
@file     log_helper.py
@author   Anders Bandt
@date     April 2024
@brief    handle logging of application to output files
"""

# import needed modules
import os
from fpdf import FPDF
import subprocess
import shutil

# # import user created modules
import utils

# import logger
from loguru import logger


#################################
#### pdf  #######################
#################################

def clear_tmp_folder():
    logger.info("Clearing tmp folder")
    del_folder = utils.BASEFILEPATH + "/tmp"
    for filename in os.listdir(del_folder):
        file_path = os.path.join(del_folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


def generate_summary_pdf(doc_name):
    ### START OF PDF CREATION
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Build full path to image folder
    image_folder_path = os.path.join(utils.BASEFILEPATH, utils.IMAGE_FOLDER)

    # Get the list of PNG files in the folder
    image_files = [f for f in os.listdir(image_folder_path) if f.endswith('.png')]

    # Add each PNG file as a page to the PDF document
    for image_file in image_files:
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=image_file, ln=True)

        # Add the PNG image to the PDF page
        pdf.image(os.path.join(image_folder_path, image_file), x=10, y=20, w=180)

    # Build full path for PDF output
    pdf_filepath = os.path.join(utils.BASEFILEPATH, doc_name)

    # Save the PDF document
    try:
        pdf.output(pdf_filepath)
    except PermissionError:
        raise BaseException("Can't generate PDF! (Do you have it open?)")
    ### END OF PDF CREATION

    # start the PDF document
    print(f"Starting .PDF at filepath: {pdf_filepath}")
    subprocess.Popen(pdf_filepath, shell=True)
