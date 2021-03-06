from contracts import contract

from .memdata_events import event_leaf_set, event_dict_setitem, event_dict_delitem, event_list_append, event_list_delete, event_list_insert
from .schema import SchemaContext, SchemaHash, SchemaList, SchemaBytes, SchemaDate, SchemaString, SchemaSimple
from .schema import data_hash_code
from mcdp.logs import logger
from mcdp_utils_misc.my_yaml import yaml_dump
from contracts.utils import indent


@contract(returns='list(dict)')
def data_diff(schema, data1, data2, prefix=()):
    ''' Returns a list of data events that when applied to data1
        give data2. '''
    schema.validate(data1)
    schema.validate(data2)
    if isinstance(schema, SchemaContext):
        events = []
        for k, schema_child in schema.children.items():
            if isinstance(schema_child, SchemaSimple):
                if data1[k] != data2[k]:
                    e = event_leaf_set(name=prefix, leaf=k, value=data2[k], _id='', who=None)
                    events.append(e)
            else:
                e = data_diff(schema_child, data1[k], data2[k], prefix=prefix+(k,))
                events.extend(e)
        if events:
            logger.info('Found:\n'+indent(yaml_dump(events), ' > '))
        return events
    
    elif isinstance(schema, SchemaHash):
        events = []
        # first add the ones that are missing
        for k in data2:
            if not k in data1:
                e = event_dict_setitem(name=prefix, key=k, value=data2[k], _id='', who=None)
                events.append(e)
        # then remove the ones that should not be there
        for k in data1:
            if not k in data2:
                e = event_dict_delitem(name=prefix, key=k, _id='', who=None)
                events.append(e)
        # then look up the changes
        common = set(data1) & set(data2)
        for k in common:
            es = data_diff(schema.prototype, data1[k], data2[k], prefix=prefix+(k,))
            events.extend(es)
        return events
    
    elif isinstance(schema, SchemaList):
        # compute the hashcodes of each element
        hc1 = map(data_hash_code, data1)
        hc2 = map(data_hash_code, data2)
        # check whether the elements are there
#         def get_map(a, b):
#             m = []
#             for x in a:
#                 if x in b:
#                     m.append(b.index(x))
#                 else:
#                     m.append(None)
#             return m
        
#         m_2_in_1 = get_map(hc2, hc1)
#         m_1_in_2 = get_map(hc1, hc2) 
#         logger.debug('map 2 in 1: %s' % m_2_in_1)
#         logger.debug('map 1 in 2: %s' % m_1_in_2)
         
        events = []
        for i in range(len(hc2)): 
            if not( len(hc1) >=  i + 1): # the first one is not in there
                e = event_list_append(name=prefix, value=data2[i], who=None, _id='')
                events.append(e)
                # modify as if we did it
                hc1.append(hc2[i]) 
                continue
            
            if hc1[i] == hc2[i]:
                continue
            else:
                # the elements differ
                # is the element in 2 already in 1, later?
                if hc2[i] in hc1[i:]:
                    # hc1 = A B C D E
                    # hc2 = A B D E
                    # yes it is at index
                    index = i + hc1.index(hc2[i])
                    # remove those in between
                    for j in range(i, index):
                        e = event_list_delete(name=prefix, index=j, who=None, _id='')
                        events.append(e)
                        hc1.pop(j)
                else:
                    # no, it is not
                    # hc1 = A B C D E
                    # hc2 = A B C n D E
                    # we insert it 
                    e = event_list_insert(name=prefix, index=i, value=data2[i], who=None, _id='')
                    events.append(e)
                    hc1.insert(i, hc2[i])
        # At this point, we are guaranteed that hc2 is a prefix of hc1
        assert hc2 == hc1[:len(hc2)]
        # the extra elements need to be removed
        if len(hc1) > len(hc2):
            extra = len(hc1) - len(hc2)
            for t in range(extra):
                i = len(hc1) - 1 - t
                e = event_list_delete(name=prefix, index=i, who=None, _id='')
                events.append(e)
                hc1.pop(i) 
   
        assert hc1 == hc2
         
        return events
    
    elif isinstance(schema, (SchemaString, SchemaDate, SchemaBytes)):
        msg = 'I was not expecting to be called for %s' % schema
        raise ValueError(msg)
    else:
        assert False, schema

