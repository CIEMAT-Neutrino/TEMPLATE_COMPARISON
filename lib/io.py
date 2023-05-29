import os
import uproot
import numpy as np
from .wvf import convert_sampling_rate, apply_smoothing

def import_templates(template_path,pretrigger=100,sampling=1/4e-9,convert_sampling=False,new_sampling=1/16e-9,wvf_length=None,same_length=True,debug=False):
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
        templates_type = os.listdir(template_path+model_folder+"/")
        
        # Load templates' type folder
        for type_folder in templates_type:
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
                    short_wvf = convert_sampling_rate(short_wvf, sampling, new_sampling, debug=debug)
                
                # Resize template
                this_wvf, max_length = resize_wvf(short_wvf, max_length, wvf_length, same_length, debug=debug)
                
                # Roll template peak to pretrigger length
                if np.argmax(this_wvf) != pretrigger:
                    this_wvf = np.roll(this_wvf,pretrigger-np.argmax(this_wvf))
                    print('This template %s OV %i int %f'%(model_folder,ov,np.sum(this_wvf[this_wvf > 0])))
                
                # Create template dictionary
                template_dict = {"INST": "CIEMAT",
                                "NAME": template,
                                "MODEL": model_folder,
                                "OV": ov,
                                "AMP": np.max(this_wvf),
                                "TYPE": wvf_type,
                                "ADC":  this_wvf.tolist(),
                                "TIME": 16e-9*np.arange(len(this_wvf))}
                # Append template dictionary to list
                template_dict_list.append(template_dict)
    
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