from ConfigParser import SafeConfigParser

parser = SafeConfigParser()
parser.read('chamber1.bpc.dacs')

print parser.get('Chip0','IKrum')
