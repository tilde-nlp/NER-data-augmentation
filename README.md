# NER-data-augmentation

This project contains sript and datasets for converting grammatically correct Latvian dataset into augmented dataset that allows to train robust NER. Our model trained on augmented dataset achieves an average F1 score of 83.5 on grammatically correct text, while keeping good performance (79 F1) on noisy texts.

In this project, https://github.com/LUMII-AILab/FullStack/tree/master/NamedEntities dataset is used, with modifications: 
 - we convert format to one more suited for NER, by keeping only words and NER annotations;  
 - we use only outer entities;  
 - convert this 9-entity tagset  to a 4-entity tagset in accordance with MUC-7 (Chinchor, 1998) entity names subtask, keeping PERSON and ORGANIZATION, joining LOCATION and GPE into LOCATION, and joining the rest of the classes into the MISC category  

The converted dataset is used to introduce various errors into it using provided script augment_data.py.
augment_data.py takes one argument - path to the folder with clean data in conllike format.
The output of this script is folders with the same dataset with errors included.
Datasets augmented this way may be used to train a NER model which would work well with test data containing the same types of errors. I.e. if test dataset contains sentences in lowercase, then the NER model trained using the lowercased dataset will perform well.
 
# Publications
---------

