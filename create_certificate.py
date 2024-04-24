import subprocess
import qrcode
import urllib.parse
import base64

CA_KEY_PATH = "CA/ecc.ca.key.pem"
IMGBUN_API_KEY = "252d562bac2de5b2bda9cd369ce294b3"

def create_timespamp(signature):

    ProcessTSQ = subprocess.Popen([
        "openssl ts -query -data {} -no_nonce -sha512 -cert -out ./ts/ts_query.tsq"
        .format(signature)
    ],
                                  shell=True,
                                  stdout=subprocess.PIPE)

    (output, error) = ProcessTSQ.communicate()

    if ProcessTSQ.returncode == 0:
        print("Create timestamp-query")
    else:
        print("Create timestamp-query failed")

    ProcessTSR = subprocess.Popen([
        'curl -H "Content-Type: application/timestamp-query" --data-binary "@./ts/ts_query.tsq" https://freetsa.org/tsr > ./ts/ts_respond.tsr'
    ],
                                  shell=True,
                                  stdout=subprocess.PIPE)
    (output, error) = ProcessTSR.communicate()

    if ProcessTSR.returncode == 0:
        print("create timestamp ts_respond")
        return True
    else:
        return False

def create_signature(info):
    
    # Save the info to a file
    info_file = open("tmp/info.txt", "w")
    info_file.write(info)
    info_file.close()

    # Create a signature
    # Hash the info
    hash_process = subprocess.run("openssl dgst -sha256 tmp/info.txt > tmp/info.hash",
                                shell=True, capture_output=True)
    if hash_process.returncode != 0:
        print("Error hashing the info")
        print(hash_process.stderr)
        return False
    
    # Sign the hash with the CA's private key
    # process = subprocess.run("openssl dgst -sha256 -sign -inkey " + CA_KEY_PATH +" -in info.txt -out signature.txt",
    signProcess = subprocess.run("openssl dgst -sha256 -sign " + CA_KEY_PATH + " -out tmp/info.sig tmp/info.hash",
                                shell=True, capture_output=True)
    if signProcess.returncode != 0:
        print("Error signing the hash")
        print(signProcess.stderr)
        return False

    print("Signature created!")
    return True

def create_image(identity):
    texte_ligne = "Attestation de réussite|délivrée à " + identity
    process = subprocess.Popen('curl "https://api.imgbun.com/png?key={}&text={}&size=40"'
                               .format(IMGBUN_API_KEY, urllib.parse.quote(texte_ligne)), shell=True, stdout=subprocess.PIPE)
    (output, error) = process.communicate()
    if process.returncode != 0:
        print("Error creating image")
        print(error)
        return False
    
    res = json.loads(output)

    process = subprocess.Popen("curl -o tmp/texte.png {}".format(res['direct_link']), shell=True, stdout=subprocess.PIPE)
    (output, error) = process.communicate()
    if process.returncode != 0:
        print("Error creating image")
        print(error)
        return False
    
    print("Image created!")
    return True
    
def combine_images():
    process = subprocess.Popen("mogrify -resize 1000x600 tmp/texte.png && composite -gravity center tmp/texte.png fond_attestation.png tmp/combinaison.png",
                               shell=True, stdout=subprocess.PIPE)
    (output, error) = process.communicate()

    if process.returncode != 0:
        print("Error combining images")
        return False
    
    process = subprocess.Popen("composite -gravity center tmp/qrcode.png tmp/combinaison.png tmp/combinaison.png",
                                 shell=True, stdout=subprocess.PIPE)
    (output, error) = process.communicate()
    if process.returncode != 0:
        print("Error combining images")
        return False
    
    print("Images combined!")
    return True
    
def create_qr_code(data):
    qr = qrcode.make(data)
    qr.save("tmp/qrcode.png", scale=2)
    print("QR code created!")

def create_certificate(identity, certif_title):
    info = identity + certif_title
    if create_signature(info):
        print("Signature created and signed")

        # Create a certificate image
        create_image(identity)

        # Create a QR code
        f = open("tmp/info.sig", "r")
        info_sig = f.read()
        f.close()
        create_qr_code(base64.b64encode(info_sig).decode())

        # Combine the images
        combine_images()

        # Create timestamp and conceal it in the image