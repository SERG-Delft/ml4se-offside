
# Learning Mistakes in Boundary Conditions: A First Exploration
  
## Description: :newspaper:  

Mistakes in boundary conditions are the cause of many bugs in software. 
These mistakes happen when, e.g., 
developers make use of '<' or '>' in cases where they should have used '<=' or '>='. 
Mistakes in boundary conditions are often hard to find and manually detecting
them might be very time-consuming for developers.

And while our community has been proposing (manual) techniques to cope with
mistakes in the boundaries for a long time, the automated detection of
such bugs still remains a challenge. As we show in this paper,
the state-of-the-practice static analysis tools are not able to detect
such bugs.
We conjecture that, for a tool to be able to precisely identify mistakes in boundary conditions, it should be able
to capture the overall context of the source code under analysis. 

In this work, we propose an initial exploring on NLP-based deep learning models that 
learn mistakes in boundary conditions and, later, are able to identify them in unseen code snippets. 
We train and test a model on over 1.5 million code snippets, with and without mistakes in different boundary conditions.
Our model shows an accuracy from 55\% up to 87\%. In the 41 real-world bugs we manually investigated, 
our model shows a more modest accuracy; however, the existing state-of-the-practice linter tools were
able to detect any of the bugs.

We hope this paper can pave the road towards deep learning models that will be able to support developers
in detecting mistakes in boundary conditions.

  
## Data Collection: :floppy_disk:  
* Raw Java large dataset was used from [Code2Seq](https://github.com/tech-srl/code2seq#datasets)    
* Preprocessed dataset available from [Our Google Drive](https://drive.google.com/open?id=1-Ko1ggxP7FIG_VAnDZvkU7iYRviWs25i)  
  
## Setting Up the Environment: :clipboard:  
* Install [conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/)  
* Create a new environment:    
  
 `conda env create -f environment.yml`  
* Update environment:    
  
  `conda env update --file environment.yml  --prune`  
* No GPU support? Then replace     
  
`tensorflow-gpu==2.0.0-rc1` with `tensorflow==2.0.0-rc1`.  
    
## Extracting Custom Code2Vec Model From the Original Weights:  
* Download the [pre-trained model](`https://s3.amazonaws.com/code2vec/model/java14m_model_trainable.tar.gz`).  
* Make sure this is the trainable model.   
* Unzip this folder in the `resources` folder in project root.  
* Download & unzip [custom_model.zip](https://drive.google.com/drive/folders/1HMOsX_Kkk3kYZETyHL5VxsubLfbT4RzH) to `resources/models`  
<!--* Run `ExtractWeightRealCode2Vec.py`. This scripts extrat the weights from the original model   
and transforms them into weights for a `Code2VecCustomModel`.-->
* Run main.py. The custom model can now be used in any tf graph. 
  
 ## Running the model on a single java file
 Assuming you have setup the anaconda environment, you have downloaded the pre trained model and stored it at `resources/models/custom3/model` and you have a java file named `Input.java`. Then you can run the model using the following comand:
 ```python main.py --weights resources/models/custom3/model --input Input.java```
  
## Running the model on a java project. 
* Create a JAR as instructed in `JavaExtractor` folder  
* If there is not one, create a folder called `data` in project root  
* Change paths in the command in next step  
* Run the command in `data` folder `java -cp ~/path/to/project/JavaExtractor/JPredict/target/JavaExtractor-0.0.2-SNAPSHOT.jar JavaExtractor.App --max_path_length 8 --max_path_width 2 --max_contexts 200 --dir path/to/java/project/to/test/ --evaluate > evaluate.txt`  
* If you have extracted the model properly in previous steps you can run `evaluate.py`  
  
## Training the model
* Before we can start the training process we need to encode the dataset into a numpy format.  This can be done using the following command: `python encode_data_set.py --dataset <path_to>/java-large.txt --output <path_to_data_folder>/ --prefix <train, val, or test>`. This will encode the dataset into numpy by createing the following files `path_source_token_idxs.npy`, `path_idxs.npy`, `path_target_token_idxs.npy`, `context_valid_masks.npy` and `Y.npy`. We need to do this for both the training and validation set since both are needed to train a model.
* Once we have encoded the training and validation set we can train the model using the following command: `python train.py --trainset <path_to_data_folder>/<train_prefix> --valset <path_to_data_folder>/<val_prefix> --batch_size 1024> --pre_trained_weights <optional path_to_code2vec model> -freeze <True or False> --output <path_to_weight_output_folder>`. Note that `<path_to_data_folder>/<prefix>` must be the same for the all the 5 created files in the encoding step as the this script loads them all automatically.


## Testing the model.
The model can be tested in 2 ways.

 1. Using the command: `validation_on_testset.py --weights <path_to_model_weights_folder> --dataset <path_to_data_folder>/<test_prefix> --threshold 0.5 --batch_size 1024`. This can be used to test the model against a unseen test set. This script will output the confusion matrix, test_loss, accuracy, f1_score, precision_score and recall_score.
 2.  Using the command: `calc_prediction_stats.py --weights <path_to_model_weights_folder> --dataset <path_to_data_folder>/<test_prefix> --threshold 0.5 --batch_size 1024 --output <path>/stats.csv`. This can be used to calculate the TP, TN, FP and FN per off-by-one type. The result will be stored in the `stats.csv` file.
