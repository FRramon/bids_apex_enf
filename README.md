# **APEX Enfant**

# **Compte rendu construction base BIDS**

François Ramon & Belen Azofra  
---

**Objectif :** Création d’une base de données IRM respectant le formalisme BIDS pour le groupe enfant de l’étude APEX.

**Outils :**   
BIDS Website : [https://bids.neuroimaging.io/](https://bids.neuroimaging.io/)  
dcm2niix: [https://github.com/rordenlab/dcm2niix](https://github.com/rordenlab/dcm2niix)  
dicm2nii: [https://github.com/xiangruili/dicm2nii](https://github.com/xiangruili/dicm2nii)  
bidscoin : [https://bidscoin.readthedocs.io/en/latest/preparation.html](https://bidscoin.readthedocs.io/en/latest/preparation.html)

Les codes de conversion : [https://github.com/FRramon/bids\_apex\_enf](https://github.com/FRramon/bids_apex_enf)

**Versions logiciels/paquets:**

- bidscoin 4.4.0  
- dcm2niix :Chris Rorden's dcm2niiX version v1.0.20240202  (JP2:OpenJPEG) (JP-LS:CharLS) Clang14.0.3 ARM (64-bit MacOS) v1.0.20240202  
- dicm2nii: v2023.02.23  
- python 3.11.5  
- Matlab R2024b

**Liste des scripts python** 

- 1\_sort\_sequences.py  
- 2\_create\_raw\_structure.py  
- 3\_copysource\_data.py  
- 4\_convert\_dot\_stop.py  
- 5\_correct\_runs\_enrich\_json.py  
- 6\_rename\_participants.py  
- bidsmap.yaml 

## **Table des matières** 

[**I. Définition des sujets : 1\_sort\_sequences.py	2**](#définition-des-sujets-:-1_sort_sequences.py)

[**II. Création d’une structure brute 2\_create\_raw\_structure.py	3**](#création-d’une-structure-brute-2_create_raw_structure.py)

[**III. Création de source\_data et conversion BIDS : 3\_copysource\_data.py	5**](#création-de-source_data-et-conversion-bids-:-3_copysource_data.py)

[**IV. Conversion des DOT et STOP 4\_convert\_dot\_stop	8**](#conversion-des-dot-et-stop-4_convert_dot_stop)

[**V. Définition des champs Json \- “json enrichment” 5\_correct\_runs\_enrich\_json.py	10**](#définition-des-champs-json---“json-enrichment”-5_correct_runs_enrich_json.py)

[**VI. Renommer les participants : 6\_rename\_participants.py	12**](#renommer-les-participants-:-6_rename_participants.py)

[**VII. Résumé des séquences : 7\_sequences\_table.py	13**](#heading=h.b0il2tis9pr)

## **DESCRIPTION GENERALE**

Conversion d’une base de données IRM brute avec acquisition au format Philips REC/PAR, en base BIDS avec images au format nii.gz / json.

1. # **Définition des sujets : 1\_sort\_sequences.py** {#définition-des-sujets-:-1_sort_sequences.py}

## **DESCRIPTION** 

Récupération d’un **dossier “sub-enf”** contenant des sous dossiers appelé par les noms apex (adoci002, etc),  et contenant une acquisition particulière ex:

sub-enfca101\_ses-post\_mri-1457529310-1-01VALAL-3DT1-3-1  
|---  1-01VALAL-3DT1.PAR  
|--- 1-01VALAL-3DT1.REC

**Nature des données :** Fichiers REC/PAR. 

Pour chaque fichier PAR dans sub-enf, lecture des métadonnées du fichier et écriture dans un csv de :

- *protocol name*  
- *patient name*  
- *StudyDate*		  
- *StudyTime*

Les patients names sont par exemple : 1-01VALAL, 2-08MORJU …

**On n’utilise à aucun moment le nom du dossier ou le nom de fichier.** Une vérification préalable des métadonnées DICOM a montré que les DICOM présents dans /source/sub-enf existent au format REC/PAR dans le même dossier. **La conversion de la base de données ne se fait donc qu’à partir des données REC/PAR**.

## **LISTE DES VARIABLES**

*source\_dir :* pointe vers source/sub-enf  
*docs\_dir* : pointe vers un dossier recevant les csv

## **OPTIONS**

| Bool option | Default | Description |
| :---- | ----- | :---- |
| *sortsequences* | True | Identifier si un id de participant est associé à plusieurs “patient\_name”  |
| *delete\_change* | True | Supprime les données copiées en 2024 du répertoire sub-enf (pare feu copies) |

2. # **Création d’une structure brute 2\_create\_raw\_structure.py** {#création-d’une-structure-brute-2_create_raw_structure.py}

## **DESCRIPTION** 

La première étape est la **correction des noms** : mauvaise orthographe, majuscule, point, de manière à suivre cette syntaxe :

* Premier caractère \= appartenance au groupe i  
* tiret  
* deux chiffres : numéro de sujet au sein du groupe  
* Cinq lettres : identifiant sujet

*Ex : 1.01 VALAL devient : 1-01VALAL*

**Cas particulier :** quelques renommages manuels dans le code

| Nom incorrect | Nom correct |
| :---: | :---: |
| *1.06gcema* | 1-06GUEMA |
| *1-43HIUEMA* | 1-43HUEMA |
| 2-010CHAPA | 2-10CHAPA |
| *apex027* | 2-09MORJU |
| *4-06MALAX* | 4-06HALAX |

Pour chaque sujet unique identifié dans le champ “patient name” :  
	•	**Création d’un dossier** portant le nom du patient.  
	•	Dans ce dossier, création d’un **fichier csv** regroupant l’adresse de chaque fichier PAR/REC pour lequel “patient name” correspond au nom du patient, ainsi que les colonnes suivantes : protocol name, StudyDate, et StudyTime.  
Dans le csv ainsi généré pour chaque dossier patient :

- Identification des dates uniques et **comptage des acquisitions** pour chaque date.  
- En général, le **nombre de dates uniques correspond au nombre de sessions** (pré, post, post diff). Ces sessions sont temporairement nommées 1, 2, et 3\.  
- Un cas particulier a été rencontré : un sujet avait 4 sessions uniques (4VALMA) car une acquisition T1 post avait été refaite (confirmation dans le cahier d’acquisition). D’autres sujets présentaient des incohérences, comme des sessions inexistantes (par exemple, 3 dates uniques, mais une seule acquisition pour l’une des dates). Ces problèmes ont été résolus individuellement.

Une fois les “vraies” sessions identifiées, elles ont été nommées **ses-00, session ses-01, et ses-02, par ordre de date croissante**.

*Règles de renommage des sessions **1,2, 3 en pré, post, postdiff:*** 

- La session 0 est toujours pré  
- La session 1 peut être post, ou postdiff, cela à été décidé s' il y avait un écart  \>45j entre ses-00 et ses-01.  
- Si il y a trois sessions c’est forcément pré/post/post/diff  
- Si il n’y a qu’une session : c’est forcément pré

Dans chaque dossier sujet, **on trouve les sous-dossiers ses-pre, ses-post, et ses-postdiff** si les acquisitions correspondantes ont eu lieu. Un **fichier csv** est également créé dans chaque dossier de session, contenant les fichiers REC/PAR associés à ce sujet et à cette session, ainsi que le nom de chaque fichier.  
Un fichier **CSV récapitulatif** est généré dans le répertoire /docs, résumant les acquisitions trouvées pour chaque participant et chaque session.

## **LISTE DES VARIABLES** 

*raw\_structure\_dir* : pointe vers un dossier recevant la structure brute  
*docs\_dir* : pointe vers le dossier contenant les csv de séquences

## **OPTIONS** 

| Bool option | Default | Description |
| :---- | ----- | :---- |
| *checkdoubles* | False | Identifier si un id de participant est associé à plusieurs “patient\_name”  |
| *correctNames* | True | Corriger les noms de sujets. Pour la nomenclature type 1-01VALAL  |
| *getSequences\_persubject* | True | identifier le nombre de sessions |
| *createSes* | True | Attribuer un nom de session (pre/post/postdiff) à la place de ses-00,ses-01,ses-02 |
| *rename\_session* | True | Copier bidsmap depuis code dir dans rawdata/code/bidsoin et exécution de bidscoin |
| *createSes\_seq* | True | Renommer sequence\_ses-.csv en suivant le nouveau nom de session |
| *createSummary* | True | Création d’un csv regroupant les aquisitions REC/PAR présentes pour chaque sujet/session  |

3. # **Création de source\_data et conversion BIDS : 3\_copysource\_data.py** {#création-de-source_data-et-conversion-bids-:-3_copysource_data.py}

## **DESCRIPTION** 

La première étape consiste à **copier les données REC/PAR** dans un nouveau répertoire source\_data. La structure de ce répertoire est créée en suivant la structure brute précédemment définie. Les fichiers REC/PAR identifiés dans chaque **fichier sequences.csv** sont ensuite copiés dans les dossiers correspondants.

*Exemple de répertoire source :*   
 *subject\_id/*  
*|-- ses-id/*  
    *|-- 3DT1.PAR*  
    *|-- DWI.PAR*  
    *|-- 3DT1.REC*  
    *|-- DWI.REC*

Deuxième étape : Renommer les participants. **Ajout du préfixe “sub-”** et suppression du tiret dans leur identifiant.

*Exemple : 1-01VALAL devient sub-101VALAL.*

Si deux fichiers ayant le même nom sont destinés au même répertoire. Alors soit:

- les deux fichiers REC/PAR ont la même taille et donc ce sont des doublons : on en copie un des deux  
- Les fichiers n’ont pas la même taille. Après vérification, le fichier le plus léger n’est pas convertible avec dcm2niix (sûrement erreur de transfert) : On copie le fichier le plus lourd.  
- Cas particulier à 434 et 431, des fichiers DBIEX.PAR/REC correspondent en terme de meta données et donc sont ajouté à source data, mais ce sont des fichiers dédoublés. Donc ils ne sont pas copiés dans source data.  
- Cas particulier pour 204HEBTO. Des fichiers DBIEX existent mais ne sont pas tous des doublons. Une copie de ces données à été faite dans le script à part.

**Troisième étape : Conversion BIDS**. La conversion des données REC/PAR est effectuée avec le logiciel bidscoin. De la même manière que heudiconv, ce logiciel interface dcm2niix (version \= 20242202). **Bidscoin, contrairement à heudiconv, est adapté pour la conversion de données REC/PAR en nifti.**   
**![][image1]**  
source **: [https://bidscoin.readthedocs.io/en/latest/workflow.html](https://bidscoin.readthedocs.io/en/latest/workflow.html)**

**Utilisation :** *bidsmapper, bidseditor, bidscoiner*

L'équivalent de l’heuristique d’heudiconv est la bidsmap avec bidscoin. elle est écrite au format yaml, en suivant les règles suivantes : 

**Une T1 peut s’appeler :**

* 3DT1-\*-1.PAR  
* 3DT1-\*-1\_run-\*.PAR

**Et DOIT contenir les champs :**      

* protocol\_name: 3DT1  
* tech: T1TFE  
* scan\_mode: 3D

**NOM BIDS :** anat/sub-\*\_ses-\*\_T1w.nii.gz

**Une T2\* peut s’appeler:**

* T2GREph-SENSE-\*-1.PAR  
* T2GREph-\*-1.PAR 

**Et DOIT contenir les champs :**      

* protocol\_name: T2GREph  
* series\_type: Image   MRSERIES  
* tech: FFE

**NOM BIDS** : anat/sub-\*\_ses-\*\_T2starw.\[nii.gz/json\] & sub-\*\_ses-\*\_part-phase\_T2starw.\[nii.gz/json\]

**Un resting state multi echo peut s’appeler :**

* rs-multi-echo-SENSE-\*-1.PAR  
* rs-multi-echo-\*-1.PAR 

**et DOIT contenir les champs :**      

* protocol\_name: rs\_multi\_echo SENSE  
* tech: FEEPI  
* diffusion: '0'  
* scan\_mode: MS

**NOM BIDS :** func/sub-\*\_ses-\*\_task-rest\_echo-\*\_bold.\[nii.gz/json\]

**Une DWI PA peut s’appeler :**

* WIP-DTI2-3-SENSE-\*-1\_run-\*.PAR  
* WIP-DTI2-3-SENSE-\*-1.PAR   
* DTI2-3-ok-\*-1.PAR  
* DTI2-3-alt-\*-1.PAR 

**et DOIT contenir les champs :**      

* protocol\_name: DTI2-3-alt  
* tech: DwiSE  
* scan\_mode: MS  
* flow\_compensation: '0'  
* max\_echoes: '1'

**NOM BIDS** : dwi/sub-\*\_ses-\*\_acq-64dirs\_dir-PA\_dwi.\[nii.gz/json/bval/bvec\]

**Une carte de champs peut s’appeler**

* WIP-B0MAP-\*-1\_run-\*.PAR,   
* WIP-B0MAP-\*-1.PAR

**Et DOIT contenir les champs :**      

*      protocol\_name: WIP B0MAP  
*      tech: T1FFE  
*      diffusion: '0'  
*      scan\_mode: MS  
*      max\_slices: '35'  
*      flow\_compensation: '1'  
* max\_echoes: '1'

**NOM BIDS :** fmap/sub-\*\_ses-\*\_\[phase1/magnitude1\].\[[nii.gz/json](http://nii.gz/json)\]

**Une DWI AP peut s’appeler :**  
DTI2-3-alt-topup-\*-1.PAR  
**et DOIT contenir les champs :**      

*       protocol\_name: DTI2-3-alt-topup  
*       tech: DwiSE  
*       scan\_resolution: '\[128 128\]'  
*       scan\_mode: MS  
*       flow\_compensation: '0'

**NOM BIDS** : fmapi/sub-\*\_ses-\*\_acq-6dirs\_dir-AP\_epi.\[nii.gz/json/bval/bvec\]

## **LISTE DES VARIABLES DE 3\_copysource\_data.py**

*code\_dir* : pointe vers le dossier code où sont les scripts 1,2, …, 7 et bidsmap.yaml  
*base\_dir* : pointe vers le dossier apex\_enf (parent de rawdata, sub-enf etc)  
*source\_data\_dir* : pointe vers le dossier source\_data (fils de base\_dir)  
*raw\_patient\_dir* : pointe vers le dossier raw\_structure  
*raw\_source\_dir* : pointe vers le dossier sub-enf

## **OPTIONS  DE 3\_copysource\_data.py**

| Bool option | Default | Description |
| :---- | ----- | :---- |
| *copysource* | True | copie des source data dans un répertoire source\_data |
| *correct\_name* | True | Correction des noms en sub-  etc  |
| *get\_unique\_sequences* | False | Génère les noms uniques de séquences, pour la définition de bidsmap.yaml  |
| *add\_run\_label* | True | Ajout d’un suffixe run dans les REC/PAR  |
| *run\_bidscoin* | True | Copie de bidsmap depuis code dir dans rawdata/code/bidsoin et exécution de bidscoin |

4. # **Conversion des DOT et STOP 4\_convert\_dot\_stop** {#conversion-des-dot-et-stop-4_convert_dot_stop}

## **DESCRIPTION**

La conversion échoue dans la plupart des cas pour les données IRM d’activation sur les tâches dot et stop.

**Identification du problème**  
La séquence décrite dans le protocole dure 277 secondes. Cependant, **ce paramètre n’est pas ajusté à l’enregistrement, car la séquence est généralement arrêtée avant la fin**. D’après les cahiers d’acquisition, les participants mettent en effet moins de 277 secondes pour exécuter la tâche.  
Les outils dcm2niix, dicomifier, et mrconvert échouent tous à convertir les données, car **le nombre d’images n’est pas proportionnel au nombre de coupe**s. Un autre problème identifié est l’arrêt brutal de la séquence, entraînant un dernier volume tronqué. En revanche, dicm2nii, implémenté en matlab, parvient à convertir ces données. Après conversion, on obtient n-1 volumes par rapport au cahier d’acquisition, car **dicm2nii exclut le volume tronqué**.  
Une interface MATLAB avec Python (**Matlab Engine**) a été mise en place pour exécuter **dicm2nii sur les tâches dot et stop** :

**Étape 1 :** Conversion des données PAR en NIfTI  
Pour chaque tâche (DOT et STOP), on identifie si le participant a reçu un ou plusieurs fichiers IRM liés à la tâche.

- Si deux fichiers PAR sont présents, les deux sont convertis et nommés run-1 et run-2.  
- Sinon, l’unique fichier IRM est converti avec dicm2nii.

**Nom BIDS**  
Les fichiers convertis respectent la nomenclature suivante :

- func/sub-/ses-/sub-\_ses-\_task-dot\_bold.nii.gz  
- func/sub-/ses-/sub-\_ses-\_task-stop\_bold.nii.gz

**Création du fichier compagnon au format JSON**  
dicm2nii génère un fichier .mat contenant les métadonnées de l’acquisition. Ce fichier est ensuite converti au format JSON. Finalement, tous les fichiers NIfTI et JSON sont copiés dans les dossiers func

La présence de deux acquisitions IRM pour une même tâche **s’explique toujours par l’une des deux acquisitions étant fortement tronquée** (arrêt prématuré ou redémarrage de la séquence). En cas de doublons, **l’image NIfTI contenant le plus grand nombre de volumes 3D est conservée**, et l’autre acquisition est supprimée.

**Note :** Matlab et dicm2nii sont donc requis pour cette étape.  
**Note 2 :** pour 2-03VALMA/post, erreur de conversion du rs fMRI. dicm2nii peut convertir, mais alors il crée un nifti, au lieu de trois (un par echo). C’est aussi le cas pour 204HEBTO/postdiff.

## **LISTE DES VARIABLES**

*source\_data\_dir*: pointe vers le dossier source\_data  
*rawdata\_dir* : pointe vers le dossier rawdata

## **OPTIONS**

| Bool option | Default | Description |
| :---- | ----- | :---- |
| *convert\_dot\_stop* | True | Conversion des IRM d’activation dot/stop REC/PAR au format nifti \+ json |
| *correct\_runs* | True | Choix d’un des deux IRM d’activation selon le nombre de volumes 3D.  |

5. # **Définition des champs Json \- “json enrichment” 5\_correct\_runs\_enrich\_json.py** {#définition-des-champs-json---“json-enrichment”-5_correct_runs_enrich_json.py}

## **DESCRIPTION**

La conversion bidscoin, malgré les définitions de la bidsmap, échoue parfois à identifier **lorsque le suffixe run doit être ajouté**. Ainsi, pour la majorité de T2starw qui sont présentes deux fois, la deuxième conversion possède le suffixe run-2, mais le premier fichier s’appelle toujours sub-\*\_ses-\*\_T2starw.nii.gz. Pour chaque cas de figure où un fichier contenant ‘run-2’ est trouvé, et un fichier sans run, alors ce fichier est renommé avec le suffixe run-1. Cette anomalie s’est aussi retrouvée dans d’autres types d’acquisition.

La conversion avec bidscoin génère les **fichiers json** attendus par le format bids, mais peu de champs sont présents. Bidscoin génère un excel bidscoiner.tsv, contenant l’historique des commandes (conversion source → target)  
Pour chaque “target”, on identifie la source REC/PAR et avec un lecteur txt on crée un nouveau fichier json. On concatène ensuite le json issu de bidscoin et ce json, créant un json final complet. 

**Gestion des autres problèmes avec les indices “run”**

Une fois que les run 1 et run 2 ont été proprement renommés, il a fallu choisir de supprimer un des deux, ou de garder les deux.

Concernant les run-1/run-2 **DWI AP et DWI PA** . Cela concernent certains sujets pour lesquels il y a eu des erreurs de nommages (ex 1-06GUEMA s’appelait 1.06guema, ou 1 06GUEMA). Ce sont des doublons. On a supprimé un, et gardé l’autre sans le suffixe “run”.

Concernant les cartes de champs **b=0 (fmap)** : Nous avons, après inspection visuelle pour run-1\_magnitude/run-2\_magnitude, renommer run-1 en magnitude, run-2 en phase

Une grande partie des sujets ont deux T2\*, bien que les cahiers d'acquisition n’y fassent pas référence. Les enfants font parfois les acquisitions en deux temps, lorsqu'ils sont petits ou agités. La T2\* dédoublée est un indice disant que **le participant à réalisé ses acquisitions en deux temps (avec 30min de pause)**. Il y a deux T2\* pour recaler les images de la première partie des acquisitions avec les images de la deuxième partie. Il faut donc garder les deux. L’index run-1/run-2 a été défini en fonction de l’heure de passage.

Il n’y avait pas de répétition du resting state multi echo. Les répétitions des IRMf d’activation ont été traitées dans la partie précédente.

**Harmonisation des clés d’identification** entre les métadonnées issues des REC/PAR, dcm2niix et dicm2nii. Au cours de ce projet, différents convertisseurs et lecteurs de métadonnées ont été utilisés. Nous avons converti tous les champs DICOM pour que les clefs correspondent au formalisme BIDS.

La conversion des fieldmap avec bidscoin **ne crée pas de fichiers bval et bvec** (alors que si ces derniers sont compris dans /dwi si). Les fichiers sont donc créés avec dcm2niix puis copiés dans les bons répertoires.  
   
**Vérification finale**

Création d’un csv (check\_conversion.csv) retraçant toutes les acquisitions trouvées dans sourcedata, et leur conversion dans rawdata. Si un fichier existe dans sourcedata mais pas dans raw data ⇒ conversion error \= 1\.

Après vérification, nous avons utilisé dicm2nii pour convertir les fichiers sur lesquels dcm2niix échouait. Les resting state euvent être convertis mais les trois échos sont concaténés dans une seule image (vol 1 echo 1, vol 2 echo 2, vol 3 echo 3, vol 4 echo 1 etc …)  
Concernant:

* l’image DWI de sub-401GUERA/postdiff, dicm2nii échoue aussi. → Problème nb slices et dimensions images (not integer). **Pas de conversion**  
* l’image DWI AP de sub-523GUYPA/post, dicm2nii échoue aussi. → Problème nb slices et dimensions images (not integer). **Pas de conversion**

## **LISTE DES VARIABLES**

*source\_data\_dir*: pointe vers le dossier source\_data  
*rawdata\_dir* : pointe vers le dossier rawdata

## **OPTIONS**

| Bool option | Default | Description |
| :---- | ----- | :---- |
| *rename\_target* | True | Identifier des run-2 dans le fichier bidscoiner.tsv, et créer un run-1 |
| *enrich\_json* | True | Récupération des métadonnées REC/PAR et copie dans les json |
| *correct\_run\_time* | True | Corrige les identifiants de run pour les séquences sauf T2\* |
| *correct\_run\_time\_T2* | True | Renommer les numéro de run T2\* en fonction de l’heure/date d'acquisition |
| *change\_field\_json* | True | Harmoniser les clés d’identification entre les métadonnées issues des REC/PAR, dcm2niix et dicm2nii |
| *correct\_fmap\_epi* | True | Ajouter les bvec et bval des fmap epi |
| *generate\_conversion\_table* | True | Créer un tableau avec les résultats de conversion |
| *check\_conversion* | True | Check visuel pour chaque erreur de conversion trouvé dans conversion\_table. |

6. # **Renommer les participants : 6\_rename\_participants.py** {#renommer-les-participants-:-6_rename_participants.py}

## **DESCRIPTION**

Les noms des participants sont renommés pour correspondre à la table de correspondance ci-dessous :

| Préfixe original | Nouveau préfixe |
| :---- | :---- |
| 1 | ca1 |
| 2 | ci2 |
| 3 | mt3 |
| 4 | pc4 |
| 5 | prema5 |

*Par exemple : sub-107MAPSA devient sub-ca107*

Chacune des apparitions du terme sub-x est remplacé par son nouveau nom dans le répertoire rawdata, c'est à dire dans les noms de fichiers json, et nifti, ainsi que dans les fichiers scans.tsv, participants.tsv

## **LISTE DES VARIABLES**

*source\_data\_dir*: pointe vers le dossier source\_data  
*rawdata\_dir* : pointe vers le dossier rawdata

## **OPTIONS**

| Bool option | Default | Description |
| :---- | ----- | :---- |
| *rename\_participants* | True | Renommer toutes les occurences de l’ancienne nomenclature en nouvelle nomenclature. |
| *rename\_tsv* | True | Renommer les occurences dans les fichiers tsv de la base bids |
| *rename\_summary\_file* | True | add a column subject\_id\_bids in the check\_conversion.csv file |

**En bref :**   
De la structure brute \++ en entrée, le téléchargement de la bidsmap (bidsmap.yaml) et l'exécution un par un des codes contenue dans le repo github [https://github.com/FRramon/bids\_apex\_enf](https://github.com/FRramon/bids_apex_enf) permet d’obtenir la structure bids.

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAloAAADjCAYAAABdAbp+AABdMklEQVR4Xu2dB5gUxdaGzTnndM053WtOv9lrDpgwp2vOASUoCAIikhEVRRBQBEVBkiKSc86whGWXuLABdpfNAay/vxpOU1M9s9s9Oz3TPX3qed5nu6vjTp+q+qrqVNUu27ZtEwzDMAzDMEz82UWPYBiGYRiGYeIDCy2GYRiGYRiXYKHFMAzDMAzjEiy0GIZhGIZhXIKFFsMwDMMwjEuw0GIYhmEYhnEJFloMwzAMwzAuwUKLCWP79u2CA4e6Bt2uGEaH8xoOXgi6XboBCy0mDM78OMQj6HbFMDqc13DwQtDt0g1YaDFhcObHIR5BtyuG0eG8hoMXgm6XbsBCiwmDMz8O8Qi6XTGMDuc1HLwQdLt0AxZaTBic+XGIR9DtimF0OK/h4IWg26UbsNBiwuDMj0M8gm5XDKPDeQ0HLwTdLt2AhRYTBmd+HOIRdLtiGB3Oazh4Ieh26QYstJgwkpH5ffLJJ+LVV1/Vo2sMu+yyi5g+fboeLcOQIUNEly5d9GgZ0tLSxF577aVHBy70799fjBo1So+OW9DtimF0kpHXbNiwQey55556dI0B+cWECRP0aBmQhtq2batHy5CZmen4WX4N55xzjli8eLHc7tixY1zzlo8++khkZGTo0XELul26AQstJoxYMr/NmzeLww47TI+2HZCQnnnmGT26xgChNXr0aD1ahjfffFNccsklerQMS5YskdcGLVx44YVh+48//rho3bp1WFw8g25XDKMTS15TVFQk85rq6mr9kK2wfv16x+kfYmn48OF6tAxNmzYVp59+uh4tw6pVqxw/y6/hrLPOEjNnzpTbF1xwgWjTpo12hv1wwgkniLVr15r7BxxwgJg6dapyRnyDbpduwEKLCSOWzC+WzEsN8RZaNYWgCq2DDjpIj3I16HbFMDqx5DWo1CH9VlVV6YdshVjyqpqEVk0hqEKrrmHfffeVPQ+JCrpdugELLSaM2jK/b775Rhx66KFit912E3fddZeMQ2ZCXHbZZTLupptuUi8Tu+++u1i3bp3cRmZ53nnnyfPR5Pzuu++aQmvXXXcVy5cvN6977rnnxH//+19znwKubdWqlTj55JPlu1x77bXmu7do0SKslnnnnXfK5v9DDjlENG/ePCzzu/XWW8Uee+whhcjAgQNl3HvvvSe6du0qW4Fw7r///W/ZDXD++efL/Ysuusi8ftmyZeKII46Q8XiPRx991DyG527dulWcffbZ8jgyo8LCQvO4Glq2bClr6vidrr76ahmHex911FHi9ttvl9evXLlSxt9///1iv/32k+992223mfdAC9XBBx8sz8X/89VXX8n4c8891/w+9Lu8/vrr8nei8NRTT8lrcA7+z02bNsl4/KaI+/zzz8WBBx4of8dXXnnFvC5a0O2KYXRqy2uQVmFzsL+nn35axpEdA+QhCEgD3333nXnd22+/LR588EFz/7777hP77LOPtG81/V966aWid+/e5nnInxo2bGjuU4DQQl5z6qmnyvzpqquuMlvUOnXqJNM/hXvuuUfsvffeMh3qeQ2OIc2ihaZv374yDuegqw15Cu6N/wl5DfIcynsowCXi8MMPl/FIh6+99pp57LHHHpPvT2kd6XzLli3mcQpr1qwRxx13nDwHec0VV1xhHmvfvr1sibr88svl8RNPPFFs3LjRPL7//vvL3wdCCCBPoKAKLeTpH3/8sXns+uuvN/PYdu3ayTj8X/id8Jzjjz9ezJkzR8YjX1O/MQKupa5bCOx7771XPh/vj9+trKxMHsPfa665RrbW4xp8AzuVcd0u3YCFFhNGbZkfjD83NzcsLlIt8brrrgvbx/HVq1fL7f/7v/8zM050BSAjI6H10EMPmZndP//8I44++mjpV6EH3A8ZAt4Z4bTTThPdu3eX282aNZMCBQEZGm0jXHnllea7Tp482fLeCG+99ZZ8J8pkICxVv65jjz1W/PLLL+Y+BbwLEj9dB4GEDL6kpETuQ9Th/9MDMihkshR++ukn+Xfp0qXy/bp162Ye++CDD2TTPAUUKIjTAzJr9X/TW7Qglpo0aSK3IdDU3wiiD787fn/8T7gPfR9k3tivzU50u2IYndpsCHZWUVERFhepRevmm2+WFUAKb7zxhrjlllvk9u+//y4LbwqoAFK6wDGIHgrITyIF5AWodNEzISQ6dOggtyFOUKgjIE9A4U4BeSA9C0IiUl6Drke1Egohhech7SEgXyNRpgb8frgf5TWPPPKIzKOKi4vl/t133y3zn9oC0j38NRE+++wz+eycnBy5j3xUfWds4xwElAHIs+j7qELrjDPOkJVVBPzeVFHG937++eflthoGDBgQ9hy9RQvHSDA9++yz4oYb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QXZ1oCkYCQ3nIrHfcccd8j4PPfSQvCfd45xzzhFnnnmmPIZuQ8Srtaz77rtPHH300fL4kUceKQYNGmT5nxl/AzGvfnMUFNiHqIK4OeSQQ0T79u3F119/Ld588015Tm5urjjooINEixYtRLdu3WQrEAobut/FF18s9thjD2m3KDjU56mtt7gPtg877DDxwQcfSFtEKxaOwZ5h308++aS0P6ogHH744TJtIJ3AliG6EN+rVy9x++23iwMPPFAWJoi79tprxcsvvyyaNWsmTjzxRFGvXj3zPc4991z5LNx7//33l6IJ/w/e55133hGtWrWS53311VfikksukdsQhEhjN9xwg2jatKlME3fffbd5T1x7xRVXiKeeeko88cQT8r5+6SKtCRZa0aF8FX+vueYacfLJJ5vHjjvuuLBzIXBGjBghbfn555838/xff/1VHn/88cfFoYceat4LaY+uRXqAvSKNNGjQQF779ttvi7POOku8/vrrYvfdd5eVDJzbp08faZe4z2233SbTF+L//PNPccEFF4hTTjlFHouU56NcOuKII+RxpL8BAwaE/Q9BxakOYqGVQFQDjia0sK0Xdqg1Yx8FEcVdeumlsiDBNgktOobmYBRAtI+M/sUXXzT3VU466SSzBQKiEIWhepzeA90l6jsBteWCSQ1021OFFtkAtTIRzzzzjOjYsaO5P2XKFFkw0P0gvNSavUokoaUexz5VKFAwoXCgY/fcc48sjGgfNXEqzCC09HuprFy50jyOFjqIIDqG/49azHCO2jqgCq33339f3HLLLWH3RQGXn59vXovWMDp2xhlnyNY99Xw/wkLLPqoNRhNa2EbFRD0XLaxIN2jxpbhjjz1WvPrqq3IbQuv66683j6HSQHYJUKmH+FefR+hlAyoK6nF6D/hr6WkIcfr9gohTHcRCy0VQMD3wwAOyRQkGqxqtE6GFxIbz1XsPHjxY1sKxDaGF2jod69KlS1gB0KRJE1kYYhtdP6jxoJZC74SuDxyrSWih60NPdEzqodueKrSwj9YdFACoPZMAQq2abIlAFzTd7/TTT7c8h7AjtNBdh21daB1//PGW55JgiiS0YOdXX3112PmIRwsXWqP0d6PnRxNaOIYuH/V8tKBRiwSOjxkzxjyGVm3qgvQzLLSiAyGCFi204Ko2BpwILXQ7oiVYPR8tt6hgYxtCS22RRS8I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>