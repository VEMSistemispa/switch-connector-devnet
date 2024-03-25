def unify(a):
    b = []
    for begin,end in sorted(a):
        if b and b[-1][1] >= begin - 1:
            b[-1][1] = max(b[-1][1], end)
        else:
            b.append([begin, end])
    return b

def range_str_to_tuples(vlans_interval: str):
    if "-" in vlans_interval:
        splitted = vlans_interval.split('-')
        return (int(splitted[0]), int(splitted[1]))
    else:
        return (int(vlans_interval), int(vlans_interval))

def range_int_to_tuples(vlans_interval: str):
    return (vlans_interval, vlans_interval)

def range_unroller(vlans_interval: str):
    if "-" in vlans_interval:
        splitted = vlans_interval.split('-')
        return [*range(int(splitted[0]), int(splitted[1])+1)]
    else:
        return [int(vlans_interval)]

def unroll_vlans(vlans: str):
    def fix_vlan_notation(vlan:str): 
        if "-" in vlan:
            return ','.join(str(vlan_number) for vlan_number in range_unroller(vlan))
        else:
            return vlan           
    return ','.join(map(lambda vlan: fix_vlan_notation(vlan),vlans.split(",")))

def vlans_str_unroll_to_int_list(vlans: str):
    vlans_list_unrolled = []
    for i in vlans.split(','):
        vlans_list_unrolled.extend(range_unroller(i))
    return vlans_list_unrolled

def adjust_vlan_set_from_list_of_str(vlan_list: list):    
    return ','.join([f"{str(range[0])}-{str(range[1])}" if range[0] != range[1] else str(range[0]) for range in unify([range_str_to_tuples(vlans_interval) for vlans_interval in vlan_list])])

def adjust_vlan_set(s: str):    
    return adjust_vlan_set_from_list_of_str(s.split(','))

def adjust_vlan_set_from_list_of_int(vlan_list: list):    
    return ','.join([f"{str(range[0])}-{str(range[1])}" if range[0] != range[1] else str(range[0]) for range in unify([range_int_to_tuples(vlans_interval) for vlans_interval in vlan_list])])

def remove_vlan_from_set(vlans: str , vlan_id: int):
    test = list(filter(lambda v: v != vlan_id, vlans_str_unroll_to_int_list(vlans=vlans)))
    return adjust_vlan_set_from_list_of_int(test)

