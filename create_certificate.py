import subprocess
import qrcode
import urllib.parse
import base64
import json
import os

from steganographie import cacher
from PIL import Image

IMGBUN_API_KEY = "252d562bac2de5b2bda9cd369ce294b3"

def create_signature(info):

    # Ensure the info is 64 bits
    if (len(info) < 64):
        gaps = 64 - len(info)
        info = info + '\x01' * gaps
    else:
        print("Info is too long. Truncating to 64 bytes")
    
    # Save the info to a file
    info_file = open("tmp/info.txt", "w")
    info_file.write(info)
    info_file.close()


    # Hash the info
    hash_process = subprocess.Popen("openssl dgst -sha256 tmp/info.txt > tmp/info.hash",
        shell=True,
        stdout=subprocess.PIPE)
    
    (output, error) = hash_process.communicate()
    if hash_process.returncode != 0:
        print("Error hashing the info")
        print(error)
        return False
    
    # Sign the hash with the CA's private key
    signProcess = subprocess.Popen("openssl dgst -sha256 -sign {} -out tmp/info.sig tmp/info.hash"
            .format("CA/ecc.ca.key.pem"),
        shell=True, stdout=subprocess.PIPE)
    (output, error) = signProcess.communicate()
    if signProcess.returncode != 0:
        print("Error signing the hash")
        print(error)
        return False

    print("Signature created!")
    return True

def create_image(identity):

    # Certificate titles
    # texte_titre = "Attestation de réussite"
    # texte_delivre = "délivrée à "
    texte_identite = identity
    # texte_ligne = "Attestation de réussite délivrée à " + identity

    # Ensure the identity is 64 characters long by adding spaces
    texte_identite = identity.center(64)
    print(texte_identite)
    
    # Create an image from the text
    process = subprocess.Popen('curl -o tmp/texte.png "https://api.imgbun.com/png?key={}&text={}&size=40&format=raw"'
                               .format(IMGBUN_API_KEY, urllib.parse.quote(texte_identite)), shell=True, stdout=subprocess.PIPE)
    (output, error) = process.communicate()
    if process.returncode != 0:
        print("Error creating image")
        print(error)
        return False
    
    print("Image created!")
    return True

def create_qr_code(data):
    qr = qrcode.make(data)
    qr.save("tmp/qrcode.png", scale=3)
    print("QR code created!")
    
def combine_images():

    # Resize and add title image to certificate
    # Add the title image to the certificate
    process = subprocess.Popen("composite -gravity center -geometry +0-100 img/texte_titre.png img/fond_attestation.png tmp/combinaison.png",
                               shell=True, stdout=subprocess.PIPE)
    (output, error) = process.communicate()

    if process.returncode != 0:
        print("Error combining images")
        return False
    
    # Add the identity image to the certificate
    process = subprocess.Popen("composite -gravity center img/texte_delivre.png tmp/combinaison.png tmp/combinaison.png",
                               shell=True, stdout=subprocess.PIPE)
    (output, error) = process.communicate()

    if process.returncode != 0:
        print("Error combining images")
        return False
    
    # Add the identity image to the certificate
    process = subprocess.Popen("mogrify -resize 600x200 tmp/texte.png && composite -gravity center -geometry +0+100 tmp/texte.png tmp/combinaison.png tmp/combinaison.png",
                               shell=True, stdout=subprocess.PIPE)
    (output, error) = process.communicate()

    if process.returncode != 0:
        print("Error combining images")
        return False
    
    # Add QR code to certificate
    process = subprocess.Popen("mogrify -resize 200x200 tmp/qrcode.png && composite -geometry +1418+934 tmp/qrcode.png tmp/combinaison.png tmp/attestation.png",
                                 shell=True, stdout=subprocess.PIPE)
    (output, error) = process.communicate()
    if process.returncode != 0:
        print("Error combining images")
        return False
    
    print("Images combined!")
    return True

def create_timestamp(signature_file):

    # Check if ts_query.tsq file exists and create it if it doesn't
    if not os.path.exists('./tmp/ts'):
        os.makedirs('./tmp/ts')
    if not os.path.exists('./tmp/ts/ts_query.tsq'):
        open('./tmp/ts/ts_query.tsq', 'a').close()

    # Create a timestamp query
    tsq_process = subprocess.Popen("openssl ts -query -data {} -no_nonce -sha512 -cert -out ./tmp/ts/ts_query.tsq"
            .format(signature_file),
        shell=True,
        stdout=subprocess.PIPE)

    (output, error) = tsq_process.communicate()

    if tsq_process.returncode == 0:
        print("Create timestamp-query success.")
    else:
        print("Create timestamp-query failed.")
        return False
    
    # Send the timestamp query to 3rd party TSA
    rsq_process = subprocess.Popen('curl -H "Content-Type: application/timestamp-query" --data-binary "@./tmp/ts/ts_query.tsq" https://freetsa.org/tsr > ./tmp/ts/ts_respone.tsr',
        shell=True,
        stdout=subprocess.PIPE)
    (output, error) = rsq_process.communicate()

    if rsq_process.returncode != 0:
        print("Create timestamp-response failed.")
        return False
    
    print("Create timestamp-response success.")    
    return True

def create_certificate(identity, certif_title):
    info = identity + certif_title
    try:
        # Create a signature
        if not create_signature(info):
            return "Error creating signature"
        
        # Create an image with the identity
        if not create_image(identity):
            return "Error creating image"
        
        # Create a QR code
        f = open("tmp/info.sig", "rb")
        info_sig = f.read()
        f.close()
        print(base64.b64encode(info_sig).decode())
        create_qr_code(base64.b64encode(info_sig).decode())

        # Combine the images
        if not combine_images():
            return "Error combining images"
        
        # Create timestamp
        if not create_timestamp("tmp/info.sig"):
            return "Error creating timestamp"
        
        # Conceal the timestamp in the image
        img = Image.open("tmp/attestation.png")

        f = open("tmp/ts/ts_respone.tsr", "rb")
        tsr_data = f.read()
        f.close()

        f = open("tmp/info.txt", "r")
        info_data = f.read()
        f.close()

        data =  info_data + base64.b64encode(tsr_data).decode()
        # The info_data have the fixed length of 64 bytes, and the total length of the data is 64 + 7328 = 7392
        # print(len(data))
        # print(len(base64.b64encode(tsr_data).decode()))
        cacher(img, data)
        img.save("tmp/attestation.png")

        print("Timestamp created and concealed in the image.")
        
    except Exception as e:
        print(e)
        return "Error creating certificate"