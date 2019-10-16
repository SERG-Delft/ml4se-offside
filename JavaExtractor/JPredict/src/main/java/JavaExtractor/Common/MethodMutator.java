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
        extractedMethods.add(new ExtractedMethod(method, "", App.noBugString));
        List<BinaryExpr> allMutationCandidates = method.getNodesByType(BinaryExpr.class).stream()
                .filter(containsOffByOne())
                .collect(Collectors.toList());
        
        for (ContainingNode containingNode : ContainingNode.values()) {
            List<BinaryExpr> mutationCandidatesForCategory = allMutationCandidates.stream()
                    .filter(SearchUtils.isContainedBy(containingNode.getNodeClass()))
                    .collect(Collectors.toList());
            if (mutationCandidatesForCategory.size() != 0) {
                extractedMethods.add(mutateMethod(method, mutationCandidatesForCategory, containingNode.toString()));
            }
            allMutationCandidates.removeAll(mutationCandidatesForCategory);
        }

        printCandidatesNotConsidered(method, allMutationCandidates);
        
        return extractedMethods;
    }
    
    private ExtractedMethod mutateMethod(MethodDeclaration method, List<BinaryExpr> mutationCandidates, String containingNode) {
        MethodDeclaration mutatedMethod = (MethodDeclaration) method.clone();

        int mutationIndex = rand.nextInt(mutationCandidates.size());
        String operator = mutateExpression(mutationCandidates.get(mutationIndex));


        return new ExtractedMethod(mutatedMethod, operator, containingNode);
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
