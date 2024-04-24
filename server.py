#!/usr/bin/python3
from bottle import route, run, template, request, response
from create_certificate import create_certificate

@route('/creation', method='POST')
def creation_attestation():
    # Get the data from the form
    contenu_identite = request.forms.get('identite')
    contenu_intitule_certification = request.forms.get('intitule_certif')

    print('nom prénom :', contenu_identite, 
          ' intitulé de la certification :', contenu_intitule_certification)
    res = create_certificate(contenu_identite, contenu_intitule_certification)
    response.set_header('Content-type', 'text/plain')
    return res

@route('/verification', method='POST')
def verification_attestation():
    contenu_image = request.files.get('image')
    contenu_image.save('attestation_a_verifier.png',overwrite=True)
    response.set_header('Content-type', 'text/plain')
    return "ok!"

@route('/fond')
def recuperer_fond():
    response.set_header('Content-type', 'image/png')
    descripteur_fichier = open('fond_attestation.png','rb')
    contenu_fichier = descripteur_fichier.read()
    descripteur_fichier.close()
    return contenu_fichier

run(host='0.0.0.0',port=8080,debug=True)