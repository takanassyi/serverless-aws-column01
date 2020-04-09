import boto3
import base64
import json
import logging
import traceback,sys
from chalice import Chalice

app = Chalice(app_name='image-classification')
app.debug = True

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


@app.route('/rekognition', methods=['POST'], content_types=['application/octet-stream'], cors=True)
def rekognition():

    try:
        body_data = app.current_request.raw_body
        body_data = body_data.split(b'base64,')

        image = base64.b64decode(body_data[1])

        rekognition_client = boto3.client(service_name='rekognition', region_name='us-east-1')

        logger.info('Invoke Rekognition')
        res = rekognition_client.detect_labels(
                        Image = { 'Bytes': image },
                        MaxLabels=5,
                        MinConfidence=10
                    )

        translate_client = boto3.client(service_name='translate', region_name='us-east-1')
        out = ''
        for label in res['Labels'] :
            trans = translate_client.translate_text(Text=label['Name'], 
                        SourceLanguageCode='en', TargetLanguageCode='ja')

            out += '[en] {} / [ja] {} / [Confidence] {:.2f}%,'.format(
                        label['Name'], trans.get('TranslatedText'), label['Confidence']
                    )

        return out[:-1]

    except Exception as e:
        tb = sys.exc_info()[2]
        return 'error:{0}'.format(e.with_traceback(tb))
