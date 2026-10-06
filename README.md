\# S3 Image to PDF Converter using AWS Lambda



A serverless AWS project that automatically converts uploaded images into compressed PDF files.



\## Architecture



User

|

| Upload Image

v

Amazon S3

|

| uploads/

v

S3 Object Created Event

|

v

AWS Lambda

|

| Pillow

| Resize

| Compress

| Convert Image to PDF

v

Amazon S3

|

| converted/

v

PDF



\## AWS Services



\- Amazon S3

\- AWS Lambda

\- AWS IAM

\- Amazon CloudWatch



\## Technologies



\- Python 3.14

\- Pillow

\- AWS Lambda

\- Amazon S3



\## S3 Structure



my-bucket-3799/



uploads/

&#x20;   image.jpg



converted/

&#x20;   image.pdf



\## How It Works



1\. User uploads an image into the `uploads/` folder.

2\. Amazon S3 generates an Object Created event.

3\. S3 triggers the Lambda function.

4\. Lambda downloads the image.

5\. Pillow processes the image.

6\. Large images are resized.

7\. Image quality is reduced for compression.

8\. Image is converted into PDF.

9\. PDF is uploaded to the `converted/` folder.



\## Supported Formats



\- JPG

\- JPEG

\- PNG

\- WEBP

\- BMP

\- TIFF



\## Example



Input:



uploads/photo.jpg



Output:



converted/photo.pdf



\## Security



The Lambda execution role uses IAM permissions to access the required S3 objects.



AWS credentials are not stored in the source code.



\## Future Improvements



\- Multiple images into one PDF

\- Better PDF compression

\- PDF password protection

\- Unique filenames

\- Web upload interface

\- API Gateway integration


Steps :

🚀 AWS S3 IMAGE TO PDF CONVERTER — COMPLETE GUIDE

I built a serverless AWS project that automatically converts uploaded images into compressed PDF files.

ARCHITECTURE:

User
  ↓
Amazon S3 (uploads/)
  ↓
S3 Object Created Event
  ↓
AWS Lambda (Python 3.14)
  ↓
Pillow Layer
  ↓
Resize + Compress + Convert to PDF
  ↓
Amazon S3 (converted/)


==================================================
STEP 1 — CREATE S3 BUCKET
==================================================

1. Open AWS Console.
2. Go to S3.
3. Click "Create bucket".
4. Give a unique bucket name.

Example:
my-image-pdf-bucket-123

5. Select region:
us-east-1

6. Keep other settings as default.
7. Click "Create bucket".


==================================================
STEP 2 — CREATE S3 FOLDERS
==================================================

Open the bucket.

Create two folders:

uploads/

converted/

Final structure:

your-bucket/
├── uploads/
└── converted/

Images will be uploaded into uploads/

PDF files will be created inside converted/


==================================================
STEP 3 — CREATE LAMBDA FUNCTION
==================================================

Go to:

AWS Console → Lambda → Create function

Select:

Author from scratch

Function name:

s3-image-to-pdf

Runtime:

Python 3.14

Architecture:

x86_64

Create a new execution role.

Click:

Create function


==================================================
STEP 4 — GIVE LAMBDA S3 PERMISSIONS
==================================================

Go to:

Lambda
→ Your Function
→ Configuration
→ Permissions
→ Execution Role

Add an inline policy.

Use:

{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ReadUploadedImages",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject"
      ],
      "Resource": "arn:aws:s3:::YOUR-BUCKET-NAME/uploads/*"
    },
    {
      "Sid": "WriteConvertedPDFs",
      "Effect": "Allow",
      "Action": [
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::YOUR-BUCKET-NAME/converted/*"
    }
  ]
}

Replace:

YOUR-BUCKET-NAME

with your actual S3 bucket name.

Also make sure the Lambda role has:

AWSLambdaBasicExecutionRole

for CloudWatch logs.


==================================================
STEP 5 — INSTALL PILLOW
==================================================

Lambda does not have Pillow by default.

On Windows, install Python first.

Open CMD and run:

mkdir C:\lambda-layer

mkdir C:\lambda-layer\python

Then install Pillow:

python -m pip install Pillow --target C:\lambda-layer\python --platform manylinux2014_x86_64 --python-version 3.14 --implementation cp --only-binary=:all:

Wait until you see:

Successfully installed Pillow-12.2.0


==================================================
STEP 6 — CREATE PILLOW ZIP
==================================================

Run:

cd C:\lambda-layer

Then:

powershell Compress-Archive -Path python -DestinationPath C:\pillow-layer.zip

You should now have:

C:\pillow-layer.zip


==================================================
STEP 7 — CREATE LAMBDA LAYER
==================================================

Go to:

AWS Console
→ Lambda
→ Layers
→ Create layer

Name:

pillow

Upload:

C:\pillow-layer.zip

Compatible runtime:

Python 3.14

Compatible architecture:

x86_64

Click:

Create


==================================================
STEP 8 — ATTACH PILLOW LAYER
==================================================

Open your Lambda function.

Go to:

Code
→ Layers
→ Add a layer

Select:

Custom layers

Choose:

pillow

Version:

1

Click:

Add


==================================================
STEP 9 — ADD LAMBDA CODE
==================================================

Go to:

Lambda
→ Code
→ lambda_function.py

Delete the existing code.

Paste this:

--------------------------------------------------

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

--------------------------------------------------

Click:

Deploy


==================================================
STEP 10 — CONFIGURE S3 TRIGGER
==================================================

Go to:

Lambda
→ Your Function
→ Add trigger

Select:

S3

Choose your bucket.

Event type:

All object create events

Prefix:

uploads/

Click:

Add

IMPORTANT:

Do NOT configure the trigger for converted/

The trigger should only watch:

uploads/


==================================================
STEP 11 — WHY uploads/ IS USED
==================================================

The workflow is:

uploads/
   ↓
Lambda
   ↓
converted/

Lambda watches uploads/

When Lambda creates:

converted/image.pdf

it does NOT trigger Lambda again.

This prevents an infinite loop.


==================================================
STEP 12 — TEST THE PROJECT
==================================================

Go to:

S3
→ Your Bucket
→ uploads/

Click:

Upload

Choose an image.

For example:

photo.jpg

Upload it.

S3 will automatically trigger Lambda.


==================================================
STEP 13 — CHECK THE PDF
==================================================

Go to:

S3
→ Your Bucket
→ converted/

You should see:

photo.pdf

Download and open the PDF.


==================================================
SUPPORTED FORMATS
==================================================

The Lambda supports:

JPG
JPEG
PNG
WEBP
BMP
TIFF


==================================================
FINAL S3 STRUCTURE
==================================================

your-bucket/
│
├── uploads/
│   ├── photo.jpg
│   ├── image.png
│   └── document.webp
│
└── converted/
    ├── photo.pdf
    ├── image.pdf
    └── document.pdf


==================================================
IF YOU GET "NO MODULE NAMED PIL"
==================================================

Error:

Runtime.ImportModuleError:
Unable to import module 'lambda_function':
No module named 'PIL'

Solution:

Go to:

Lambda
→ Code
→ Layers

Make sure:

pillow
Version 1

is attached to the Lambda function.


==================================================
IF YOU GET "KEYERROR: RECORDS"
==================================================

If you manually click the Lambda Test button without an S3 event, you may get:

KeyError: 'Records'

This is normal.

Instead, test by uploading a NEW image into:

uploads/

S3 will automatically send the correct event to Lambda.


==================================================
CHECK CLOUDWATCH LOGS
==================================================

If something fails:

Lambda
→ Monitor
→ View CloudWatch logs

Look for:

S3 event received
Bucket:
File:
Original file size:
Original image size:
Compressed size:
PDF uploaded:


==================================================
GITHUB PROJECT STRUCTURE
==================================================

Create a GitHub repository:

s3-image-to-pdf-lambda

Recommended structure:

s3-image-to-pdf-lambda/
│
├── lambda/
│   └── lambda_function.py
│
├── layer/
│   └── requirements.txt
│
├── events/
│   └── s3-test-event.json
│
├── iam/
│   └── lambda-s3-policy.json
│
├── README.md
│
└── .gitignore


requirements.txt:

Pillow==12.2.0


==================================================
GITHUB COMMANDS
==================================================

Open CMD:

cd C:\s3-image-to-pdf-lambda

Initialize Git:

git init

Set main branch:

git branch -M main

Add files:

git add .

Commit:

git commit -m "Add S3 image to PDF Lambda project"

Connect GitHub:

git remote add origin https://github.com/YOUR-USERNAME/s3-image-to-pdf-lambda.git

Push:

git push -u origin main


==================================================
IMPORTANT SECURITY
==================================================

NEVER upload these to GitHub:

AWS Access Keys
AWS Secret Keys
AWS credentials
.env files
Passwords
API keys
Private tokens

Use the Lambda execution role for AWS permissions.


==================================================
HOW THE PROJECT WORKS
==================================================

User uploads an image.

        ↓

Amazon S3 receives the image.

        ↓

S3 Object Created event triggers Lambda.

        ↓

Lambda downloads the image.

        ↓

Pillow processes the image.

        ↓

Image is resized and compressed.

        ↓

Image is converted to PDF.

        ↓

PDF is uploaded to:

converted/

Final workflow:

User
↓
S3 uploads/
↓
S3 Event
↓
AWS Lambda
↓
Pillow
↓
Resize + Compress
↓
Convert to PDF
↓
S3 converted/


==================================================
TECHNOLOGIES USED
==================================================

Amazon S3
AWS Lambda
Python 3.14
Pillow
AWS IAM
AWS CloudWatch
Lambda Layers
Serverless Architecture


==================================================
PROJECT DESCRIPTION
==================================================

This project demonstrates a serverless AWS architecture where Amazon S3 automatically triggers an AWS Lambda function whenever an image is uploaded.

The Lambda function uses Python and Pillow to resize, compress and convert the image into a PDF. The generated PDF is then stored in a separate S3 folder.

This project demonstrates practical experience with:

• AWS S3
• AWS Lambda
• Lambda Layers
• IAM permissions
• CloudWatch
• Event-driven architecture
• Serverless computing
• Python image processing
• Git and GitHub
