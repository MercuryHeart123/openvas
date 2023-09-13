import json
import xmltodict


def xmlToJson(xml):
    dictStr = xmltodict.parse(xml)
    result = json.dumps(dictStr)
    return result
