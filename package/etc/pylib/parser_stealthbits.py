

class alerttext_kv(object):
    def init(self, options):
        return True

    def parse(self, log_message):
        pairs = log_message[".values.AlertText"].decode("utf-8").split('; ')
        if len(pairs)==0:
            return False
        for p in pairs:
            k,v=p.split(': ')
            cleank=k.replace(' ','_').replace('.','_')
            log_message[f".values.AlertValues.{cleank}"]=v.strip()
        return True

