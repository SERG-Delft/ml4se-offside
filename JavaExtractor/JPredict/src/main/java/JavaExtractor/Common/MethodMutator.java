package JavaExtractor.Common;

import JavaExtractor.App;
import JavaExtractor.Common.Statistics.ContainingNode;
import JavaExtractor.FeaturesEntities.ExtractedMethod;
import com.github.javaparser.ast.body.MethodDeclaration;
import com.github.javaparser.ast.expr.BinaryExpr;

import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Paths;
import java.util.*;
import java.util.stream.Collectors;

import static JavaExtractor.Common.SearchUtils.containsOffByOne;

public class MethodMutator {
    private final Random rand = new Random();

    public List<ExtractedMethod> processMethod(MethodDeclaration method) {
        List<ExtractedMethod> extractedMethods = new ArrayList<>();
        StringBuilder mutatedNodes = new StringBuilder("#");

        
        for (ContainingNode containingNode : ContainingNode.values()) {
            MethodDeclaration mutatedMethod = (MethodDeclaration) method.clone();
            List<BinaryExpr> allMutationCandidates = mutatedMethod.getNodesByType(BinaryExpr.class).stream()
                    .filter(containsOffByOne())
                    .collect(Collectors.toList());
            List<BinaryExpr> mutationCandidatesForCategory = allMutationCandidates.stream()
                    .filter(SearchUtils.isContainedBy(containingNode.getNodeClass()))
                    .collect(Collectors.toList());
            if (mutationCandidatesForCategory.size() != 0) {
                ExtractedMethod extractedMethod = mutateMethod(mutatedMethod, mutationCandidatesForCategory, containingNode.toString());
                extractedMethods.add(extractedMethod);
                mutatedNodes.append(containingNode.toString()).append(extractedMethod.getOriginalOperator()).append("#");
            }
//            allMutationCandidates.removeAll(mutationCandidatesForCategory);
        }

        if  (extractedMethods.size() != 0) {
            extractedMethods.add(new ExtractedMethod(method, mutatedNodes.toString(), App.noBugString));
        }

//        printCandidatesNotConsidered(method, allMutationCandidates);
        
        return extractedMethods;
    }
    
    private ExtractedMethod mutateMethod(MethodDeclaration method, List<BinaryExpr> mutationCandidates, String containingNode) {

        int mutationIndex = rand.nextInt(mutationCandidates.size());
        String operator = mutateExpression(mutationCandidates.get(mutationIndex));


        return new ExtractedMethod(method, operator, containingNode);
    }

    private String mutateExpression(BinaryExpr expression) {
        BinaryExpr.Operator operator = expression.getOperator();
        if (operator.equals(BinaryExpr.Operator.greater)) expression.setOperator(BinaryExpr.Operator.greaterEquals);
        else if (operator.equals(BinaryExpr.Operator.greaterEquals)) expression.setOperator(BinaryExpr.Operator.greater);
        else if (operator.equals(BinaryExpr.Operator.lessEquals)) expression.setOperator(BinaryExpr.Operator.less);
        else if (operator.equals(BinaryExpr.Operator.less)) expression.setOperator(BinaryExpr.Operator.lessEquals);
        return operator.name();
    }

    private void printCandidatesNotConsidered(MethodDeclaration method, List<BinaryExpr> candidatesNotConsidered) {
        if (candidatesNotConsidered.size() == 0) return;

        StringBuilder sb = new StringBuilder();
        String lineSeparator = System.lineSeparator();
        for (BinaryExpr binaryExpr: candidatesNotConsidered) {
            sb.append("#############################################").append(lineSeparator);
            sb.append("A new type of containing node found: ").append(SearchUtils.getContainingNodeType(binaryExpr)).append(lineSeparator);
            sb.append("Node").append(lineSeparator);
            sb.append(binaryExpr).append(lineSeparator);
            sb.append("Method").append(lineSeparator);
            sb.append(method).append(lineSeparator);
        }
        try {
            FileWriter fw = new FileWriter(Paths.get(System.getProperty("user.dir"),  "newContainingNodes.txt").toString());
            fw.write(sb.toString());
            fw.close();
        } catch (IOException e) {
            e.printStackTrace();
        }

    }
}
