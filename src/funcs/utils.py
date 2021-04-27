import pandas as pd
import requests
import math
import tqdm as tqdm
import os
import pprint


def get_drugs(url, parameters):
    import requests
    drug_set = set()
    with requests.Session() as s:
        r = s.get(url, params=parameters, stream=True).json()['facets']
        x = r['drugs']['children']
        for i in range(len(x)):
            try:
                y = x[i]['data']['name']
                drug_set.add(y)
            except:
                continue
        drug_list = list(drug_set)
        drug_list.sort()
        df = pd.DataFrame(drug_list, columns=['drug'])

    return df


def get_data_fields(url, parameters):
    import os
    import requests
    with requests.Session() as s:
        r = s.get(url, params=parameters).json()
    x = r.keys()
    df = pd.DataFrame(x, columns=[''])

    return df


def get_drug_ae(url, drug_list, parameters):
    drug_name = []
    ae_list = []
    for drug in tqdm.tqdm(drug_list):
        parameters['drugs'] = drug

        with requests.Session() as s:
            try:
                r = s.get(url, params=parameters, stream=True).json()['facets']
                x = r['effects']['children']
                for i in range(len(x)):
                    y = x[i]['data']['name']
                    ae_list.append(y)
                    drug_name.append(drug)
            except:
                ae_list.append(None)
                drug_name.append(drug)

    df = pd.DataFrame(list(zip(drug_name, ae_list)), columns=['drug_name', 'ae'])

    return df


def get_facet_fields(url, parameters):
    import os
    import requests
    with requests.Session() as s:
        r = s.get(url, params=parameters, stream=True).json()
    df = pd.DataFrame(r, columns=['facet_fields'])

    return df


def extract_values(obj, key):
    """Recursively pull values of specified key from nested JSON."""
    arr = []

    def extract(obj, arr, key):
        """Return all matching values in an object."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    extract(v, arr, key)
                elif k == key:
                    arr.append(v)
        elif isinstance(obj, list):
            for item in obj:
                extract(item, arr, key)
        return arr

    results = extract(obj, arr, key)
    return results


def get_pk_params(url, parameters):
    # url = 'https://api.elsevier.com/pharma/pk/search'
    pk_param_list = []
    with requests.Session() as s:
        r = s.get(url, params=parameters, stream=True).json()['facets']
        x = r['parameters']['children']
        for i in range(len(x)):
            y = x[i]['data']['name']
            pk_param_list.append(y)
    df = pd.DataFrame(pk_param_list, columns=['pk_parameters'])

    return df


def make_list_variable(field_lst):
    from collections import OrderedDict

    field_dict = OrderedDict.fromkeys(field_lst)
    for field in field_lst:
        field_dict[field] = []

    return field_dict


def get_PK_data(url, drugList, field_list, pk_param_list, parameters):
    import time
    field_dict = make_list_variable(field_list)

    with requests.Session() as s:
        for drug in tqdm.tqdm(drugList):
            parameters["drugs"] = drug
            parameters["displayColumns"] = str(",".join(field_list))
            r = s.get(url, params=parameters, stream=False).json()
            hits = r['data']['countTotal']
            parameters["limitation.count"] = 1
            parameters["limitation.count"] = 500
            lim = math.ceil(hits / parameters["limitation.count"])

            for j in range(lim):
                parameters["limitation.firstRow"] = j * parameters["limitation.count"]
                r = s.get(url, params=parameters, stream=True).json()
                x = r['data']['items']
                try:
                    len(x)
                except:
                    continue
                for i in range(len(x)):
                    if x[i]['parameter'] in pk_param_list:
                        for field in [*field_dict.keys()]:
                            y = x[i].get(field, None)
                            field_dict[field].append(y)
                    else:
                        continue
                time.sleep(0.25)

        df = pd.DataFrame(list(zip(*field_dict.values())),
                          columns=field_list)

        return df


def get_drug_aes_faers(url, drug_list, parameters):
    ae_list = []
    count_lst = []
    drugLst = []
    leaf_list = []
    with requests.Session() as s:
        for drug in tqdm.tqdm(drug_list):
            parameters['drugs']=drug
            # drugLst.append(drug)
            r = s.get(url, params=parameters, stream=True).json()['facets']
            x = r['effects']['children']
            print(len(x))
            # pprint.pprint(x)

            for i in range(len(x)):
                # print(x[1])
                ae = x[i]['data'].get('name', None)
                # leaf = x[i]['data'].get('isLeaf', None)
                ae_list.append(ae)
                count = x[i]['data'].get('count', None)
                count_lst.append(count)
                drugLst.append(drug)
                # leaf_list.append(leaf)

    df = pd.DataFrame(zip(drugLst, ae_list, count_lst), columns=['drug', 'ae', 'count'])

    return df
