from dataclasses import dataclass
import cv_viewer.labels as labels
import json
import numpy as np
import ast

@dataclass
class ObjectsOutput:
    nObjects: str
    objects: list


@dataclass
class ObjectOutput:
    label : str
    #height: list # [x, y, z]
    #weight: list # [x, y, z]
    position: list# [x, y, z]
    dimensions: list # [width, height, length]


def write_json(obj_output) : 
    with open("data.txt", "w")  as f : 
        #json.dump(obj_output.__dict__, f)
        f.write(str(obj_output.__dict__))
        f.write('\n')
        f.close()

def retrieve_data(objects, label) : 
    #if len(objects.object_list) == 0 : return
    objects_out = []
    for obj in objects:    
        print(obj.raw_label, "et",label)

        if obj.raw_label != label: continue
        if len(obj.bounding_box) == 0 : continue  
        if np.isnan(obj.position).any(): continue
     
        #height = list(obj.bounding_box[0] - obj.bounding_box[4])
        #weight = list(obj.bounding_box[3] - obj.bounding_box[0])
        position = list(obj.position)
        label = labels.labelDict[int(obj.raw_label)] 
        dimensions = list(obj.dimensions)
        
        obj_output = ObjectOutput(label=label, position=position, dimensions=dimensions) 
        objects_out.append(obj_output)  
    
    objs_output = ObjectsOutput(nObjects=len(objects), objects=objects_out) 
    write_json(objs_output)  


def get_z_values(n:int):
    # Liste pour stocker les valeurs z
    z_values = []
    
    # Ouvre le fichier en mode lecture
    with open("data.txt", "r") as f: 
        for line in f:
            line = line.replace("ObjectOutput(", "{").replace(")", "}")
            line = line.replace("label=", "'label':").replace("position=", "'position':").replace("dimensions=", "'dimensions':")
            if '}{' in line:  # Si il y a plusieurs objets dans une ligne
                line = line.replace('}{', '},{')  # Ajouter une virgule entre les objets
                

                # Convertir la ligne en dictionnaire
            data_list = ast.literal_eval(line.strip())
            
            if isinstance(data_list, list):
                for data in data_list:                        # Vérifier si le nombre d'objets est supérieur à 0
                    if isinstance(data, dict) and 'nObjects' in data and data['nObjects'] > 0:
                        # Récupérer les objets
                        objects = data['objects']
                        for obj in objects:
                            # Récupérer la position et la valeur z                                position = obj['position']
                            z = position[n] 
                            z_values.append(z)
            else:
                    # Si le résultat n'est pas une liste, traiter comme un seul dictionnaire
                if isinstance(data_list, dict) and 'nObjects' in data_list and data_list['nObjects'] > 0:
                    objects = data_list['objects']
                    for obj in objects:
                        position = obj['position']
                        z = position[n]
                        z_values.append(z)

    return z_values
        
def get_distance(n:int):
    z_values = get_z_values(n)
    first_average = sum(z_values) / len(z_values)
    true_z_values = []
    for val in z_values:
        if (val < first_average + 0.3) and (val > first_average - 0.3):
            true_z_values.append(val)
        
    if len(true_z_values) == 0:  # Vérifier si la liste z_values est vide
        return None
    true_average = sum(true_z_values) / len(true_z_values)
    print("x" if n == 0 else "y" if n == 1 else "z" if n == 2 else "error")
    print("True Average: ", true_average)
    return true_average

        