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

