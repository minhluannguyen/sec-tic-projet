import subprocess
import base64
import os
import zbarlight

from steganographie import recuperer
from PIL import Image

# Recover information from the certificate image
def recover_info_from_image():
    try:
        img = Image.open("tmp/attestation_a_verifier.png")
        full_info  = recuperer(img,7392)
        info = full_info[:64]
        timeStamp = full_info[64:]
        timeStamp = base64.b64decode(timeStamp)

        print(info)
        # Write information and timestamp to files
        f = open("tmp/ts/verify_timestamp.tsr","wb")
        f.write(timeStamp)
        f.close()

        f = open("tmp/verify_info.txt", "w")
        f.write(info)
        f.close()

        return info, timeStamp
    except Exception as e:
        print(e)
        return "Error recovering info!"

# Extract QR code from the certificate image
def get_qrcode():
    attestation = Image.open("tmp/attestation_a_verifier.png")
    qr = attestation.crop((1418,934, 1418+200, 934+200))
    qr.save("tmp/verify_qrcode.png", format="png")
    print("Get QR code successfully!")

# Recover data from the QR code
def recover_data_from_qrcode():
    img = Image.open("tmp/verify_qrcode.png")
    data = zbarlight.scan_codes(['qrcode'], img)

    # Decode the base64-encoded data
    data = base64.b64decode(data[0])

    # Write the recovered data to a file
    f = open("tmp/verify_sig_qrcode.sig","wb")
    f.write(data)
    f.close()

# Verify the timestamp
def verify_timestamp(timestamp):

     # Check if ts_query_verify.tsq file exists and create it if it doesn't
    if not os.path.exists('./tmp/ts'):
        os.makedirs('./tmp/ts')
    if not os.path.exists('./tmp/ts/ts_query_verify.tsq'):
        open('./tmp/ts/ts_query_verify.tsq', 'a').close()

    # Create a timestamp query
    tsq_process = subprocess.Popen(["openssl ts -query -data ./tmp/verify_sig_qrcode.sig -no_nonce -sha512 -cert -out ./tmp/ts/ts_query_verify.tsq"],
        shell=True,
        stdout=subprocess.PIPE) 
    
    (output, error) = tsq_process.communicate()

    # Check if timestamp query creation was successful
    if tsq_process.returncode == 0:
        print("Create timestamp-query success!")
    else:
        print("Create timestamp-query failed!")
        return False

    # Verify the timestamp
    rsq_process = subprocess.Popen(["openssl ts -verify -in {} -queryfile ./tmp/ts/ts_query_verify.tsq -CAfile ./CA/cacert.pem -untrusted ./CA/tsa.crt".format(timestamp)],
        shell=True,
        stdout=subprocess.PIPE)
    
    (output, error) = rsq_process.communicate()

    # Check if timestamp verification was successful
    if rsq_process.returncode == 0 and output.decode() == 'Verification: OK\n':
        print("Verify timestamp success!")
        return True
    else:
        print("Verify timestamp failed!")
        return False

def verify_signature(signature):

    # Hash the info for verification
    hash_process = subprocess.Popen("openssl dgst -sha256 -binary tmp/verify_info.txt > tmp/verify_info.hash",
        shell=True,
        stdout=subprocess.PIPE)
    
    (output, error) = hash_process.communicate()
    if hash_process.returncode != 0:
        print("Error hashing the info")
        print(error)
        return False
    
    # Verify the signature
    process = subprocess.Popen(["openssl dgst -verify CA/ecc.ca.public.pem -signature {} tmp/verify_info.hash".format(signature)],
        shell=True,
        stdout=subprocess.PIPE)

    (output, error) = process.communicate()

    # Check if signature verification was successful
    if process.returncode == 0 and output.decode() == 'Verified OK\n':
        print("Verify signature success!")
        return True
    else:
        print("Verify signature failed!")
        return False

# Verify the entire certificate
def verify_certificate():
    # Recover information and timestamp
    _, _ = recover_info_from_image()

    # Extract QR code 
    get_qrcode()

    # Recover data from QR code
    recover_data_from_qrcode()

    # Verify the signature and timestamp
    if (verify_signature("tmp/verify_sig_qrcode.sig") == True) and (verify_timestamp("tmp/ts/verify_timestamp.tsr") == True):
        return "Verify certificate success!\n"
    else:
        return "Verify certificate failed!\n"