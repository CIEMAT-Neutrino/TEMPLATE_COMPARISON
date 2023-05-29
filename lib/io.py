import os
import uproot
import numpy as np
import plotly.express as px
from .wvf import convert_sampling_rate, apply_smoothing
from itertools import product

def import_templates(template_path,these_types=[],pretrigger=100,sampling=4e-9,convert_sampling=False,new_sampling=16e-9,wvf_length=None,same_length=True,debug=False):
    '''
    .git/CIEMAT/templates/
    template_path: path to the templates folder
    sampling: sampling rate of the templates
    wvf_length: desired length of the templates
    same_length: if True, all templates will be padded with zeros to match the length of the longest template or the desired length
    debug: if True, print debug information
    '''
    # Initialize variables
    template_dict_list = []
    this_wvf = []
    max_length = 0

    # Load templates' folder
    templates_model = os.listdir(template_path)
    if debug: print(templates_model)
    
    # Load templates' model folder
    for model_folder in templates_model:
        if debug: print("Loading model: {}".format(model_folder))
        
        if these_types != []:
            types = these_types
        else:
            types = os.listdir(template_path+model_folder+"/")
        
        # Load templates' type folder
        for type_folder in types:
            templates = os.listdir(template_path+model_folder+"/"+type_folder+"/")
            
            # Load templates
            for template in templates:
                # Get template type from folder name and ov from file name
                if type_folder == "LASER": wvf_type = "LASER"
                elif type_folder == "SCINT": wvf_type = "SCINT"
                elif type_folder == "SPE": wvf_type = "SPE"
                elif type_folder == "NOISE": wvf_type = "NOISE"
                elif type_folder == "TEMPLATE": wvf_type = "TEMPLATE"
                else: wvf_type = "UNKNOWN"
                if debug: print("Loading type: {}".format(wvf_type))

                if "OV1" in template: ov = 1
                elif "OV2" in template: ov = 2
                elif "OV3" in template: ov = 3
                else: ov = 0
                
                # Load template
                short_wvf = read_file(template_path+model_folder+"/"+type_folder+"/"+template,debug=debug)
                if short_wvf is None: continue

                # Convert sampling rate
                if convert_sampling:
                    short_wvf = convert_sampling_rate(short_wvf, 1/sampling, 1/new_sampling, debug=debug)
                    sample = new_sampling
                else:
                    sample = sampling

                # Resize template
                this_wvf, max_length = resize_wvf(short_wvf, max_length, wvf_length, same_length, debug=debug)
                
                # Roll template peak to pretrigger length
                if np.argmax(this_wvf) != pretrigger:
                    if np.argmax(this_wvf) > pretrigger:
                        this_wvf = np.roll(this_wvf,pretrigger-np.argmax(this_wvf))
                    else:
                        this_wvf = np.concatenate((np.zeros(pretrigger-np.argmax(this_wvf)),this_wvf[:-pretrigger+np.argmax(this_wvf)]),axis=0)

                area = np.sum(this_wvf[this_wvf > 0])
                if debug: print('Loaded template %s OV %i int %f'%(model_folder,ov,area))
                
                # Create template dictionary
                template_dict = {"INST": "CIEMAT",
                                "NAME": template,
                                "MODEL": model_folder,
                                "TYPE": wvf_type,
                                "OV": ov,
                                "SAMPING": sample,
                                "AMP": np.max(this_wvf),
                                "INT": area,
                                "ADC":  this_wvf.tolist(),
                                "TIME": sample*np.arange(len(this_wvf))}
                # Append template dictionary to list
                template_dict_list.append(template_dict)
    print("Done!")
    return template_dict_list

def read_file(template,debug=False):
    if debug: print("Loading template: {}".format(template))
    if template.endswith(".txt"):
        short_wvf = np.loadtxt(template)
        return short_wvf
    
    elif template.endswith(".npz"):
        short_wvf = np.load(template, allow_pickle=True)["arr_0"][0]
        return short_wvf

    elif template.endswith(".root"):
        root_file = uproot.open(template)
        short_wvf = root_file[root_file.keys()[0]].to_numpy()[0]
        return short_wvf

    else:
        if debug: print("Unknown template format: {}".format(template)) 
        return None

def resize_wvf(short_wvf,max_length,wvf_length,same_length,debug=False):
    if same_length:
        if wvf_length is not None:
            if len(short_wvf) < wvf_length:
                this_wvf = np.concatenate((short_wvf,np.zeros(wvf_length-len(short_wvf))))
                max_length = wvf_length
            else:
                this_wvf = short_wvf[:wvf_length]
                max_length = len(this_wvf)
        else:
            if len(short_wvf) < max_length:
                this_wvf = np.concatenate((short_wvf,np.zeros(max_length-len(short_wvf))))
                max_length = len(this_wvf)
            else:
                this_wvf = short_wvf
            max_length = len(this_wvf)
    else:
        this_wvf = short_wvf
        max_length = len(this_wvf)
    
    return this_wvf, max_length

def generate_templates(df,sampling,new_sampling,main_folder,type_folder,models,ovs,max_length,save=True,debug=False):
    templates = []
    for ov,model in product(ovs,models):
        laser = df[(df["OV"] == ov) & (df["MODEL"] == model) & (df["TYPE"] == "LASER")]["ADC"].values[0]
        spe= df[(df["OV"] == ov) & (df["MODEL"] == model) & (df["TYPE"] == "SPE")]["ADC"].values[0]

        template = np.asarray(laser)*np.max(spe)/np.max(laser)
        if new_sampling != sampling:
            template = convert_sampling_rate(template, 1/sampling, 1/new_sampling, debug=False)
            sample = new_sampling
        else:
            sample = sampling

        template = template[np.argmax(template)-10:]
        templates.append({
            "INST": df["INST"].values[0],
            "NAME": "%s_SPE_CAEN_OV%i"%(model,ov),
            "MODEL": model,
            "TYPE": "TEMPLATE",
            "OV": ov,
            "SAMPING": sample,
            "AMP": np.max(template),
            "INT": np.sum(template[template > 0]),
            "ADC": template[:max_length],
            "TIME": sample*np.arange(max_length)
        })

        if  debug: px.line(x=sample*np.arange(max_length),y=template[:max_length]).show()
        if save:
            try:
                np.savetxt("wvfs/%s/%s/%s/%s_SPE_CAEN_OV%i.txt"%(main_folder,model,type_folder,model,ov), template[:max_length])
            except FileNotFoundError:
                os.makedirs("wvfs/%s/%s/%s/"%(main_folder,model,type_folder))
                np.savetxt("wvfs/%s/%s/%s/%s_SPE_CAEN_OV%i.txt"%(main_folder,model,type_folder,model,ov), template[:max_length])
    return templates