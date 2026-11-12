import json,base64,sys,glob
def st(p):
    d=json.load(open(p));b=lambda k:base64.b64decode(d[k]);oc=b('ocean');ki=b('kind');te=b('terr');K=d['K']
    land=sum(1 for v in oc if not v);bl=sum(1 for i,v in enumerate(ki) if not oc[i] and v>=K['RES'] and v!=K.get('PARK',-1));rd=sum(1 for i,v in enumerate(ki) if not oc[i] and v==K['ROAD']);wa=sum(1 for i,v in enumerate(te) if not oc[i] and v==d['TWA'])
    return land,bl,rd,wa,d['hmax']
if __name__=='__main__':
    for p in sys.argv[1:]:print(p.split('/')[-1],st(p))
