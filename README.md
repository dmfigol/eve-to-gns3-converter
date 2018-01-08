# EVE-NG to GNS3 topology converter
This script converts network topologies created in [EVE-NG](http://www.eve-ng.net) to [GNS3](https://www.gns3.com) format.  

Coding of this project was live streamed on [https://twitch.tv/dmfigol](https://twitch.tv/dmfigol)  
Recordings are posted on my [YouTube channel](https://www.youtube.com/channel/UCS8yWZCX-fdxft8yFAffZCg)

To run the script, you will need to have Python 3.6+ installed.  
Dependencies are listed in **requirements.txt**. You can install them using:  
`pip3 install -r requirements.txt`  

### How to use the script
```
python3 eve-to-gns3-converter.py [-h] (-f SRC_TOPOLOGY_FILE | -s SRC_DIR)
                                 [-d DST_DIR] [-c CONSOLE_START_PORT]
                                 [--l2_iol_image L2_IOL_IMAGE]
                                 [--l3_iol_image L3_IOL_IMAGE]
```
Example:
`python3 eve-to-gns3-converter.py -s src/ -d dst/`

#### Arguments:  
* **-f, --src_topology_file** specifies a single **.unl* file you would like to convert  
Alternatively, use:  
* **-s, --src_dir** specifies a source directory containing **.unl* files. This directory is scanned recursively and all found **.unl* files will be converted.  

Either **--src_topology_file** or **--src_dir** *must* be specified.  
* **-d, --dst_dir** specifies destination folder. This is where the script will put generated GNS3 topologies. Default is **dst/**
* **-c, --console_start_port** specifies the first port for the console in GNS3. Default is 5000.
* **--l2_iol_image** specifies an L2 IOL image path in GNS3 if differs from EVE-NG.
* **--l3_iol_image** specifies an L3 IOL image path in GNS3 if differs from EVE-NG

Two options above may be useful if IOL images are named differently in EVE-NG and GNS3 or if completely different versions are imported in these two emulators.  
This is implemented only for IOL. In future, there will be support of a mapping file, where you could specify mapping of image path/name in EVE-NG and corresponding image path/name in GNS3. Check #3

If the script does not work/crashes, please raise an issue.