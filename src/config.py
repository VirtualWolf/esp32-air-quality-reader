import ujson

file = open('config.json', 'r')
config = ujson.load(file)
file.close()

def read_configuration():
    return config
