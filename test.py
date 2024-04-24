# texte_ligne="Attestation de réussite|délivrée à P-F.B"
# curl -o texte.png "http://chart.apis.google.com/chart" --data-urlencode "chst=d_text_outline" --data-urlencode "chld=000000|56|h|FFFFFF|b|${texte_ligne}"

# curl -o texte.png "https://api.imgbun.com/png?key=252d562bac2de5b2bda9cd369ce294b3&text=At%C3%A9tation%20DMCS&color=000000&size=18"

# mogrify -resize 1000x600 texte.png

#QR

# import qrcode
# data = "https://p-fb.net/"
# nom_fichier = "qrcode.png"
# qr = qrcode.make(data)
# qr.save(nom_fichier, scale=2)

# import subprocess
# import json
# import urllib.parse
# IMGBUN_API_KEY = "252d562bac2de5b2bda9cd369ce294b3"
# texte_ligne = "Attestation de réussite|délivrée à " + "identity"
# en = urllib.parse.quote(texte_ligne)
# print(en)
# process = subprocess.Popen('curl "https://api.imgbun.com/png?key={}&text={}&size=20"'
#                             .format(IMGBUN_API_KEY, en), shell=True, stdout=subprocess.PIPE)
# # process = subprocess.Popen('curl "https://api.imgbun.com/png?key=252d562bac2de5b2bda9cd369ce294b3&text=AtC3%A9tation%20DMCS&size=40"', shell=True, stdout=subprocess.PIPE)
# (output, error) = process.communicate()
# if process.returncode != 0:
#     print("Error creating image")

# print(output)
# res = json.loads(output)

# process = subprocess.Popen("curl -o texte.png {}".format(res['direct_link']), shell=True, stdout=subprocess.PIPE)
# (output, error) = process.communicate()
# if process.returncode != 0:
#     print("Error creating image")

# print("Image created!")

from steganographie import recuperer, cacher

from PIL import Image

image = Image.open("tmp/attestation.png")
a = recuperer(image, 7392)
print(a[:64])
print(a[64:])
# import os
# if not os.path.exists('./tmp/ts'):
#     os.makedirs('./tmp/ts')
# if not os.path.exists('./tmp/ts/ts_query.tsq'):
#     f = open('./tmp/ts/ts_query.tsq', 'a')
#     f.close()

# f = open('./tmp/ts/ts_query.tsq', 'a')
# f.close()