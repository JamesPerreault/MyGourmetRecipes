from gourmet import convert
from gourmet.gdebug import debug
import re

def parse_ingredient (s, conv=None, get_key=True):
        """Handed a string, we hand back a dictionary representing a parsed ingr
edient (sans recipe ID)"""
        #if conv:
        #    print 'parse_ingredient: conv argument is now ignored'
        debug('ingredient_parser handed: %s'%s,0)
        # Strip whitespace and bullets...
        d={}
        #s = s.decode('utf8').strip(
        s = s.strip(
            u'\u2022\u2023\u2043\u204C\u204D\u2219\u25C9\u25D8\u25E6\u2619\u2765\u2767\u29BE\u29BF\n\t #*+-')
        s = str(s)
        option_m = re.match('\s*optional:?\s*',s,re.IGNORECASE)
        if option_m:
            s = s[option_m.end():]
            d['optional']=True
        debug('ingredient_parser handed: "%s"'%s,1)
        m=convert.ING_MATCHER.match(s)
        if m:
            debug('ingredient parser successfully parsed %s'%s,1)
            a,u,i=(m.group(convert.ING_MATCHER_AMT_GROUP),
                   m.group(convert.ING_MATCHER_UNIT_GROUP),
                   m.group(convert.ING_MATCHER_ITEM_GROUP))
            if a:
                debug('ingredient parser matched ammount %s'%a,1)
                asplit = convert.RANGE_MATCHER.split(a)
                if len(asplit)==2:
                    d['amount']=convert.frac_to_float(asplit[0].strip())
                    d['rangeamount']=convert.frac_to_float(asplit[1].strip())
                else:
                    d['amount']=convert.frac_to_float(a.strip())
            if u:
                debug('ingredient parser matched unit %s'%u,1)
                conv = convert.get_converter()
                if conv and conv.unit_dict.has_key(u.strip()):
                    # Don't convert units to our units!
                    d['unit']=u.strip()
                else:
                    # has this unit been used
                    prev_uses = False # self.fetch_all(self.ingredients_table,unit=u.strip())
                    if prev_uses:
                        d['unit']=u
                    else:
                        # otherwise, unit is not a unit
                        i = u + ' ' + i
            if i:
                optmatch = re.search('\s+\(?[Oo]ptional\)?',i)
                if optmatch:
                    d['optional']=True
                    i = i[0:optmatch.start()] + i[optmatch.end():]
                d['item']=i.strip()
                # if get_key: d['ingkey']=self.km.get_key(i.strip())
            debug('ingredient_parser returning: %s'%d,0)
            return d
        else:
            debug("Unable to parse %s"%s,0)
            d['item'] = s
            return d

