import Levenshtein

#take the keys file which is a data dump from BQ
#and map to the markers file using a string compare measure
biorna_markers=[]
biorna_mappings={}
with open('c:\\Users\\tihor\\Downloads\\Biorna_Markers.txt') as fp:
    for line in fp:
        biorna_markers.append(line.strip())

with open('c:\\Users\\tihor\\Downloads\\CMAP_Markers.txt') as fp:
    for line in fp:
        marker=line.strip()
        max_ratio=-1.0
        for item in biorna_markers:
            ratio=Levenshtein.ratio(item.lower(),marker.lower())
            if ratio>max_ratio:
                max_ratio=ratio
                biorna_mappings[marker]=item
with open('lab_to_internal_mapping_CMEP.json','w') as output_file:
    for key in biorna_mappings:
        print(key,biorna_mappings[key])
        output_file.write('{"LabName":"'+key+'","InternalName":"'+biorna_mappings[key]+'"}\n')