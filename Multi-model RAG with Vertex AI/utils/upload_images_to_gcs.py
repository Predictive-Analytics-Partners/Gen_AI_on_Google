from pdf2image import convert_from_path
import os
from google.cloud import storage
from PIL import Image
import io
from dotenv import load_dotenv
import time

load_dotenv()


def save_to_gcs(bucket_name, image, file_name):
    """Saves a PIL Image to Google Cloud Storage.

    Args:
        bucket_name (str): Name of the bucket.
        image (PIL.Image.Image): Image to be saved.
        file_name (str): Name of the file in the bucket.
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)

    image_byte_arr = io.BytesIO()
    image.save(image_byte_arr, format="PNG")
    image_byte_arr = image_byte_arr.getvalue()

    blob.upload_from_file(io.BytesIO(image_byte_arr))

    print(f"Saved to GCS! {file_name} uploaded to {bucket_name}/{blob.name}\n") 

def pdf_to_pngs(pdf_path, bucket_name, dpi=300): 
    """
    Converts each page of a PDF to a PNG image and uploads them to Google Cloud Storage.
    Checks if files already exist, times the process, and prints a completion message.

    Args:
        pdf_path (str): Path to the PDF file.
        bucket_name (str): Name of the Google Cloud Storage bucket.
        dpi (int, optional): Resolution for the PNG images. Defaults to 300.
    """

    start_time = time.time()

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name) 

    pages = convert_from_path(
        pdf_path,
        dpi=dpi,
        poppler_path=r"/usr/local/Cellar/poppler/24.04.0_1/bin",
    )

    for page_num, page in enumerate(pages):
        filename = f"Doc1/Doc1_images/page_{page_num}.png" 

        blob = bucket.blob(filename)
        if blob.exists():
            print(f"Skipping {filename} - already exists in GCS")
            continue

        save_to_gcs(bucket.name, page, filename)

    end_time = time.time()
    elapsed_time = end_time - start_time

    if pages: 
        print(f"Upload complete! {filename} uploaded to {bucket_name}/{blob.name}\n") 
    else:
        print("No new images uploaded.") 

    print(f"Time taken: {elapsed_time:.2f} seconds")

    return elapsed_time

def upload_pdf_to_gcs(bucket_name, pdf_path, destination_blob_name):
    """Uploads a PDF file to Google Cloud Storage.

    Args:
        bucket_name (str): Name of the bucket.
        pdf_path (str): Local path to the PDF file.
        destination_blob_name (str): Name of the file in the bucket.
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)


    with open(pdf_path, "rb") as pdf_file:
        blob.upload_from_file(pdf_file)

    print(f"Upload complete! {destination_blob_name} uploaded to {bucket_name}/{blob.name}") 

# Get the absolute path of the current script's directory

script_dir = os.path.dirname(os.path.realpath(__file__))



# Construct the absolute paths to the PDF and the destination blob

pdf_path = os.path.join(script_dir, "../current-investor-presentation_en.pdf")

destination_blob_name = "Doc1/current-investor-presentation_en.pdf"



# Upload the PDF
upload_pdf_to_gcs(os.getenv("GS_BUCKET"), pdf_path, destination_blob_name)


# Call pdf_to_pngs with the bucket name from the environment variable
pdf_to_pngs(pdf_path, os.getenv("GS_BUCKET")) 
