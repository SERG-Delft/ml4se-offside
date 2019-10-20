# JavaExtractor :file_folder:
The JavaExtractor sub-project is meant to
* Process the original Java projects  
* Extract methods from Java files 
* Mutate the off-by-one situations (if there is none, method is discarded)
* Hash context paths (if not provided with `--no_hash` parameter)
* Output method in the following format:  
`label start_terminal,hashed_context_path,end_terminal start_terminal,hashed_context_path,end_terminal ...,...,...`
* This JAR does NOT use vocabulary to translate terminal tokens into integers (only context paths)

### Creating the JAR
* Install [Maven](https://maven.apache.org/)
* Run `mvn install` inside `JPredict/` folder
* `JavaExtractor-0.0.2-SNAPSHOT` will be created in `Jpredict/target/`

### Usage Example
JAR must be already created in order to continue (see above)
#### Generating data for training
* `java -cp path/to/JavaExtractor-0.0.2-SNAPSHOT.jar JavaExtractor.App 
--max_path_length 8 --max_path_width 2 --max_contexts 200 
--dir path/to/training/Java/projects/ > java-large-training.txt`
* This command will have labels in the first column for training

#### Generating data for testing
* `java -cp path/to/JavaExtractor-0.0.2-SNAPSHOT.jar JavaExtractor.App
--max_path_length 8 --max_path_width 2 --max_contexts 200 
--dir path/to/training/Java/projects/ --evaluate > evaluate.txt`
* This command will generate context paths with file and method name in first column in order
to find the faulty method when feeding the context paths to the models