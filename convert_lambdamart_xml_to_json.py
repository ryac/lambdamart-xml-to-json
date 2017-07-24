# converts LambdaMART XML models to JSON for Solr..

import sys
import requests
import json
import xml.etree.ElementTree as ET


# --------------------------
# model params and configs..

modelClass = 'org.apache.solr.ltr.model.MultipleAdditiveTreesModel'
featureStoreName = ''  # ADD_FEATURE_STORE_NAME
modelStoreName = ''  # ADD_MODEL_STORE_NAME

solrEndpoint = ''  # ADD_SOLR_ENDPOINT (eg: http://localhost:8983)
collection = ''  # ADD_COLLECTION_NAME_IN_SOLR

# path and filename without the .xml extension,
# it'll output a JSON file in the same directory..
filename = 'path/to/model/filename_wo_xml_extension'

# --------------------------

features = []


def main():

    global features

    try:
        features = getFeatures()
    except:
        print('>> error getting features..')
        return 1

    model = {
        'store': featureStoreName,
        'name': modelStoreName,
        'class': modelClass,
        'features': features
    }

    lambdaModel = ET.parse('{0}.xml'.format(filename)).getroot()

    trees = []
    for node in lambdaModel:
        t = {
            'weight': str(node.attrib['weight']),
            'root': parseSplits(node[0])
        }
        trees.append(t)

    # print(trees)
    model['params'] = {'trees': trees}

    jsonModel = open('{0}.json'.format(filename), 'w')
    jsonModel.write(json.dumps(model, indent=2))
    jsonModel.close()
    print('done.')


def parseSplits(split):
    obj = {}
    for el in split:
        if (el.tag == 'feature'):
            obj['feature'] = features[(int(el.text.strip()) - 1)]['name']
        elif (el.tag == 'threshold'):
            obj['threshold'] = str(el.text.strip())
        elif (el.tag == 'split' and 'pos' in el.attrib):
            obj[el.attrib['pos']] = parseSplits(el)
        elif (el.tag == 'output'):
            obj['value'] = str(el.text.strip())
    return obj


def getFeatures():
    r = requests.get('{0}/solr/{1}/schema/feature-store/{2}'.format(solrEndpoint, collection, featureStoreName))

    response = r.json()

    fs = []
    for feature in response['features']:
        fs.append({'name': feature['name']})

    return fs


if __name__ == '__main__':
    sys.exit(main())
