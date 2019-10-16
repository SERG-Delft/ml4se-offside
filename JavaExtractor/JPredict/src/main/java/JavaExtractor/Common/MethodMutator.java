package JavaExtractor.Common;

import com.github.javaparser.ast.body.MethodDeclaration;
import com.github.javaparser.ast.expr.BinaryExpr;

import java.util.List;
import java.util.Random;
import java.util.stream.Collectors;

import static JavaExtractor.Common.SearchUtils.containsOffByOne;

public class MethodMutator {
    private final Random rand = new Random();

    public MethodDeclaration mutateMethod(MethodDeclaration method) {
        MethodDeclaration mutatedMethod = (MethodDeclaration) method.clone();

        List<BinaryExpr> mutationCandidates = mutatedMethod.getNodesByType(BinaryExpr.class).stream()
                .filter(containsOffByOne())
                .collect(Collectors.toList());

        int mutationIndex = rand.nextInt(mutationCandidates.size());
        mutateExpression(mutationCandidates.get(mutationIndex));


        return mutatedMethod;
    }

    private void mutateExpression(BinaryExpr expression) {
        BinaryExpr.Operator operator = expression.getOperator();
        if (operator.equals(BinaryExpr.Operator.greater)) expression.setOperator(BinaryExpr.Operator.greaterEquals);
        else if (operator.equals(BinaryExpr.Operator.greaterEquals)) expression.setOperator(BinaryExpr.Operator.greater);
        else if (operator.equals(BinaryExpr.Operator.lessEquals)) expression.setOperator(BinaryExpr.Operator.less);
        else if (operator.equals(BinaryExpr.Operator.less)) expression.setOperator(BinaryExpr.Operator.lessEquals);
    }
}
