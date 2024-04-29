import subprocess
import qrcode
import base64
import os
import zbarlight

from steganographie import recuperer
from PIL import Image

def recover_info_from_image():
    try:
        img = Image.open("tmp/attestation_a_verifier.png")
        full_info  = recuperer(img,7392)
        print(full_info)
        info = full_info[:64]
        timeStamp = full_info[64:]
        print(len(info))
        timeStamp = base64.b64decode(timeStamp)
        print(len(timeStamp))

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

def get_qrcode():
    attestation = Image.open("tmp/attestation_a_verifier.png")
    qr = attestation.crop((1418,934, 1418+200, 934+200))
    qr.save("tmp/verify_qrcode.png", scale=3)
    print("Get QR code successfully!")

def recover_data_from_qrcode():
    img = Image.open("tmp/verify_qrcode.png")
    data = zbarlight.scan_codes(['qrcode'],img)
    print(data)
    data = base64.b64decode(data[0])
    print(data)

    f = open("tmp/verify_sig_qrcode.sig","wb")
    f.write(data)
    f.close()

def verify_timestamp(timestamp):

     # Check if ts_query.tsq file exists and create it if it doesn't
    if not os.path.exists('./tmp/ts'):
        os.makedirs('./tmp/ts')
    if not os.path.exists('./tmp/ts/ts_query_verify.tsq'):
        open('./tmp/ts/ts_query_verify.tsq', 'a').close()

    tsq_process = subprocess.Popen(["openssl ts -query -data ./tmp/verify_sig_qrcode.sig -no_nonce -sha512 -cert -out ./tmp/ts/ts_query_verify.tsq"],
        shell=True,
        stdout=subprocess.PIPE) 
    
    (output, error) = tsq_process.communicate()

    if tsq_process.returncode == 0:
        print("Create timestamp-query success!")
    else:
        print("Create timestamp-query failed!")
        return False

    rsq_process = subprocess.Popen(["openssl ts -verify -in {} -queryfile ./tmp/ts/ts_query_verify.tsq -CAfile ./tmp/ts/cacert.pem -untrusted ./ts/tsa.crt".format(timestamp)],
        shell=True,
        stdout=subprocess.PIPE)
    
    (output, error) = rsq_process.communicate()

    if rsq_process.returncode == 0 and output.decode() == 'Verification: OK\n':
        print("Verify timestamp success!")
        return True
    else:
        print("Verify timestamp failed!")
        return False

def verify_signature(signature):
    process = subprocess.Popen(["openssl dgst -verify CA/ecc.ca.pubkey.pem -signature {} tmp/info.txt".format(signature)],
        shell=True,
        stdout=subprocess.PIPE)

    (output, error) = process.communicate()
    if process.returncode == 0 and output.decode() == 'Verified OK\n':
        print("Verify signature  success!")
        return True
    else:
        print("Verify signature  failed!")
        return False

def verify_certificate():
    _, _ = recover_info_from_image()
    get_qrcode()
    recover_data_from_qrcode()
    if (verify_signature("tmp/verify_sig_qrcode.sig")== True) and (verify_timestamp("tmp/verify_timestamp.tsr") == True):
        return "Verify certificate success!"
    else:
        return "Verify certificate failed!"