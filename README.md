# ML4SA

## Description: 
Replicate the Deep Bugs paper covered in the first lecture and combine it with Code2VecCustomModel and explore the benefits of other NN architectures. We plan on picking 2-3 types of bugs and create a model that can indicate how likely a piece of code (single function) is to contain any of those bugs. The bugs we are currently looking at are:

- Missing (or unnecessary) negation
- Mixed and/or operators
- (Mixed <,>,= symbols)

Other considered types of bugs

- For loops
- Incorrect increment/decrement
- Incorrect termination statement
- Incorrect initialization
- Missing bit-shift
- Swapped function arguments

The input to the model would be an AST of a single function and the output would be the percentage likelihood of each specific bug.

##Sources: 
- Pradel, M., & Sen, K. (2018). DeepBugs: A learning approach to name-based bug detection. Proceedings of the ACM on Programming Languages, 2 (OOPSLA), 147.

##Data collection: 
Use already parsed and validated trees from https://github.com/src-d/awesome-machine-learning-on-source-code#datasets and assume them to contain "correct code". We then generate negative examples by removing, adding or changing respective nodes in the trees.

##Setting up env:
 
 create a new env:
 
 `conda env create -f environment.yml`
 
 update env:
 
  `conda env update --file environment.yml  --prune`
  
  No GPU support? Then replace `tensorflow-gpu==2.0.0-rc1` with `tensorflow==2.0.0-rc1`.
  
##Extracting custom code2vec model from the original weights:
Step 1: Download the pre trained model from `https://s3.amazonaws.com/code2vec/model/java14m_model_trainable.tar.gz`.
Make sure this the trainable model. Then unzip this folder in the `resources` folder.

Step 2: Run `ExtractWeightRealCode2Vec.py`. This scripts extrat the weights from the original model and transforms them into weights for a `Code2VecCustomModel`.

The custom model can now be used in the any tf graph. 


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

And finaly you can run the model using:
`python code2vec.py --load models/java14m_trainable/saved_model_iter8 --predict`