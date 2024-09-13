# DCS Data Catalog

This repository contains some of the core 3rd party dependencies for the DSC Tosca project. 
 - geonode
 - geoserver
 - geoserver-data

The 3rd party dependencies are being adjusted, configured and extended to meet the requirements of the DSC Tosca project. They are being packaged as docker images and published to the Github Container Registry.

## Workflow
The images are being built and published to the Github Container Registry using Github Actions. The workflow is defined in the `.github/workflows` directory.

### Geonode

### Geoserver

### Geoserver Data

docker compose -f docker-compose-dev.yml build --no-cache
docker compose -f docker-compose-dev.yml up -d

## NOTES

- admin selection staff member icin gorulmuyor. onu kontrol edip eger kullanici staff sa onu gosterelim

2 tane post endpoint senaryomuz var
1- rating   >> sadece rating olursa geometrisini backend olusturalim. 
2- rating feat feedback form

- endate bugun olmamali. bundan buyuk olmali.
- enddate i bugunden buyuk olanlari doneceez. start_date de bugun yada bugunden kucukleri donmek lazim. 
- active diye bir default column ekleyip endate de sonra deactive yapabiliriz.
- campaign de enddate dolduysa hata donmek lazim. nice to have
