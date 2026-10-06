import boto3
import io
import os
import urllib.parse
from PIL import Image

s3 = boto3.client("s3")

INPUT_PREFIX = "uploads/"
OUTPUT_PREFIX = "converted/"

ALLOWED_EXTENSIONS = [
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".bmp",
    ".tiff"
]


def lambda_handler(event, context):

    print("S3 event received")
    print(event)

    try:

        bucket = event["Records"][0]["s3"]["bucket"]["name"]

        key = event["Records"][0]["s3"]["object"]["key"]

        key = urllib.parse.unquote_plus(key)

        print("Bucket:", bucket)
        print("File:", key)

        if not key.startswith(INPUT_PREFIX):
            print("File is not inside uploads/. Skipping.")

            return {
                "statusCode": 200,
                "body": "Skipped"
            }

        file_name = os.path.basename(key)

        extension = os.path.splitext(file_name)[1].lower()

        if extension not in ALLOWED_EXTENSIONS:

            print("Unsupported image:", extension)

            return {
                "statusCode": 200,
                "body": "Unsupported image format"
            }

        response = s3.get_object(
            Bucket=bucket,
            Key=key
        )

        image_data = response["Body"].read()

        print(
            "Original file size:",
            len(image_data),
            "bytes"
        )

        image = Image.open(
            io.BytesIO(image_data)
        )

        print(
            "Original image size:",
            image.size
        )

        if image.mode != "RGB":
            image = image.convert("RGB")

        image.thumbnail(
            (2000, 2000),
            Image.Resampling.LANCZOS
        )

        compressed_image = io.BytesIO()

        image.save(
            compressed_image,
            format="JPEG",
            quality=70,
            optimize=True
        )

        compressed_image.seek(0)

        print(
            "Compressed size:",
            compressed_image.getbuffer().nbytes,
            "bytes"
        )

        compressed = Image.open(
            compressed_image
        )

        pdf_buffer = io.BytesIO()

        compressed.save(
            pdf_buffer,
            format="PDF",
            resolution=100.0
        )

        pdf_buffer.seek(0)

        base_name = os.path.splitext(file_name)[0]

        output_key = f"{OUTPUT_PREFIX}{base_name}.pdf"

        s3.put_object(
            Bucket=bucket,
            Key=output_key,
            Body=pdf_buffer.getvalue(),
            ContentType="application/pdf"
        )

        print("PDF uploaded:", output_key)

        return {
            "statusCode": 200,
            "body": f"Successfully created {output_key}"
        }

    except Exception as error:

        print("ERROR:", str(error))

        raise