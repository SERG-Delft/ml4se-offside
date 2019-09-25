# ML4SA

## Description: 
Replicate the Deep Bugs paper covered in the first lecture and combine it with Code2Vec and explore the benefits of other NN architectures. We plan on picking 2-3 types of bugs and create a model that can indicate how likely a piece of code (single function) is to contain any of those bugs. The bugs we are currently looking at are:

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

## Sources: 
- Pradel, M., & Sen, K. (2018). DeepBugs: A learning approach to name-based bug detection. Proceedings of the ACM on Programming Languages, 2 (OOPSLA), 147.

## Data collection: 
Use already parsed and validated trees from https://github.com/src-d/awesome-machine-learning-on-source-code#datasets and assume them to contain "correct code". We then generate negative examples by removing, adding or changing respective nodes in the trees.