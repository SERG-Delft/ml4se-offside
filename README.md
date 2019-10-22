# Using Distributed Representation of Code for Bug Detection :blue_book:

## Description: :newspaper:
The aim of this project is to use [Code2Vec](www.code2vec.org) model and replace the final layer used for method naming 
with a layer for bug detection. More specifically, we train the new model to detect 
[off-by-one](https://en.wikipedia.org/wiki/Off-by-one_error) errors. 

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
* Run `ExtractWeightRealCode2Vec.py`. This scripts extrat the weights from the original model 
and transforms them into weights for a `Code2VecCustomModel`.
* The custom model can now be used in the any tf graph. 
* Run `main.py` to see an example


## Generating Test Data
* Create a JAR as instructed in `JavaExtractor` folder
* If there is not one, create a folder called `data` in project root
* Change paths in the command in next step
* Run the command in `data` folder `java -cp ~/path/to/project/JavaExtractor/JPredict/target/JavaExtractor-0.0.2-SNAPSHOT.jar JavaExtractor.App --max_path_length 8 --max_path_width 2 --max_contexts 200 --dir path/to/java/project/to/test/ --evaluate > evaluate.txt`
* If you have extracted the model properly in previous steps you can run `evaluate.py`

<!---
##Setting up the original code2vec project.
Run the following commands (best done in a venv):
```
git clone https://github.com/tech-srl/code2vec
cd code2vec

pip install -r requirements.txt
```
Make sure you have the correct TensorFlow version as specified in the `requirements.txt` file. As newer version do not work.


Now you have to download a pretrained model and extract it into `/code2vec/models`. Beaware this must be the trainable model.
On linux this can be done using:
```
wget https://s3.amazonaws.com/code2vec/model/java14m_model_trainable.tar.gz
tar -xvzf java14m_model_trainable.tar
```

And finally you can run the model using:
`python code2vec.py --load models/java14m_trainable/saved_model_iter8 --predict`
-->
