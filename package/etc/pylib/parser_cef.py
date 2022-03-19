import re

class cef_kv(object):
    def init(self, options):
        return True

    def parse(self, log_message):

        try:
            data = log_message[".metadata.cef.ext"].decode("utf-8")

            rpairs = re.findall(r'([^=\s]+)=((?:[\\]=|[^=])+)(?:\s|$)', data)
            pairs={}
            keys=[]
            for p in rpairs:
                pairs[p[0]]=p[1]
                keys.append(p[0])


            cleanpairs={}
            for k in keys:
                if k.endswith('Label'):
                    vk=k.rstrip('Label')
                    l = pairs[k]
                    if vk in pairs:            
                        pairs[l]=pairs[vk]
                        del pairs[vk]
                    del pairs[k]
                elif k == 'rawEvent':
                    pairs[k]=pairs[k].replace('\=','=').replace('&&','\n')
                    
            for k,v in pairs.items():
                kc = k.replace(' ','_').replace('.','_')
                log_message[f".values.{kc}"]=v
                
        except:
            return False
        return True
